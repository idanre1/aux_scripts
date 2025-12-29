import re
from pathlib import Path
import pandas as pd
import shutil
from tqdm import tqdm

def get_filelist(path):
	files = []
	for p in Path(path).rglob(f'*'): # Quick disk action, no tqdm
		files.append(p)

	if len(files) == 0:
		print('No new files found')
		exit()

	return files

def normalize(name: str) -> str:
	"""Normalize filename by removing '-' using regex."""
	s = name.lower()
	return re.sub(r"-", "", s)

def collect_files(folder: Path):
	"""Return dict: normalized_name → (original_name, size_bytes)"""
	files = {}
	for p in tqdm(get_filelist(folder)):
		if p.is_file():
			norm = normalize(p.name)
			files[norm] = (p.name, p.resolve())
	return files

def compare_folders(p_from: Path, p_to: Path):
	# Collect normalized filenames
	print("Collecting from")
	f1 = collect_files(p_from)
	print("Collecting to")
	f2 = collect_files(p_to)

	print("Building DB")
	all_keys = sorted(set(f1.keys()) | set(f2.keys()))
	rows = []
	for key in tqdm(all_keys):
		f1_name, f1_path = f1.get(key, ("-", None))
		f2_name, f2_path = f2.get(key, ("-", None))
		# DataFrame columns attribution
		if f1_path is None:
			f1_size = "-"
		else:
			p1 = Path(f1_path)
			f1_size=p1.stat().st_size
		if f2_path is None:
			f2_size = "-"
		else:
			p2 = Path(f2_path)
			f2_size=p2.stat().st_size

		# Decision
		if f1_name != "-" and f2_name != "-":
			status = "BOTH"
		elif f1_name != "-":
			status = "ONLY_F1"
		else:
			status = "ONLY_F2"
		rows.append({
		# DataFrame columns attribution
			"STATUS": status,
			"NORMALIZED": key,
			"F1_NAME": f1_name,
			"F1_SIZE": f1_size,
			"F1_PATH": f1_path,
			"F2_NAME": f2_name,
			"F2_SIZE": f2_size,
			"F2_PATH": f2_path,
			})
		
	return pd.DataFrame(rows).sort_values(by=["STATUS", "NORMALIZED"])

def write_txt_table(df: pd.DataFrame, output_path: Path):
	"""Write a fixed-width TXT table."""
	# Convert DataFrame to a nicely aligned text table
	txt = df.to_string(index=False)
	output_path.write_text(txt, encoding="utf-8")

def wsl_to_windows(path: Path) -> str:
	"""
	Convert a WSL/Linux Path to a Windows-style path.
	"""
	# Example: /mnt/c/Users/Me/file.txt → C:\Users\Me\file.txt

	p = path.resolve()
	parts = p.parts

	if len(parts) > 2 and parts[1] == "mnt":
		drive = parts[2].upper() + ":"
		rest = Path(*parts[3:])
		return str(Path(drive) / rest).replace("/", "\\")
	else:
		# fallback: just replace slashes
		return str(p).replace("/", "\\")

def move_if_both(src_file: str, dst_file: str, ps_script: str):
	"""
	Instead of moving files, write PowerShell commands to a .ps1 script.
	- Removes old destination file
	- Moves source → destination
	- Converts WSL paths to Windows paths
	"""
	# make all str to Path
	ps_script = Path(ps_script)
	src_file = Path(src_file)
	dst_file = Path(dst_file)

	src_win = wsl_to_windows(src_file)
	dst_win = wsl_to_windows(dst_file)

	ps_script.parent.mkdir(parents=True, exist_ok=True)

	with ps_script.open("a", encoding="utf-8") as f:
		f.write(f"# Move {src_win} → {dst_win}\n")
		f.write(f"if (Test-Path \"{dst_win}\") {{ Remove-Item -Force \"{dst_win}\" }}\n")
		f.write(f"Move-Item -Force \"{src_win}\" \"{dst_win}\"\n\n")


# Example usage:
if __name__ == "__main__":
	import argparse

	parser = argparse.ArgumentParser()
	parser.add_argument("-p1", "--path1", help="From path")
	parser.add_argument("-p2", "--path2", help="To path")
	args = parser.parse_args()

	p_from = Path(args.path1)
	p_to = Path(args.path2)

	df = compare_folders(p_from, p_to)

	write_txt_table(df, Path("comparison_report.txt"))

	df = df[df['STATUS'] == 'BOTH']
	df = df[df['NORMALIZED'].str.contains('amy')]

	print("Moving")
	for idx,row in tqdm(df.iterrows()):
		move_if_both(row['F1_PATH'], row['F2_PATH'], "move.ps1")
