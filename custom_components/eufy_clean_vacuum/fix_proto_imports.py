#!/usr/bin/env python3
"""Script to fix protobuf imports in generated pb2 files."""
import os
import re
from pathlib import Path

def fix_imports(file_path: Path) -> None:
    """Fix imports in a protobuf file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace imports from proto.cloud to use the full package path
    content = re.sub(
        r'from proto\.cloud import (\w+) as proto_dot_cloud_dot_(\w+)__pb2',
        r'from custom_components.eufy_clean_vacuum.proto.cloud import \1 as proto_dot_cloud_dot_\2__pb2',
        content
    )

    # Replace the source path in the generated comment
    content = re.sub(
        r'# source: proto/cloud/(.+)\.proto',
        r'# source: custom_components/eufy_clean_vacuum/proto/cloud/\1.proto',
        content
    )

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    """Main function."""
    # Get the directory containing this script
    script_dir = Path(__file__).parent
    proto_dir = script_dir / 'proto' / 'cloud'

    # Process all pb2 files
    for pb2_file in proto_dir.glob('*_pb2.py'):
        print(f"Processing {pb2_file}")
        fix_imports(pb2_file)

if __name__ == '__main__':
    main()
