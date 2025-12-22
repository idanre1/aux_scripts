# aggregate filenames in a single path
import re
import argparse
import os
from pathlib import Path
import shutil

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--in")
parser.add_argument("-o", "--out")
parser.add_argument("-t", "--type")
args = parser.parse_args()

# mkdir dest path
Path(args.out).mkdir(parents=True, exist_ok=True)

# Grep all database files
files = []
for path in Path(args.inn).rglob(f'*.{args.type}'):
    files.append(path)

if len(files) == 0:
    print('No new files found')
    exit()

for f in files:
    # original related file
    hier=f.relative_to(args.inn)
    print(hier)

    # dest path
    dest=f'{args.out}/{str(hier).replace("/","_")}'

    # copy
    shutil.copy(f, dest)
