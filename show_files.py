#!/usr/bin/env python3
"""
Simple program to visualize directory structure.
Run with: python3 show_files.py [path]
If no path is provided, uses current directory.
Add -w flag to generate HTML for browser view.
"""

import os
import sys
import html
from pathlib import Path
from datetime import datetime


def format_size(size_bytes):
    """Convert bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def count_items(path):
    """Count files and directories in a path."""
    try:
        items = list(os.scandir(path))
        files = sum(1 for item in items if item.is_file())
        dirs = sum(1 for item in items if item.is_dir())
        return files, dirs
    except (PermissionError, OSError):
        return 0, 0


def print_tree(path, prefix="", is_last=True, max_depth=3, current_depth=0):
    """Print directory tree structure."""
    path = Path(path)

    if not path.exists():
        print(f"Error: Path '{path}' does not exist")
        return

    # Print current item
    connector = "└── " if is_last else "├── "
    name = path.name if path.name else str(path)

    if path.is_dir():
        print(f"{prefix}{connector}📁 {name}/")
    else:
        size = format_size(path.stat().st_size)
        print(f"{prefix}{connector}📄 {name} ({size})")

    # Print children for directories
    if path.is_dir() and current_depth < max_depth:
        try:
            items = sorted(os.scandir(path), key=lambda x: (not x.is_dir(), x.name.lower()))
            # Filter out hidden files unless -a flag is used
            if not show_hidden:
                items = [item for item in items if not item.name.startswith('.')]

            for i, item in enumerate(items):
                is_last_item = i == len(items) - 1
                extension = "    " if is_last else "│   "
                print_tree(item.path, prefix + extension, is_last_item, max_depth, current_depth + 1)

            if len(list(os.scandir(path))) > len(items):
                print(f"{prefix}{'    ' if is_last else '│   '}... (hidden items)")

        except PermissionError:
            print(f"{prefix}{'    ' if is_last else '│   '}[Permission Denied]")
        except OSError as e:
            print(f"{prefix}{'    ' if is_last else '│   '}[Error: {e}]")


def generate_html_tree(path, show_hidden=False, max_depth=4, current_depth=0):
    """Generate HTML tree structure."""
    path = Path(path)

    if not path.exists():
        return ""

    if path.is_file():
        size = format_size(path.stat().st_size)
        modified = datetime.fromtimestamp(path.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
        return f'<div class="file"><span class="file-icon">📄</span> <span class="name">{html.escape(path.name)}</span> <span class="meta">{size} • {modified}</span></div>'

    if not path.is_dir():
        return ""

    try:
        items = sorted(os.scandir(path), key=lambda x: (not x.is_dir(), x.name.lower()))
        if not show_hidden:
            items = [item for item in items if not item.name.startswith('.')]
    except (PermissionError, OSError):
        return f'<div class="error">[Permission Denied]</div>'

    if current_depth >= max_depth:
        return '<div class="truncated">... (max depth reached)</div>'

    children_html = ""
    for item in items:
        child_html = generate_html_tree(item.path, show_hidden, max_depth, current_depth + 1)
        if child_html:
            children_html += f'<div class="tree-item">{child_html}</div>'

    if children_html:
        return f'''
        <details class="folder" {"open" if current_depth < 2 else ""}>
            <summary><span class="folder-icon">📁</span> <span class="name">{html.escape(path.name)}</span></summary>
            <div class="children">{children_html}</div>
        </details>
        '''
    else:
        return f'<div class="folder-empty"><span class="folder-icon">📁</span> <span class="name">{html.escape(path.name)}</span> <span class="meta">(empty)</span></div>'


def generate_html_report(target_path, output_path="file_tree.html"):
    """Generate HTML file with directory tree."""
    path = Path(target_path).resolve()

    # Count stats
    total_files = 0
    total_dirs = 0
    total_size = 0

    for root, dirs, files in os.walk(path):
        if not show_hidden:
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            files = [f for f in files if not f.startswith('.')]

        total_dirs += len(dirs)
        total_files += len(files)

        for file in files:
            try:
                total_size += os.path.getsize(os.path.join(root, file))
            except (OSError, PermissionError):
                pass

    tree_html = generate_html_tree(path, show_hidden)

    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Directory Tree - {html.escape(path.name)}</title>
    <style>
        * {{
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 28px;
        }}
        .header .path {{
            opacity: 0.9;
            font-size: 14px;
            word-break: break-all;
        }}
        .stats {{
            display: flex;
            justify-content: center;
            gap: 40px;
            padding: 20px;
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
        }}
        .stat {{
            text-align: center;
        }}
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-label {{
            font-size: 12px;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .tree-container {{
            padding: 30px;
            max-height: 70vh;
            overflow-y: auto;
        }}
        details {{
            margin: 4px 0;
        }}
        summary {{
            cursor: pointer;
            padding: 8px 12px;
            border-radius: 8px;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        summary:hover {{
            background: #f0f4ff;
        }}
        details[open] > summary {{
            background: #e8edff;
        }}
        .children {{
            padding-left: 28px;
            border-left: 2px solid #e9ecef;
            margin-left: 12px;
            margin-top: 4px;
        }}
        .file {{
            padding: 8px 12px;
            margin: 4px 0;
            border-radius: 8px;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.2s;
        }}
        .file:hover {{
            background: #f8f9fa;
        }}
        .folder-empty {{
            padding: 8px 12px;
            color: #6c757d;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .name {{
            font-weight: 500;
            color: #212529;
        }}
        .meta {{
            font-size: 12px;
            color: #6c757d;
            margin-left: auto;
        }}
        .folder-icon, .file-icon {{
            font-size: 18px;
        }}
        .truncated {{
            color: #6c757d;
            font-style: italic;
            padding: 8px 12px;
        }}
        .error {{
            color: #dc3545;
            padding: 8px 12px;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            color: #6c757d;
            font-size: 12px;
        }}
        /* Scrollbar styling */
        .tree-container::-webkit-scrollbar {{
            width: 8px;
        }}
        .tree-container::-webkit-scrollbar-track {{
            background: #f1f1f1;
        }}
        .tree-container::-webkit-scrollbar-thumb {{
            background: #888;
            border-radius: 4px;
        }}
        .tree-container::-webkit-scrollbar-thumb:hover {{
            background: #555;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📂 Directory Tree</h1>
            <div class="path">{html.escape(str(path))}</div>
        </div>

        <div class="stats">
            <div class="stat">
                <div class="stat-value">{total_dirs}</div>
                <div class="stat-label">Folders</div>
            </div>
            <div class="stat">
                <div class="stat-value">{total_files}</div>
                <div class="stat-label">Files</div>
            </div>
            <div class="stat">
                <div class="stat-value">{format_size(total_size)}</div>
                <div class="stat-label">Total Size</div>
            </div>
        </div>

        <div class="tree-container">
            {tree_html}
        </div>

        <div class="footer">
            Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} •
            {'Hidden files shown' if show_hidden else 'Hidden files hidden (use -a to show)'}
        </div>
    </div>
</body>
</html>'''

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return output_path


def show_summary(path):
    """Show summary statistics for a directory."""
    path = Path(path)
    if not path.is_dir():
        return

    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)

    total_files = 0
    total_dirs = 0
    total_size = 0

    for root, dirs, files in os.walk(path):
        if not show_hidden:
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            files = [f for f in files if not f.startswith('.')]

        total_dirs += len(dirs)
        total_files += len(files)

        for file in files:
            try:
                total_size += os.path.getsize(os.path.join(root, file))
            except (OSError, PermissionError):
                pass

    print(f"📁 Total Directories: {total_dirs}")
    print(f"📄 Total Files:       {total_files}")
    print(f"💾 Total Size:        {format_size(total_size)}")


if __name__ == "__main__":
    # Parse flags
    show_hidden = '-a' in sys.argv
    web_mode = '-w' in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith('-')]

    # Get target directory
    target_path = args[0] if args else "."

    if web_mode:
        print(f"\n🌐 Generating HTML view...")
        output_file = generate_html_report(target_path)
        output_path = Path(output_file).resolve()
        print(f"✅ HTML file created: {output_path}")
        print(f"\nOpening in browser...")

        # Open in browser
        import webbrowser
        webbrowser.open(f'file://{output_path}')
    else:
        print(f"\n📂 Directory Tree: {Path(target_path).resolve()}")
        print("=" * 50)
        print()

        print_tree(target_path)
        show_summary(target_path)

        print(f"\nTip: Use 'python3 {sys.argv[0]} -w' for browser view")
        print(f"     Use 'python3 {sys.argv[0]} -a' to show hidden files")
