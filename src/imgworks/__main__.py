from dataclasses import dataclass
from pathlib import Path
from typing import List, Set

import imageio.v3 as iio
import typer
from PIL import Image

ORIGINAL_IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
}

FORMATS = {
    ".png": "png",
    ".jpg": "jpeg",
    ".jpeg": "jpeg",
    ".webp": "webp",
}

sizes = []

app = typer.Typer()

@dataclass
class ImageData:
    path: Path
    image: Image

@app.command()
def convert_webp(
    folder: Path = typer.Argument(
        Path("."), exists=True, file_okay=False, dir_okay=True, resolve_path=True
    ),
    to_format: str = typer.Argument(
        "jpg",
        help="Format to convert to",
        show_default=True,
    )):

    images = load_images(folder, extensions={".webp"})

    if not to_format.startswith("."):
        to_format = "."+to_format

    format = FORMATS.get(to_format, None)

    for im in images:
        im.image.save(im.path.with_suffix(to_format), format)

@app.command()
def resize(
    folder: Path = typer.Argument(
        Path("."), exists=True, file_okay=False, dir_okay=True, resolve_path=True
    ),
    width: str  =  typer.Argument(default="min", help=(
        "Width of the resized images in pixels. "
        "Use 'min' or 'max' to use the minimum or maximum width of the images in the folder"
        )
    )
):
    """Resize images in a folder to a given width"""
    images = load_images(folder, extensions=ORIGINAL_IMAGE_EXTENSIONS)

    try:
        new_width = int(width)
    except ValueError:
        if width == "min":
            new_width = min([ im.image.width for im in images], key=lambda width: width)
        elif width == "max":
            new_width = max([ im.image.width for im in images], key=lambda width: width)
        else:
            raise typer.BadParameter(f"Invalid width: {width}")

    resized = resize_images(images, new_width)

    resized_folder = folder / "resized"
    save_files(resized, resized_folder)

def save_files(resized, resized_folder):
    resized_folder.mkdir(exist_ok=True)
    for im in resized:
        im.image.save(resized_folder / im.path.name)



def resize_images(images, width):
    resized_images: List[ImageData] = []
    for im in images:
        ratio = width / im.image.size[0]
        new_height = int(im.image.size[1] * ratio)
        new_width = int(im.image.size[0] * ratio)

        resized_image = im.image.resize((new_width, new_height))
        resized_images.append(ImageData(
            path=im.path,
            image=resized_image,
        ))

    return resized_images

def load_images(folder: Path, extensions: Set[str]) -> List[ImageData]:
    images: List[ImageData] = []
    for file in folder.iterdir():
        if file.is_file():
            if file.suffix in extensions:
                full_path = (folder / file).resolve()
                image =  Image.fromarray(iio.imread(full_path))
                image_data = ImageData(
                    path=full_path,
                    image=image,
                )
                images.append(image_data)
    return images



if __name__ == "__main__":
    app()
