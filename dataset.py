"""Module to fetch and update the database of all CF Div4 contests"""
import time
import argparse
import requests
import pandas as pd

from typing import List

def get_list_of_all_contests() -> List[dict]:
    """Fetches list of all contests from CF

    Returns:
        List[dict]: List of dictionaries containing all contests from CF
    """
    url = "https://codeforces.com/api/contest.list?gym=false"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['result']
    else:
        print(response.status_code)
    return None

def filter_contests(division: int, contests: List[dict]) -> List[dict]:
    """Filters the list of contests for contests of a specific division

    Args:
        division (int): _description_
        list_of_all_contests (List[dict]): _description_

    Returns:
        List[dict]: _description_
    """
    assert 4 >= division > 0, f"Div {division} doesn't exist on CF, as of the time of this writing"

    div_str = [f"Div. {div}" for div in range(division, 5)]

    filtered_list = []
    for contest in contests:
        for div in div_str:
            if div in contest['name'] and contest['relativeTimeSeconds'] > 0:
                filtered_list.append(contest)
                break 
    assert filtered_list is not None, f"There should be Div {division} on CF, man."
    return filtered_list


def get_problem_info(contestId: int) -> List[dict | None]:
    url =  f"https://codeforces.com/api/contest.standings?contestId={contestId}"
    response = requests.get(url)
    if response.status_code == 200:
        problem_info_list = []
        data = response.json()
        all_problem_info = data['result']['problems']

        for problem_info in all_problem_info:
            index = problem_info['index']
            name = problem_info['name']

            temp_log = {
                "contestId": contestId,
                "index": index,
                "name": name
            }
            problem_info_list.append(temp_log)
        return problem_info_list
    return None

if __name__ == "__main__":

    # Add argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument("--div", type=int, required=True, 
                       help="Division number (1-4)")
    args = parser.parse_args()

    list_of_all_contests = get_list_of_all_contests()
    assert list_of_all_contests is not None, "List of contests shouldn't be none"

    print(f"In total, there are {len(list_of_all_contests)} codeforces contests.")

    list_of_contests = filter_contests(args.div, list_of_all_contests)

    print(f"There are {len(list_of_contests)} contests that are >= div {args.div}")

    problem_info_list, faulty_response = [], []
    for contest in list_of_contests:
        contestId = contest['id']
        contest_details = get_problem_info(contestId)
        if contest_details:
            problem_info_list.extend(contest_details)
        else:
            faulty_response.append(contest)
        time.sleep(2)

    dataframe = pd.DataFrame(problem_info_list)
    dataframe.to_csv(f"datafiles/div{args.div}.csv", index=False)

    print(f"In total, there are {len(problem_info_list)} codeforces problems scraped")
    print(f"Faulty responses \n{faulty_response}")
