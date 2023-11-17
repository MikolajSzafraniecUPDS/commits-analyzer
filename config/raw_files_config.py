"""
Configuration of raw data files
"""

# Format of file containing general information
GENERAL_INFO_FORMAT = "'%H;%ae;%an;%at;%ce;%cn'"

# Names of output files
OUTPUT_FILES = {
    "commits_hashes": "commits_hashes_no_merges.csv",
    "merges_info": "merges_info.csv",
    "commits_info": "commits_general_info.csv",
    "commits_messages": "commits_messages.csv",
    "insertions_deletions": "insertions_deletions.csv"
}

# Files headers
HEADERS = {
    "commits_hashes": ["commit_hash"],
    "merges_info": ["merge_hash", "merge_unix_time"],
    "commits_info": [
        "commit_hash",
        "author_email",
        "author_name",
        "commit_unix_time",
        "commiter_email",
        "commiter_name"
    ],
    "commits_messages": ["commit_hash", "commit_message"],
    "insertions_deletions": ["commit_hash", "insertions", "deletions"]
}
