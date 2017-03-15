import argparse as ap
from PIL import Image as I

from PIL import ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True


def ImageCompress(file_path, output_file_path,x,y,q,f):
    fd_img = open(file_path, 'r')
    img = I.open(fd_img)
    img.thumbnail((x, y), I.ANTIALIAS)
    img.save(output_file_path,f, quality=q)
    fd_img.close()
    return output_file_path

def main():
    parser = ap.ArgumentParser(description="Image compression !!!")
    parser.add_argument("file_path", help='input file path to compress',nargs='?',default=None)
    parser.add_argument("output_file_path", help='output file path to save compressed file',nargs='?',default=None)
    parser.add_argument("width", help='width of the image to which image should be compressed. Defaults to 100', nargs='?', default=100,type=int)
    parser.add_argument("height", help='height of the image to which image should be compressed. Defaults to 100', nargs='?', default=100,type=int)
    parser.add_argument("quality", help='quality of the image starts from 0 to 100, Defaults to 75', nargs='?', default=75,type=int)
    parser.add_argument("file_format", help='file format Ex: JPEG,PNG etc. Defaults to JPEG', nargs='?', default="JPEG")

    args, unknown = parser.parse_known_args()
    print "Compressing started"

    if args.file_path not in [None, '', ' ']:
        if args.output_file_path in [None, '', ' ']:
            output_file_path = "output.jpg"
        else:
            output_file_path = args.output_file_path
        output_file_path = ImageCompress(args.file_path, output_file_path,args.width,args.height,args.quality,args.file_format)
        print "file saved to ",output_file_path
    else:
        print "Please provide filepath to compress!!"


if __name__ == '__main__':
    main()

