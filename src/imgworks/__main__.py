from pathlib import Path

import typer
from pillow_heif import register_heif_opener

from imgworks.image import load_images, resize_images, save_files
from imgworks.settings import FORMATS, ORIGINAL_IMAGE_EXTENSIONS

sizes = []

app = typer.Typer()


@app.command()
def convert_webp(
    folder: Path = typer.Argument(Path("."), exists=True, file_okay=False, dir_okay=True, resolve_path=True),
    to_format: str = typer.Argument(
        "jpg",
        help="Format to convert to",
        show_default=True,
    ),
):
    images = load_images(folder, extensions={".webp"})

    if not to_format.startswith("."):
        to_format = "." + to_format

    format = FORMATS.get(to_format, None)

    for im in images:
        im.image.save(im.path.with_suffix(to_format), format)


@app.command()
def convert_heic(
    folder: Path = typer.Argument(Path("."), exists=True, file_okay=False, dir_okay=True, resolve_path=True),
    to_format: str = typer.Argument(
        "jpg",
        help="Format to convert to",
        show_default=True,
    ),
):
    register_heif_opener()
    images = load_images(folder, extensions={".heic"})
    if not to_format.startswith("."):
        to_format = "." + to_format

    format = FORMATS.get(to_format, None)

    for im in images:
        im.image.save(im.path.with_suffix(to_format), format)


@app.command()
def resize(
    folder: Path = typer.Argument(Path("."), exists=True, file_okay=False, dir_okay=True, resolve_path=True),
    width: str = typer.Argument(
        default="min",
        help=(
            "Width of the resized images in pixels. "
            "Use 'min' or 'max' to use the minimum or maximum width of the images in the folder"
        ),
    ),
):
    """Resize images in a folder to a given width"""
    images = load_images(folder, extensions=ORIGINAL_IMAGE_EXTENSIONS)

    try:
        new_width = int(width)
    except ValueError:
        if width == "min":
            new_width = min([im.image.width for im in images], key=lambda width: width)
        elif width == "max":
            new_width = max([im.image.width for im in images], key=lambda width: width)
        else:
            raise typer.BadParameter(f"Invalid width: {width}")

    resized = resize_images(images, new_width)

    resized_folder = folder / "resized"
    save_files(resized, resized_folder)


if __name__ == "__main__":
    app()
