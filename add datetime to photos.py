import os
import sys

from PIL import Image, ImageDraw, ImageFont, ExifTags

def get_date_taken(path):
    """Extracts the original date and time the photo was taken from the EXIF data."""
    try:
        image = Image.open(path)
        info = image._getexif()

        if info is not None:
            for tag, value in info.items():
                if ExifTags.TAGS.get(tag) == 'DateTimeOriginal':
                    return value
        else:
            print(f"No EXIF data found for image {path}.")
    except Exception as e:
        print(f"Exception occurred in get_date_taken: {e}")

    return None

def correct_orientation(image):
    """Corrects the image orientation based on the EXIF Orientation metadata."""
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = image._getexif()

        if exif is not None and orientation in exif:
            if exif[orientation] == 3:
                image = image.rotate(180, expand=True)
            elif exif[orientation] == 6:
                image = image.rotate(270, expand=True)
            elif exif[orientation] == 8:
                image = image.rotate(90, expand=True)
    except Exception as e:
        print(f"Exception occurred in correct_orientation: {e}")

    return image

def add_timestamp(path):
    try:
        """Opens the image, corrects its orientation, adds the timestamp, and saves the image."""
        image = Image.open(path)
        image = correct_orientation(image)
        draw = ImageDraw.Draw(image)
        image_width, image_height = image.size

        text = get_date_taken(path)
        if text is None:
            print(f"Could not find DateTimeOriginal in EXIF data for image {path}.")
            text = input("Please enter the text you'd like to add as a timestamp: ")

        # Dynamically set font size and margin based on the smaller of image width and height
        font_size = int(min(image_width, image_height) * font_ratio)
        font = ImageFont.truetype('arial.ttf', font_size)
        margin = int(min(image_width, image_height) * margin_ratio)

        # Calculate text position using textbbox to get text width and height
        left, upper, right, lower = draw.textbbox((0, 0), text, font=font)
        text_width, text_height = right - left, lower - upper
        text_position = (image_width - text_width - margin, image_height - text_height - margin)

        # Draw shadow
        for adj in range(shadow_offset):
            draw.text((text_position[0]-adj, text_position[1]-adj), text, font=font, fill=shadow_color)

        # Draw text
        draw.text(text_position, text, font=font, fill="white")

        # Construct output path and save the image
        output_path = os.path.splitext(path)[0] + '_with_timestamp.jpg'
        image.save(output_path)
        print(f"Saved image with timestamp as {output_path}.")
        # Close the image file to free up memory
        image.close()
    except Exception as e:
        print(f"Exception occurred in add_timestamp: {e}")

# Specify the shadow offset in pixels and shadow color
shadow_offset = 3
shadow_color = "black"

# Specify the ratio of the font size and margin to the image width or height
font_ratio = 0.05
margin_ratio = 0.02

# Get all files in the current directory
files = os.listdir()

# Filter for image files and add timestamp to each one
for file in files:
    # You may need to adjust this line to match the image types you're working with
    if os.path.splitext(file)[1].lower() in ('.jpg', '.jpeg', '.png'):
        add_timestamp(file)
