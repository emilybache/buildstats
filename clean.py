#!/usr/bin/env python3
import os
import sys
from pathlib import Path


def main(args):
    """Remove old log files. Use this after you successfully processed their testdata into a csv file"""
    if args:
        data_folder = args[0]
    else:
        data_folder = Path.cwd() / "testdata"
    for root, directories, files in os.walk(data_folder):
        for file in files:
            if file.endswith(".log"):
                os.remove(os.path.join(root, file))


if __name__ == "__main__":
    main(sys.argv[1:])