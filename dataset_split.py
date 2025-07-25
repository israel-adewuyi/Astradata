import os
import csv
import json
from typing import List

def flatten_problem_data(contest_id, problem_key, problem_data):
    """
    Flatten each problem into a single row dictionary.
    """
    examples = problem_data.get("examples", [])
    processed_examples = [
        {
            'input': ['\n'.join(item['input'])] if isinstance(item['input'], list) else [item['input']],
            'output': ['\n'.join(item['output'])] if isinstance(item['output'], list) else [item['output']],
            'explanation': item.get('explanation', '')
        }
        for item in examples
    ]
    
    row = {
        "contest_id": contest_id,
        "problem_id": f"{contest_id}{problem_key}",
        "problem_key": problem_key,
        "name": problem_data.get("name", ""),
        "statement": problem_data.get("statement", ""),
        "input_format": problem_data.get("input_format", ""),
        "output_format": problem_data.get("output_format", ""),
        "examples": json.dumps(processed_examples),
        "notes": problem_data.get("notes", ""),
        "datasource": problem_data.get("datasource", "")
    }
    return row

def split_json_to_csv(input_path):
    """
    Reads the merged JSON, splits into train and test CSVs based on:
    - Test: CF contests >= 2008 or AtC contests >= 350
    - Train: All others
    """
    # Check if file exists
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"The file {input_path} does not exist.")

    # Load JSON data
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        raise ValueError("The file is not a valid JSON format.")

    # Initialize train and test rows
    train_rows = []
    test_rows = []

    # Fieldnames for CSV
    fieldnames = [
        "contest_id", "problem_id", "problem_key", "name", "statement",
        "input_format", "output_format", "examples", "notes", "datasource"
    ]

    # Process each contest and problem
    for contest_id, problems in data.items():
        for problem_key, problem_data in problems.items():
            row = flatten_problem_data(contest_id, problem_key, problem_data)
            # Determine if test or train
            datasource = problem_data.get("datasource", "")
            try:
                # Extract numeric contest ID (handle CF_ prefix for Codeforces)
                numeric_id = int(contest_id.replace("CF_", "") if contest_id.startswith("CF_") else contest_id)
                if (datasource == "CF" and numeric_id >= 2030) or (datasource == "AtC" and numeric_id >= 383):
                    test_rows.append(row)
                else:
                    train_rows.append(row)
            except ValueError:
                print(f"Warning: Invalid contest_id format {contest_id}, defaulting to train")
                train_rows.append(row)

    # Get directory and base name
    dir_name = os.path.dirname(input_path)
    base_name = os.path.splitext(os.path.basename(input_path))[0]

    # Save train CSV
    train_file = os.path.join(dir_name, f"{base_name}_train.csv")
    with open(train_file, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(train_rows)
    print(f"Saved train dataset ({len(train_rows)} rows) to {train_file}")

    # Save test CSV
    test_file = os.path.join(dir_name, f"{base_name}_test.csv")
    with open(test_file, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(test_rows)
    print(f"Saved test dataset ({len(test_rows)} rows) to {test_file}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python dataset_split.py <path_to_merged_json>")
    else:
        split_json_to_csv(sys.argv[1])