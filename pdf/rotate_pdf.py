# Rotate pdf files

from pathlib import Path

def rotate_pdf_clockwise(from_filename, output_filename, clockwise_angle=90):
	from PyPDF2 import PdfReader, PdfWriter
	pdf_fh_in  = open(from_filename, 'rb')
	pdf_reader = PdfReader(str(from_filename))
	pdf_writer = PdfWriter()

	#######################################
	# Rotation
	#######################################
	n = len(pdf_reader.pages)
	print(f'File: {from_filename} rotate {n} pages')
	for n in range(len(pdf_reader.pages)):
		page = pdf_reader.pages[n]
		page.rotate(clockwise_angle)
		pdf_writer.add_page(page)

	pdf_fh_out = open(output_filename, 'wb')
	pdf_writer.write(pdf_fh_out)

	pdf_fh_in.close()
	pdf_fh_out.close()


if __name__ == "__main__":
	#######################################
	# Args
	#######################################
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument("-p", "--path", help="path to process")
	parser.add_argument("-a", "--angle", default=90, help="path to process")
	args = parser.parse_args()
	clockwise_angle = int(args.angle)

	files = []
	for path in Path(args.path).rglob('*.pdf'):
		files.append(path)
	for path in Path(args.path).rglob('*.PDF'):
		files.append(path)
		
	if len(files) == 0:
		print('No new files found')
		exit()

	for f in files:
		print(f'Processing: {f.name} to {f.stem}_book.pdf')
		rotate_pdf_clockwise(f, f'{f.parent}/{f.stem}_rotated.pdf',clockwise_angle)
