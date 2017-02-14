import os
import glob
from PIL import Image, ImageDraw, ImageFont, ExifTags
from colorama import Fore, Style
from imagebot import settings
from imagebot.config import get_config_data


def check_for_orientation(image):
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = dict(image._getexif().items())

        if exif[orientation] == 3:
            image = image.rotate(180, expand=True)
            print("-> Girando 180", end=" ")
        elif exif[orientation] == 6:
            image = image.rotate(270, expand=True)
            print("-> Girando 270", end=" ")
        elif exif[orientation] == 8:
            image = image.rotate(90, expand=True)
            print("-> Girando 90", end=" ")
        return image
    except (AttributeError, KeyError, IndexError):
        return image


def resize_image(image, width=None, height=None, percent=True, alias=True):
    imageWidth, imageHeight = image.size

    if width is None and height is not None:
        if percent:
            height = imageHeight * height / 100
        imageWidth = (imageWidth * height) / imageHeight
        imageHeight = height
    elif width is not None and height is None:
        if percent:
            width = imageWidth * width / 100
        imageHeight = (imageHeight * width) / imageWidth
        imageWidth = width
    elif width is not None and height is not None:
        if percent:
            width = imageWidth * width / 100
            height = imageHeight * height / 100
        imageWidth = width
        imageHeight = width

    if alias:
        return image.resize(
            (int(imageWidth),
             int(imageHeight)),
            Image.ANTIALIAS)
    else:
        return image.resize((int(imageWidth), int(imageHeight)))


def watermark_image_with_text(image, text, data, color=None, fontfamily=None):
    if not color:
        color = data['font_color']
    if not fontfamily:
        fontfamily = data['font']

    imageWatermark = Image.new('RGBA', image.size, (255, 255, 255, 0))

    draw = ImageDraw.Draw(imageWatermark)

    width, height = image.size
    margin = 10
    font = ImageFont.load_default()
    textWidth, textHeight = draw.textsize(text, font)
    x = width - textWidth - margin
    y = height - textHeight - margin

    draw.text((x, y), text, color, font)

    return Image.alpha_composite(image, imageWatermark)


def watermark_image_with_image(image, data):
    # Converte imagem original
    rgba_image = image.convert('RGBA')
    # Carrega o logo
    logo = Image.open(data['logo_path'])
    # O maior lado do logo
    # tem que ser 1/4 do
    # maior lado da foto
    hlogo, wlogo = logo.size
    himage, wimage = image.size
    if hlogo > wlogo:
        if hlogo != int(himage / 3):
            logo = resize_image(
                logo,
                height=int(
                    himage / 4),
                percent=False,
                alias=False)
    elif wlogo != int(wimage / 3):
        logo = resize_image(
            logo,
            width=int(
                wimage / 4),
            percent=False,
            alias=False)

    # Converte o logo para P&B
    logo_pb = logo.convert("L").point(lambda x: min(x, 100))
    # Cria a máscara
    logo_mask = Image.new("RGBA", logo_pb.size)
    logo_mask.putalpha(logo_pb)
    # O logo final deve ter o tamanho
    # da imagem original, mas com o logo
    # centralizado
    final_logo = Image.new('RGBA', image.size)
    wImage, hImage = image.size
    wLogo, hLogo = logo_mask.size
    position = (
        int(wImage / 2) - int(wLogo / 2),
        int(hImage / 2) - int(hLogo / 2)
    )
    final_logo.paste(logo_mask, position)

    return Image.alpha_composite(rgba_image, final_logo)


def watermark_folder(text, folder):
    data = get_config_data()
    if not data:
        return False

    print(Fore.YELLOW + ">> Aplicar: Marca d'Água")
    print(Style.RESET_ALL)
    # Calcula diretório
    base_dir = os.getcwd()
    if folder:
        if os.path.exists(folder):
            base_dir = folder
        else:
            print('Pasta não encontrada')
            return False

    count = 0
    extension_list = [
        e.upper()
        for e in settings.IMAGE_EXTENSIONS
    ]
    extension_list += settings.IMAGE_EXTENSIONS

    for extension in extension_list:
        path = os.path.join(
            base_dir,
            "**/*.{}".format(extension)
        )
        for file in glob.glob(path, recursive=True):
            current_dir = os.path.dirname(file)
            if os.path.split(current_dir)[-1] == settings.WATERMARK_FOLDER:
                continue
            final_folder = os.path.join(current_dir, settings.WATERMARK_FOLDER)
            fn, ex = os.path.splitext(file)
            name = os.path.split(fn)[-1]
            ext = ex.replace('.', '')

            if ext.lower() == "jpg":
                image_format = "JPEG"
            else:
                image_format = ext.upper()

            print(file, end=" ")
            image = Image.open(file)

            image = check_for_orientation(image)

            width, height = image.size
            if max(width, height) > 1600:
                print('-> Alterando tamanho', end=" ")
                cur_image = resize_image(image, width=50)
            else:
                cur_image = image

            if text:
                watermarked_image = watermark_image_with_text(
                    cur_image, text, data)
            else:
                watermarked_image = watermark_image_with_image(cur_image, data)

            # Cria o diretorio se precisar
            if not os.path.exists(final_folder):
                os.mkdir(final_folder)
            if watermarked_image:
                watermarked_image.save(
                    fp=os.path.join(final_folder, "{}-WM.{}".format(
                        name, ext)),
                    format=image_format
                )
                count += 1
                print ("-> OK")
            else:
                print("ERRO")

    if count:
        print("{} imagens modificadas na pasta {}".format(count, final_folder))
    else:
        print("Nenhuma imagem processada")

    return True
