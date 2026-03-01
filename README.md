# File Tree Viewer

A simple Python tool to visualize directory structures in your terminal or browser.

## Features

- 📁 **Tree visualization** - Display folders and files hierarchically
- 📊 **File statistics** - Shows file sizes and last modified dates
- 🌐 **Web view** - Generate beautiful HTML for browser viewing
- 🔍 **Interactive** - Expand/collapse folders in browser view
- 📈 **Summary stats** - Total directories, files, and combined size

## Installation

```bash
git clone https://github.com/didigamnithin/file-tree-viewer.git
cd file-tree-viewer
```

## Usage

### Terminal View (Default)

```bash
# Show current directory
python3 show_files.py

# Show specific directory
python3 show_files.py Desktop

# Show hidden files
python3 show_files.py -a
```

### Web/Browser View

```bash
# Generate HTML and open in browser
python3 show_files.py -w

# Web view for specific directory
python3 show_files.py -w Desktop

# Web view with hidden files
python3 show_files.py -w -a
```

## Examples

```bash
# View your home directory
python3 show_files.py ~

# View with web browser
python3 show_files.py -w /path/to/folder
```

## Requirements

- Python 3.x
- No external dependencies required

## License

MIT
