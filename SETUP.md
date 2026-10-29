<div align="center">

<samp><b>LEETCODE AUTO-SYNC · SETUP GUIDE</b></samp>

<samp>github actions · python · graphql · automation</samp>

</div>

---

<div align="center"><samp>A practical guide to setting up, running, and troubleshooting the LeetCode → GitHub sync.</samp></div>

<h2 align="center"><samp><b>How It Works</b></samp></h2>

- <samp>GitHub Actions runs the workflow defined in `.github/workflows/leetcode.yml`.</samp>
- <samp>The workflow installs Python 3.12 and the `requests` package.</samp>
- <samp>`scripts/leetcode_sync.py` authenticates with LeetCode, retrieves solved questions, and finds accepted submissions.</samp>
- <samp>Solutions are organized into `Easy/`, `Medium/`, and `Hard/` folders.</samp>
- <samp>GitHub Actions commits and pushes any detected changes.</samp>

<div align="center"><samp>The workflow can be started manually or run automatically every six hours (UTC).</samp></div>

---

<h2 align="center"><samp><b>1 · Configure Repository Secrets</b></samp></h2>

<samp>Open [Leetcode → Settings → Secrets and variables → Actions](https://github.com/yo5on/Leetcode/settings/secrets/actions), then select **New repository secret**.</samp>

| <samp>Secret</samp> | <samp>Value to add</samp> |
|---|---|
| <samp>`LEETCODE_USERNAME`</samp> | <samp>Your LeetCode username: `yo5on`</samp> |
| <samp>`LEETCODE_SESSION`</samp> | <samp>The current `LEETCODE_SESSION` cookie value</samp> |
| <samp>`LEETCODE_CSRF_TOKEN`</samp> | <samp>The current `csrftoken` cookie value</samp> |

<samp>Secret names are case-sensitive. Copy the cookie **values**, not their names, and avoid adding quotes or whitespace.</samp>

<h3 align="center"><samp><b>Find the Cookie Values</b></samp></h3>

1. <samp>Sign in to [LeetCode](https://leetcode.com/).</samp>
2. <samp>Open Developer Tools using **F12** or **Ctrl + Shift + I**.</samp>
3. <samp>Open **Application → Storage → Cookies → https://leetcode.com**. Depending on your browser, this may appear under **Storage**.</samp>
4. <samp>Find `LEETCODE_SESSION` and `csrftoken`.</samp>
5. <samp>Copy each cookie's **Value** into its matching GitHub repository secret.</samp>

> <samp><b>Security:</b> These cookies can grant access to your account. Never place their values in this file, source code, workflow YAML, screenshots, commits, or messages. Use only your own session. If a cookie expires, obtain a fresh value and update the secret.</samp>

---

<h2 align="center"><samp><b>2 · Enable Workflow Permissions</b></samp></h2>

1. <samp>Open the repository's **Settings → Actions → General**.</samp>
2. <samp>Make sure GitHub Actions is allowed to run.</samp>
3. <samp>Under **Workflow permissions**, enable **Read and write permissions** if required by the repository settings.</samp>

<samp>The workflow declares `permissions: contents: write` so it can commit synchronized solutions.</samp>

---

<h2 align="center"><samp><b>3 · Run Your First Sync</b></samp></h2>

1. <samp>Open the [Leetcode Actions tab](https://github.com/yo5on/Leetcode/actions).</samp>
2. <samp>Select **LeetCode Sync** from the workflow list.</samp>
3. <samp>Click **Run workflow**, select the `main` branch, and start the run.</samp>
4. <samp>Open the run to review its steps and logs.</samp>
5. <samp>After a successful run, check the `Easy/`, `Medium/`, and `Hard/` folders.</samp>

<h3 align="center"><samp><b>Automatic Schedule</b></samp></h3>

<samp>The workflow is scheduled to run every six hours:</samp>

```yaml
schedule:
  - cron: "0 */6 * * *"
```

<samp>The schedule uses UTC. GitHub Actions may start a scheduled run a little later during busy periods.</samp>

---

<h2 align="center"><samp><b>4 · Troubleshooting</b></samp></h2>

<h3 align="center"><samp><b>Authentication Failed or Wrong Account</b></samp></h3>

- <samp>Confirm `LEETCODE_USERNAME` matches your LeetCode account.</samp>
- <samp>Refresh `LEETCODE_SESSION` and `LEETCODE_CSRF_TOKEN` from the same signed-in account.</samp>
- <samp>Check that you copied the cookie values, not the cookie names.</samp>
- <samp>Save the updated values as repository secrets and rerun the workflow.</samp>

<h3 align="center"><samp><b>Missing Secret</b></samp></h3>

<samp>Check the spelling and capitalization of all three secret names. GitHub does not display saved secret values after you add them.</samp>

<h3 align="center"><samp><b>GraphQL or Progress Endpoint Error</b></samp></h3>

<samp>LeetCode's authenticated endpoints can change. Inspect the failed Actions run. If the response or schema has changed, `scripts/leetcode_sync.py` may need an update. Never paste authentication cookies into logs or issue reports.</samp>

<h3 align="center"><samp><b>No New Solutions Appeared</b></samp></h3>

<samp>The script commits only when it finds eligible solutions that are not already reflected in the repository. Review the run logs and confirm that the correct account was authenticated.</samp>

<h3 align="center"><samp><b>Push or Permission Error</b></samp></h3>

<samp>Confirm Actions is enabled and the workflow has contents write permission. The workflow commits as `github-actions[bot]` and pushes to the branch checked out by the run.</samp>

---

<h2 align="center"><samp><b>5 · Project Files</b></samp></h2>

- <samp>`.github/workflows/leetcode.yml` — scheduled and manual workflow, permissions, dependencies, and commit step.</samp>
- <samp>`scripts/leetcode_sync.py` — authentication, LeetCode queries, submission selection, and file organization.</samp>
- <samp>`Easy/`, `Medium/`, `Hard/` — destination folders for synchronized solutions.</samp>

---

<div align="center">

<samp><b>Keep your credentials private.</b></samp>

<samp>Refresh expired cookies, rerun the workflow, and inspect Actions logs when troubleshooting.</samp>

</div>
