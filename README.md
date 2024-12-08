# What It Does

This script is designed to make regularizing title/author pairs from data relatively painless. It uses fuzzy matching to compare an instance of "{title} by {author}" with every other title/author combination, retrieving the best match either from pairs that have already been regularized (preferentially) or from pairs that have not yet had a similar comparison run.

# How to Use

## Clone the Repository

### Acquiring `git`

If you already have `git`, skip to the next section.

#### Linux/Unix

`git` is available in the package manager for most distributions.

#### Windows

The easiest way to get `git` is to install [Git for Windows](https://gitforwindows.org/), which comes with a terminal, Git Bash.

### Cloning

Find the green `Code` button towards the top right of your screen. Open a terminal (Git Bash or your preferred), navigate to the folder you want to work in, and `git clone https://github.com/smartflutist661/rfantasy-bingo-stats.git`. You can also use SSH, if you have a key set up.

## Install Python (>=3.10) and Dependencies

### Install Python

If you already have Python 3.10 installed and you can run it from your terminal of choice, you can skip this step.

#### Linux/Unix

It's likely your distro has Python 3.10 available. Follow [the instructions](https://docs.python.org/3/using/unix.html) in the Python documentation if running `python --version` in your terminal of choice doesn't show at least 3.10.

#### Windows

You'll likely need to install Python. Download the installer from the [Python website](https://www.python.org/downloads/) and follow the wizard.

### Install Dependencies

From a terminal at the top level of the cloned repository (likely `rfantasy-bingo-stats`), run `pip install -r requirements.txt`. (If you need to use a virtual environment, you should know; otherwise this should not conflict with the system Python.)

## Running the Script

Open a terminal at the top level of the cloned repository (likely `rfantasy-bingo-stats`). Run `python -m process_data`. You will see a list of choices that looks something like this:

```
Processing possible misspellings. You may hit ctrl+C at any point to exit, or enter `e` at the prompt. Progress will be saved.

Tentative match found: Sweep of the Heart by Ilona Andres -> Sweep of the Heart by Ilona Andrews, score 99
Choose the best version:
[1] Sweep of the Heart by Ilona Andres
[2] Sweep of the Heart by Ilona Andrews
[3] Not a match
[e] Save and exit
Selection: 
```

Type the value of your selection in the prompt and hit Enter. You'll see something like

```
Sweep of the Heart by Ilona Andres recorded as duplicate of Sweep of the Heart by Ilona Andrews
```

You can exit at any time using Ctrl + C to kill the script, or by entering `e` (really, anything but a valid selection) at the selection prompt. The script will go on to calculate stats on the updated version of the bingo data, which may or may not be complete.

For instructions on sharing your updates, see the guide to CONTRIBUTING.

### Options

Run `python -m process_data -h` to see a list of options.

### Adjusting the Match Sensitivity

I believe the default sensitivity is set reasonably well. However, if you'd like to make matching more or less sensitive, pass the argument `--match-score` to the command. The default value is 90. This is approximately a percentage; adjust accordingly. For example, to make title/author combinations match only if they're already almost perfect, run `python -m process_data --match-score 99`. On the other hand, to make some pretty bad matches appear, run `python -m process_data --match-score 80`.

### Rescanning previously-unmatched books

If you'd like to go over books that were previously thought to be unique with a lower match sensitivity, pass `--rescan-non-dupes` to the module. Because this set gets smaller each time you find a match, processing over lower and lower `match-score`s seems likely to be a useful strategy, though you'll reach a point of diminishing returns where most matches are just noise (at which point, congrats, I guess it's done!).
