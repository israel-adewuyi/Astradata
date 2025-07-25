import json
import argparse
from collections import defaultdict
from typing import List
import jsonschema
from dotenv import load_dotenv
from groq import Groq
import time

load_dotenv()

# Initialize Groq client
client = Groq()

# Define JSON schema for problem data
problem_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "statement": {"type": "string"},
        "input_format": {"type": "string"},
        "output_format": {"type": "string"},
        "examples": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "input": {"type": "array", "items": {"type": "string"}},
                    "output": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["input", "output"]
            }
        },
        "notes": {"type": "string"},
        "datasource": {"type": "string"}
    },
    "required": ["name", "statement", "input_format", "output_format", "examples", "datasource"]
}

def load_data(file_dir: str) -> List[dict]:
    """Load JSON data from file."""
    with open(file_dir, "r", encoding="utf-8") as data_file:
        data = json.load(data_file)
    return data

def save_data(file_dir: str, new_data: dict, new_problems: dict) -> None:
    """Save processed data to two JSON files."""
    with open(file_dir.replace('1.json', '2.json'), "w", encoding="utf-8") as data_file:
        json.dump(new_data, data_file, indent=2)
    with open(file_dir.replace('1.json', '2_new_problems.json'), "w", encoding="utf-8") as problems_file:
        json.dump(new_problems, problems_file, indent=2)

def validate_json(result_json: dict) -> bool:
    """Validate JSON against schema."""
    try:
        jsonschema.validate(instance=result_json, schema=problem_schema)
        return True
    except jsonschema.ValidationError as e:
        print(f"JSON validation failed: {e}")
        return False

def get_new_problem_data(problem_data: dict) -> dict:
    """Process problem data via Groq API to normalize case-insensitive responses."""
    try:
        completion = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "system",
                    "content": (
                        """You are given a competitive programming problem. Your task is to preprocess the problem data. "
                        "Do not solve the problem. Remove references to case-insensitive output in the 'statement' and "
                        "'output_format' fields, ensuring only a single solution format remains (e.g., 'YES' instead of "
                        "allowing 'yes', 'Yes', etc.). Return the modified problem data in JSON format.
                        "Some of these problems are saying that you can output multiple solutions, but I want this to be a single solution. The only fields you should consider changing are the statement and/or the output_format fields. \n\nRemove references for mention of case-insensivity. \n\nAs an example input, \n{\n            \"name\": \"A. False Alarm\",\n            \"statement\": \"Yousef is at the entrance of a long hallway with $$$n$$$ doors in a row, numbered from $$$1$$$ to $$$n$$$. He needs to pass through all the doors from $$$1$$$ to $$$n$$$ in order of numbering and reach the exit (past door $$$n$$$).\\nEach door can be open or closed. If a door is open, Yousef passes through it in $$$1$$$ second. If the door is closed, Yousef can't pass through it.\\nHowever, Yousef has a special button which he can use at most once at any moment. This button makes all closed doors become open for $$$x$$$ seconds.\\nYour task is to determine if Yousef can pass through all the doors if he can use the button at most once.\",\n            \"input_format\": \"Input\\nThe first line of the input contains an integer $$$t$$$ ($$$1 \\\\le t \\\\le 1000$$$) — the number of test cases.\\nThe first line of each test case contains two integers $$$n, x$$$ ($$$1 \\\\le n, x \\\\le 10$$$) — the number of doors and the number of seconds of the button, respectively.\\nThe second line of each test case contains $$$n$$$ integers $$$a_1, a_2, ..., a_n$$$ ($$$a_i \\\\in \\\\{0, 1\\\\}$$$) — the state of each door. Open doors are represented by '0' , while closed doors are represented by '1' .\\n'0'\\n'1'\\nIt is guaranteed that each test case contains at least one closed door.\",\n            \"output_format\": \"Output\\nFor each test case, output \\\" YES \\\" if Yousef can reach the exit, and \\\" NO \\\" otherwise.\\nYES\\nNO\\nYou can output the answer in any case (upper or lower). For example, the strings \\\" yEs \\\", \\\" yes \\\", \\\" Yes \\\", and \\\" YES \\\" will be recognized as positive responses.\\nyEs\\nyes\\nYes\\nYES\",\n            \"examples\": [\n                {\n                    \"input\": [\n                        \"7\",\n                        \"4 2\",\n                        \"0 1 1 0\",\n                        \"6 3\",\n                        \"1 0 1 1 0 0\",\n                        \"8 8\",\n                        \"1 1 1 0 0 1 1 1\",\n                        \"1 2\",\n                        \"1\",\n                        \"5 1\",\n                        \"1 0 1 0 1\",\n                        \"7 4\",\n                        \"0 0 0 1 1 0 1\",\n                        \"10 3\",\n                        \"0 1 0 0 1 0 0 1 0 0\"\n                    ],\n                    \"output\": [\n                        \"YES\",\n                        \"NO\",\n                        \"YES\",\n                        \"YES\",\n                        \"NO\",\n                        \"YES\",\n                        \"NO\"\n                    ]\n                }\n            ],\n            \"notes\": \"Note\\nIn the first test case, the optimal way is as follows:\\nAt time $$$0$$$, the door is open, so Yousef passes. At time $$$1$$$, the door is closed, Yousef can use the button now and pass through the door. At time $$$2$$$, the button's effect is still on, so Yousef can still pass. At time $$$3$$$, the button's effect has finished, but the door is open. Yousef passes and reaches the exit.\\nAt time $$$0$$$, the door is open, so Yousef passes.\\nAt time $$$1$$$, the door is closed, Yousef can use the button now and pass through the door.\\nAt time $$$2$$$, the button's effect is still on, so Yousef can still pass.\\nAt time $$$3$$$, the button's effect has finished, but the door is open. Yousef passes and reaches the exit.\\nIn the second test case, Yousef has a 3-second button, but he would need at least a 4-second button to reach the exit. Therefore, the answer is NO .\\nNO\\nIn the third test case, Yousef can turn on the button before starting to move. All the doors will stay open until he reaches the exit.\",\n            \"datasource\": \"CF\"\n        },\n\nExample Output: \n{\n            \"name\": \"A. False Alarm\",\n            \"statement\": \"Yousef is at the entrance of a long hallway with $$$n$$$ doors in a row, numbered from $$$1$$$ to $$$n$$$. He needs to pass through all the doors from $$$1$$$ to $$$n$$$ in order of numbering and reach the exit (past door $$$n$$$).\\nEach door can be open or closed. If a door is open, Yousef passes through it in $$$1$$$ second. If the door is closed, Yousef can't pass through it.\\nHowever, Yousef has a special button which he can use at most once at any moment. This button makes all closed doors become open for $$$x$$$ seconds.\\nYour task is to determine if Yousef can pass through all the doors if he can use the button at most once.\",\n            \"input_format\": \"Input\\nThe first line of the input contains an integer $$$t$$$ ($$$1 \\\\le t \\\\le 1000$$$) — the number of test cases.\\nThe first line of each test case contains two integers $$$n, x$$$ ($$$1 \\\\le n, x \\\\le 10$$$) — the number of doors and the number of seconds of the button, respectively.\\nThe second line of each test case contains $$$n$$$ integers $$$a_1, a_2, ..., a_n$$$ ($$$a_i \\\\in \\\\{0, 1\\\\}$$$) — the state of each door. Open doors are represented by '0' , while closed doors are represented by '1' .\\n'0'\\n'1'\\nIt is guaranteed that each test case contains at least one closed door.\",\n            \"output_format\": \"Output\\nFor each test case, output \\\" YES \\\" if Yousef can reach the exit, and \\\" NO \\\" otherwise.\n            \"examples\": [\n                {\n                    \"input\": [\n                        \"7\",\n                        \"4 2\",\n                        \"0 1 1 0\",\n                        \"6 3\",\n                        \"1 0 1 1 0 0\",\n                        \"8 8\",\n                        \"1 1 1 0 0 1 1 1\",\n                        \"1 2\",\n                        \"1\",\n                        \"5 1\",\n                        \"1 0 1 0 1\",\n                        \"7 4\",\n                        \"0 0 0 1 1 0 1\",\n                        \"10 3\",\n                        \"0 1 0 0 1 0 0 1 0 0\"\n                    ],\n                    \"output\": [\n                        \"YES\",\n                        \"NO\",\n                        \"YES\",\n                        \"YES\",\n                        \"NO\",\n                        \"YES\",\n                        \"NO\"\n                    ]\n                }\n            ],\n            \"notes\": \"Note\\nIn the first test case, the optimal way is as follows:\\nAt time $$$0$$$, the door is open, so Yousef passes. At time $$$1$$$, the door is closed, Yousef can use the button now and pass through the door. At time $$$2$$$, the button's effect is still on, so Yousef can still pass. At time $$$3$$$, the button's effect has finished, but the door is open. Yousef passes and reaches the exit.\\nAt time $$$0$$$, the door is open, so Yousef passes.\\nAt time $$$1$$$, the door is closed, Yousef can use the button now and pass through the door.\\nAt time $$$2$$$, the button's effect is still on, so Yousef can still pass.\\nAt time $$$3$$$, the button's effect has finished, but the door is open. Yousef passes and reaches the exit.\\nIn the second test case, Yousef has a 3-second button, but he would need at least a 4-second button to reach the exit. Therefore, the answer is NO .\\nNO\\nIn the third test case, Yousef can turn on the button before starting to move. All the doors will stay open until he reaches the exit.\",\n            \"datasource\": \"CF\"\n        },"
                        """
                    )
                },
                {
                    "role": "user",
                    "content": f"Solve and return in json mode\n{json.dumps(problem_data)}"
                },
            ],
            temperature=1,
            max_completion_tokens=2048,
            top_p=1,
            stream=False,
            response_format={"type": "json_object"},
            stop=None,
        )
        result = json.loads(completion.choices[0].message.content)
        if validate_json(result):
            return result
        else:
            print(f"Skipping invalid response for problem: {problem_data['name']}")
            return None
    except Exception as e:
        print(f"Error processing problem {problem_data['name']}: {e}")
        return None

def process_problems(file_dir: str, temp_set_dir: str = None) -> None:
    """Main function to process problems, normalize data, and save results to two files."""
    data = load_data(file_dir)
    temp_set = load_data(temp_set_dir) if temp_set_dir else defaultdict(dict)

    new_data = defaultdict(dict)
    new_problems = defaultdict(dict)
    invalid_count = 0
    edited_count = 0

    # Process each problem
    for contest in data:
        for problem in data[contest]:
            problem_data = data[contest][problem]
            # Check if problem needs normalization
            if 'yEs' in problem_data.get('statement', '') or \
               'yEs' in problem_data.get('output_format', ''):
                if contest in temp_set and problem in temp_set[contest]:
                    new_data[contest][problem] = temp_set[contest][problem]
                    new_problems[contest][problem] = temp_set[contest][problem]
                    continue

                processed_data = get_new_problem_data(problem_data)
                if processed_data:
                    new_data[contest][problem] = processed_data
                    new_problems[contest][problem] = processed_data
                    edited_count += 1
                else:
                    invalid_count += 1
                    new_data[contest][problem] = problem_data
                time.sleep(4)
            else:
                new_data[contest][problem] = problem_data

    print(f"Processed {len(data)} contests, {edited_count} problems edited, {invalid_count} problems failed validation.")
    save_data(file_dir, new_data, new_problems)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process competitive programming problems.")
    parser.add_argument("--dir", type=str, required=True, help="Location of JSON file containing problem info")
    parser.add_argument("--temp_set", type=str, required=False)
    args = parser.parse_args()
    process_problems(args.dir, args.temp_set)