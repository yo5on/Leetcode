# Setup

This repository syncs accepted LeetCode solutions into `Easy/`, `Medium/`, and `Hard/` with GitHub Actions and keeps the progress stats in [README.md](README.md) up to date. This page covers setup, account changes, and troubleshooting.

## How It Works

1. GitHub Actions runs [`.github/workflows/leetcode.yml`](.github/workflows/leetcode.yml) on a schedule or on demand.
2. The workflow installs Python 3.12 and `requests`, then runs [`scripts/leetcode_sync.py`](scripts/leetcode_sync.py).
3. The script signs in with your LeetCode cookies, checks that they belong to `LEETCODE_USERNAME`, and fetches every problem you have solved.
4. It rewrites the block between `<!-- LEETCODE-STATS:START -->` and `<!-- LEETCODE-STATS:END -->` in `README.md` with your profile link and your Total, Easy, Medium, and Hard counts. Keep both markers in the README, or the sync fails.
5. For each solved problem it saves the latest accepted submission as `<Difficulty>/<NNNN-Title>/solution.<ext>`, where the extension comes from the submission's language.
6. It deletes `solution.*` files for problems the account has not solved, and older files in other languages for a problem it re-syncs. Other files you put in those folders are never touched.
7. The workflow commits and pushes any changes as `github-actions[bot]`.

## Prerequisites

- A LeetCode account you can sign in to in a desktop browser.
- Write access to this repository on GitHub.
- [GitHub CLI](https://cli.github.com/) for setting secrets and running the workflow from a terminal:
  - Windows: `winget install --id GitHub.cli`
  - macOS: `brew install gh`
  - Linux: see the [installation guide](https://github.com/cli/cli#installation)
- Sign in to the CLI once with `gh auth login` and confirm with `gh auth status`.
- Python 3.12 with `requests` installed (`pip install requests`), only if you want to run the self-test locally.

## 1. Get the Cookie Values

1. Sign in to [LeetCode](https://leetcode.com/) with the account you want to sync.
2. Open Developer Tools with **F12** or **Ctrl + Shift + I**.
3. Open **Application → Storage → Cookies → https://leetcode.com** (in Firefox: **Storage → Cookies**).
4. Find `LEETCODE_SESSION` and `csrftoken`, and copy each cookie's **Value**, without its name, quotes, or whitespace.

> **Security:** these cookies give access to your LeetCode account. Never put their values in files, source code, workflow YAML, screenshots, commits, issues, or chat messages. Store them only as GitHub secrets.

## 2. Configure Repository Secrets

| Secret | Value |
|---|---|
| `LEETCODE_USERNAME` | Your LeetCode username |
| `LEETCODE_SESSION` | The `LEETCODE_SESSION` cookie value |
| `LEETCODE_CSRF_TOKEN` | The `csrftoken` cookie value |

Set them with the GitHub CLI. Each command prompts for the value, so it never lands in your shell history:

```bash
gh secret set LEETCODE_USERNAME -R yo5on/Leetcode
gh secret set LEETCODE_SESSION -R yo5on/Leetcode
gh secret set LEETCODE_CSRF_TOKEN -R yo5on/Leetcode
```

Or open [Settings → Secrets and variables → Actions](https://github.com/yo5on/Leetcode/settings/secrets/actions) and select **New repository secret**. Secret names are case-sensitive, and GitHub never shows a saved value again.

## 3. Enable Workflow Permissions

1. Open [Settings → Actions → General](https://github.com/yo5on/Leetcode/settings/actions).
2. Make sure GitHub Actions is allowed to run.
3. Under **Workflow permissions**, enable **Read and write permissions** if your repository settings require it.

The workflow declares `permissions: contents: write` so it can commit synced solutions.

## 4. Run the Workflow Manually

From the terminal:

```bash
gh workflow run leetcode.yml -R yo5on/Leetcode
gh run watch -R yo5on/Leetcode
```

Or open the [Actions tab](https://github.com/yo5on/Leetcode/actions), select **LeetCode Sync**, click **Run workflow** on the `main` branch, and open the run to read its logs. After a successful run, check `README.md` and the difficulty folders.

## Automatic Sync Schedule

The workflow also runs every six hours (UTC):

```yaml
schedule:
  - cron: "0 */6 * * *"
```

GitHub may start scheduled runs a little late during busy periods, and it pauses schedules in repositories with no activity for 60 days. Only one sync runs at a time.

## Connect or Switch LeetCode Accounts

1. Sign in to the new account on leetcode.com, ideally in a browser profile you stay signed in to.
2. Copy fresh `LEETCODE_SESSION` and `csrftoken` values (step 1).
3. Update all three secrets, including `LEETCODE_USERNAME` (step 2).
4. Run the workflow manually (step 4).

The sync refuses to run if the cookies belong to a different account than `LEETCODE_USERNAME`. On the next successful run, the README shows the new account's profile and stats, and solutions for problems the new account has not solved are removed. Earlier solutions stay in the git history.

## Session Cookie Expiration and Renewal

`LEETCODE_SESSION` stops working 14 days after you copy it, or as soon as you log out of the browser you copied it from. Each run logs the expiry date and shows a warning when fewer than 3 days are left.

To renew it, sign in to leetcode.com, copy both cookies again, and update the two cookie secrets:

```bash
gh secret set LEETCODE_SESSION -R yo5on/Leetcode
gh secret set LEETCODE_CSRF_TOKEN -R yo5on/Leetcode
```

## Troubleshooting

### Authentication Failed or Wrong Account

- Read the error: it says whether the cookie is malformed, expired on a given date, or was revoked by logging out.
- Confirm `LEETCODE_USERNAME` matches the account the cookies came from.
- Copy both cookies again from the same signed-in account, copying the values and not the names.
- Update the secrets and run the workflow again.

### Missing Secret

Check the spelling and capitalization of all three secret names with `gh secret list -R yo5on/Leetcode`.

### GraphQL or Progress Endpoint Error

LeetCode's authenticated endpoints can change. Read the failed run's logs. If the response or schema has changed, `scripts/leetcode_sync.py` may need an update. Never paste cookies into logs or issue reports.

### Sync Finished With Failed Problems

Some problems could not be fetched, usually because the session dropped or LeetCode rate-limited the run. Everything that did sync is still committed. Run the workflow again later.

### No New Solutions Appeared

The workflow commits only when something changed. Check the run logs and confirm that the expected account was authenticated.

### Push or Permission Error

Confirm Actions is enabled and the workflow has write permission (step 3).

## Run the Self-Test Locally

The self-test checks cookie expiry parsing, the README stats rendering, and stale-solution cleanup. It does not contact LeetCode and needs no secrets:

```bash
python scripts/leetcode_sync.py --self-test
```

It prints `Self-test passed.` on success.

## Repository Structure

```text
Leetcode/
├── .github/workflows/leetcode.yml   # scheduled and manual sync workflow
├── scripts/leetcode_sync.py         # sign-in, LeetCode queries, file and README updates
├── Easy/  Medium/  Hard/            # synced solutions, one folder per problem
├── README.md                        # LeetCode progress, updated by each sync
└── SETUP.md                         # this guide
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

This project is an independent community tool and is not affiliated with or endorsed by LeetCode. It relies on authenticated LeetCode endpoints, so it may break if LeetCode changes its website or API.

## License

The original code is licensed under the MIT License. See [LICENSE](LICENSE).
