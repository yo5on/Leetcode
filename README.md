<div align="center">

<img src="https://raw.githubusercontent.com/yo5on/yo5on/main/hd-projects.svg" width="620" alt="projects"/>

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

<div align="center"><samp><b>Setup</b></samp></div>

<samp><b>Enable GitHub Actions</b></samp>

<samp>Open:</samp>

```text
Repository
→ Settings
→ Actions
→ General
```

<samp>Make sure GitHub Actions are allowed to run and the workflow has permission to write changes to the repository.</samp>

<samp><b>Add Repository Secrets</b></samp>

<samp>Create these repository secrets:</samp>

```text
LEETCODE_USERNAME
LEETCODE_SESSION
LEETCODE_CSRF_TOKEN
```

<samp><b>Important:</b> <code>LEETCODE_SESSION</code> and <code>LEETCODE_CSRF_TOKEN</code> are authentication credentials. Never commit or share their values.</samp>

---

<div align="center"><samp><b>Obtaining the LeetCode Cookies</b></samp></div>

1. <samp>Sign in to LeetCode.</samp>
2. <samp>Open browser Developer Tools with <code>F12</code> or <code>Ctrl + Shift + I</code>.</samp>
3. <samp>Open <code>Application → Storage → Cookies → https://leetcode.com</code>.</samp>
4. <samp>Locate <code>LEETCODE_SESSION</code> and <code>csrftoken</code>.</samp>
5. <samp>Copy only their Value fields into the corresponding GitHub repository secrets.</samp>

<samp>If either credential is exposed, revoke or refresh the LeetCode session and replace the affected GitHub Secret.</samp>

---

<div align="center"><samp><b>How Synchronization Works</b></samp></div>

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

---

<div align="center"><samp><b>Automatic Synchronization</b></samp></div>

<samp>The workflow runs every 6 hours:</samp>

```yaml
schedule:
  - cron: "0 */6 * * *"
```

<samp>The schedule uses UTC time. Synchronization can also be started manually from the Actions tab.</samp>

---

<div align="center"><samp><b>Manual Synchronization</b></samp></div>

```text
GitHub Repository
→ Actions
→ LeetCode Sync
→ Run workflow
→ Run workflow
```

---

<div align="center"><samp><b>Security Considerations</b></samp></div>

<samp><b>Never:</b></samp>

- <samp>Commit authentication cookies to Git</samp>
- <samp>Add them to source code</samp>
- <samp>Put them in workflow YAML</samp>
- <samp>Share them in screenshots</samp>
- <samp>Post them publicly</samp>
- <samp>Send them to other people</samp>

<samp>Use GitHub Repository Secrets instead.</samp>

---

<div align="center"><samp><b>Troubleshooting</b></samp></div>

<samp><b>Workflow authentication errors</b></samp>

<samp>Check that the username and both authentication secrets are current and belong to the correct LeetCode account.</samp>

<samp><b>Solutions are not appearing</b></samp>

<samp>Run the workflow manually and inspect the workflow logs.</samp>

<samp><b>LeetCode API errors</b></samp>

<samp>The project uses LeetCode's authenticated GraphQL endpoints. These endpoints may change without notice. If the GraphQL schema changes, <code>scripts/leetcode_sync.py</code> may need to be updated.</samp>

---

<div align="center"><samp><b>Project Files</b></samp></div>

```text
.github/workflows/leetcode.yml
```

<samp>GitHub Actions workflow responsible for scheduled and manual synchronization.</samp>

```text
scripts/leetcode_sync.py
```

<samp>Python synchronization logic that retrieves solved problems and writes solutions to the repository.</samp>

---

<div align="center"><samp><b>Disclaimer</b></samp></div>

<samp>This project is an independent community tool and is not affiliated with or endorsed by LeetCode.</samp>

<samp>Because it relies on authenticated LeetCode endpoints, functionality may change if LeetCode modifies its website or API.</samp>

---

<div align="center"><samp><b>License</b></samp></div>

<samp>You are free to use, modify, and distribute this setup for personal or educational purposes.</samp>
