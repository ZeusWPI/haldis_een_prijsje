import os

# Directory path
directory_path = "C:/Users/Gebruiker/Desktop/ugent/zeus/2025/haldis_menus/menus"

# List of .hlds files without extension
hlds_files = [
    os.path.splitext(file)[0]
    for file in os.listdir(directory_path)
    if file.endswith(".hlds")
]

for file_name in hlds_files:
    if file_name not in ["pitta_metropol", "la_bicylette"]:
        print(file_name)