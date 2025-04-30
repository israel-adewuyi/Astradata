import os
import csv
import json
import time
import pandas as pd
import cloudscraper
from bs4 import BeautifulSoup
from typing import Dict, List, Optional

class CodeforcesScraper:
    def __init__(self, output_dir: str = "codeforces_problems"):
        self.base_url = "https://codeforces.com"
        self.output_dir = output_dir
        self.scraper = cloudscraper.create_scraper()  # Use cloudscraper to bypass Cloudflare
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Referer": "https://codeforces.com/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5"
        }
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def get_problem_page(self, contest_id: str, problem_id: str) -> Optional[BeautifulSoup]:
        url = f"{self.base_url}/contest/{contest_id}/problem/{problem_id}"
        try:
            response = self.scraper.get(url, headers=self.headers)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def extract_problem_data(self, soup: BeautifulSoup) -> Dict:
        # print(soup.prettify())
        problem_data = {
            "name": "",
            "statement": "",
            "input_format": "",
            "output_format": "",
            "examples": [],
            "notes": ""
        }

        # Problem name
        title = soup.find("div", class_="title")
        if title:
            problem_data["name"] = title.text.strip()

        # Problem statement
        statement = soup.find("div", class_="problem-statement")
        if statement:
            paragraphs = statement.find_all("div", recursive=False)[1]  # Skip header
            problem_data["statement"] = "\n".join(p.text.strip() for p in paragraphs if p.text.strip())

        # Input format
        input_section = soup.find("div", class_="input-specification")
        if input_section:
            problem_data["input_format"] = "\n".join(p.text.strip() for p in input_section.find_all("p"))

        # Output format
        output_section = soup.find("div", class_="output-specification")
        if output_section:
            problem_data["output_format"] = "\n".join(p.text.strip() for p in output_section.find_all("p"))

        # Examples
        sample_tests = soup.find_all("div", class_="sample-test")
        for sample in sample_tests:
            input_data = sample.find("div", class_="input")
            output_data = sample.find("div", class_="output")
            if input_data and output_data:
                # Extract individual lines for input
                input_lines = [
                    line.text.strip() for line in input_data.find("pre").find_all("div", class_="test-example-line")
                ]
                # Extract individual lines for output
                output_lines = [
                    line.text.strip() for line in output_data.find("pre").find_all("div", class_="test-example-line")
                ]
                # If no test-example-line divs, fall back to pre text split by newlines
                if not input_lines:
                    input_lines = input_data.find("pre").text.strip().split("\n")
                if not output_lines:
                    output_lines = output_data.find("pre").text.strip().split("\n")
                problem_data["examples"].append({"input": input_lines, "output": output_lines})

        # Constraints
        # constraints = soup.find("div", class_="input-constraints") or soup.find("div", class_="constraints")
        # if constraints:
        #     problem_data["constraints"] = "\n".join(p.text.strip() for p in constraints.find_all("p"))

        # Notes
        notes = soup.find("div", class_="note")
        if notes:
            problem_data["notes"] = "\n".join(p.text.strip() for p in notes.find_all("p"))

        return problem_data

    def save_problem(self, contest_id: str, problem_id: str, data: Dict):
        filename = f"{self.output_dir}/contest_{contest_id}_problem_{problem_id}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Saved problem {contest_id}/{problem_id} to {filename}")

    def scrape_problems(self, contest_ids: List[int], problem_ids: List[str]):
        all_problems_data = {}
        total, success = 0, 0
        unsuccessful_list = []

        for contest_id, problem_id in zip(contest_ids, problem_ids):
            total += 1
            if contest_id not in all_problems_data:
                all_problems_data[contest_id] = {}

            soup = self.get_problem_page(contest_id, problem_id)
            if soup:
                data = self.extract_problem_data(soup)
                all_problems_data[contest_id][problem_id] = data
                success += 1
            else:
                unsuccessful_list.append(f"{contest_id}/{problem_id}")

            time.sleep(4)

        print(f"Successfully scraped {success} of {total} pages")
        with open("div4_problems.json", "w", encoding="utf-8") as f:
            json.dump(all_problems_data, f, indent=4, ensure_ascii=False)

        if unsuccessful_list:
            with open("unsuccessful_scrapes.txt", "w", encoding="utf-8") as f:
                f.writelines(unsuccessful_list)

def main():
    scraper = CodeforcesScraper()

    obj = pd.read_csv("demo_list.csv")
    contest_ids = obj["contestId"].tolist()
    problem_ids = obj["index"].tolist()

    assert len(contest_ids) == len(problem_ids)

    scraper.scrape_problems(contest_ids, problem_ids)


if __name__ == "__main__":
    main()