"""
Created on Apr 9, 2023

@author: fred
"""
from pathlib import Path

from git.exc import GitCommandError
from git.repo import Repo
from github import Github
from github.GithubException import GithubException

from .data.constants import REMOTE_REPO

REPO_PATH = Path(__file__).parents[1]


def get_branch_name(github_client: Github) -> str:
    """Generate a branch name for the changes"""
    github_user = github_client.get_user().login
    return f"updates/{github_user}"


def commit_push_pr(github_pat: str) -> None:
    """Commit changes, push to remote, and open a PR if one doesn't exist"""
    github_client = Github(github_pat)
    github_user = github_client.get_user().login

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
            if repo.is_dirty():
                commit_push_pr(github_pat)
            else:
                repo.git.checkout("main")
                remote_repo.pull()

    else:
        raise ValueError(
            "You're on a branch that cannot be automatically managed."
            + f" Check out `main` or `{branch_name}`, or remove the `--github-pat` argument."
        )
