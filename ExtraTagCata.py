import os
from tqdm import tqdm


def extract_multiline_metadata_from_file(filepath):
    metadata = {'tags': [], 'categories': []}
    current_metadata_type = None

    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line.startswith("tags:") or line.startswith("tag:"):
                current_metadata_type = 'tags'
            elif line.startswith("categories:"):
                current_metadata_type = 'categories'
            elif line.startswith("subtitle:"):
                metadata['subtitle'] = line.split("subtitle:")[1].strip()
            elif line.startswith("-") and current_metadata_type:
                item = line[1:].strip()  # Remove hyphen and any leading/trailing spaces
                metadata[current_metadata_type].append(item)
            else:
                current_metadata_type = None
    return metadata


def process_markdown_files(directory):
    subtitle_dict = {}
    metadata_dict = {'tags': {}, 'categories': {}}
    filenames = [f for f in os.listdir(directory) if f.endswith(".md")]
    for filename in tqdm(filenames, desc="Processing files"):
        full_path = os.path.join(directory, filename)
        metadata = extract_multiline_metadata_from_file(full_path)
        if metadata.get('subtitle'):
            subtitle_dict[filename] = metadata.get('subtitle')
        for tag in metadata['tags']:
            metadata_dict['tags'].setdefault(tag, []).append(filename)
        for category in metadata['categories']:
            metadata_dict['categories'].setdefault(category, []).append(filename)
        # print(filename, "meta: ", metadata)
    return metadata_dict, subtitle_dict


def create_markdown_files_for_metadata(metadata_dict, subtitle_dict, directory):
    ori_dir = directory
    for metadata_type in metadata_dict:
        directory = os.path.join(ori_dir, metadata_type)
        for key, files in tqdm(metadata_dict[metadata_type].items(), desc=f"Creating {metadata_type} files"):
            file_path = os.path.join(directory, f"{key}.md")
            with open(file_path, 'w', encoding='utf-8') as file:
                for filename in files:
                    subtitle = subtitle_dict.get(filename, "No Subtitle")
                    file.write(f"- [[{filename}]] : {subtitle}" + '\n')


# Define the directory containing your markdown files
directory = '...../Post/'
# Replace with your directory path
print("Starting the processing of markdown files...")

# Process the markdown files
metadata_dict, subtitle_dict = process_markdown_files(directory)
print("Creating markdown files for each tag and category...")
# Create markdown files for each tag and categories
outputdire = "...../workspace/tmp/blog_tags"
create_markdown_files_for_metadata(metadata_dict, subtitle_dict, outputdire)
print("Processing completed.")
