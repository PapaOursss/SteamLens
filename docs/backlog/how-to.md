# How to use the backlog (humans and agents)

**A ticket** = one file, `tickets/steamlens-T-NN-<slug>.md` (a few words of the title): a `# T-NN · Title` heading, then six fixed lines, then the details:

    # T-NN · Short title that says what to achieve
    - **Type**: task
    - **Priority**: 🟡 normal
    - **Status**: todo
    - **Opened**: YYYY-MM-DD
    - **Effort**: S · **Owner**: … · **Due**: —
    - **Origin**: where it comes from · audit `docs/_archive/<folder>/README.md` l. 10-20

    Why, what to do (as a `- [ ]` checklist when there are several steps), where to look.

- **ID** `T-NN`: stable, never reused, quoted as is in commits and branches.
  The next free one is in [README.md](README.md).
- **Type**, one of: `bug` (something is broken); `improvement` (it works, it could work
  better); `idea` (nothing exists yet, to be explored); `task` (work that is neither: a release,
  a decision, a check).
- **Status**, one of: `todo`; `in progress — branch <name>, since YYYY-MM-DD`;
  `blocked — waiting for <who or what>`; `to verify — <where>`.
- **Priority**, one of:
  🔴 critical (now), 🟠 important (before the north star), 🟡 normal, ⚪ background
  (long-running work, debt, ideas still to be explored).
- **Effort**: XS (under an hour), S (half a day), M (one or two days), L (more).
- **Owner**: `—` (free, anyone may take it), a member's GitHub login (`@login`) or first name
  (the ticket is reserved for them), `Claude` (an agent's job), or `contributor — #NN` (kept for
  an outside contributor). An agent only works on a free ticket or one owned by the account it
  works for (`gh api user --jq .login`): it skips the others and, asked for one, says who owns
  it instead of doing it. **Each member writes only their own login**: taking a free ticket, or
  turning their own first name into their login; never someone else's (only the owner hands a
  ticket over).
- **Releases**: one file per planned release in [releases/](releases/), listing its open tickets;
  numbers are planned, not promised.
- **Closing a ticket**: delete its file, take its line out of its release, and add a line at the
  top of [done.md](done.md): `- **YYYY-MM-DD** · T-NN · Title — what was done (branch) · opened YYYY-MM-DD`.
- **Details in archived audits**: when a ticket quotes lines of `docs/_archive/`, the original
  finding is there in full; it is old, check it against the current code.
- **Locations quoted are hints, not addresses.**
- Overview: `grep -rE '^(# T-|- \*\*Status)' docs/backlog/tickets/`.

An audit writes its dated report here (`audit-<topic>-YYYY-MM-DD.md`) while it runs, copies its
open findings into tickets, then moves to `docs/_archive/YYYY-MM-DD-topic/`. Archives can be
read but are old, to be checked against the code, and are never edited.
