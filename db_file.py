import hashlib
import json
import os
from os.path import exists
from typing import Dict, List

db_filename = "db.json"


def init_db():
    file_exists = exists(db_filename)
    if not file_exists:
        print("Initializing json file database")
        with open(db_filename, "w") as db_file:
            db_file.write("{}")


init_db()


def _load_db():
    with open(db_filename, "r") as db_file:
        db = json.loads(db_file.read())
        return db


def _save_db(db):
    with open(db_filename, "w") as db_file:
        db_file.write(json.dumps(db, indent=4))


def calculate_file_hash(file_path: str) -> str:
    """
    Calculate the SHA256 hash of a file's contents.
    :param file_path: Path to the file
    :return: Hexadecimal hash as a string
    """
    hasher = hashlib.sha256()
    with open(file_path, "rb") as file:
        while chunk := file.read(8192):  # Read file in chunks
            hasher.update(chunk)
    return hasher.hexdigest()


def is_file_different(hlds_file: str, menu_file: str) -> bool:
    """
    Compare two files based on their SHA256 hashes to determine if they are different.
    :param hlds_file: Path to the file in the hlds_menus directory
    :param menu_file: Path to the file in the menus directory
    :return: True if the files are different, False otherwise
    """
    hlds_hash = calculate_file_hash(hlds_file)
    menu_hash = calculate_file_hash(menu_file)
    return hlds_hash != menu_hash


def dos2unix(path: str) -> str:
    """
    Converts Windows-style backslashes in a file path to Unix-style forward slashes.
    :param path: The input file path (string)
    :return: The normalized file path with forward slashes
    """
    return path.replace("\\", "/")


def get_manual_file_mapping() -> Dict[str, str]:
    """
    Creates a manual mapping of file names between the hlds_menus directory and the menus directory.
    :return: A dictionary mapping file paths from hlds_menus to menus
    """
    hlds_dir = "hlds_files"
    menu_dir = "menus"

    # Manual mapping of file names
    file_mapping = {
        dos2unix(os.path.join(hlds_dir, "bicyclette.hlds")): dos2unix(os.path.join(menu_dir, "la_bicylette.hlds")),
        dos2unix(os.path.join(hlds_dir, "bocca_ovp.hlds")): dos2unix(os.path.join(menu_dir, "bocca_ovp.hlds")),
        dos2unix(os.path.join(hlds_dir, "metropol.hlds")): dos2unix(os.path.join(menu_dir, "pitta_metropol.hlds")),
        dos2unix(os.path.join(hlds_dir, "pizza_donna.hlds")): dos2unix(os.path.join(menu_dir, "prima_donna.hlds")),
        dos2unix(os.path.join(hlds_dir, "s5.hlds")): dos2unix(os.path.join(menu_dir, "s5.hlds")),
        dos2unix(os.path.join(hlds_dir, "simpizza.hlds")): dos2unix(os.path.join(menu_dir, "simpizza.hlds")),
        # Add more mappings here as needed
    }

    return file_mapping


def get_mapped_path(file_path: str) -> str:
    """
    Maps a given file path using the manual mapping or returns the same path if not in the mapping.
    Ensures the returned path uses forward slashes.
    :param file_path: The input file path
    :return: The mapped file path or the original path
    """
    file_mapping = get_manual_file_mapping()
    normalized_path = dos2unix(file_path)
    return file_mapping.get(normalized_path, normalized_path)


def test_file_comparison():
    """
    Compares all files based on the manual mapping and prints whether they are different or identical.
    """
    hlds_dir = "hlds_files"
    menu_dir = "menus"

    # Get a list of files in the `hlds_files` directory
    hlds_files = [
        dos2unix(os.path.join(hlds_dir, f))
        for f in os.listdir(hlds_dir) if os.path.isfile(os.path.join(hlds_dir, f))
    ]

    for hlds_file in hlds_files:
        menu_file = get_mapped_path(hlds_file)

        if not os.path.exists(hlds_file):
            print(f"{hlds_file} does not exist. Skipping...")
            continue

        if not os.path.exists(menu_file):
            print(f"{menu_file} does not exist. File {hlds_file} is new.")
            add_file_to_db(hlds_file, menu_file)  # Add the new file to the database
            continue

        if is_file_different(hlds_file, menu_file):
            print(f"Files {hlds_file} and {menu_file} are different.")
            add_file_to_db(hlds_file, menu_file)  # Add the different file to the database
        else:
            print(f"Files {hlds_file} and {menu_file} are identical.")


def add_file_to_db(hlds_file, menu_file):
    """
    Adds a new file to the database if it is different.
    :param hlds_file: The file from the hlds_menus directory.
    :param menu_file: The file from the menus directory.
    """
    db = _load_db()
    files = db.get("files", {})

    # Add or update the file entry in the database
    files[hlds_file] = {
        "local_file_path": hlds_file,
        "metadata": {"sync-to": menu_file},
    }

    db["files"] = files
    _save_db(db)
    print(f"Added {hlds_file} to the database as different.")


def get_latest_sync_time() -> int:
    db = _load_db()
    return db.get("latest_sync_time", 0)


def set_latest_sync_time(le_date) -> None:
    db = _load_db()
    db["latest_sync_time"] = le_date
    _save_db(db)


def get_files() -> List[str]:
    db = _load_db()
    files = db.get("files", {})
    return files


def set_local_file_path(file_id, local_file_path):
    db = _load_db()
    file = db["files"][file_id]
    file["local_file_path"] = local_file_path
    _save_db(db)
    return file


test_file_comparison()
