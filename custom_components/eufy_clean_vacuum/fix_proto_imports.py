"""Fix protobuf imports in generated files."""
import os
import re

def fix_imports(file_path: str) -> None:
    """Fix imports in a single file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace 'from proto.cloud' with relative import
    content = re.sub(
        r'from proto\.cloud import (\w+)',
        r'from . import \1',
        content
    )

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    """Fix imports in all protobuf files."""
    # Get the directory containing this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    proto_dir = os.path.join(current_dir, 'proto', 'cloud')

    # Process all Python files in the proto directory
    for filename in os.listdir(proto_dir):
        if filename.endswith('_pb2.py'):
            file_path = os.path.join(proto_dir, filename)
            print(f"Fixing imports in {filename}")
            fix_imports(file_path)

if __name__ == '__main__':
    main()
