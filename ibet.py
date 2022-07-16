#!/usr/bin/env python

import argparse
import os
import time

from enum import Enum
from functools import partial
from PIL import Image, ImageOps


class Operations(Enum):
    SOLARIZE = 0, partial(ImageOps.solarize, threshold=128)
    INVERT = 1, ImageOps.invert

    @property
    def func(self):
        return self.value[1]


def batch_edit(operation, in_dir: str, out_dir: str) -> None:
    files = [os.path.join(in_dir, f) for f in os.listdir(in_dir)]
    img_files = list(filter(verify_if_image, files))

    if len(img_files) == 0:
        print(f'Found no images in {in_dir}')
        exit(1)

    start = time.time()
    print(f"Running on directory \"{in_dir}\"")
    for img_file in img_files:
        _, img_filename = os.path.split(img_file)
        img = Image.open(img_file)
        processed_img = operation.func(img)
        processed_img.save(os.path.join(out_dir, img_filename))
    end = time.time()
    print(f"Finished, total processing time: {(end - start):2f} seconds")


def verify_if_image(file_path: str) -> bool:
    _, filename = os.path.split(file_path)
    image_extensions = ('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')

    return True if filename.lower().endswith(image_extensions) else False


def verify_dir_paths(in_dir: str, out_dir: str) -> (str, str):
    if not os.path.isabs(in_dir):
        in_dir = os.path.abspath(in_dir)
    if not out_dir:
        out_dir = in_dir
    elif not os.path.isabs(out_dir):
        out_dir = os.path.abspath(out_dir)
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)
    verify_overwrite(in_dir, out_dir)

    return in_dir, out_dir


def verify_overwrite(in_dir: str, out_dir: str) -> None:
    question = "Input and output directories are the same. " \
               "Images will be overwritten. Are you sure?"
    if in_dir == out_dir and not confirm(question):
        exit(1)


def confirm(question):
    reply = str(input(question + ' [y/N]: ')).lower().strip() or 'n'
    if reply[0] == 'y':
        return True
    if reply[0] == 'n':
        return False
    else:
        return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Batch edit images.')
    parser.add_argument('operation',
                        choices=Operations,
                        type=Operations.__getitem__,
                        help=f"Operation to perform. Choices: "
                             f"{', '.join([op.name for op in Operations])}")
    parser.add_argument('--read-from',
                        default=os.getcwd(),
                        type=str,
                        help='Directory containing images to process.')
    parser.add_argument('--write-to',
                        type=str,
                        help='Directory to save processed image to.')

    args = parser.parse_args()
    batch_edit(args.operation, *verify_dir_paths(args.read_from, args.write_to))
