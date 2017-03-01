"""
Create slides for a slideshow

Each slide is a heading plus a list of rows.

Each row is a list of text strings or image names.

This uses PIL to create an image for each slide.
"""
from PIL import Image, ImageDraw, ImageFont

from . import imagefind, image2exif

FONT = '/usr/share/fonts/TTF/Vera.ttf'
FONTSIZE = 36
WIDTH = 1024
HEIGHT = 768

class Slide2png:

    def __init__(self):

        self.pos = 0
        self.padding = 10
        self.cache = 'show'
        self.font = ImageFont.truetype(FONT, FONTSIZE)

        self.finder = imagefind.ImageFind()

    def interpret(self, msg):
        """ Load input """
        slides = msg.get('slides', [])
        self.cache = msg.get('folder', '.')
        self.gallery = msg.get('gallery', ['..'])
        self.finder.interpret(dict(galleries=self.gallery))

        # in case slides is a generator, turn it into a list
        # since I am going to go through it twice
        slides = [slide for slide in slides]

        logname = msg.get('logname')
        if logname:
            self.write_slide_list(logname, slides)

        # Now spin through slides again
        for slide in slides:

            image = self.draw_slide(slide)

            heading = slide['heading']['text']
            filename = self.get_image_name(heading)

            self.cache_image(filename, image)

        # fixme -- just return info in slides.txt as list of dicts
        return

    def write_slide_list(self, logname, slides):
        """ Write list of slides to logfile """
        # Write slides.txt with list of slides
        with open('%s/%s' % (self.cache, logname), 'w') as logfile:
            for slide in slides:
                heading = slide['heading']['text']
                filename = self.get_image_name(heading)
                
                print('%s,%d' % (filename, slide.get('time', 0)),
                      file=logfile)

    def draw_slide(self, slide):
        """ Return layout information for slide """

        image = Image.new('RGB', (WIDTH, HEIGHT), 'black')
        draw = ImageDraw.Draw(image)
        draw.font = self.font
        
        self.draw_slide_text(draw, slide)

        self.draw_slide_images(draw, slide, image)

        return image

    def draw_slide_text(self, draw, slide):

        heading = slide['heading']
        rows = slide['rows']

        
        left, top = heading['top'], heading['left']
        
        draw.text((left, top), heading['text'], fill='gold')
        print(heading['text'])

        for row in rows:
            for item in row['items']:
                top, left = item['top'], item['left']
                
                text = item.get('text')

                if not text:
                    continue

                draw.text((left, top), text, fill='white')

                      
    def draw_slide_images(self, draw, slide, image):

        heading = slide['heading']
        rows = slide['rows']
        
        left, top = heading['top'], heading['left']
        
        for row in rows:
            for item in row['items']:
                top, left = item['top'], item['left']
                
                image_file = item.get('image')

                if not image_file: continue

                source = self.find_image(item)
                if source:
                    print('Using {} for {}'.format(
                        source, item['image']))
                    
                    self.draw_image(image, item, source)
                else:
                    # no image, just use text
                    draw.text((left, top), image_file, fill='white')
                        
                      
        print()


    def find_image(self, item):
        """ Try and find the image file 

        some magic here would be good.

        FIXME move elsewhere and make so everyone can use.

        interpreter that finds things?
        """
        image_file = item['image']
        return self.finder.find_image(image_file)


    def rotate(self, img):
        """ Rotate image if exif says it needs it """
        try:
            exif = image2exif.get_exif(img)
        except AttributeError:
            # image format doesn't support exif
            return img
        
        orientation = exif.get('Orientation', 1)

        landscape = img.height < img.width
        
        if orientation == 6 and landscape:
            print("ROTATING")
            return img.rotate(-90)

        return img
        

    def draw_image(self, image, item, source):
        """ Add an image to the image """
        top, left = item['top'], item['left']
        width, height = item['width'], item['height']
        image_file = item['image']

        img = Image.open(source)

        img = self.rotate(img)

        iwidth, iheight = img.size

        wratio = width / iwidth
        hratio = height / iheight

        ratio = min(wratio, hratio)

        img = img.resize((int(iwidth * ratio),
                          int(iheight * ratio)),
                         Image.ANTIALIAS)
        

        # get updated image size
        iwidth, iheight = img.size
        
        # Adjust top, left for actual size of image so centre
        # is in the same place as it would have been
        
        top += (height - iheight) // 2
        left += (width - iwidth) // 2
        
        # now paste the image
        image.paste(img, (left, top))
        

    def slugify(self, name):
        """ Turn name into a slug suitable for an image file name """
        slug = ''
        last = ''
        for char in name.replace('#', '').lower().strip():
            if not char.isalnum():
                char = '_'

            if last == '_' and char == '_':
                continue

            slug += char
            last = char

        return slug
    
    def cache_image(self, name, image):
        
        
        with open(name, 'w') as slide:
            image.save(name)

        return name


    def get_image_name(self, label):

        return "%s/%s.png" % (self.cache, self.slugify(label))
