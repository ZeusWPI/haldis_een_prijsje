from __future__ import print_function

import os
import pathlib

import git
import giteapy

import tomllib
from pprint import pprint

# import mattermost_communication

with open("config.toml", mode="rb") as config_toml:
    config = tomllib.load(config_toml)

# https://docs.gitea.com/api/1.20/


REPO_FOLDER = config["gitea"]["local_repo_folder"]
TOKEN = config["gitea"]["access_token"]

GIT_ORG = config["gitea"]["remote_org"]
GIT_REPO = config["gitea"]["remote_repo"]


def init_sync():
    repo = get_repo()

    configuration = giteapy.Configuration()
    configuration.host = f"https://{config['gitea']['server_url']}/api/v1"
    configuration.api_key["token"] = config["gitea"]["access_token"]
    configuration.debug = False

    # create an instance of the API class
    api_instance = giteapy.RepositoryApi(giteapy.ApiClient(configuration))

    return repo, api_instance


def get_repo():
    if os.path.exists(REPO_FOLDER):
        print("Repo already exists")
        repo = git.Repo(REPO_FOLDER)
    else:
        print("Cloning repo")
        repo = git.Repo.clone_from(
            f"https://{TOKEN}@{config['gitea']['server_url']}/{GIT_ORG}/{config['gitea']['remote_repo']}",
            REPO_FOLDER,
        )
        with repo.config_writer() as cw:
            cw.set_value("user", "email", config["gitea"]["commit_user_email"])
            cw.set_value("user", "name", config["gitea"]["commit_user_name"])
    repo.remotes.origin.fetch()
    return repo


def clear_repo(repo):
    repo.git.restore("--staged", "--", "*")
    repo.git.restore("--", "*")


def prune_remote(repo):
    """
    Prunes stale remote branches for the 'origin' remote.
    """
    print("Pruning stale remote branches...")
    repo.git.remote("prune", "origin")
    print("Pruning complete.")


def delete_stale_local_branches(repo):
    """
    Deletes stale local branches that no longer exist on the remote.
    """
    print("Checking for stale local branches...")
    remote_refs = [ref.strip() for ref in repo.git.branch("-r").split("\n")]
    local_branches = [ref.strip("* ").strip() for ref in repo.git.branch().split("\n")]

    # Identify local branches that are no longer on the remote
    for branch in local_branches:
        remote_branch_ref = f"origin/{branch}"
        if branch != "master" and remote_branch_ref not in remote_refs:
            print(f"Deleting stale local branch: {branch}")
            repo.git.branch("-D", branch)  # Force delete the branch
    print("Local cleanup complete.")


def checkout_branch(repo, branch_name):
    repo.git.switch("master")
    prune_remote(repo)
    delete_stale_local_branches(repo)
    # status = repo.git.status()
    # print("\nGit Status:\n", status)
    repo.git.fetch("--all")
    # Get a list of all remote branches
    remote_branches = [ref.strip() for ref in repo.git.branch("-r").split("\n")]
    # print(remote_branches)
    remote_branch_full = f"origin/{branch_name}"
    if remote_branch_full in remote_branches:
        # If the branch exists on the remote, check it out and pull changes
        print(f"Checking out existing branch: {branch_name}")
        repo.git.checkout(branch_name)
        repo.git.pull("origin", branch_name)
    else:
        # If the branch doesn't exist, create it and push to the remote
        print(f"Branch {branch_name} does not exist on origin. Creating the branch.")
        repo.git.checkout("-b", branch_name)
        repo.git.push("-u", "origin", branch_name)
    # status = repo.git.status()
    # print("\nGit Status:\n", status)
    if branch_name in repo.remotes.origin.refs:
        repo.heads[branch_name].set_tracking_branch(
            repo.remotes.origin.refs[branch_name]
        )
        repo.remotes.origin.pull()


def sync_file(repo, api_instance, file_info):
    path = file_info["local_file_path"]
    sync_to = file_info["metadata"]["sync-to"]

    # branch_name = f"hlds-sync_{sync_to}"
    branch_name = f"haldis_sync_{os.path.basename(sync_to).replace(".hlds", "")}"
    print(f"Starting sync of {path}")
    clear_repo(repo)
    print(f"  Checking out onto branch: {branch_name}")
    checkout_branch(repo, branch_name)
    # return  # barrier to stop PR's while testing TODO remove
    with open(path) as r:
        # pathlib.Path(f"{REPO_FOLDER}/{sync_to}").mkdir(
        #     parents=True, exist_ok=True
        # )
        print(sync_to)
        with open(f"{sync_to}", "w") as w:
            w.write(r.read())
    if repo.git.diff() or repo.untracked_files:
        print("  Note has changes. Making a commit.")
        print("working tree dir: ", repo.working_tree_dir)
        repo.index.add([os.path.basename(sync_to)])
        repo.index.commit("Updating file with hlds version")
        print(f"  Pushing to branch: {branch_name}")
        repo.git.push("-u", "origin", branch_name)

        resp = api_instance.repo_list_pull_requests(GIT_ORG, GIT_REPO, state="open")
        open_branch_requests = [
            r for r in resp if r.head.ref == branch_name and r.state == "open"
        ]
        if len(open_branch_requests) == 0:
            branch_requests = [r for r in resp if r.head.ref == branch_name]
            if len(branch_requests) > 0:
                print(
                    "  Creating a new merge request to update the git menu with the new version from the hlds menu."
                )
                api_instance.repo_create_pull_request(
                    GIT_ORG,
                    GIT_REPO,
                    body=giteapy.CreatePullRequestOption(
                        base="master",
                        head=branch_name,
                        title=f"[hlds sync] Update document {sync_to}",
                    ),
                )
            else:
                print("  Creating a new merge request to add the Menu to git.")
                api_instance.repo_create_pull_request(
                    GIT_ORG,
                    GIT_REPO,
                    body=giteapy.CreatePullRequestOption(
                        base="master",
                        head=branch_name,
                        title=f"[hlds sync] Add document {sync_to}",
                    ),
                )
        else:
            print("  Merge request was already open.")
    else:
        print("  Menu has no changes.")
