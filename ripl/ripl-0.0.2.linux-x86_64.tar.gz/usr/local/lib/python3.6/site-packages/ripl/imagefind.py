"""
Look for an image based on its name.

Searches through folders looking for image files.

Looks for an exact match.

Failing that, anything that contains part of the file name.

If there are full matches, picks one at random.

If there are no full matches picks one at random from the partial
matches.

"""
import os
from numpy.random import randint

class ImageFind:

    def __init__(self):

        self.folders = set()
        self.images = []

        self.exts = ['.gif', '.png', '.jpg']

    def add_folder(self, folder):
        """ Add a folder scan images there """
        if folder in self.folders:
            return

        self.folders.add(folder)
        
        for subfolder, junk, filenames in os.walk(folder):
            for filename in filenames:
                name, ext = os.path.splitext(filename)
                if ext in self.exts:
                    self.images.append(
                        os.path.join(subfolder, filename))
                
        

    def interpret(self, msg):
        """ Try and find the image file 

        some magic here would be good.

        FIXME move elsewhere and make so everyone can use.

        interpreter that finds things?
        """
        for gallery in msg.get('galleries', []):
            self.add_folder(gallery)
            
        image_file = msg.get('image')
        if not image_file: return

        return self.find_image(image_file)

    def find_image(self, image_file):
        
        matches = []
        partials = []

        folder, filename  = os.path.split(image_file)
        base, ext = os.path.splitext(filename)
        for image in self.images:
            if image.endswith(image_file):
                matches.append(image)
                continue

            if base in image:
                partials.append(image)

        if matches:
            return matches[randint(len(matches))]

        if partials:
            return partials[randint(len(partials))]
                
        return None


x = ImageFind()

interpret = x.interpret
