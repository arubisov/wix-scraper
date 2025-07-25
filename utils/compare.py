"""
PATH: ./wix-scraper/utils/

Functions:
- prompt_yes_no(message): Repeatedly prompts the user for a yes/no input and returns True or False.
- get_directory_input(prompt_text): Prompts the user for a valid directory path and validates its existence.
- is_timestamped_dir(name): Returns True if the given directory name matches the YYYYMMDD-HHMMSS timestamp format.
- run_comparison(dir1, dir2): Confirms timestamp sort order and prompts user for comparison approval.
- main(old_dir, new_dir): Executes hashing and diff generation between the given directories.
- cli(): CLI interface for directory input, comparison validation, and main execution call.
"""


import re, argparse, logging
from pathlib import Path
from utils.configs.config import setup_logger
from utils.diffscripts.hashcomparator import hash_and_compare
from utils.diffscripts.diffgen import generate_diff_report
from utils.yn import prompt_yes_no

lgg = setup_logger(logging.INFO)


def get_directory_input(prompt_text: str) -> Path:
    while True:
        path = Path(input(f"{prompt_text}: ").strip()).resolve()
        if path.is_dir():
            return path
        lgg.er("That path does not exist. Try again.")


def is_timestamped_dir(name: str) -> bool:
    return bool(re.match(r"^\d{8}-\d{6}$", name))


def run_comparison(dir1: Path, dir2: Path) -> tuple[Path, Path] | None:
    base1_input = dir1.name
    base2_input = dir2.name

    if is_timestamped_dir(base1_input) and is_timestamped_dir(base2_input):
        if base1_input > base2_input:
            lgg.w(f"'{base1_input}' appears newer than '{base2_input}', but was passed as the OLD directory.")
            if not prompt_yes_no("Would you like to auto-sort them (older first) before proceeding?"):
                lgg.i("Operation cancelled.")
                return None
            lgg.i(f"Auto-sorting directories: {base2_input} (OLD), {base1_input} (NEW)")
            dir1, dir2 = dir2, dir1

    lgg.w(f"You are about to compare:\n  OLD: {dir1}\n  NEW: {dir2}")
    if not prompt_yes_no("Proceed with comparison?"):
        lgg.i("Operation cancelled.")
        return None

    return dir1, dir2


def main(old_dir: Path, new_dir: Path) -> None:
    differences, added_files, removed_files = hash_and_compare(str(old_dir), str(new_dir))
    generate_diff_report(differences, added_files, removed_files, str(old_dir), str(new_dir))


def cli():
    parser = argparse.ArgumentParser(description="Execution handler for hash & diff tools.")
    parser.add_argument("olddir", nargs="?", help="Old directory (positional)")
    parser.add_argument("newdir", nargs="?", help="New directory (positional)")
    args = parser.parse_args()

    dir1 = Path(args.olddir).resolve() if args.olddir else get_directory_input("Enter path to OLD directory")
    dir2 = Path(args.newdir).resolve() if args.newdir else get_directory_input("Enter path to NEW directory")

    sorted_dirs = run_comparison(dir1, dir2)
    if not sorted_dirs:
        return

    old_dir, new_dir = sorted_dirs
    main(old_dir, new_dir)



if __name__ == "__main__":
    cli()
