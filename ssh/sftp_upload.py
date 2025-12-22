from functools import partial
import os
from pathlib import Path
import asyncio
# from io import StringIO

import paramiko
# paramiko.util.log_to_file("paramiko.log")

class SftpUpload():
	def __init__(self, hostname, user, password):
		# SSH
		self.ssh = paramiko.SSHClient()
		self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
		self.user = user
		self.password = password
		self.hostname = hostname

		# self.ssh.load_system_host_keys('/home/user/.ssh/known_hosts')
		# private_key = open('/home/user/.ssh/id_ssh','r')
		# s = private_key.read()
		# self.private_key = paramiko.RSAKey.from_private_key(StringIO(s))


	def upload_sync(self, filename, dest_path='.'):
		print(f'Uploading {filename}')
		(result, data) = asyncio.run(self.upload(filename, dest_path))
		if result:
			# No errors
			print(f'Uploading {filename}...done')
			# os.remove(filename)
		else:
			print(f'ERROR Uploading: {data}')
			# os.remove(filename)

	async def upload(self, filename, dest_path='.'):
		try:
			timeout=60*30 #https://stackoverflow.com/questions/58844902/how-to-timeout-paramiko-sftp-put-with-signal-module-or-other-in-python
			self.ssh.connect(hostname=self.hostname, port=22,
							username=self.user,
							password=self.password,
							timeout=timeout,
							# disabled_algorithms=dict(pubkeys=['rsa-sha2-256', 'rsa-sha2-512']) # https://www.reddit.com/r/learnpython/comments/sixjay/how_to_use_disabled_algorithms_in_paramiko/
							# pkey=self.private_key,
							)
			sftp = self.ssh.open_sftp()									
			# sftp.chdir('/storage/external_storage/sdcard1/Music/downloads')  # change directory on remote server
			try:
				sftp.mkdir(dest_path)
			except Exception as e:
				# existing path throw OSError exception with value Failure
				pass
			sftp.get_channel().settimeout(timeout)
			sftp.put(filename, f'{dest_path}/{filename}')
			sftp.close()
			self.ssh.close()
			return (True, "")
		except Exception as e:
			return (False, f'{type(e).__name__}: {e}')
		
if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser(description='Upload file to remote server')
	parser.add_argument('hostname', type=str, help='Remote server hostname')
	parser.add_argument('-f', '--filename', type=str, help='Filename to upload')
	parser.add_argument('-u', '--user', type=str, help='Remote server username')
	parser.add_argument('--dest_path', type=str, default='.', help='Destination path on remote server')
	args = parser.parse_args()

	import getpass
	print('Enter password')
	pw = getpass.getpass()

	sftp = SftpUpload(args.hostname, args.user, pw)
	sftp.upload_sync(args.filename, args.dest_path)


