import os
import json
import re


def find_metadata_files(root_dir):
    """Recursively find all metadata.json files in the given directory."""
    metadata_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        if "metadata.json" in filenames:
            metadata_files.append(os.path.join(dirpath, "metadata.json"))
    return metadata_files


def extract_oblique_strategy(task_text):
    """Extract the second occurrence of text inside single quotes from the task string."""
    matches = re.findall(r"'([^']+)'", task_text)
    return matches[1] if len(matches) > 1 else None


def update_metadata_file(file_path):
    """Update the metadata.json file with the extracted oblique strategy."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "task" in data:
            strategy = extract_oblique_strategy(data["task"])
            if strategy:
                data["strategy"] = strategy

                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                print(f"Updated: {file_path}")
            else:
                print(f"No second oblique strategy found in task: {file_path}")
        else:
            print(f"No 'task' key found in: {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")


def extract_strategies(root_directory):
    metadata_files = find_metadata_files(root_directory)

    for metadata_file in metadata_files:
        update_metadata_file(metadata_file)


# Run optimization
def main():
    import argparse
    parser = argparse.ArgumentParser(description="Extracts strategies in a given directory.")
    parser.add_argument("--directory", type=str, help="Path to the directory containing errors.")

    args = parser.parse_args()

    # If the directory was not provided via CLI, ask for it interactively
    target_directory = args.directory if args.directory else input("Enter the directory path to scan: ").strip()

    # Validate the directory
    if os.path.exists(target_directory):
        extract_strategies(target_directory)
    else:
        print("Invalid directory path. Please enter a valid path.")


if __name__ == "__main__":
    main()