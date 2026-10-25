"""Extract an explicitly requested foreground mask from alpha; no photo segmentation."""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image")
    parser.add_argument("--output", required=True)
    parser.add_argument("--alpha-threshold", type=int, default=128)
    args = parser.parse_args(argv)
    try:
        if not 1 <= args.alpha_threshold <= 255:
            raise ValueError("alpha threshold must be 1..255")
        output = Path(args.output)
        if output.exists():
            raise ValueError("Output already exists")
        with Image.open(args.image) as image:
            if image.width * image.height > 4_194_304:
                raise ValueError("Image exceeds 2048x2048 pixel budget")
            if "A" not in image.getbands():
                raise ValueError("Image needs a meaningful alpha channel; supply a manual foreground mask for photographs")
            alpha = np.asarray(image.getchannel("A"))
        mask = (alpha >= args.alpha_threshold).astype(np.uint8) * 255
        if not np.any(mask):
            raise ValueError("Alpha threshold produced an empty foreground")
        Image.fromarray(mask).save(output)
        print(f"Saved alpha-derived mask: {output}")
    except (OSError, ValueError) as error:
        parser.exit(2, f"Cannot extract mask: {error}\n")


if __name__ == "__main__":
    main()
