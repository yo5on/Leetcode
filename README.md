<div align="center">
<samp><b>LEETCODE → GITHUB AUTO SYNC</b></samp>

<samp>python · github actions · graphql · automation</samp>

</div>

---

<div align="center"><samp>Automatically synchronize your accepted LeetCode solutions with a GitHub repository using GitHub Actions.</samp></div>

<samp>The workflow retrieves solved problems, identifies their difficulty and submission language, and organizes solutions into a clean repository structure.</samp>

---

<div align="center"><samp><b>Features</b></samp></div>

- <samp>Automatically syncs accepted LeetCode solutions</samp>
- <samp>Retrieves solved-problem history</samp>
- <samp>Organizes solutions by Easy, Medium, and Hard</samp>
- <samp>Preserves the programming language used for each submission</samp>
- <samp>Runs automatically every 6 hours</samp>
- <samp>Supports manual synchronization through GitHub Actions</samp>
- <samp>Requires no browser extension</samp>
- <samp>Uses GitHub Secrets for authentication data</samp>

---

<div align="center"><samp><b>Repository Structure</b></samp></div>

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

<samp>Each problem is placed inside its corresponding difficulty folder, and the solution file extension is determined automatically from the language used on LeetCode.</samp>

---

<div align="center"><samp><b>Supported Languages</b></samp></div>

| <samp>Language</samp> | <samp>Extension</samp> |
|---|---|
| <samp>Python</samp> | <samp>.py</samp> |
| <samp>Java</samp> | <samp>.java</samp> |
| <samp>C</samp> | <samp>.c</samp> |
| <samp>C++</samp> | <samp>.cpp</samp> |
| <samp>JavaScript</samp> | <samp>.js</samp> |
| <samp>TypeScript</samp> | <samp>.ts</samp> |
| <samp>Kotlin</samp> | <samp>.kt</samp> |
| <samp>Go</samp> | <samp>.go</samp> |
| <samp>Rust</samp> | <samp>.rs</samp> |
| <samp>Swift</samp> | <samp>.swift</samp> |
| <samp>C#</samp> | <samp>.cs</samp> |
| <samp>Ruby</samp> | <samp>.rb</samp> |
| <samp>PHP</samp> | <samp>.php</samp> |
| <samp>Scala</samp> | <samp>.scala</samp> |
| <samp>Dart</samp> | <samp>.dart</samp> |
| <samp>SQL</samp> | <samp>.sql</samp> |

---

<div align="center"><samp><b>Setup & Configuration</b></samp></div>

<h2 align="center"><samp><b>How It Works</b></samp></h2>

- <samp><samp>GitHub Actions runs the workflow defined in `.github/workflows/leetcode.yml`.</samp></samp>
- <samp><samp>The workflow installs Python 3.12 and the `requests` package.</samp></samp>
- <samp><samp>`scripts/leetcode_sync.py` authenticates with LeetCode, retrieves solved questions, and finds accepted submissions.</samp></samp>
- <samp><samp>Solutions are organized into `Easy/`, `Medium/`, and `Hard/` folders.</samp></samp>
- <samp><samp>GitHub Actions commits and pushes any detected changes.</samp></samp>

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

1. <samp><samp>Sign in to [LeetCode](https://leetcode.com/).</samp></samp>
2. <samp><samp>Open Developer Tools using **F12** or **Ctrl + Shift + I**.</samp></samp>
3. <samp><samp>Open **Application → Storage → Cookies → https://leetcode.com**. Depending on your browser, this may appear under **Storage**.</samp></samp>
4. <samp><samp>Find `LEETCODE_SESSION` and `csrftoken`.</samp></samp>
5. <samp><samp>Copy each cookie's **Value** into its matching GitHub repository secret.</samp></samp>

> <samp><b>Security:</b> These cookies can grant access to your account. Never place their values in this file, source code, workflow YAML, screenshots, commits, or messages. Use only your own session. If a cookie expires, obtain a fresh value and update the secret.</samp>

---

<h2 align="center"><samp><b>2 · Enable Workflow Permissions</b></samp></h2>

1. <samp><samp>Open the repository's **Settings → Actions → General**.</samp></samp>
2. <samp><samp>Make sure GitHub Actions is allowed to run.</samp></samp>
3. <samp><samp>Under **Workflow permissions**, enable **Read and write permissions** if required by the repository settings.</samp></samp>

<samp>The workflow declares `permissions: contents: write` so it can commit synchronized solutions.</samp>

---

<h2 align="center"><samp><b>3 · Run Your First Sync</b></samp></h2>

1. <samp><samp>Open the [Leetcode Actions tab](https://github.com/yo5on/Leetcode/actions).</samp></samp>
2. <samp><samp>Select **LeetCode Sync** from the workflow list.</samp></samp>
3. <samp><samp>Click **Run workflow**, select the `main` branch, and start the run.</samp></samp>
4. <samp><samp>Open the run to review its steps and logs.</samp></samp>
5. <samp><samp>After a successful run, check the `Easy/`, `Medium/`, and `Hard/` folders.</samp></samp>

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

- <samp><samp>Confirm `LEETCODE_USERNAME` matches your LeetCode account.</samp></samp>
- <samp><samp>Refresh `LEETCODE_SESSION` and `LEETCODE_CSRF_TOKEN` from the same signed-in account.</samp></samp>
- <samp><samp>Check that you copied the cookie values, not the cookie names.</samp></samp>
- <samp><samp>Save the updated values as repository secrets and rerun the workflow.</samp></samp>

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

- <samp><samp>`.github/workflows/leetcode.yml` — scheduled and manual workflow, permissions, dependencies, and commit step.</samp></samp>
- <samp><samp>`scripts/leetcode_sync.py` — authentication, LeetCode queries, submission selection, and file organization.</samp></samp>
- <samp><samp>`Easy/`, `Medium/`, `Hard/` — destination folders for synchronized solutions.</samp></samp>

---

<div align="center"><samp><b>Disclaimer</b></samp></div>

<samp>This project is an independent community tool and is not affiliated with or endorsed by LeetCode.</samp>

<samp>Because it relies on authenticated LeetCode endpoints, functionality may change if LeetCode modifies its website or API.</samp>

---

<div align="center"><samp><b>License</b></samp></div>

<samp>You are free to use, modify, and distribute this setup for personal or educational purposes.</samp>
