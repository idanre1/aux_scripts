# Install:
# sudo apt-get install pkg-config libpoppler-cpp-dev
# pip install cmake  
# pip install --prefix="~/py3env" python-poppler

import logging
import logging.config
logging.config.fileConfig('/nas/settings/logging.cfg')
log = logging.getLogger('standard')

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--path')
args = parser.parse_args()

from pathlib import Path
files = []
for path in Path(args.path).rglob('*.pdf'):
    files.append(path)
      
if len(files) == 0:
    print('No new files found')
    exit()

import os

from poppler import load_from_file
def list_files(f):
    pdf_document = load_from_file(f)
    if pdf_document.has_embedded_files():
        files = pdf_document.embedded_files()
        log.info(f'Number of files: {len(files)}')
        for attachment in files:
            print(attachment.name)
        print('END')
    else:
        log.warning("No embedded files")

for f in files:
    desc = f.relative_to(args.path)
    output = f'{desc.parent}/{desc.stem}.pdf'
    # desc=str(desc).replace('/','\n')
    log.info(f'{f}: {output}')

    # List embedded files in pdf
    list_files(f)

