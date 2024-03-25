import subprocess
from collections import defaultdict

# Set the start date to 2 years ago
start_date = "2 years ago"

# Command to get all commits since the start date, excluding merge commits
git_command = f'git log --pretty=format:"%h,%an,%ae" --since="{start_date}" --no-merges --name-only'

# Run the git command and capture the output
output = subprocess.run(git_command, shell=True, stdout=subprocess.PIPE, text=True).stdout

# Initialize a defaultdict to store commit information per file per committer
commit_info = defaultdict(lambda: defaultdict(int))

# Process the output to extract commit information
lines = output.strip().split('\n')
current_commit = None
for line in lines:
    if line.startswith("commit"):
        current_commit = line.split()[1]
    elif line and not line.startswith(' '):  # File names start at the beginning of a line
        commit_info[line][current_commit] += 1

# Print the results
for file_name, commits in commit_info.items():
    for commit, count in commits.items():
        print(f"File: {file_name.strip()}, Committer: {commit.split(',')[1]}, Email: {commit.split(',')[2]}, Commits: {count}")
