import sys
import os


def split_by_chars(file_path, max_chars=3500):
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    total_chars = len(content)
    file_root, file_ext = os.path.splitext(file_path)

    # Define and create the output subdirectory
    output_dir = f"{file_root}_parts"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for i in range(0, total_chars, max_chars):
        chunk = content[i : i + max_chars]
        part_num = (i // max_chars) + 1

        # Save files inside the new directory
        base_name = os.path.basename(file_root)
        output_filename = os.path.join(
            output_dir, f"{base_name}_part_{part_num}{file_ext}"
        )

        with open(output_filename, "w", encoding="utf-8") as out_f:
            out_f.write(chunk)

        print(f"Created: {output_filename} ({len(chunk)} characters)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python split_chars.py <filename>")
    else:
        split_by_chars(sys.argv[1])
