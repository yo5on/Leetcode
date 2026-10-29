<div align="center">

<samp><b>LEETCODE AUTO-SYNC · SETUP GUIDE</b></samp>

<samp>github actions · python · graphql · configuration</samp>

</div>

---

<div align="center"><samp>Configure the LeetCode → GitHub automation from a fresh setup, refresh credentials, and troubleshoot failed runs.</samp></div>

## 1. How it works

- GitHub Actions runs the workflow in `.github/workflows/leetcode.yml`.
- The workflow installs Python 3.12 and the `requests` package.
- `scripts/leetcode_sync.py` authenticates to LeetCode's GraphQL endpoint, checks the account, fetches solved questions, and finds the latest accepted submission.
- Solutions are organized into `Easy/`, `Medium/`, and `Hard/` folders.
- GitHub Actions commits and pushes any detected changes.

The workflow can run manually or on a six-hour schedule (UTC).

## 2. Add the required GitHub repository secrets

Open the [Leetcode repository settings](https://github.com/yo5on/Leetcode/settings/secrets/actions).

Choose **Secrets and variables → Actions → New repository secret**. Add these three secrets with the exact names shown:

| Secret name | Value |
|---|---|
| `LEETCODE_USERNAME` | Your LeetCode username (for this repository, `yo5on`) |
| `LEETCODE_SESSION` | The current value of the `LEETCODE_SESSION` cookie from your signed-in LeetCode session |
| `LEETCODE_CSRF_TOKEN` | The current value of the `csrftoken` cookie from the same session |

Secret names are case-sensitive. Copy only the cookie values, without surrounding quotes or extra whitespace.

### Find the cookie values

1. Sign in to [LeetCode](https://leetcode.com/).
2. Open browser Developer Tools (usually **F12** or **Ctrl + Shift + I**).
3. Open **Application → Storage → Cookies → https://leetcode.com**. In some browsers, the equivalent is under **Storage**.
4. Find `LEETCODE_SESSION` and `csrftoken`.
5. Copy each cookie's **Value** into the matching GitHub repository secret.

These cookies grant access to your account. **Never put their values in this file, source code, workflow YAML, screenshots, commits, or chat messages.** Do not use someone else's cookies. If a cookie has expired, repeat the process with your own currently signed-in session and update the corresponding secret.

## 3. Allow the workflow to push commits

1. Open the repository's **Settings → Actions → General**.
2. Ensure GitHub Actions is allowed to run.
3. Under **Workflow permissions**, enable **Read and write permissions** if the repository's settings require it.

The workflow also declares `permissions: contents: write`, which it needs to commit synchronized solutions.

## 4. Run the first sync

1. Open the [Actions tab](https://github.com/yo5on/Leetcode/actions).
2. Select **LeetCode Sync** in the workflow list.
3. Click **Run workflow**, select the `main` branch, and run it.
4. Open the new run and inspect the steps if anything fails.
5. When successful, check the `Easy/`, `Medium/`, and `Hard/` folders for synchronized solutions.

The workflow also runs automatically every six hours using this schedule:

```yaml
schedule:
  - cron: "0 */6 * * *"
```

GitHub Actions cron schedules use UTC and may start a little later during busy periods.

## 5. Troubleshooting

### Authentication failed or the account does not match

- Confirm `LEETCODE_USERNAME` is your actual LeetCode username.
- Refresh `LEETCODE_SESSION` and `LEETCODE_CSRF_TOKEN` from the same signed-in account.
- Make sure the secrets contain cookie values, not the cookie names.
- Save the updated values as repository secrets and rerun the workflow.

### Missing-secret error

Check that all three secret names match the spelling and capitalization in section 2. Secret values are not displayed back to you by GitHub.

### LeetCode GraphQL or progress endpoint error

The sync relies on authenticated LeetCode endpoints that can change. Open the failed Actions run and inspect the error message. If the API response/schema has changed, `scripts/leetcode_sync.py` may need a code update. Avoid pasting cookies or other credentials into logs or issue reports.

### The workflow succeeds but no new files appear

The script only has changes to commit when it finds eligible solved questions and accepted submissions not already reflected in the repository. Check the run logs and confirm that the correct LeetCode account is authenticated.

### Push or permission error

Confirm Actions is enabled and the workflow has contents write permission. The workflow commits as `github-actions[bot]` and pushes to the branch that was checked out.

## 6. Files involved

- `.github/workflows/leetcode.yml` — scheduled/manual workflow, dependencies, permissions, and commit step.
- `scripts/leetcode_sync.py` — LeetCode authentication, query logic, solution selection, and file organization.
- `Easy/`, `Medium/`, `Hard/` — destination folders for synchronized solutions.

---

<div align="center"><samp>Keep authentication cookies private and periodically refresh them when LeetCode invalidates the session.</samp></div>
