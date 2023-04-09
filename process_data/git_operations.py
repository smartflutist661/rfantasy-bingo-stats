"""
Created on Apr 9, 2023

@author: fred
"""
from pathlib import Path
from time import sleep

from git.exc import GitCommandError
from git.repo import Repo
from github import Github
from github.GithubException import GithubException
from requests import exceptions

from .data.constants import REMOTE_REPO

REPO_PATH = Path(__file__).parents[1]


def get_github_user(github_client: Github) -> str:
    """Attempt to retrieve the GitHub username"""
    long_retries = 0
    while True:
        try:
            return github_client.get_user().login
        except exceptions.ConnectionError as exc:
            long_retries += 1
            if long_retries > 3:
                raise exc
            print("Failed to connect to GitHub. Retrying in 10 seconds.")
            sleep(10)


def get_branch_name(github_client: Github) -> str:
    """Generate a branch name for the changes"""

    github_user = get_github_user(github_client)
    return f"updates/{github_user}"


def commit_push_pr(github_pat: str) -> None:
    """Commit changes, push to remote, and open a PR if one doesn't exist"""
    github_client = Github(github_pat)
    github_user = get_github_user(github_client)

    repo = Repo(REPO_PATH)

    branch_name = get_branch_name(github_client)

    try:
        repo.git.branch(branch_name)
    except GitCommandError:
        pass
    repo.git.checkout(branch_name)

    repo.git.add(update=True)
    repo.index.add(repo.untracked_files)

    repo.index.commit(f"Auto-commit changes from {github_user}")

    repo.git.push("-u", repo.remote(), branch_name)

    github_repo = github_client.get_repo(REMOTE_REPO)
    prs = github_repo.get_pulls(state="open", base="main", head=branch_name)
    if len(list(prs)) == 0:
        github_repo.create_pull(
            title=f"Merge changes from {github_user}", body="", base="main", head=branch_name
        )
        print("Created a pull request to merge your latest changes.")
    else:
        print("New changes pushed to an existing pull request.")


def synchronize_github(github_pat: str) -> None:
    """Synchronize local repository with remote, if possible"""
    github_client = Github(github_pat)

    repo = Repo(REPO_PATH)

    branch_name = get_branch_name(github_client)
    remote_repo = repo.remote()

    print(repo.active_branch)
    if str(repo.active_branch) == "main":
        remote_repo.pull()
    elif str(repo.active_branch) == branch_name:
        github_remote_repo = github_client.get_repo(REMOTE_REPO)
        try:
            github_remote_repo.get_branch(branch=branch_name)
        except GithubException:
            print("Remote branch does not exist.")
            if repo.is_dirty():
                print("Repository is dirty. Attempting to merge `main`.")
                repo.git.pull("main")
                commit_push_pr(github_pat)
            else:
                print("Repository is clean. Checking out `main` and deleting existing branch.")
                repo.git.checkout("main")
                repo.git.pull("-p")
                repo.git.branch("-d", branch_name)
    else:
        raise ValueError(
            "You're on a branch that cannot be automatically managed."
            + f" Check out `main` or `{branch_name}`, or remove the `--github-pat` argument."
        )

    print("Pulling current branch.")
    repo.git.pull()
