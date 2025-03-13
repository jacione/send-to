import imageio
from PIL import Image
import sys
from matplotlib import colormaps, pyplot as plt
import tifffile as tf
from pathlib import Path
import numpy as np
from src.utils import smart_input


def make_gif(f, fps, cmap, logscale, clip):
    print("Making GIF...",end="")
    image_stack = tf.imread(f.as_posix())
    if not image_stack.ndim == 3:
        raise IndexError(f"Cannot make GIF from {image_stack.ndim} dimensional data.")
    if logscale:
        image_stack = np.log(image_stack + 1)
    vmax = clip * np.max(image_stack)
    frames = []
    temp_files = [Path(f"{f.parent.as_posix()}/temporary_{i:05}.png") for i, _ in enumerate(image_stack)]
    for temp, img in zip(temp_files, image_stack):
        plt.imsave(temp, img, cmap=cmap, vmax=vmax)
    for temp, img in zip(temp_files, image_stack):
        reload = Image.open(temp)
        frames.append(reload)
        temp.unlink()
    imageio.mimsave(f"{f.parent.as_posix()}/{f.name}.gif", frames, duration=1000/fps)
    print("Done!")


if __name__ == '__main__':
    print("*"*50)
    print(f"{'Data >>> GIF':^50}")
    print("*"*50)
    print()
    _file = Path(sys.argv[1])
    print(f"TIFF file: {_file.as_posix()}")
    print()
    _fps = smart_input("Frames per second (default=10): ", ret_type="float", default=10.0)
    _cmap = smart_input("Colormap (default='plasma'): ", ret_type="float", default='plasma')
    _log = smart_input("Log scale (default=y): ", ret_type="float", default='y')
    _clip = smart_input("Clipping value (default=1): ", ret_type="float", default=1.0)
    make_gif(_file, _fps, _cmap, _log, _clip)
    input("Press enter to close...")