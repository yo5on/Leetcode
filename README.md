<div align="center">

<img src="https://raw.githubusercontent.com/yo5on/yo5on/main/hd-projects.svg" width="620" alt="projects"/>

<samp><b>LEETCODE → GITHUB AUTO SYNC</b></samp>

<samp>python · github actions · graphql · automation</samp>

**[Repository](https://github.com/yo5on/Leetcode)**

</div>

---

Automatically synchronize your accepted LeetCode solutions with a GitHub repository using GitHub Actions.

The workflow retrieves solved problems, identifies their difficulty and submission language, and organizes solutions into a clean repository structure.

## Features

- Automatically syncs accepted LeetCode solutions
- Retrieves solved-problem history
- Organizes solutions by Easy, Medium, and Hard
- Preserves the programming language used for each submission
- Runs automatically every 6 hours
- Supports manual synchronization through GitHub Actions
- Requires no browser extension
- Uses GitHub Secrets for authentication data

## Repository Structure

```text
Leetcode/
├── .github/
│   └── workflows/
│       └── leetcode.yml
├── scripts/
│   └── leetcode_sync.py
├── Easy/
├── Medium/
└── Hard/
```

Each problem is placed inside its corresponding difficulty folder, and the solution file extension is determined automatically from the language used on LeetCode.

## Supported Languages

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

### Enable GitHub Actions

Open:

```text
Repository
→ Settings
→ Actions
→ General
```

Make sure GitHub Actions are allowed to run and the workflow has permission to write changes to the repository.

### Add Repository Secrets

Create these repository secrets:

```text
LEETCODE_USERNAME
LEETCODE_SESSION
LEETCODE_CSRF_TOKEN
```

`LEETCODE_SESSION` and `LEETCODE_CSRF_TOKEN` are authentication credentials. Never commit or share their values.

## Obtaining the LeetCode Cookies

1. Sign in to LeetCode.
2. Open browser Developer Tools with `F12` or `Ctrl + Shift + I`.
3. Open `Application → Storage → Cookies → https://leetcode.com`.
4. Locate `LEETCODE_SESSION` and `csrftoken`.
5. Copy only their Value fields into the corresponding GitHub repository secrets.

If either credential is exposed, revoke or refresh the LeetCode session and replace the affected GitHub Secret.

## How Synchronization Works

```text
LeetCode
   |
   v
Accepted submission
   |
   v
GitHub Actions
   |
   v
Retrieve solved problems
   |
   v
Detect difficulty and language
   |
   v
Easy / Medium / Hard
   |
   v
Commit changes
   |
   v
GitHub repository
```

## Automatic Synchronization

The workflow runs every 6 hours:

```yaml
schedule:
  - cron: "0 */6 * * *"
```

The schedule uses UTC time. Synchronization can also be started manually from the Actions tab.

## Manual Synchronization

```text
GitHub Repository
→ Actions
→ LeetCode Sync
→ Run workflow
→ Run workflow
```

## Security Considerations

Never:

- Commit authentication cookies to Git
- Add them to source code
- Put them in workflow YAML
- Share them in screenshots
- Post them publicly
- Send them to other people

Use GitHub Repository Secrets instead.

## Troubleshooting

### Workflow authentication errors

Check that the username and both authentication secrets are current and belong to the correct LeetCode account.

### Solutions are not appearing

Run the workflow manually and inspect the workflow logs.

### LeetCode API errors

The project uses LeetCode's authenticated GraphQL endpoints. These endpoints may change without notice. If the GraphQL schema changes, `scripts/leetcode_sync.py` may need to be updated.

## Project Files

```text
.github/workflows/leetcode.yml
```

GitHub Actions workflow responsible for scheduled and manual synchronization.

```text
scripts/leetcode_sync.py
```

Python synchronization logic that retrieves solved problems and writes solutions to the repository.

## Disclaimer

This project is an independent community tool and is not affiliated with or endorsed by LeetCode.

Because it relies on authenticated LeetCode endpoints, functionality may change if LeetCode modifies its website or API.

## License

You are free to use, modify, and distribute this setup for personal or educational purposes.
