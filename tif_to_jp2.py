"""Simple utility to convert a TIFF image to JPEG2000 using GDAL.

Usage:
    python tif_to_jp2.py input.tif output.jp2 [--quality 25]

This script relies on the GDAL Python bindings and the open-source
`JP2OpenJPEG` driver. Ensure GDAL is installed with JPEG2000 support.
"""

import argparse
from osgeo import gdal


def convert_tiff_to_jp2(src_path: str, dst_path: str, quality: int) -> None:
    """Convert a GeoTIFF file to JPEG2000.

    Parameters
    ----------
    src_path : str
        Path to the source TIFF image.
    dst_path : str
        Desired path for the JPEG2000 output.
    quality : int
        Compression quality (1-100); higher is better quality and larger
        file sizes.
    """

    dataset = gdal.Open(src_path)
    if dataset is None:
        raise RuntimeError(f"Cannot open source file: {src_path}")

    creation_options = [f"QUALITY={quality}"]
    gdal.Translate(
        dst_path,
        dataset,
        format="JP2OpenJPEG",
        creationOptions=creation_options,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("src", help="Input TIFF image path")
    parser.add_argument("dst", help="Output JPEG2000 path")
    parser.add_argument(
        "--quality",
        type=int,
        default=25,
        help="JPEG2000 quality (1-100). Default: 25",
    )
    args = parser.parse_args()
    convert_tiff_to_jp2(args.src, args.dst, args.quality)
