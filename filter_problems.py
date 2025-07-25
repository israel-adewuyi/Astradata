import re
import json
import argparse
from collections import defaultdict
from typing import List

def load_data(file_dir: str) -> List[dict]:
    with open(file_dir, "r", encoding="utf-8") as data_file:
        data = json.load(data_file)
    return data

def is_valid_problem(problem_data: dict) -> bool:
    statement = problem_data["statement"]
    output_format = problem_data["output_format"]

    is_interactive = "interactive" in statement or "interactive" in output_format
    has_multi_sol = "print any of" in statement or "print any of" in output_format or \
                    "output any" in statement or "output any" in output_format
    return False if is_interactive or has_multi_sol else True

def filter_dataset(file_dir: str):
    data = load_data(file_dir)

    new_data = defaultdict(dict)
    for contest in data:
        for problem in data[contest]:
            problem_data = data[contest][problem]
            if problem_data['name']:
                if contest == "1213" and problem == "A":
                    print(problem_data)
                flag = is_valid_problem(problem_data)
                if flag:
                    new_data[contest][problem] = problem_data

    with open(f"datafiles/cp_datasetv1.json", "w", encoding="utf-8") as f:
        json.dump(new_data, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=str, required=True,
                       help="Location of csv containing problem info")

    args = parser.parse_args()

    filter_dataset(args.dir)
    