# aggregate filenames in a single path
import re
import os
from pathlib import Path
import shutil

def rename_regex(path, pattern):
    # Grep all files
    files = []
    for p in Path(path).rglob(f'*'):
        files.append(p)

    if len(files) == 0:
        print('No new files found')
        exit()

    for f in files:
        print(f)
        
        m = pattern.match(f.stem)
        if m:
            new_file=f"{m.group(1)}{f.suffix}"
            # dest=f"{p.parent}/{new_file}"
            dest=f.with_name(new_file)
            f.rename(dest)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path")
    args = parser.parse_args()

    pattern = re.compile(r"^(.*?)(\s*\[.*\]\s*$)")

    rename_regex(args.path, pattern)