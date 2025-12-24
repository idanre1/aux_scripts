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

def move_if_both(src_file: Path, dst_file: Path):
    """
    Move src_file → dst_file.
    If dst_file exists, remove it first.
    Both arguments must be full Path objects.
    """
    src_file = src_file.resolve()
    dst_file = dst_file.resolve()

    # Ensure destination folder exists
    dst_file.parent.mkdir(parents=True, exist_ok=True)

    # Remove old destination file if present
    print(f"Delete: {dst_file}")
    if dst_file.exists():
        dst_file.unlink()
    else:
        assert f"Dest file {dst_file} does not exists!"

    # Build new dst file
    dest_folder = dst_file.parent
    dst_file_new = dest_folder / src_file.name # Destination path preserves original filename

    # Move the file
    print(f"move: {src_file}, {dst_file_new}")
    shutil.copy(str(src_file), str(dst_file_new))
    print(f"Delete: {src_file}")
    src_file.unlink()

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
        move_if_both(Path(row['F1_PATH']), Path(row['F2_PATH']))
