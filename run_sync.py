import traceback

import db
# import dir_utils
# import mattermost_client
# import mattermost_communication
import sync_gitmate as sync


def sync_files_to_gitea():
    repo, api_handler = sync.init_sync()
    # print(db.get_files().items())
    for file_id, file_info in db.get_files().items():
        # print(file_id, file_info)
        try:
            sync.sync_file(repo, api_handler, file_info)
        except Exception as e:
            print("Critical error: Failed to sync file to Gitea")
            traceback.print_exc()


def sync_gitmate():
    print()
    print("================================================")
    print("== Syncing files to git ==")
    sync_files_to_gitea()
    print()
    return {
        "synced": "success"
    }


if __name__ == "__main__":
    print()
    print("================================================")
    print("== Syncing files to git ==")
    sync_files_to_gitea()
    print()
