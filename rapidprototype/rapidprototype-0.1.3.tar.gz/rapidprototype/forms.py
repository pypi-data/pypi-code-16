from PIL import Image, ImageDraw, ImageColor
from django import forms
from io import BytesIO


class PlaceHolderImageForm(forms.Form):
    width = forms.IntegerField(min_value=1, max_value=2000)
    height = forms.IntegerField(min_value=1, max_value=2000)

    def generate(self, image_format='PNG', text=None, color_string=None):
        height = self.cleaned_data['height']
        width = self.cleaned_data['width']
        try:
            color = ImageColor.getcolor(color_string, 'RGB')
        except Exception as e:
            color = 'black'
        image = Image.new('RGB', (width, height), color=color)

        draw = ImageDraw.Draw(image)

        text = '{} x {}'.format(width, height) if text==None else text

        textwidth, textheight = draw.textsize(text)

        if textwidth < width and textheight < height:
            texttop = (height - textheight) // 2
            textleft = (width - textwidth) // 2
            draw.text((textleft, texttop), text, fill=(255, 255, 255))

        content = BytesIO()
        image.save(content, image_format)
        content.seek(0)
        return content