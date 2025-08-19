# Python27tools

This repository contains assorted utilities written in Python. It now includes
`tif_to_jp2.py`, a small open-source script that compresses TIFF images to
JPEG2000 using the GDAL `JP2OpenJPEG` driver.

## Requirements

- [GDAL](https://gdal.org) with JPEG2000 support (``JP2OpenJPEG`` driver).

## Usage

```bash
python tif_to_jp2.py input.tif output.jp2 --quality 25
```

Adjust the `--quality` value (1-100) to trade off compression against
image fidelity. Higher values produce larger files with better quality.
