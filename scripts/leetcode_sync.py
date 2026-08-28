import os
import re
import time
import requests
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

LEETCODE_URL = "https://leetcode.com/graphql/"

SESSION = os.environ["LEETCODE_SESSION"]
CSRF = os.environ["LEETCODE_CSRF_TOKEN"]

cookies = {
    "LEETCODE_SESSION": SESSION,
    "csrftoken": CSRF,
}

headers = {
    "Content-Type": "application/json",
    "Referer": "https://leetcode.com/progress/",
    "Origin": "https://leetcode.com",
    "User-Agent": "Mozilla/5.0",
}


# ============================================================
# GRAPHQL HELPER
# ============================================================

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

    if not data.get("data"):
        raise Exception("LeetCode returned no data")

    return data["data"]


# ============================================================
# GET ALL SOLVED PROBLEMS
# ============================================================

def get_all_solved_problems():

    query = """
    query userProgressQuestionList(
        $filters: UserProgressQuestionListInput
    ) {
        userProgressQuestionList(filters: $filters) {
            totalNum
            questions {
                frontendId
                title
                titleSlug
                difficulty
                lastSubmittedAt
            }
        }
    }
    """

    all_questions = []
    skip = 0
    limit = 100

    while True:

        print(
            f"Fetching solved problems "
            f"(starting at {skip})..."
        )

        result = graphql(
            query,
            {
                "filters": {
                    "questionStatus": "SOLVED",
                    "skip": skip,
                    "limit": limit,
                }
            },
            "userProgressQuestionList",
        )

        progress = result["userProgressQuestionList"]

        questions = progress["questions"]

        all_questions.extend(questions)

        total = progress["totalNum"]

        print(
            f"Found {len(all_questions)} / {total} solved problems"
        )

        if len(all_questions) >= total:
            break

        if not questions:
            break

        skip += limit

        # Avoid hammering LeetCode
        time.sleep(1)

    return all_questions


# ============================================================
# GET SUBMISSIONS FOR A PROBLEM
# ============================================================

def get_submissions(title_slug):

    query = """
    query submissionList(
        $offset: Int!,
        $limit: Int!,
        $questionSlug: String!
    ) {
        questionSubmissionList(
            offset: $offset,
            limit: $limit,
            questionSlug: $questionSlug
        ) {
            submissions {
                id
                statusDisplay
                lang
                timestamp
            }
        }
    }
    """

    result = graphql(
        query,
        {
            "offset": 0,
            "limit": 20,
            "questionSlug": title_slug,
        },
        "submissionList",
    )

    return result["questionSubmissionList"]["submissions"]


# ============================================================
# GET ACTUAL SOURCE CODE
# ============================================================

def get_submission_details(submission_id):

    query = """
    query submissionDetails($submissionId: Int!) {
        submissionDetails(submissionId: $submissionId) {
            code
            lang {
                name
            }
            statusDisplay
        }
    }
    """

    result = graphql(
        query,
        {
            "submissionId": int(submission_id),
        },
        "submissionDetails",
    )

    return result["submissionDetails"]


# ============================================================
# LANGUAGE → FILE EXTENSION
# ============================================================

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

    "ruby": "rb",

    "php": "php",

    "scala": "scala",

    "dart": "dart",

    "sql": "sql",

}


# ============================================================
# CLEAN FILE/FOLDER NAMES
# ============================================================

def clean_name(name):

    name = re.sub(
        r'[<>:"/\\|?*]',
        "",
        name
    )

    name = name.strip()

    return name.replace(" ", "-")


# ============================================================
# FIND LATEST ACCEPTED SUBMISSION
# ============================================================

def get_latest_accepted_submission(title_slug):

    submissions = get_submissions(title_slug)

    accepted = [
        submission
        for submission in submissions
        if submission["statusDisplay"] == "Accepted"
    ]

    if not accepted:
        return None

    # Newest submission first
    accepted.sort(
        key=lambda x: int(x["timestamp"]),
        reverse=True
    )

    return accepted[0]


# ============================================================
# MAIN SYNC
# ============================================================

print("=" * 60)
print("        LEETCODE → GITHUB SYNC")
print("=" * 60)

try:

    solved_problems = get_all_solved_problems()

except Exception as error:

    print(
        "ERROR while getting solved problems:"
    )

    print(error)

    raise


print()
print(
    f"Total solved problems found: "
    f"{len(solved_problems)}"
)

print()


# ============================================================
# PROCESS EVERY SOLVED PROBLEM
# ============================================================

for index, problem in enumerate(
    solved_problems,
    start=1
):

    title = problem["title"]
    slug = problem["titleSlug"]
    difficulty = problem["difficulty"]

    try:

        print(
            f"[{index}/{len(solved_problems)}] "
            f"{difficulty} - {title}"
        )

        # ----------------------------------------------------
        # Find accepted submission
        # ----------------------------------------------------

        submission = get_latest_accepted_submission(
            slug
        )

        if not submission:

            print(
                f"  ⚠ No accepted submission found"
            )

            continue

        # ----------------------------------------------------
        # Get source code
        # ----------------------------------------------------

        details = get_submission_details(
            submission["id"]
        )

        if not details:

            print(
                f"  ⚠ Could not get submission details"
            )

            continue

        if details["statusDisplay"] != "Accepted":

            print(
                f"  ⚠ Submission is not accepted"
            )

            continue

        code = details["code"]

        # ----------------------------------------------------
        # Get language
        # ----------------------------------------------------

        language = details["lang"]["name"]

        extension = LANG_EXTENSIONS.get(
            language.lower()
        )

        if not extension:

            print(
                f"  ⚠ Unsupported language: "
                f"{language}"
            )

            continue

        # ----------------------------------------------------
        # Problem number
        # ----------------------------------------------------

        number = str(
            problem["frontendId"]
        ).zfill(4)

        clean_title = clean_name(
            title
        )

        # ----------------------------------------------------
        # Create folder
        #
        # Example:
        #
        # Easy/
        # └── 0121-Best-Time-to-Buy-and-Sell-Stock/
        #     └── solution.java
        #
        # ----------------------------------------------------

        folder = Path(
            difficulty,
            f"{number}-{clean_title}"
        )

        folder.mkdir(
            parents=True,
            exist_ok=True
        )

        solution_file = (
            folder /
            f"solution.{extension}"
        )

        # ----------------------------------------------------
        # Write solution
        # ----------------------------------------------------

        solution_file.write_text(
            code,
            encoding="utf-8"
        )

        print(
            f"  ✓ Synced → "
            f"{folder}/solution.{extension}"
        )

        # Small delay
        time.sleep(1)

    except Exception as error:

        print(
            f"  ✗ Error processing "
            f"{title}: {error}"
        )

        # Continue with the next problem
        continue


# ============================================================
# FINISHED
# ============================================================

print()
print("=" * 60)
print("           SYNC COMPLETED")
print("=" * 60)
