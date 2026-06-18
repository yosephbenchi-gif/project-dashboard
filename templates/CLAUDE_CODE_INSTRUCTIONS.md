# Claude Code Instructions: Status File Maintenance

## When to update
At the end of every coding session where meaningful work occurred, update both
`PROJECT_STATUS.md` and `status.json` in the project root.

## Rules for updating
- Do NOT exaggerate progress. Only mark something complete when it is fully working.
- Do NOT mark blockers as resolved until the block is actually gone.
- Use plain language in the manager-facing summary. No jargon, no abbreviations.
- progress_percent should reflect honest completion, not effort spent.
- Append to update history, never overwrite it.

## What to include in each update
1. What changed this session (specific, factual)
2. What was completed (working code, shipped features, finished tasks)
3. What remains to be done
4. Any new blockers or risks that appeared
5. Any blockers or risks that were resolved

## Update procedure
After every meaningful session, run this mentally:

1. Read the current `status.json`
2. Update these fields:
   - `last_updated` → current ISO timestamp
   - `progress_percent` → honest estimate
   - `status` → one of: "Not Started", "In Progress", "Waiting", "Blocked", "Completed"
   - `current_focus` → what is actively happening
   - `completed_work` → prepend new items with today's date
   - `next_steps` → reorder based on current state
   - `blockers` → add new ones, remove resolved ones
   - `is_overdue` → compare due_date to today
   - `summary_for_manager` → rewrite in plain language
3. Append a new entry to `recent_updates` with timestamp and summary
4. Mirror all changes to `PROJECT_STATUS.md`

## Status definitions
- **Not Started**: No work has begun
- **In Progress**: Actively being worked on
- **Waiting**: Waiting on something external (review, approval, dependency)
- **Blocked**: Cannot proceed — specific blocker must be named
- **Completed**: All work done and delivered/shipped

## Do not
- Do not delete update history entries
- Do not use vague language like "some progress made"
- Do not mark as Completed if anything material is still pending
- Do not skip this update step even if the session was short
