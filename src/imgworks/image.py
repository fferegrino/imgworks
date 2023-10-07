from dataclasses import dataclass
from pathlib import Path
from typing import List, Set

from imageio import v3 as iio
from PIL import Image


@dataclass
class ImageData:
    path: Path
    image: Image


def load_images(folder: Path, extensions: Set[str]) -> List[ImageData]:
    images: List[ImageData] = []
    for file in folder.iterdir():
        if file.is_file():
            if file.suffix.lower() in extensions:
                full_path = (folder / file).resolve()
                image = Image.fromarray(iio.imread(full_path))
                image_data = ImageData(
                    path=full_path,
                    image=image,
                )
                images.append(image_data)
    return images


def resize_images(images, width):
    resized_images: List[ImageData] = []
    for im in images:
        ratio = width / im.image.size[0]
        new_height = int(im.image.size[1] * ratio)
        new_width = int(im.image.size[0] * ratio)

        resized_image = im.image.resize((new_width, new_height))
        resized_images.append(
            ImageData(
                path=im.path,
                image=resized_image,
            )
        )

    return resized_images


def save_files(resized, resized_folder):
    resized_folder.mkdir(exist_ok=True)
    for im in resized:
        im.image.save(resized_folder / im.path.name)
