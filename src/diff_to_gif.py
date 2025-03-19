import sys
from pathlib import Path
from PIL import Image

import numpy as np
from matplotlib import colormaps, pyplot as plt, colorizer
import tifffile as tf
import imageio

import src.utils as ut


INFO = {
    "name": Path(__file__).stem,
    "title": "TIFF (data) to GIF",
}


def main(*data_files):
    ut.print_banner(INFO["title"])
    # Set additional parameters
    duration = 1000 / ut.smart_input("Frames per second", ret_type="float", default=20.0)
    cmap = ut.smart_input("Colormap", ret_type="float", default='plasma', options=list(colormaps))
    logscale = ut.smart_input("Log scale", ret_type="float", default='y')
    vmax = ut.smart_input("Clipping value", ret_type="float", default=1.0)
    rev = ut.smart_input("Reverse order", ret_type="bool", default=False)

    c = colorizer.Colorizer(cmap)

    print("TIFF files:")
    for data_file in data_files:
        data_file = Path(data_file)
        image_stack = tf.imread(data_file.as_posix())
        if not image_stack.ndim == 3:
            print(f"\t\tERROR: Cannot make GIF from {image_stack.ndim}-dimensional data.")
            continue
        c.set_clim(vmax=vmax)
        print(f"\t{data_file.name}")
        if logscale:
            image_stack = np.log(image_stack + 1)
        frames = [Image.fromarray(c.to_rgba(img), mode='RGBA') for img in image_stack]
        if rev:
            frames = reversed(frames)
        imageio.mimsave(f"{data_file.parent.as_posix()}/{data_file.stem}.gif", frames, repeat=-1, duration=duration)

    print("Done!")


if __name__ == '__main__':
    main(*sys.argv[1:])
    input("Press enter to close...")
