import requests
from bs4 import BeautifulSoup
import re
import time
import json
from tqdm import tqdm
from urllib.parse import urljoin

def clean_text(text):
    return ' '.join(text.strip().split())

def scrape_problem(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch {url}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    problem_data = {}

    # Problem Title
    title_span = soup.find('span', class_='h2')
    if title_span:
        # Extract text nodes, excluding nested tags like <a> for editorial
        title_text = ''.join(t for t in title_span.find_all(string=True) if t.parent.name != 'a').strip()
        problem_data['name'] = clean_text(title_text)
    else:
        problem_data['name'] = 'Unknown'

    # Problem Statement
    statement_sections = soup.find_all('div', class_='part')
    problem_statement = []
    for section in statement_sections:
        if section.find('h3', string=re.compile(r'Problem Statement|Task', re.I)):
            paragraphs = section.find_all(['p', 'pre', "ul"])
            for p in paragraphs:
                if p.name == 'pre':
                    problem_statement.append(f"```\n{p.text.strip()}\n```")
                else:
                    problem_statement.append(clean_text(p.text))
    problem_data['statement'] = '\n\n'.join(problem_statement)

    # Constraints
    constraints = []
    for section in statement_sections:
        if section.find('h3', string=re.compile(r'Constraints', re.I)):
            items = section.find_all(['p', 'li', 'pre',])
            for item in items:
                constraints.append(clean_text(item.text))
            # print(items, end='\n\n\n')
    # problem_data['constraints'] = '\n'.join(constraints)
    constraints = '\n'.join(constraints)

    # Input Format
    input_format = []
    for section in statement_sections:
        if section.find('h3', string=re.compile(r'Input', re.I)):
            items = section.find_all(['pre'])

            for item in items:
                if item.name == 'pre':
                    input_format.append(f"```\n{item.text.strip()}\n```")
                else:
                    input_format.append(clean_text(item.text))
            if input_format is not None:
                break
    # problem_data['input_format'] = '\n'.join(input_format)
    problem_data['input_format'] = constraints + ' \n '.join(input_format)

    # Output Format
    output_format = []
    for section in statement_sections:
        if section.find('h3', string=re.compile(r'Output', re.I)):
            items = section.find_all(['p', 'pre'])
            for item in items:
                if item.name == 'pre':
                    output_format.append(f"```\n{item.text.strip()}\n```")
                else:
                    output_format.append(clean_text(item.text))
            if output_format is not None:
                break
    problem_data['output_format'] = ' \n '.join(output_format)

    # Example Tests
    examples = []
    sample_idx = 1
    while True:
        sample_input_section = None
        sample_output_section = None
        for section in statement_sections:
            h3 = section.find('h3')
            if h3:
                if f'Sample Input {sample_idx}' in h3.text:
                    sample_input_section = section
                elif f'Sample Output {sample_idx}' in h3.text:
                    sample_output_section = section
        if not (sample_input_section or sample_output_section):
            break

        example = {}
        if sample_input_section:
            input_pre = sample_input_section.find('pre')
            example['input'] = input_pre.text.strip() if input_pre else ''
        if sample_output_section:
            output_pre = sample_output_section.find('pre')
            example['output'] = output_pre.text.strip() if output_pre else ''
            # Explanation (if available)
            explanation = []
            p_tags = sample_output_section.find_all('p')
            for p in p_tags:
                explanation.append(clean_text(p.text))
            if explanation:
                example['explanation'] = '\n'.join(explanation)
        examples.append(example)
        sample_idx += 1
    problem_data['examples'] = examples

    return problem_data

def main():
    base_url = 'https://atcoder.jp'
    problems = {}

    problems_count = 0

    for contest_id in tqdm(range(50, 411), desc="Processing", total=(411-50)):
        formatted_contest_id = f"{contest_id:03d}"
        problems[formatted_contest_id] = {}
        contest_url = f"https://atcoder.jp/contests/abc{formatted_contest_id}/tasks"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(contest_url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch contest page for {contest_url}")
            continue

        soup = BeautifulSoup(response.content, 'html.parser')
        task_table = soup.find('table', class_='table table-bordered table-striped')
        if not task_table:
            print("Task table not found")
            break

        for row in task_table.find('tbody').find_all('tr'):
            link = row.find('td', class_='text-center no-break').find('a')
            if link and 'href' in link.attrs:
                problem_url = urljoin(base_url, link['href'])
                problem_data = scrape_problem(problem_url)
                if problem_data:
                    problems_count += 1
                    problem_id = problem_data['name'].split('-')[0]
                    problems[formatted_contest_id][problem_id] = problem_data
                    # problems.append(problem_data)
                # break
        time.sleep(2)

    # Save to JSON
    with open('datafiles/abc_problems.json', 'w', encoding='utf-8') as f:
        json.dump(problems, f, indent=4, ensure_ascii=False)

    print(f"Scraped {problems_count} problems and saved to abc_problems.json")

if __name__ == '__main__':
    main()
