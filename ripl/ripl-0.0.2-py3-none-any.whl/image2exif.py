
from PIL import Image, ExifTags

def get_exif(im):

    exif = im._getexif()

    result = {}
    for key, value in exif.items():
        result[ExifTags.TAGS.get(key, key)] = value

    return result
    

class Im2Exif:

    def interpret(self, msg, who=None):

        im = Image.open(msg)

        return get_exif(im)

    
