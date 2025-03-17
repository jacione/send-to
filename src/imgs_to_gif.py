import sys
from pathlib import Path
from PIL import Image

import imageio

import src.utils as ut


INFO = {
    "name": Path(__file__).stem,
    "title": "Images to GIF",
}


def main(image_files):
    ut.print_banner(INFO["title"])

    print("Images:")
    for _file in image_files:
        if _file.suffix not in (".png", ".jpg", ".jpeg"):
            raise ValueError("All file extensions must be .png or .jpg")
        print(f"\t{_file.as_posix()}")
    print()

    output = ut.smart_input("Output file name (default='output'): ", ret_type="str", default="output")
    output = image_files[0].parent / f"{output.removesuffix(".gif")}.gif"
    duration = 1000 / ut.smart_input("Frames per second (default=10): ", ret_type="float", default=10.0)

    print("Creating GIF...", end="")
    frames = []
    for image_file in image_files:
        img = Image.open(image_file)
        frames.append(img)
    # Save the frames as a GIF animation
    imageio.mimwrite(output, frames, loop=0, duration=duration)

    print("Done!")
    print(f"Output:\n\t{output.as_posix()}")


if __name__ == "__main__":
    main([Path(f) for f in sorted(sys.argv[1:])])
    input("Press enter to close...")
