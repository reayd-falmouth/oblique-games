import ast
import json
import os
import re


def find_metadata_files(root_dir):
    """Recursively finds all metadata.json files in the given directory tree."""
    metadata_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename == "metadata.json":
                metadata_files.append(os.path.join(dirpath, filename))
    return metadata_files


def fix_json_format(file_path):
    """Attempts to fix JSON formatting issues and rewrite the file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw_content = f.read()

        # Try to load JSON normally
        fixed_data = json.loads(raw_content)

        # Detect and fix improperly formatted JSON fields
        for key, value in fixed_data.items():
            if isinstance(value, str):
                # Remove surrounding newlines, excessive spaces, and backticks
                cleaned_value = value.strip()

                # Detect triple backticks and remove them
                cleaned_value = re.sub(r"^```|```$", "", cleaned_value).strip()

                # Try to convert it into a valid JSON object
                try:
                    parsed_value = json.loads(cleaned_value)
                    fixed_data[key] = parsed_value
                except json.JSONDecodeError:
                    # If json.loads fails, try ast.literal_eval (for dictionary-like strings)
                    try:
                        fixed_data[key] = ast.literal_eval(cleaned_value)
                    except (SyntaxError, ValueError):
                        # If all else fails, leave it as a string
                        fixed_data[key] = cleaned_value

        # Convert back to properly formatted JSON
        corrected_json = json.dumps(fixed_data, indent=4)

        # Overwrite the file with fixed JSON
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(corrected_json)

        return "Fixed and reformatted JSON."

    except json.JSONDecodeError as e:
        return f"Could not auto-fix JSON: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


def find_errors(directory):
    print(f"Scanning directory: {directory}...\n")
    metadata_files = find_metadata_files(directory)
    report = {}

    for file in metadata_files:
        result = fix_json_format(file)
        report[file] = result

    print("\nProcessing Results:")
    for file, result in report.items():
        print(f"\n{file}:")
        print(f"  - {result}")


# Run optimization
def main():
    import argparse

    parser = argparse.ArgumentParser(description="Fix errors in a given directory.")
    parser.add_argument(
        "--directory", type=str, help="Path to the directory containing errors."
    )

    args = parser.parse_args()

    # If the directory was not provided via CLI, ask for it interactively
    target_directory = (
        args.directory
        if args.directory
        else input("Enter the directory path to scan: ").strip()
    )

    # Validate the directory
    if os.path.exists(target_directory):
        find_errors(target_directory)
    else:
        print("Invalid directory path. Please enter a valid path.")


if __name__ == "__main__":
    main()
