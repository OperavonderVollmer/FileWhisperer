# FileWhisperer

FileWhisperer is a Python package designed for handling file metadata, renaming, and translation of file names and metadata. It supports various file types, including images, audio, and text-based files.

## Features

- Extract metadata from image and audio files
- Modify and save metadata changes
- Rename files based on extracted or translated metadata
- Translate file names and metadata into different languages
- Handle multiple file formats efficiently

## Installation

### Prerequisites

- Python 3.x
- Required dependencies (install using pip):
  ```sh
  pip install pytaglib python-magic-bin pillow
  ```
- [OperaPowerRelay](https://github.com/OperavonderVollmer/OperaPowerRelay) (Required for additional utilities)
  ```sh
  pip install git+https://github.com/OperavonderVollmer/OperaPowerRelay.git@v1.1.2
  ```

### Manual Installation

1. Clone or download the repository.
2. Navigate to the directory containing `setup.py`:
   ```sh
   cd /path/to/FileWhisperer
   ```
3. Install the package in **editable mode**:
   ```sh
   pip install -e .
   ```

### Installing via pip:

```sh
pip install git+https://github.com/OperavonderVollmer/FileWhisperer.git@latest
```

Make sure you have the necessary dependencies installed in your environment.

## License

FileWhisperer is licensed under the MIT License.
