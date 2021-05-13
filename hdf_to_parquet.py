import pandas as pd
import re
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--path", help="path to process")
args = parser.parse_args()

# Grep all database files
from pathlib import Path
files = []
for path in Path(args.path).rglob('*.hdf'):
    files.append(path)
for path in Path(args.path).rglob('*.hd5'):
    files.append(path)

if len(files) == 0:
    print('No new files found')
    exit()

for f in files:
    # target output
    desc = f#.relative_to(args.path)
    output = f'{desc.parent}/{desc.stem}.parquet'

    # Original
    print(f'Converting from: {f}')
    df = pd.read_hdf(f)

    # execute
    print(f'Converting to:{output}')
    df.to_parquet(output)

    # FOLD
    print(f'RM: {f}')
    os.remove(f)
