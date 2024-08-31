# histogram.py

`histogram.py` is a Python utility designed to analyze and visualize audio files by generating histogram charts. These charts offer insights into the mastering process of albums, revealing details like compression and soft/hard clipping, which are often not captured by traditional dynamic range meters.

![histogram](https://github.com/user-attachments/assets/61cb4479-598a-45e3-be63-b2bf6b0b601a)

## Installation

To use `histogram.py`, ensure you have Python 3.8+ installed along with the following packages:

```bash
pip install numpy matplotlib soundfile
```

## Usage

You can run the script from the command line as follows:

```bash
python3 histogram.py [options]
```

### Examples

1. **Process a single file:**
   ```bash
   python3 histogram.py path/to/audio.flac
   ```

2. **Process a single album folder:**
   ```bash
   python3 histogram.py path/to/album
   ```

3. **Process all album folders recursively:**
   ```bash
   python3 histogram.py /path/to/albums --recursive
   ```

4. **Specify output image size and DPI:**
   ```bash
   python3 histogram.py /path/to/audio.flac --size 12 8 --dpi 150
   ```

5. **Display the histogram in a window:**
   ```bash
   python3 histogram.py /path/to/audio.flac --window
   ```

6. **Use custom regular expression for matching files:**
   ```bash
   python3 histogram.py /path/to/directory --match "\.wav$"
   ```

### Arguments

- `input`: Path to a file or directory (default: current working directory).
- `-f, --filename`: Name of the output image file (default: `histogram.png`).
- `-r, --recursive`: Recursively process directories.
- `-c, --concurrency`: Number of threads to use for processing (default: 1).
- `-s, --size`: Output image size in inches (default: `[10.24, 6.4]`).
- `--dpi`: DPI for the output image (default: `100`).
- `-m, --match`: Regular expression to match files (default: `(?i)\\.flac$`).
- `-w, --window`: Display histogram in a window.
- `-o, --overwrite`: Overwrite existing image files.

## Contributing

Feel free to open issues or submit pull requests if you have ideas for improvement or encounter any bugs.
