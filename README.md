# Project Status Dashboard — Setup Guide

## What this system does

Every time you work on a project with Claude Code or Claude Projects, Claude
updates a `status.json` file in the project folder. A sync script collects all
those files and writes a single `dashboard-data.json`. The HTML dashboard reads
that file and displays everything in one clean view for your manager.

---

## Folder structure

```
project-dashboard/              ← this repo
├── docs/
│   ├── index.html              ← the manager-facing dashboard
│   ├── dashboard-data.json     ← auto-generated, do not edit
│   └── dashboard-history.json  ← auto-generated
├── scripts/
│   ├── sync.py                 ← aggregates all status.json files
│   └── config.json             ← list of your project directories
├── templates/
│   ├── PROJECT_STATUS.md       ← template for each project
│   ├── status.json             ← template for each project
│   ├── CLAUDE_CODE_INSTRUCTIONS.md   ← paste into CLAUDE.md
│   └── CLAUDE_PROJECTS_PROMPT.md    ← paste into Claude Projects
└── .github/
    └── workflows/
        └── sync-dashboard.yml  ← auto-syncs on every push
```

Each of your actual projects lives in its own folder (or repo):

```
projects/
├── analytics-pipeline/
│   ├── status.json             ← Claude updates this
│   └── PROJECT_STATUS.md       ← Claude updates this
├── user-onboarding/
│   ├── status.json
│   └── PROJECT_STATUS.md
└── customer-portal/
    ├── status.json
    └── PROJECT_STATUS.md
```

---

## One-time setup (15 minutes)

### Step 1: Create the dashboard repo

1. Create a new GitHub repository: `project-dashboard`
2. Copy all files from this package into it
3. Commit and push

### Step 2: Enable GitHub Pages

1. Go to repo Settings → Pages
2. Source: Deploy from branch `main`, folder `/docs`
3. Save. GitHub gives you a URL like `https://yourusername.github.io/project-dashboard/`
4. Share that URL with your manager

### Step 3: Configure your projects

Edit `scripts/config.json`:
```json
{
  "owner": "Your Name",
  "project_dirs": [
    "/path/to/your/project-1",
    "/path/to/your/project-2"
  ]
}
```

Or, if all projects are sub-folders of one parent:
```json
{
  "owner": "Your Name",
  "project_dirs": ["../projects"]
}
```

### Step 4: Add status files to each project

For each project, copy the templates:
```bash
cp templates/status.json /path/to/your/project/status.json
cp templates/PROJECT_STATUS.md /path/to/your/project/PROJECT_STATUS.md
```

Edit each file to fill in the project name, owner, due date, and links.

### Step 5: Set up Claude Code

For each project that uses Claude Code, add this to your `CLAUDE.md` file
(create it in the project root if it doesn't exist):

```
## Status file maintenance
(paste the contents of templates/CLAUDE_CODE_INSTRUCTIONS.md here)
```

### Step 6: Set up Claude Projects

For each Claude Project, go to Project Instructions and paste the contents of
`templates/CLAUDE_PROJECTS_PROMPT.md`, filling in the project-specific details.

### Step 7: Test it

```bash
python scripts/sync.py
```

Open `docs/index.html` in your browser. You should see your projects.

Commit and push — GitHub Pages will serve the live version.

---

## Daily workflow

### When you finish a Claude Code session
Claude automatically updates `status.json` and `PROJECT_STATUS.md` at the end
of the session (because of the CLAUDE.md instructions). Just push your changes:

```bash
git add status.json PROJECT_STATUS.md
git commit -m "update: project status"
git push
```

The GitHub Action runs automatically and updates the dashboard within ~1 minute.

### When you finish a Claude Projects session
1. Claude produces a STATUS UPDATE block at the end of the session
2. Copy the block
3. Open `status.json` in your project folder
4. Update the relevant fields manually (takes 2 minutes)
5. Push

Alternatively, paste the update block to Claude Code and say:
"Update status.json with this update block."

### Running the sync manually
```bash
python scripts/sync.py
```

---

## Giving your manager access

Just share the GitHub Pages URL:
`https://yourusername.github.io/project-dashboard/`

The dashboard auto-refreshes the data every time the page is opened.
No login required. No accounts needed.

---

## Generating a weekly summary

1. Open the dashboard
2. Click "Weekly summary" — it copies a prompt to your clipboard
3. Paste it into Claude
4. Claude writes a professional email summary you can send your manager

---

## Customizing

### Change the dashboard owner name
Edit `scripts/config.json` → `owner`

### Add a new project
1. Copy `templates/status.json` and `templates/PROJECT_STATUS.md` to the project
2. Add the project path to `scripts/config.json`
3. Add `CLAUDE_CODE_INSTRUCTIONS.md` to the project's `CLAUDE.md`
4. Run `python scripts/sync.py` to verify

### Change sync frequency
Edit `.github/workflows/sync-dashboard.yml` → the `cron` value.
Default is every 4 hours. `0 8 * * 1-5` = weekdays at 8am.

---

## Troubleshooting

**Dashboard shows "Could not load dashboard data"**
→ Run `python scripts/sync.py` first. Make sure `docs/dashboard-data.json` exists.

**A project is not appearing**
→ Check that the project path is in `config.json` and that `status.json` exists.

**Status is stale**
→ Check that Claude Code is reading `CLAUDE.md` — verify the file is in the project root.
→ For Claude Projects, remind Claude with: "Please update the status block."

**GitHub Pages not updating**
→ Check the Actions tab in your repo for errors. Make sure the workflow has
`contents: write` permission.
