import sys
from pathlib import Path
from PIL import Image

import numpy as np
from matplotlib import colormaps, pyplot as plt
import tifffile as tf
import imageio

import src.utils as ut


INFO = {
    "name": Path(__file__).stem,
    "title": "TIFF (data) to GIF",
}


def main(data_file):
    ut.print_banner(INFO["title"])

    print(f"TIFF file:\n\t{data_file.as_posix()}")
    print()
    image_stack = tf.imread(data_file.as_posix())
    if not image_stack.ndim == 3:
        print(f"Cannot make GIF from {image_stack.ndim}-dimensional data.")
        return

    # Set additional parameters
    duration = 1000 / ut.smart_input("Frames per second", ret_type="float", default=20.0)
    cmap = ut.smart_input("Colormap", ret_type="float", default='plasma', options=list(colormaps))
    if ut.smart_input("Log scale", ret_type="float", default='y'):
        image_stack = np.log(image_stack + 1)
    vmax = np.max(image_stack) * ut.smart_input("Clipping value", ret_type="float", default=1.0)

    print("Making GIF...",end="")

    frames = []
    temp_files = [Path(f"{data_file.parent.as_posix()}/temporary_{i:05}.png") for i, _ in enumerate(image_stack)]
    for temp, img in zip(temp_files, image_stack):
        plt.imsave(temp, img, cmap=cmap, vmax=vmax)
    for temp, img in zip(temp_files, image_stack):
        reload = Image.open(temp)
        frames.append(reload)
    imageio.mimsave(f"{data_file.parent.as_posix()}/{data_file.stem}.gif", frames, repeat=0, duration=duration)
    for temp in temp_files:
        temp.unlink()

    print("Done!")


if __name__ == '__main__':
    main(Path(sys.argv[1]))
    input("Press enter to close...")
