# sudo apt install ffmpeg
import numpy as np

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--path')
args = parser.parse_args()

from pathlib import Path
files = []
for path in Path(args.path).rglob('*.wmv'):
    files.append(path)
for path in Path(args.path).rglob('*.flv'):
    files.append(path)
for path in Path(args.path).rglob('*.mp*g'):
    files.append(path)
      
if len(files) == 0:
    print('No new files found')
    exit()

def check_for_old_formats(filename):
    not_supported = np.array(['mpeg1video', 'wmv2'])
    
    cmd = f'ffprobe -v error -select_streams v:0 -show_entries stream=codec_name -of default=noprint_wrappers=1:nokey=1 {filename}'
    stdout, stderr = _exe_cmd(cmd)
    
    # print(stdout); quit()
    if np.isin(stdout.rstrip(), not_supported).sum() > 0:
        return True
    elif len(stdout.rstrip()) == 0:
        return True
    else:
        return False

def _exe_cmd(cmd):
    p = Popen(cmd,
          shell=True, bufsize=-1,
          stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
    stdout, stderr = p.communicate()
    stdout = stdout.decode("utf-8")
    stderr = stderr.decode("utf-8")
    return (stdout, stderr)

def slow_convert(f, output):
    cmd = f'sudo /usr/bin/ffmpeg -y -i "{f}" "{output}"'
    stdout, stderr = _exe_cmd(cmd)
    # if len(stderr) > 0:
    #     print(stderr)
    #     quit()
    assert len(stdout) == 0

def fast_convert(f, output):
    cmd = f'sudo /usr/bin/ffmpeg -y -i "{f}" -vcodec copy -acodec copy "{output}"'
    stdout, stderr = _exe_cmd(cmd)
    if len(stderr) > 0:
        print('FAST_WARNING - fallback to slow')
        slow_convert(f, output)
    else:
        assert len(stdout) == 0


import os
from subprocess import Popen, PIPE
for f in files:
    desc = f.relative_to(args.path)
    output = f'{desc.parent}/{desc.stem}.mp4'
    # desc=str(desc).replace('/','\n')
    slow = check_for_old_formats(f)
    if slow:
        print(f'SLOW - {f}: {output}')
        slow_convert(f, output)
    else:
        print(f'FAST - {f}: {output}')
        fast_convert(f, output)
