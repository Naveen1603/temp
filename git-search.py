import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

# Function to search for 'YYYY' in a single repository
def search_repo(repo_name, org_name, token):
    headers = {"Authorization": f"token {token}"}
    results = []
    page = 1

    while True:
        url = f"https://api.github.com/search/code?q=YYYY+in:file+repo:{org_name}/{repo_name}&per_page=100&page={page}"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Error: {response.status_code}, {response.json().get('message')}")
            break

        data = response.json()
        items = data.get("items", [])

        # Collect data from the API response
        for item in items:
            file_name = item['name']
            file_path = item['path']
            file_url = item['html_url']

            # Fetch file contents to get the exact line with 'YYYY'
            file_response = requests.get(item['url'], headers=headers)
            if file_response.status_code == 200:
                file_content = file_response.json().get('content', '')
                try:
                    file_content = bytes(file_content, 'utf-8').decode('base64')  # Decode base64
                except Exception:
                    file_content = ""

                for line_no, line in enumerate(file_content.splitlines(), start=1):
                    if "YYYY" in line:  # Case-sensitive check
                        results.append({
                            "Organization": org_name,
                            "Repository": repo_name,
                            "File Name": file_name,
                            "File Path": file_path,
                            "Line Number": line_no,
                            "Line Content": line.strip(),
                            "File URL": file_url,
                        })

        # Check if there are more pages
        if "next" not in response.links:
            break

        page += 1

    return results


# Function to process repositories in parallel
def process_repositories_parallel(org_name, repos, token, max_threads):
    results = []
    with ThreadPoolExecutor(max_threads) as executor:
        futures = {executor.submit(search_repo, repo, org_name, token): repo for repo in repos}
        for future in futures:
            repo = futures[future]
            try:
                repo_results = future.result()
                results.extend(repo_results)
                print(f"Finished processing repository: {repo}")
            except Exception as e:
                print(f"Error processing repository {repo}: {e}")
    return results


# Main function
def main():
    # Replace with your GitHub personal access token and organization name
    GITHUB_TOKEN = "your_personal_access_token"
    ORG_NAME = "your_organization_name"
    OUTPUT_FILE = "GitHub_YYYY_Search_Results.xlsx"

    # List of repositories (you can fetch this programmatically using the GitHub API)
    repositories = [
        "Repo1",
        "Repo2",
        "Repo3",
        # Add more repository names here
    ]

    # Max threads for parallel processing
    MAX_THREADS = 5

    # Fetch search results in parallel
    print(f"Searching for 'YYYY' across repositories in the organization: {ORG_NAME}")
    search_results = process_repositories_parallel(ORG_NAME, repositories, GITHUB_TOKEN, MAX_THREADS)

    # Save results to an Excel file
    if search_results:
        df = pd.DataFrame(search_results)
        df.to_excel(OUTPUT_FILE, index=False)
        print(f"Results saved to {OUTPUT_FILE}")
    else:
        print("No results found.")


if __name__ == "__main__":
    main()
