import os
import re
import requests
from pathlib import Path

LEETCODE_URL = "https://leetcode.com/graphql/"

SESSION = os.environ["LEETCODE_SESSION"]
CSRF = os.environ["LEETCODE_CSRF_TOKEN"]
USERNAME = os.environ["LEETCODE_USERNAME"]

cookies = {
    "LEETCODE_SESSION": SESSION,
    "csrftoken": CSRF,
}

headers = {
    "Content-Type": "application/json",
    "Referer": "https://leetcode.com/",
    "Origin": "https://leetcode.com",
    "User-Agent": "Mozilla/5.0",
}


def graphql(query, variables, operation_name):
    response = requests.post(
        LEETCODE_URL,
        json={
            "operationName": operation_name,
            "query": query,
            "variables": variables,
        },
        headers=headers,
        cookies=cookies,
        timeout=30,
    )

    if response.status_code != 200:
        print("LeetCode response:", response.text)
        response.raise_for_status()

    data = response.json()

    if "errors" in data:
        raise Exception(data["errors"])

    return data["data"]


# Get recent accepted submissions
recent_query = """
query recentAcSubmissionList($username: String!, $limit: Int!) {
    recentAcSubmissionList(username: $username, limit: $limit) {
        id
        title
        titleSlug
        timestamp
    }
}
"""

recent = graphql(
    recent_query,
    {
        "username": USERNAME,
        "limit": 100,
    },
    "recentAcSubmissionList",
)["recentAcSubmissionList"]


# Get problem information
def get_question(slug):
    query = """
    query questionData($titleSlug: String!) {
        question(titleSlug: $titleSlug) {
            questionFrontendId
            title
            titleSlug
            difficulty
        }
    }
    """

    return graphql(
        query,
        {"titleSlug": slug},
        "questionData",
    )["question"]


# Get submitted code
def get_submission(submission_id):
    query = """
    query submissionDetails($submissionId: Int!) {
        submissionDetails(submissionId: $submissionId) {
            code
            lang
            statusDisplay
        }
    }
    """

    return graphql(
        query,
        {"submissionId": int(submission_id)},
        "submissionDetails",
    )["submissionDetails"]


# Supported languages
LANG_EXTENSIONS = {
    "python": "py",
    "python3": "py",
    "java": "java",
    "c": "c",
    "cpp": "cpp",
    "c++": "cpp",
    "javascript": "js",
    "typescript": "ts",
    "kotlin": "kt",
    "go": "go",
    "rust": "rs",
    "swift": "swift",
    "csharp": "cs",
    "c#": "cs",
}


def clean_name(name):
    name = re.sub(r'[<>:"/\\|?*]', "", name)
    name = name.strip()
    return name.replace(" ", "-")


# Process submissions
for submission in recent:

    try:
        question = get_question(submission["titleSlug"])

        if not question:
            continue

        difficulty = question["difficulty"]

        if difficulty not in ["Easy", "Medium", "Hard"]:
            continue

        details = get_submission(submission["id"])

        if not details:
            continue

        if details["statusDisplay"] != "Accepted":
            continue

        code = details["code"]
        language = details["lang"]

        extension = LANG_EXTENSIONS.get(language.lower())

        if not extension:
            print(f"Skipping unsupported language: {language}")
            continue

        number = str(question["questionFrontendId"]).zfill(4)
        title = clean_name(question["title"])

        folder = Path(
            difficulty,
            f"{number}-{title}"
        )

        folder.mkdir(
            parents=True,
            exist_ok=True
        )

        solution_file = folder / f"solution.{extension}"

        solution_file.write_text(
            code,
            encoding="utf-8"
        )

        print(
            f"Synced: {difficulty}/{number}-{title}/"
            f"solution.{extension}"
        )

    except Exception as error:
        print(
            f"Error processing {submission['title']}: {error}"
        )


print("LeetCode sync completed!")
