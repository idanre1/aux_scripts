#https://stackoverflow.com/questions/42024255/bulk-join-json-with-jpg-from-google-takeout
#https://exiftool.org/

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--path')
args = parser.parse_args()

from pathlib import Path
files = []
for path in Path(args.path).rglob('*.jp*g'):
    files.append(path)
      
if len(files) == 0:
    print('No new files found')
    exit()

import os
for f in files:
    desc = f.relative_to(args.path).parent
    # desc=str(desc).replace('/','\n')
    print(f'{f}:')
    os.system(f'/usr/bin/exiftool -overwrite_original -Caption-Abstract="{desc}" -Description="{desc}" -ImageDescription="{desc}" "{f}"')
    # quit()
