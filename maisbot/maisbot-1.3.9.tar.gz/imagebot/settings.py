from collections import OrderedDict

IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif']

CONFIG_FILE = 'ibconfig'

CONFIG_DICT = OrderedDict.fromkeys(
    [
        'logo_path',
        'font',
        'font_color'
    ]
)

WATERMARK_FOLDER = 'marca_dagua'
