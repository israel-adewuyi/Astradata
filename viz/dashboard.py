import streamlit as st
import pandas as pd
import json
from typing import Dict, List, Tuple

# Configuration
KEYWORDS = ["interactive", "case-insensitive", "yEs", "valid solution", "print any of", "output any"]

# Component: File Upload
def file_uploader_component() -> Dict:
    """Handles file upload and returns parsed JSON data."""
    uploaded_file = st.file_uploader("Upload JSON dataset", type=["json"])
    if uploaded_file:
        try:
            data = json.load(uploaded_file)
            return data
        except json.JSONDecodeError:
            st.error("Invalid JSON file. Please upload a valid JSON file.")
            return {}
    return {}

# Component: Data Processing
def flatten_dataset(data: Dict) -> List[Dict]:
    """Flattens nested JSON dataset into a list of rows for display."""
    rows = []
    for contest_id, problems in data.items():
        for problem_id, details in problems.items():
            row = {
                "contest_id": contest_id,
                "problem_id": problem_id,
                **details
            }
            # Flatten examples list into a string
            if "examples" in row:
                row["examples"] = "; ".join(
                    [f"Input: {ex['input']}, Output: {ex['output']}" for ex in row["examples"]]
                )
            rows.append(row)
    return rows

# Component: Keyword Search
def search_keywords(rows: List[Dict]) -> Tuple[Dict[str, int], Dict[str, List[int]]]:
    """Searches for keywords in rows and returns counts and matching row indices."""
    keyword_counts = {keyword: 0 for keyword in KEYWORDS}
    keyword_matches = {keyword: [] for keyword in KEYWORDS}
 
    for idx, row in enumerate(rows):
        # Combine text fields for searching
        text = " ".join(
            str(row.get(field, ""))
            for field in ["name", "statement", "input_format", "output_format", "examples"]
        )
        for keyword in KEYWORDS:
            if keyword in text:
                keyword_counts[keyword] += 1
                keyword_matches[keyword].append(idx)
    
    return keyword_counts, keyword_matches

# Component: Sidebar Keyword Analysis
def keyword_analysis_component(keyword_counts: Dict[str, int], keyword_matches: Dict[str, List[int]], rows: List[Dict]):
    """Displays keyword counts and handles filtering in the sidebar."""
    st.sidebar.header("Keyword Analysis")
    if not keyword_counts:
        st.sidebar.info("No keywords found.")
        return
    
    # Initialize session state for selected keyword
    if "selected_keyword" not in st.session_state:
        st.session_state.selected_keyword = None
    
    for keyword, count in keyword_counts.items():
        col1, col2 = st.sidebar.columns([3, 1])
        with col1:
            st.write(f"{keyword}: {count} rows")
        with col2:
            if count > 0 and st.button("View", key=f"view_{keyword}"):
                st.session_state.selected_keyword = keyword
    
    # Reset button
    if st.session_state.selected_keyword and st.sidebar.button("Reset Filter"):
        st.session_state.selected_keyword = None

# Component: Data Display
def display_dataset(rows: List[Dict], keyword_matches: Dict[str, List[int]]):
    """Displays dataset as a scrollable table, filtered by selected keyword if applicable."""
    if not rows:
        st.info("No data to display. Please upload a JSON file.")
        return

    selected_keyword = st.session_state.get("selected_keyword", None)
    if selected_keyword and keyword_matches.get(selected_keyword):
        st.subheader(f"Rows containing '{selected_keyword}'")
        filtered_indices = keyword_matches[selected_keyword]
        filtered_rows = [rows[i] for i in filtered_indices]
        df = pd.DataFrame(filtered_rows)
    else:
        st.subheader("Dataset Preview")
        st.subheader(f"{len(pd.DataFrame(rows))} items")
        df = pd.DataFrame(rows)

    st.dataframe(df, height=500, use_container_width=True)

# Main App
def main():
    st.title("Astracode Dataset Dashboard")

    # Sidebar for file upload and keyword analysis
    with st.sidebar:
        st.header("Upload Data")
        data = file_uploader_component()

    # Main content
    if data:
        rows = flatten_dataset(data)
        keyword_counts, keyword_matches = search_keywords(rows)
        keyword_analysis_component(keyword_counts, keyword_matches, rows)
        display_dataset(rows, keyword_matches)
    else:
        st.write("Upload a JSON file to visualize the dataset.")

if __name__ == "__main__":
    main()
