"""
PATH: ./wix-scraper/utils/diffscripts/

Functions:
- generate_diff_report(changed_files, added_files, removed_files, dir1, dir2):
  Compares matching files line-by-line and outputs a diff report, including added and removed files.
"""

import logging
from pathlib import Path
from difflib import SequenceMatcher
from shutil import copy2
from utils.configs.config import setup_logger

lgg = setup_logger(logging.INFO)

def generate_diff_report(changed_files, added_files, removed_files, dir1, dir2):
    dir1_path = Path(dir1).resolve()
    dir2_path = Path(dir2).resolve()

    name1 = dir1_path.name
    name2 = dir2_path.name
    filename_out = f"{name1}_{name2}.diff.txt"

    export_folder_name = name2
    project_root = Path(__file__).resolve().parents[2]
    exports_dir = project_root / "results" / "exports" / export_folder_name
    pdf_exports_dir = exports_dir / "pdf"
    pdf_exports_dir.mkdir(parents=True, exist_ok=True)

    output_file = exports_dir / filename_out

    with output_file.open("w", encoding="utf-8") as out:
        for filename in changed_files:
            file1_path = dir1_path / filename
            file2_path = dir2_path / filename

            try:
                with file1_path.open("r", encoding="utf-8") as f1, file2_path.open("r", encoding="utf-8") as f2:
                    lines1 = f1.readlines()
                    lines2 = f2.readlines()

                matcher = SequenceMatcher(None, lines1, lines2)
                for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                    if tag == 'equal':
                        continue

                    out.write(f"\n--- Change ({tag.upper()}): {filename}\n")

                    if tag in ('replace', 'delete'):
                        out.write(f"<<<< {name1}/{filename} [lines {i1 + 1}-{i2}]\n")
                        out.writelines(line if line.strip() else "[BLANK LINE]\n" for line in lines1[i1:i2])

                    if tag in ('replace', 'insert'):
                        out.write(f">>>> {name2}/{filename} [lines {j1 + 1}-{j2}]\n")
                        out.writelines(line if line.strip() else "[BLANK LINE]\n" for line in lines2[j1:j2])

                    out.write("\n")

            except FileNotFoundError as e:
                out.write(f"Error: {e}\n")
            except Exception as e:
                out.write(f"Unexpected error comparing {filename}: {e}\n")

        # Summary of added and removed files
        out.write("\n-----------------------\nAdded files:\n")
        out.writelines(f"{file}\n" for file in added_files) if added_files else out.write("(None)\n")

        out.write("\n------------------------\nRemoved files:\n")
        out.writelines(f"{file}\n" for file in removed_files) if removed_files else out.write("(None)\n")

    lgg.i(f"Differences written to: {output_file}")

    # Export added files to ./pdf
    for file in added_files:
        src = dir2_path / file
        dst = pdf_exports_dir / file
        try:
            copy2(src, dst)
            lgg.i(f"Exported added file: {file}")
        except Exception as e:
            lgg.i(f"Failed to export '{file}': {e}")

    # Export changed files to ./pdf
    for file in changed_files:
        src = dir2_path / file
        dst = pdf_exports_dir / file
        try:
            copy2(src, dst)
            lgg.i(f"Exported changed file: {file}")
        except Exception as e:
            lgg.i(f"Failed to export changed file '{file}': {e}")