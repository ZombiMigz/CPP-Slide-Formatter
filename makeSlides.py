import os
import pathlib
import shutil
from PIL import Image, ImageFont, ImageDraw


# SETTINGS
# Resize images? either "True" or "False"
RESIZE_IMAGES = True
# Add text? either "True" or "False"
OVERLAY_TEXT = True
# path to font
PATH_FONT = "./OpenSans-ExtraBold.ttf"
# possible file extensions, reference https://pillow.readthedocs.io/en/stable/index.html to see valid filetypes
VALID_EXTENSIONS = ("jpg", "png")
# output format (png is invalid because it doesn't support alpha colour channels for transparent text boxes)
OUTPUT_EXTENSION = "jpg"
# image width
IMG_WIDTH = 400
# image height
IMG_HEIGHT = 200
# text box padding
BOX_PADDING = IMG_HEIGHT / 20
# text box transparency percentage (in decimal form. i.e. 70% = .7)
BOX_TRANSPARENCY = .7
# font size
FONT_SIZE = 30
# space between text (pixels)
TEXT_SPACING = 4


# ---------------------------------------------------------------------------
#
# WARNING: DO NOT EDIT ANYTHING AFTER THIS UNLESS YOU KNOW WHAT YOU ARE DOING
#
# ---------------------------------------------------------------------------


# CONSTANTS
# input file (relative to makeSlides.py)
PATH_IN = "./in"
# output file (relative to makeSlides.py)
PATH_OUT = "./out"


def get_images():
    # get files in ./in
    files = [str(filePath) for filePath in pathlib.Path(
        PATH_IN).iterdir() if filePath.is_file()]
    # filter out invalid files & return
    return [image for image in files if os.path.splitext(image)[1][1:].lower() in VALID_EXTENSIONS]


def duplicate_images(images: list[str]) -> list[str]:
    res = []
    for imagePath in images:
        image = Image.open(imagePath)
        # convert image to rgba
        image = image.convert("RGB")
        # save image
        image.save(
            "out" + os.path.splitext(imagePath[2:])[0] + "." + OUTPUT_EXTENSION)
        # add image to result
        res.append(
            "out" + os.path.splitext(imagePath[2:])[0] + "." + OUTPUT_EXTENSION)
    return res


def resize_images(images: list[str]):
    for imagePath in images:
        image = Image.open(imagePath)
        # if image is too tall
        if (image.height / IMG_HEIGHT > image.width / IMG_WIDTH):
            # calc the new height of the image
            new_height = int(float(image.height) *
                             IMG_WIDTH / float(image.width))
            # resize image
            image = image.resize((IMG_WIDTH, new_height))
            # crop vertically to fit height (centered)
            crop_margin = max((image.height - IMG_HEIGHT) / 2, 0)
            image = image.crop(
                (0, crop_margin, IMG_WIDTH, image.height - crop_margin))
        # if image is too wide
        if (image.height / IMG_HEIGHT < image.width / IMG_WIDTH):
            # calc the new width of the image
            new_width = int(float(image.width) *
                            IMG_HEIGHT / float(image.height))
            # resize image
            image = image.resize((new_width, IMG_HEIGHT))
            # crop vertically to fit width (left aligned)
            image = image.crop(
                (0, 0, IMG_WIDTH, image.height))
        # save to out
        image.save(imagePath)


def get_wrapped_text(text: str, font: ImageFont.ImageFont,
                     line_length: int) -> list[str]:
    '''modified code from https://stackoverflow.com/a/67203353/6078882'''
    lines = ['']
    for word in text.split():
        line = f'{lines[-1]} {word}'.strip()
        if font.getlength(line) <= line_length:
            lines[-1] = line
        else:
            lines.append(word)
    return lines


def add_text(images: list[str]):
    '''adds text to the output images along with a transparent textbox'''
    for imagePath in images:
        image = Image.open(imagePath)
        # get font
        font = ImageFont.truetype(PATH_FONT, FONT_SIZE)
        # get text
        text = os.path.splitext(imagePath)[0].removeprefix("out" + os.sep)
        # get wrapped text
        wrapped_text = get_wrapped_text(text, font, IMG_WIDTH*.75)

        # draw box (rgba for transparency)
        draw = ImageDraw.Draw(image, "RGBA")
        # calc text height
        textH = (font.getbbox(text)[
            3] - font.getbbox(text)[1])
        # calculate box height
        boxH = textH * (len(wrapped_text))
        # add padding to box height
        boxH += BOX_PADDING * 2
        # add text spacing to box height
        boxH += (len(wrapped_text) + 1) * TEXT_SPACING
        # draw rectangle (box)
        draw.rectangle((0, IMG_HEIGHT / 2 - boxH / 2,
                        IMG_WIDTH * .75, IMG_HEIGHT / 2 + boxH / 2), fill=(0, 0, 0, int(255*BOX_TRANSPARENCY)))

        # write text over box
        # get horizontal center
        xCenter = IMG_WIDTH * .75 / 2
        # set curr y to vertical start
        y = IMG_HEIGHT / 2 - boxH / 2 + BOX_PADDING + TEXT_SPACING
        # draw each line
        for line in wrapped_text:
            draw.text((xCenter, y), line,
                      fill="white", anchor="mt", font=font)
            y += textH + TEXT_SPACING

        # save to out
        image.save(imagePath)


def main():
    input = get_images()
    out = duplicate_images(input)
    if RESIZE_IMAGES:
        resize_images(out)
    if OVERLAY_TEXT:
        add_text(out)


main()
