import os
import sys
from tqdm import tqdm

def date_format(paras):
    """
    Formats the date string found in the markdown metadata.

    Args:
    - paras (str): The original line containing the date metadata.

    Returns:
    - str: The formatted date line ready to be written back to the file.
    """
    # Replace 'date' with 'calendar_date' to match project naming conventions.
    new_line = paras.replace('date', 'calendar_date')
    # Reconstruct the string to match the required format, ignoring time if present.
    new_line = " ".join(new_line.split(" ")[:2])
    # Append a newline character to the end of the string.
    new_line += "\n"
    return new_line

def extract_single_metadata(dirpath, max_num=999):
    """
    Processes markdown files in a given directory, updating their metadata.

    Args:
    - dirpath (str): The path to the directory containing markdown files.
    - max_num (int): The maximum number of files to process.

    Returns:
    - bool: True if the process is completed successfully, otherwise False.
    """
    file_list = [f for f in os.listdir(dirpath) if f.endswith(".md")]
    processed_file = 0
    for md in tqdm(file_list, desc="Processing files"):
        if processed_file >= max_num:
            break
        processed_file += 1
        md_path = os.path.join(dirpath, md)
        modify_calendar_meta(md_path)
    return True

def modify_calendar_meta(filepath):
    """
    Modifies the 'date' metadata in a markdown file to 'calendar_date'.

    Args:
    - filepath (str): The path to the markdown file being modified.
    """
    with open(filepath, 'r', encoding='utf-8') as file:
        contents = file.readlines()

    chang_idx = -1
    insert_idx = -1
    origin_string = ""

    # Search for the 'date' and 'create_date' lines in the file.
    for idx, line in enumerate(contents):
        if line.startswith('date:'):
            origin_string = date_format(line)
            insert_idx = idx + 1
        if line.startswith('create_date:'):
            chang_idx = idx

    # Modify or insert the 'create_date' line.
    if chang_idx != -1:
        contents[chang_idx] = origin_string
    elif insert_idx != -1:
        contents.insert(insert_idx, origin_string)

    # Write the modified contents back to the file.
    with open(filepath, 'w', encoding='utf-8') as file:
        file.writelines(contents)

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) < 1:
        print('Usage: $1 -> dirpath, markdown files should be stored as dirpath/*.md; $2 (optional) -> max files to process')
    else:
        max_files = int(args[1]) if len(args) > 1 else 999
        extract_single_metadata(args[0], max_num=max_files)