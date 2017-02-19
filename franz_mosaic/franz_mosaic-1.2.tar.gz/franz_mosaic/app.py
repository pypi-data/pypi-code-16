import PIL
import glob
import os
import math
import argparse
import colorsys

from PIL import Image


class FranzMosaic:
    INPUT_DIR = 'img/'
    OUTPUT_DIR = 'out/'

    def resize_folder(self):
        allFiles = glob.glob(self.INPUT_DIR + '/**/*.jpg', recursive=True)
        for path in allFiles:
            self.resize(path)

    def resize(self, input_image):
        img = Image.open(input_image)
        img = img.resize((1, 1), PIL.Image.ANTIALIAS)
        filename = os.path.basename(input_image)
        img.save(self.OUTPUT_DIR + filename)

    def create_new_imate(self):
        all_files = glob.glob(self.OUTPUT_DIR + '/*.jpg')
        len_of_sides = math.floor(math.sqrt(len(all_files)))
        til = Image.new("RGB", (len_of_sides, len_of_sides))
        n = 0
        for y in range(len_of_sides):
            for x in range(len_of_sides):
                print(n)
                im = Image.open(all_files[n])  # 25x25
                til.paste(im, (x, y))
                n += 1

        til.save("new.png")

    def create_new_sorted_image(self):
        all_files = glob.glob(self.OUTPUT_DIR + '/*.jpg')
        len_of_sides = math.floor(math.sqrt(len(all_files)))
        len_of_sides = 50
        pixel_list = []
        print('mo')
        for n, file in enumerate(all_files[:len_of_sides*len_of_sides]):
            im = Image.open(all_files[n])
            pix = im.load()
            color = pix[0, 0]
            pixel_list.append(color)

        #print(pixel_list)
        #exit(0)
        pixel_list.sort(key=lambda rgb: colorsys.rgb_to_hsv(*rgb))
        #pixel_list.sort(key=hilbert.Hilbert_to_int)
        print(pixel_list)


        new = Image.new('RGB', (len_of_sides+1, len_of_sides+1))
        new.putdata(pixel_list)
        new.save("naive_tidy.png")


def main():
    max = 0
    parser = argparse.ArgumentParser(
        description="rescale images and put it together again")

    parser.add_argument('--rescale', '-r', help='Rescale Images to one pixel')
    parser.add_argument('--new', '-n', help='Produce new image')
    parser.add_argument('--sorted', '-s', help='Produce new sorted image')

    args = parser.parse_args()
    pic = FranzMosaic()

    if args.rescale:
        pic.resize_folder()

    if args.new:
        pic.create_new_imate()

    if args.sorted:
        pic.create_new_sorted_image()

if __name__ == '__main__':
    main()
