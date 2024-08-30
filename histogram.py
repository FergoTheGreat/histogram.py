#!/usr/bin/env python3

# This is free and unencumbered software released into the public domain.
#
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.
#
# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# For more information, please refer to <https://unlicense.org>

import sys
import re
import argparse
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import soundfile as sf
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

def regex_type(value):
    try:
        return re.compile(value)
    except re.error as e:
        raise argparse.ArgumentTypeError(f"Invalid regular expression: {e}")

def db(value):
    return 20 * np.log10(value) if value > 0 else -np.inf

def main():
    parser = argparse.ArgumentParser(description="Generate histograms from audio files")
    parser.add_argument("input", nargs="?", default=Path.cwd(), type=Path, help="Directory or file path (default: current working directory)")
    parser.add_argument("-f", "--filename", nargs="?", type=str, default="histogram.png", help="Output image filename (default: histogram.png)")
    parser.add_argument("-r", "--recursive", action="store_true", help="Recursively process directories")
    parser.add_argument("-c", "--concurrency", nargs="?", type=int, default=1, help="Set the maximum number of threads (default: 1)")
    parser.add_argument("-s", "--size", type=float, nargs=2, default=[10.24, 6.4], help="Output image size in inches", metavar=("WIDTH", "HEIGHT"))
    parser.add_argument("--dpi", type=int, nargs="?", default=100, help="DPI for the output image (default: 100)")
    parser.add_argument("-m", "--match", type=regex_type, nargs="?", default=r"(?i)\.flac$", help="Regular expression to match files (default: \"(?i)\\.flac$\")")
    parser.add_argument("-w", "--window", action="store_true", help="Display the histogram in a window instead of saving to a file (will ignore --recursive)")
    parser.add_argument("-o", "--overwrite", action="store_true", help="Overwrite existing image files")
    args = parser.parse_args()

    if not args.input.exists():
        raise argparse.ArgumentTypeError(f"No file or directory named \"{args.input}\".")

    if any(d <= 0 for d in args.size):
        raise argparse.ArgumentTypeError("Size dimensions must be positive integers.")

    if not args.window:
        matplotlib.use("agg")
   
    if not args.window and args.recursive and args.input.is_dir():
        paths = [args.input] + [p for p in args.input.rglob("*") if p.is_dir()]
        with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
            executor.map(lambda path : create_histogram(path, args), paths)
    else:
        create_histogram(args.input, args)
    
def create_histogram(path, args):
    title = path.stem if path.is_file() else path.name
    output_path = (path.parent if path.is_file() else path) / args.filename

    if not args.window and not args.overwrite and output_path.exists():
        return

    files = [path] if path.is_file() else [
        file for file in path.glob("*") if file.is_file() and re.search(args.match, file.name)
    ]

    if not files:
        return

    tracks, length, peak, rms, samples = decode(files)
    hist, bin_edges = np.histogram(samples, bins=1000, range=(-1, 1))

    plt.rcParams.update({
        "lines.color": "white",
        "patch.edgecolor": "white",
        "text.color": "white",
        "axes.facecolor": "black",
        "axes.edgecolor": "lightgray",
        "axes.labelcolor": "white",
        "xtick.color": "white",
        "ytick.color": "white",
        "grid.color": "gray",
        "figure.facecolor": "black",
        "figure.edgecolor": "black",
        "savefig.facecolor": "black",
        "savefig.edgecolor": "black"})

    fig, ax = plt.subplots(figsize=args.size)
    ax.plot(bin_edges[:-1], hist, color="red", linewidth=1)
    ax.grid(True, which="both", linestyle="--", linewidth=0.5)
    ax.set_yscale("log")
    ax.set_yticks(np.logspace(0, 8, 9))
    ax.set_ylim(ymin=1)
    ax.set_ylabel("Number of Samples")
    ax.set_xlabel("Sample Value")
    ax.set_title(title, wrap=True, pad=15)
    fig.text(0.01, 0.01, f"Tracks: {tracks}, Length: {fmt_length(length)}", va="bottom", ha="left")
    fig.text(0.99, 0.01, f"Peak: {peak:.2f} dB FS, RMS(Sine): {rms:.2f} dB FS", va="bottom", ha="right")

    if args.window:
        plt.show()
    else:
        plt.savefig(output_path, dpi=args.dpi)
        print(f"Processed: {title}")

    plt.close(fig)

def decode(files):
    length = 0.0
    sample_arrays = []
    for file in files:
        samples, samplerate = sf.read(file)
        length += len(samples) / samplerate
        sample_arrays.append(samples.flatten() if samples.ndim > 1 else samples)
    tracks = len(sample_arrays)
    samples = np.clip(np.concatenate(sample_arrays), -1, 1)
    peak = db(np.max(np.abs(samples)))
    rms = db(np.sqrt(np.mean(samples ** 2)) * np.sqrt(2))
    return tracks, length, peak, rms, samples

def fmt_length(seconds):
    hours, seconds = divmod(round(seconds), 3600)
    minutes, seconds = divmod(seconds, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)