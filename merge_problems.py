import json
import os

def merge_jsons(atcoder_path, codeforces_path, output_path):
    # Load AtCoder JSON
    if not os.path.isfile(atcoder_path):
        raise FileNotFoundError(f"AtCoder file {atcoder_path} does not exist.")
    with open(atcoder_path, 'r', encoding='utf-8') as f:
        atcoder_data = json.load(f)

    # Load Codeforces JSON
    if not os.path.isfile(codeforces_path):
        raise FileNotFoundError(f"Codeforces file {codeforces_path} does not exist.")
    with open(codeforces_path, 'r', encoding='utf-8') as f:
        codeforces_data = json.load(f)

    # Initialize merged data
    merged_data = {}

    # Process AtCoder data
    for contest_id, problems in atcoder_data.items():
        merged_data[contest_id] = {}
        for problem_key, problem_data in problems.items():
            problem_data['datasource'] = 'AtC'
            merged_data[contest_id][problem_key] = problem_data

    # Process Codeforces data
    for contest_id, problems in codeforces_data.items():
        if contest_id in merged_data:
            # Handle potential contest ID conflicts by prefixing Codeforces contests
            contest_id = f"CF_{contest_id}"
        merged_data[contest_id] = {}
        for problem_key, problem_data in problems.items():
            problem_data['datasource'] = 'CF'
            merged_data[contest_id][problem_key] = problem_data

    # Save merged data
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, indent=2, ensure_ascii=False)

    print(f"Merged {len(merged_data)} contests into {output_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Usage: python merge_problems.py <atcoder_json_path> <codeforces_json_path> <output_json_path>")
    else:
        merge_jsons(sys.argv[1], sys.argv[2], sys.argv[3])