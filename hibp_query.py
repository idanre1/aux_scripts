# Have I Been Pwnd?
# https://haveibeenpwned.com/Passwords
# Search database for pawned passwords
import hashlib
import mmap

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('password')
parser.add_argument("db" , help="", nargs='?', default='/nas/pwned-passwords-sha1-ordered-by-count-v7.txt') # Positional optional argument
args = parser.parse_args()

hash = hashlib.sha1(args.password.encode()).hexdigest().upper()
print(f'Hash:   {hash}')

with open(args.db, 'rb', 0) as file, \
     mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as s:
    pos = s.find(str.encode(hash))
    if pos != -1:
        s.seek(pos)
        print(f'Result: {s.readline().decode()}')
    else:
        print('Not found!')