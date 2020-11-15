#https://github.com/hMatoba/Piexif/blob/master/piexif/_exif.py
#http://www.cipa.jp/std/documents/e/DC-008-2012_E.pdf
#types on each field https://piexif.readthedocs.io/en/latest/appendices.html
import piexif
from pprint import pprint

def adjust_exif(exif_dict, text):
    exif_dict['1st'][piexif.ImageIFD.ImageDescription]=text
    exif_dict['Exif'][piexif.ExifIFD.SceneType]=b'\x01' # Some parsing error fix in library
    return exif_dict

path = "test.jpg"
exif_dict = piexif.load(path)
pprint(exif_dict)
quit()
new_exif = adjust_exif(exif_dict,'blah')
exif_bytes = piexif.dump(new_exif)
piexif.insert(exif_bytes, "test.jpg")
