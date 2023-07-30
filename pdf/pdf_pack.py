# Pack all jpg files in a folder to a pdf file
from pathlib import Path

def filelist_to_pdf(lst, filename):
	from PIL import Image
	img_list = [Image.open(l) for l in lst]
	rgb_list = [i.convert('RGB') for i in img_list]

	img = rgb_list.pop(0)
	img.save(f'{filename}.pdf', save_all=True, append_images=rgb_list)

if __name__ == "__main__":
	#######################################
	# Args
	#######################################
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument("-p", "--path", help="path to process")
	parser.add_argument("-f", "--filename", help="path to process")
	args = parser.parse_args()

	files = []
	for path in Path(args.path).rglob('*.jpg'):
		files.append(path)
	for path in Path(args.path).rglob('*.jpgeg'):
		files.append(path)
	for path in Path(args.path).rglob('*.JPG'):
		files.append(path)
	for path in Path(args.path).rglob('*.JPGEG'):
		files.append(path)
		
	if len(files) == 0:
		print('No new files found')
		exit()

	for f in files:
		print(f'Processing: {f.name} to {args.filename}.pdf')
	filelist_to_pdf(files, args.filename)