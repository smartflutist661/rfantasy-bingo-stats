# Basics

If you have not done so, run `git checkout -b [some-meaningful-name]`, where `some-meaningful-name` is a meaningful name you choose to represent your updates.
Run `git push -u origin [some-meaningful-name]` to send these changes to GitHub.

## Pushing changes

After you've run the script, run:

```
git add -u
git commit -m "a useful message"
git push
```

Ideally, you then go to GitHub, create a Pull Request into `main`, and your updates become available for others to use after approval. Admins of the repository can also merge changes to `main` manually, and email alerts are set up for pushes.

# For developers

## Pre-commit

There's a very basic `pyproject.toml` with settings for mypy, pylint, black, and isort, and a `pre-commit` shell script (intended for bash, but should be agnostic) that you can run before submitting a pull request. The requirements for the pre-commit script are included in `requirements.txt`. An identical sequence is run as an Action for each pull request.

The only standard not currently enforced by this script is using relative imports.
