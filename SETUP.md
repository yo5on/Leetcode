# Setup

This repository does two separate jobs with GitHub Actions:

| Job | Workflow | Runs | Needs cookies? |
|---|---|---|---|
| **Stats**: Total, Easy, Medium, and Hard counts in [README.md](README.md) | [`leetcode-stats.yml`](.github/workflows/leetcode-stats.yml) | Every 6 hours and on demand | **No** |
| **Solutions**: accepted code in `Easy/`, `Medium/`, `Hard/` | [`leetcode.yml`](.github/workflows/leetcode.yml) | On demand only | Yes |

The stats keep themselves up to date forever with only your username. Cookies are needed only when you want to pull new solution code.

## How It Works

### Stats (no login)

1. [`leetcode-stats.yml`](.github/workflows/leetcode-stats.yml) runs [`scripts/leetcode_stats.py`](scripts/leetcode_stats.py) every six hours.
2. The script asks LeetCode's public GraphQL API for `matchedUser(username).submitStats`, the same data anyone can see on your profile page. No cookie, token, or password is sent.
3. It rewrites the block between `<!-- LEETCODE-STATS:START -->` and `<!-- LEETCODE-STATS:END -->` in `README.md` with your profile link and counts. Keep both markers in the README, or the update fails.
4. If LeetCode returns no profile or an incomplete response, the script fails and leaves the README as it was.
5. The workflow commits `README.md` only when the numbers changed.

Your profile must be public, which is LeetCode's default.

### Solutions (login required)

1. You run [`leetcode.yml`](.github/workflows/leetcode.yml) by hand. It runs [`scripts/leetcode_sync.py`](scripts/leetcode_sync.py).
2. The script signs in with your LeetCode cookies, checks that they belong to `LEETCODE_USERNAME`, and fetches every problem you have solved.
3. For each solved problem it saves the latest accepted submission as `<Difficulty>/<NNNN-Title>/solution.<ext>`, where the extension comes from the submission's language.
4. It deletes `solution.*` files for problems the account has not solved, and older files in other languages for a problem it re-syncs. Other files you put in those folders are never touched. If LeetCode returns no solved problems at all, nothing is deleted.
5. The workflow commits and pushes `Easy/`, `Medium/`, and `Hard/` as `github-actions[bot]`. It does not touch the README.

### Why solutions still need cookies

LeetCode only shows submission source code to the account that wrote it. The endpoints that list your submissions and return their code (`questionSubmissionList`, `submissionDetails`) answer only to a signed-in session, and LeetCode offers no API token or OAuth app that could replace the session cookie. So there is no unauthenticated way to fetch your code.

That is why the solution sync no longer runs on a schedule: a scheduled job with cookies fails every time they expire (14 days, or as soon as you log out), which is what used to force regular cookie updates. Now an expired cookie only matters on the day you choose to sync solutions.

Safer options, from least to most exposure:

1. **Commit solutions yourself.** Paste the code into `<Difficulty>/<NNNN-Title>/solution.<ext>` and push. No LeetCode credentials go anywhere.
2. **Run the sync locally.** Set the cookies as environment variables in your own terminal for one run (see [Run the Solution Sync Locally](#run-the-solution-sync-locally)). They never leave your machine and are gone when you close the terminal.
3. **Run the sync workflow on demand.** Store fresh cookies as GitHub secrets just before a run. GitHub encrypts them, but they stay valid there until they expire.

Never give your LeetCode password or cookies to a third-party website or service that offers to sync for you.

## Prerequisites

- Write access to this repository on GitHub.
- [GitHub CLI](https://cli.github.com/) for setting secrets and running workflows from a terminal:
  - Windows: `winget install --id GitHub.cli`
  - macOS: `brew install gh`
  - Linux: see the [installation guide](https://github.com/cli/cli#installation)
- Sign in to the CLI once with `gh auth login` and confirm with `gh auth status`.
- Python 3.12 with `requests` installed (`pip install requests`), only if you want to run the scripts locally.

## 1. Set Your Username (Stats)

The stats job needs only your LeetCode username. It is public, so store it as a repository **variable**:

```bash
gh variable set LEETCODE_USERNAME -R yo5on/Leetcode
```

Or open [Settings → Secrets and variables → Actions → Variables](https://github.com/yo5on/Leetcode/settings/variables/actions). An existing `LEETCODE_USERNAME` secret also works; the variable wins if both are set.

## 2. Enable Workflow Permissions

1. Open [Settings → Actions → General](https://github.com/yo5on/Leetcode/settings/actions).
2. Make sure GitHub Actions is allowed to run.
3. Under **Workflow permissions**, enable **Read and write permissions** if your repository settings require it.

Both workflows declare `permissions: contents: write` so they can commit.

## 3. Run the Stats Workflow

```bash
gh workflow run leetcode-stats.yml -R yo5on/Leetcode
gh run watch -R yo5on/Leetcode
```

Or open the [Actions tab](https://github.com/yo5on/Leetcode/actions), select **LeetCode Stats**, and click **Run workflow**. After that it runs every six hours (UTC) on its own:

```yaml
schedule:
  - cron: "0 */6 * * *"
```

GitHub may start scheduled runs a little late during busy periods, and it pauses schedules in repositories with no activity for 60 days. The stats commits count as activity, but only when your numbers change. The two workflows share a concurrency group, so they never push at the same time.

That is all the setup the stats need. The rest of this page is only for syncing solution code.

## 4. Sync Solutions (Optional, Needs Cookies)

### Get the cookie values

1. Sign in to [LeetCode](https://leetcode.com/) with the account you want to sync.
2. Open Developer Tools with **F12** or **Ctrl + Shift + I**.
3. Open **Application → Storage → Cookies → https://leetcode.com** (in Firefox: **Storage → Cookies**).
4. Find `LEETCODE_SESSION` and `csrftoken`, and copy each cookie's **Value**, without its name, quotes, or whitespace.

> **Security:** these cookies give access to your LeetCode account. Never put their values in files, source code, workflow YAML, screenshots, commits, issues, or chat messages. Store them only as GitHub secrets or in a terminal session's environment.

### Run the solution sync workflow

| Secret | Value |
|---|---|
| `LEETCODE_USERNAME` | Your LeetCode username (or the variable from step 1) |
| `LEETCODE_SESSION` | The `LEETCODE_SESSION` cookie value |
| `LEETCODE_CSRF_TOKEN` | The `csrftoken` cookie value |

Each command prompts for the value, so it never lands in your shell history:

```bash
gh secret set LEETCODE_SESSION -R yo5on/Leetcode
```

```bash
gh secret set LEETCODE_CSRF_TOKEN -R yo5on/Leetcode
```

```bash
gh workflow run leetcode.yml -R yo5on/Leetcode
```

Each run logs the cookie's expiry date and warns when fewer than 3 days are left. To limit exposure, you can delete the cookie secrets after the run:

```bash
gh secret delete LEETCODE_SESSION -R yo5on/Leetcode
```

```bash
gh secret delete LEETCODE_CSRF_TOKEN -R yo5on/Leetcode
```

### Run the solution sync locally

From the repository root, in Git Bash or a Unix shell. `read -s` keeps the values off the screen and out of shell history:

```bash
read -s -p "LEETCODE_SESSION: " LEETCODE_SESSION && read -s -p "csrftoken: " LEETCODE_CSRF_TOKEN && export LEETCODE_SESSION LEETCODE_CSRF_TOKEN LEETCODE_USERNAME=yo5on && python scripts/leetcode_sync.py
```

Then review the changes with `git status` and commit them yourself.

## Connect or Switch LeetCode Accounts

1. Update `LEETCODE_USERNAME` (step 1). The next stats run shows the new account's profile and counts.
2. To replace the solutions as well, sign in to the new account and run the solution sync with its cookies (step 4).

The solution sync refuses to run if the cookies belong to a different account than `LEETCODE_USERNAME`. It removes solutions for problems the new account has not solved. Earlier solutions stay in the git history.

## Troubleshooting

### Stats: "LeetCode returned no profile"

The username is wrong or the profile is private. Check `gh variable list -R yo5on/Leetcode` and open `https://leetcode.com/u/<username>/` in a private browser window.

### Stats: README markers missing

Restore the `<!-- LEETCODE-STATS:START -->` and `<!-- LEETCODE-STATS:END -->` lines in `README.md`.

### Solutions: Authentication Failed or Wrong Account

- Read the error: it says whether the cookie is malformed, expired on a given date, or was revoked by logging out.
- Confirm `LEETCODE_USERNAME` matches the account the cookies came from.
- Copy both cookies again from the same signed-in account, copying the values and not the names.

### Solutions: Missing Secret

Check the spelling and capitalization of the secret names with `gh secret list -R yo5on/Leetcode`.

### GraphQL or Progress Endpoint Error

LeetCode's endpoints can change. Read the failed run's logs. If the response or schema has changed, the script may need an update. Never paste cookies into logs or issue reports.

### Solutions: Sync Finished With Failed Problems

Some problems could not be fetched, usually because the session dropped or LeetCode rate-limited the run. Everything that did sync is still committed. Run the workflow again later.

### Push or Permission Error

Confirm Actions is enabled and the workflows have write permission (step 2).

## Run the Self-Tests Locally

Neither self-test contacts LeetCode or needs secrets:

```bash
python scripts/leetcode_stats.py --self-test
```

```bash
python scripts/leetcode_sync.py --self-test
```

Each prints `Self-test passed.` on success. The first checks response validation and the README stats rendering; the second checks cookie expiry parsing and stale-solution cleanup.

To try the real public stats fetch without committing, run it and inspect the result with `git diff README.md`:

```bash
LEETCODE_USERNAME=yo5on python scripts/leetcode_stats.py
```

## Repository Structure

```text
Leetcode/
├── .github/workflows/
│   ├── leetcode-stats.yml   # every 6 hours: public stats → README, no login
│   └── leetcode.yml         # on demand: solution code, needs cookies
├── scripts/
│   ├── leetcode_stats.py    # public profile query and README update
│   └── leetcode_sync.py     # sign-in, submission queries, solution files
├── Easy/  Medium/  Hard/    # synced solutions, one folder per problem
├── README.md                # LeetCode progress, updated by the stats job
└── SETUP.md                 # this guide
```

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

Submissions in other languages are skipped.

## Disclaimer

This project is an independent community tool and is not affiliated with or endorsed by LeetCode. It relies on LeetCode's GraphQL endpoints, so it may break if LeetCode changes its website or API.

## License

The original code is licensed under the MIT License. See [LICENSE](LICENSE).
