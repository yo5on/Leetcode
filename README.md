# LeetCode → GitHub Auto Sync

Automatically synchronize your accepted LeetCode solutions with a GitHub repository using GitHub Actions.

The workflow retrieves your solved problems, identifies their difficulty and submission language, and organizes the solutions into a clean, structured repository.

## Features

- Automatically syncs accepted LeetCode solutions
- Retrieves your complete solved-problem history
- Organizes solutions by difficulty: Easy, Medium, and Hard
- Preserves the programming language used for each submission
- Runs automatically every 6 hours
- Supports manual synchronization through GitHub Actions
- Requires no browser extension
- Uses GitHub Secrets to securely store LeetCode authentication data

## Repository Structure

After synchronization, the repository will look similar to:

```text
Leetcode/
├── .github/
│   └── workflows/
│       └── leetcode.yml
│
├── scripts/
│   └── leetcode_sync.py
│
├── Easy/
│   ├── 0001-Two-Sum/
│   │   └── solution.cpp
│   ├── 0009-Palindrome-Number/
│   │   └── solution.c
│   └── 0121-Best-Time-to-Buy-and-Sell-Stock/
│       └── solution.java
│
├── Medium/
│   ├── 0055-Jump-Game/
│   │   └── solution.java
│   └── 0120-Triangle/
│       └── solution.java
│
└── Hard/
    └── 0051-N-Queens/
        └── solution.java
```

Each problem is placed inside its corresponding difficulty folder, and the solution file extension is determined automatically from the language used on LeetCode.

## Supported Languages

The synchronization script currently supports:

| Language | Extension |
|---|---|
| Python | `.py` |
| Java | `.java` |
| C | `.c` |
| C++ | `.cpp` |
| JavaScript | `.js` |
| TypeScript | `.ts` |
| Kotlin | `.kt` |
| Go | `.go` |
| Rust | `.rs` |
| Swift | `.swift` |
| C# | `.cs` |
| Ruby | `.rb` |
| PHP | `.php` |
| Scala | `.scala` |
| Dart | `.dart` |
| SQL | `.sql` |

## Setup

### 1. Fork the Repository

Fork this repository to your GitHub account.

Alternatively, create a new repository and copy the following files:

```text
.github/workflows/leetcode.yml
scripts/leetcode_sync.py
```

### 2. Enable GitHub Actions

Open:

```text
Repository
→ Settings
→ Actions
→ General
```

Make sure GitHub Actions are allowed to run.

The workflow also requires permission to write changes to the repository.

### 3. Add Repository Secrets

Go to:

```text
Repository
→ Settings
→ Secrets and variables
→ Actions
→ New repository secret
```

Create the following secrets:

#### `LEETCODE_USERNAME`

Your LeetCode username.

Example:

```text
your-leetcode-username
```

#### `LEETCODE_SESSION`

Your LeetCode `LEETCODE_SESSION` cookie value.

#### `LEETCODE_CSRF_TOKEN`

Your LeetCode `csrftoken` cookie value.

> **Security:** Never commit these values to the repository, put them directly in the Python script, or share them publicly.

## Obtaining the LeetCode Cookies

You can use Brave, Chrome, Edge, or another Chromium-based browser.

### Step 1: Sign in to LeetCode

Open:

https://leetcode.com/

Sign in to your account.

### Step 2: Open Developer Tools

Press:

```text
F12
```

or:

```text
Ctrl + Shift + I
```

### Step 3: Open the Application tab

Navigate to:

```text
Application
→ Storage
→ Cookies
→ https://leetcode.com
```

### Step 4: Locate the cookies

Find:

```text
LEETCODE_SESSION
```

and:

```text
csrftoken
```

Copy only their **Value** fields.

Add them to GitHub as:

```text
LEETCODE_SESSION
LEETCODE_CSRF_TOKEN
```

Do not share the values with anyone.

## How Synchronization Works

```text
             LeetCode
                 │
                 ▼
          Solve a problem
                 │
                 ▼
          Submit solution
                 │
                 ▼
             Accepted
                 │
                 ▼
        LeetCode account
                 │
                 ▼
         GitHub Actions
                 │
                 ▼
      Retrieve solved problems
                 │
                 ▼
       Retrieve accepted code
                 │
                 ▼
       Detect difficulty/language
                 │
          ┌──────┼──────┐
          ▼      ▼      ▼
        Easy   Medium   Hard
          │      │      │
          └──────┼──────┘
                 ▼
          Commit changes
                 │
                 ▼
          GitHub repository
```

## Automatic Synchronization

The workflow is configured to run every 6 hours:

```yaml
schedule:
  - cron: "0 */6 * * *"
```

The schedule uses UTC time.

You can also start synchronization manually at any time.

## Manual Synchronization

To sync immediately:

```text
GitHub Repository
→ Actions
→ LeetCode Sync
→ Run workflow
→ Run workflow
```

This is useful when you have just solved a problem and do not want to wait for the next scheduled run.

## Example

If you solve:

```text
121. Best Time to Buy and Sell Stock
```

using Java, the workflow creates:

```text
Easy/
└── 0121-Best-Time-to-Buy-and-Sell-Stock/
    └── solution.java
```

If you solve another problem using Python:

```text
Easy/
├── 0121-Best-Time-to-Buy-and-Sell-Stock/
│   └── solution.java
│
└── 0020-Valid-Parentheses/
    └── solution.py
```

## Security Considerations

The `LEETCODE_SESSION` and `csrftoken` values are authentication credentials.

Never:

- Commit them to Git
- Add them to source code
- Put them in the workflow YAML
- Share them in screenshots
- Post them publicly
- Send them to other people

Use **GitHub Repository Secrets** instead.

If you accidentally expose either cookie, revoke or refresh your LeetCode session and replace the affected GitHub Secret.

## Troubleshooting

### Workflow fails with authentication errors

Check that:

- `LEETCODE_USERNAME` is correct
- `LEETCODE_SESSION` is current
- `LEETCODE_CSRF_TOKEN` is current
- The secrets were added to the correct repository
- You are logged into the correct LeetCode account

### Solutions are not appearing

Run the workflow manually:

```text
Actions
→ LeetCode Sync
→ Run workflow
```

Then open the workflow run and inspect the logs.

### LeetCode API errors

This project uses LeetCode's authenticated GraphQL endpoints. These endpoints are subject to change and are not guaranteed to remain compatible indefinitely.

If LeetCode changes its GraphQL schema, the queries in:

```text
scripts/leetcode_sync.py
```

may need to be updated.

## Project Files

```text
.github/workflows/leetcode.yml
```

Contains the GitHub Actions workflow responsible for running the synchronization automatically.

```text
scripts/leetcode_sync.py
```

Contains the Python synchronization logic that retrieves solved problems and writes the solutions to the repository.

## Contributing

Contributions and improvements are welcome.

If you find a bug or want to add support for another programming language, feel free to open an issue or submit a pull request.

## Disclaimer

This project is an independent community tool and is not affiliated with or endorsed by LeetCode.

Because it relies on authenticated LeetCode endpoints, functionality may change if LeetCode modifies its website or API.

## License

You are free to use, modify, and distribute this setup for personal or educational purposes.

---

If this project is useful to you, consider giving the repository a star.

Happy coding!
