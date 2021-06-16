from PyPDF2 import PdfFileReader, PdfFileWriter
from io import BytesIO
import copy

#######################################
# Args
#######################################
from pathlib import Path
pdf_path = (
	Path.home()
	/ "tmp"
	/ "vanilla.pdf"
)
output_path = (
	Path.home()
	/ "tmp"
	/ "exp.pdf"
)

pdf_reader = PdfFileReader(str(pdf_path))
pdf_writer = PdfFileWriter()
buffer     = BytesIO()

#######################################
# Rotation
#######################################
n = pdf_reader.getNumPages()
print(f'File: {pdf_path} pre rotate constains {n} pages')
for n in range(pdf_reader.getNumPages()):
	page = pdf_reader.getPage(n)
	if n % 2 == 0:
		page.rotateCounterClockwise(90)
	else:
		page.rotateClockwise(90)
	pdf_writer.addPage(page)

pdf_writer.write(buffer)

#######################################
# Cropping
#######################################
import numpy as np
import math
from collections import Counter, OrderedDict
def reorder(n):
	'''
	Example: For 4 double sided pages you actually get 16 pages
	    Ordered as: 8, 9, 10, 7
                    6, 11, 12, 5
					4, 13, 14, 3
					2, 15, 16, 1
	'''
	n_all = (n+1)*2
	# total_range = int(math.ceil(n_all//4.0)*2)
	total_range = int(math.ceil(n_all/2.0))
	out = []
	for a in range(1,total_range,2):
		tmp=[]
		tmp.append(a+1)
		tmp.append(n_all-a)
		tmp.append(n_all-a+1)
		tmp.append(a)
		out.append(tmp)
	arr = np.concatenate(np.array(out)[::-1])
	duplicates = [item for item, count in Counter(arr).items() if count > 1]
	assert len(duplicates) == 0, f"Page ordering - Duplicate error: {duplicates}\n{arr}"
	assert float(n+1) == len(arr)/2.0, f"Page ordering - length error: golden={float(n+1)}, revised={len(arr)/2.0}"
	return list(arr)

# Crop
pdf_reader0 = PdfFileReader(buffer)
pdf_reader1 = PdfFileReader(buffer)
pdf_writer = PdfFileWriter()
pages = reorder(n)
print(f'File: {pdf_path} after booking constains {n+1}*2={n*2+2} pages')
print(f'Page ordering: {pages}')
threshold = 0.02
out = {}
for n in range(pdf_reader.getNumPages()):
	page1 = pdf_reader0.getPage(n)
	page2 = pdf_reader1.getPage(n)
	# get dimensions
	# The first two: x,y coordinates of the lower-left  corner
	# The secnd two: x,y coordinates of the Upper-right corner
	(ll_height, ll_width, ur_height, ur_width) = page1.mediaBox

	# print(page1["/Rotate"], page2["/Rotate"])
	# Right (first) page
	# When rotation comes into play, x,y dimensions are still from original image
	if page1["/Rotate"] == 90:
		page1.mediaBox.lowerLeft = (ll_height, int(ur_width/2.0-threshold*ur_width))
	else: # == -90
		page1.mediaBox.upperRight = (ur_height, int(ur_width/2.0+threshold*ur_width))

	if page2["/Rotate"] == 90:
		page2.mediaBox.upperRight = (ur_height, int(ur_width/2.0+threshold*ur_width))
	else:
		page2.mediaBox.lowerLeft = (ll_height, int(ur_width/2.0-threshold*ur_width))

	# Force page ordering as book enforces
	try:
		n1 = pages.pop(0)
		n2 = pages.pop(0)
		# print(f'id: {n} right:{n1}, left:{n2}')
		out[n1] = page1
		out[n2] = page2
	except:
		raise Exception(f'Page ordering - During crop reordered pages does not match')
print("Done cropping")

# Reorder pages
od = OrderedDict(sorted(out.items()))
for k, v in od.items():
	# print(k)
	pdf_writer.addPage(v)
print("Done reordering")

# Writing output
with output_path.open(mode="wb") as output_file:
	pdf_writer.write(output_file)