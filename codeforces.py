import os
import csv
import json
import time
import argparse
import pandas as pd
import cloudscraper

from tqdm import tqdm
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import re

class CodeforcesScraper:
    def __init__(self, div: int):
        self.base_url = "https://codeforces.com"
        self.div = div
        self.scraper = cloudscraper.create_scraper()  # Use cloudscraper to bypass Cloudflare
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Referer": "https://codeforces.com/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5"
        }

    def get_problem_page(self, contest_id: str, problem_id: str) -> Optional[BeautifulSoup]:
        url = f"{self.base_url}/contest/{contest_id}/problem/{problem_id}"
        try:
            response = self.scraper.get(url, headers=self.headers)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except Exception as e:
            print(f"Error fetching {url}: {str(e).encode('utf-8', errors='replace').decode()}")
            return None

    def extract_problem_data(self, soup: BeautifulSoup) -> Dict:
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

        # Helper function to extract text from all nested elements
        def extract_all_text(section) -> str:
            if not section:
                return ""
            texts = []
            for elem in section.find_all(recursive=True):
                if elem.name in ["script", "style"]:
                    continue
                text = elem.get_text(separator=" ", strip=True)
                if text:
                    texts.append(text)
            return "\n".join(texts)

        # Input format
        input_section = soup.find("div", class_="input-specification")
        problem_data["input_format"] = extract_all_text(input_section)

        # Output format
        output_section = soup.find("div", class_="output-specification")
        problem_data["output_format"] = extract_all_text(output_section)

        # Examples
        sample_tests = soup.find_all("div", class_="sample-test")
        for sample in sample_tests:
            input_data = sample.find("div", class_="input")
            output_data = sample.find("div", class_="output")
            if input_data and output_data:
                input_lines = [
                    line.text.strip() for line in input_data.find("pre").find_all("div", class_="test-example-line")
                ]
                output_lines = [
                    line.text.strip() for line in output_data.find("pre").find_all("div", class_="test-example-line")
                ]
                if not input_lines:
                    input_lines = input_data.find("pre").text.strip().split("\n")
                if not output_lines:
                    output_lines = output_data.find("pre").text.strip().split("\n")
                problem_data["examples"].append({"input": input_lines, "output": output_lines})

        # Notes
        notes = soup.find("div", class_="note")
        problem_data["notes"] = extract_all_text(notes)

        return problem_data

    def scrape_problems(self, contest_ids: List[int], problem_ids: List[str]):
        all_problems_data = {}
        total, success = 0, 0
        unsuccessful_list = []

        print("Scraping CF data")

        for _, (contest_id, problem_id) in tqdm(enumerate(zip(contest_ids, problem_ids)), desc="Processing", total=len(contest_ids)):
            total += 1
            if contest_id not in all_problems_data:
                all_problems_data[contest_id] = {}

            soup = self.get_problem_page(str(contest_id), problem_id)
            if soup:
                data = self.extract_problem_data(soup)
                all_problems_data[contest_id][problem_id] = data
                success += 1
            else:
                unsuccessful_list.append(f"{contest_id}/{problem_id}")

            time.sleep(4)

        # Save all kept problems
        with open(f"datafiles/div{self.div}_problems.json", "w", encoding="utf-8") as f:
            json.dump(all_problems_data, f, indent=4, ensure_ascii=False)

        # Print statistics
        print(f"\nScraping Statistics for Division {self.div}:")
        print(f"Total problems processed: {total}")
        print(f"Successfully scraped: {success}")
        print(f"Failed to scrape: {len(unsuccessful_list)}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=str, required=True,
                       help="Location of csv containing problem info")
    parser.add_argument("--div", type=int, required=True,
                       help="Division number (1-4)")

    args = parser.parse_args()
    scraper = CodeforcesScraper(args.div)

    obj = pd.read_csv(args.dir)
    contest_ids = obj["contestId"].tolist()
    problem_ids = obj["index"].tolist()

    assert len(contest_ids) == len(problem_ids)

    scraper.scrape_problems(contest_ids, problem_ids)

if __name__ == "__main__":
    main()
