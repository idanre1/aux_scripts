from pathlib import Path
files = []
for path in Path(args.path).rglob('*.csv.gz'):
     20         files.append(path)
     21 
     22     if len(files) == 0:
     23         print('No new files found')
     24         exit()
