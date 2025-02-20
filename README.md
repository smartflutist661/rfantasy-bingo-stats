# What It Does

This script is designed to make regularizing title/author pairs (books) from data relatively painless.
It uses fuzzy matching to compare an instance of "{title} /// {author}" with every other book,
retrieving the best matches from books that have already been regularized or from books that have not yet had a similar comparison run.

# How to Use

## Clone the Repository

### Linux/Unix

`git` is available in the package manager for most distributions.

### Windows

The easiest way to get `git` is to install [Git for Windows](https://gitforwindows.org/), which comes with a terminal, Git Bash.

### Cloning

Find the green `Code` button towards the top right of your screen. Open a terminal (Git Bash or your preferred), navigate to the folder you want to work in, and `git clone https://github.com/smartflutist661/rfantasy-bingo-stats.git`. You can also use SSH, if you have a key set up.

## Install `uv`

To install `uv`, see [the documentation](https://docs.astral.sh/uv/getting-started/installation/), abbreviated below.

### Linux/Unix

Run `curl -LsSf https://astral.sh/uv/install.sh | sh`. 

### Windows

Run `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`.

## Running the Script

Open a terminal at the top level of the cloned repository (likely `rfantasy-bingo-stats`). Run `uv run clean-data`. You will see a list of choices that looks something like this:

```
Processing possible misspellings. You may hit ctrl+C at any point to exit, or enter `e` at the prompt. Progress will be saved.

Matching Asher Elbein, Tiffany Turrill:
Choose the best version:
[0] Asher Elbein, Tiffany Turrill
[1] Tiffany Turrill

[r] Remove one or more matches
[c] Enter a better version of all
[e] Save and exit
Selection: 
```

Remove any matches that are not actually duplicates of the primary item by entering `r`, then selecting the appropriate numbers.
Enter `d` when you have removed all of the non-duplicates to return to this selection.
(You can enter `d` at any time and then select `r` again, which can be useful for particularly long lists of bad matches.)
If you remove all of the potential matches, the primary item will be recorded as unique.
Future matches of the primary item with any removed items are automatically ignored.

Enter the number of the best (preferably canonical) version of the remaining matches,
or enter `c` to mark all of the potential matches as a duplicate of a value not present in the match list.
For multiple authors, be sure they are comma-separated. For books, be sure to use the appropriate separator format.

Once you've made the final selection, you'll see something like this,
so you can double-check the decisions you've made and fix them manually if you hit the wrong button or some such.

```
Sweep of the Heart by Ilona Andres recorded as duplicate of Sweep of the Heart by Ilona Andrews
```

You can exit at any time using Ctrl + C to kill the script, or by entering `e` (really, anything but a valid selection) at the selection prompt.
There are two phases of author cleaning and one of book cleaning,
then the script will go on to calculate stats on the updated version of the bingo data,
even if cleaning is not complete.

For instructions on sharing your updates, see the guide to CONTRIBUTING.

### Options

Run `uv run clean-data -h` to see a list of options.

### Adjusting the Match Sensitivity

I believe the default sensitivity is set reasonably well.
However, if you'd like to make matching more or less sensitive, pass the argument `--match-score` to the command.
The default value is 90. This is approximately a percentage; adjust accordingly.
For example, to make title/author combinations match only if they're already almost perfect,
run `uv run clean-data --match-score 99`.
On the other hand, to make some pretty bad matches appear, run `uv run clean-data --match-score 80`.

### Rescanning previously-unmatched books

If you'd like to go over books that were previously thought to be unique with a lower match sensitivity,
pass `--rescan-non-dupes` to the module. Because this set gets smaller each time you find a match,
processing over lower and lower `match-score`s seems likely to be a useful strategy,
though you'll reach a point of diminishing returns where most matches are just noise (at which point, congrats, I guess it's done!).
