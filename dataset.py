"""Module to fetch and update the database of all CF Div4 contests"""
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
    return None

def filter_contests(division: int, contests: List[dict]) -> List[dict]:
    """Filters the list of contests for contests of a specific division

    Args:
        division (int): _description_
        list_of_all_contests (List[dict]): _description_

    Returns:
        List[dict]: _description_
    """
    assert 4 <= division > 0, f"Div {division} doesn't exist on CF, as of the time of this writing"

    div_str = f"Div. {division}"
    filtered_list = []
    for contest in contests:
        if div_str in contest['name']:
            filtered_list.append(contest)
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
    list_of_all_contests = get_list_of_all_contests()
    assert list_of_all_contests is not None, "List of contests shouldn't be none"

    list_of_div4_contests = filter_contests(4, list_of_all_contests)

    problem_info_list = []
    for contest in list_of_div4_contests:
        contestId = contest['id']
        problem_info_list.extend(get_problem_info(contestId))

    dataframe = pd.DataFrame(problem_info_list)
    dataframe.to_csv("demo_list.csv", index=False)

    print(len(problem_info_list))
