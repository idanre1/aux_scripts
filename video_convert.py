# sudo apt install ffmpeg
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
for path in Path(args.path).rglob('*.flv'):
    files.append(path)
      
if len(files) == 0:
    print('No new files found')
    exit()

import os
for f in files:
    desc = f.relative_to(args.path)
    output = f'{desc.parent}/{desc.stem}.mp4'
    # desc=str(desc).replace('/','\n')
    log.info(f'{f}: {output}')
    cmd = f'sudo /usr/bin/ffmpeg -i "{f}" -vcodec copy -acodec copy "{output}"'
    log.debug(os.popen(cmd).read())
    break

