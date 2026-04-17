# Email-validator-V2

Bulk email validator for terminal. Built to clean up mailing lists before a campaign goes out — catches dead addresses, disabled inboxes, disposable emails, before they become bounces.

Works in two modes. Free mode needs no account or key. API key mode unlocks provider-specific checks for Gmail, Outlook, Microsoft.

```
  +══════════════════════════════════════════════════════════+
  |   ███████╗███╗   ███╗ █████╗ ██╗██╗                    |
  |   ██╔════╝████╗ ████║██╔══██╗██║██║                    |
  |   █████╗  ██╔████╔██║███████║██║██║                    |
  |   ██╔══╝  ██║╚██╔╝██║██╔══██║██║██║                   |
  |   ███████╗██║ ╚═╝ ██║██║  ██║██║███████╗              |
  |   ╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚══════╝             |
  |                                                          |
  |  Email Validator  powered by ychecker.com                 |
  +══════════════════════════════════════════════════════════+

  Mode: Free   (4 to change)

    1  Single email check
    2  Bulk check — type emails in
    3  Bulk check — load from file
    4  Settings  (API key, mode)
    q  Quit
```

---

## What it does

Checks whether an email address exists, is disabled, is a disposable throwaway, or simply does not exist at the provider level. Not a syntax checker — it queries the actual mail provider.

Results show in a colour-coded table. Green is deliverable. Red is dead. Yellow is uncertain. Everything exports to CSV.

---

## Modes

**Free mode** — no account needed. 100 checks per day per IP. This is the default when you run the script with no key set.

**API key mode** — full access via sonjj.com. Routes each email to the right endpoint automatically. Gmail addresses go through the Gmail check. Outlook goes through Microsoft. Everything else goes through the general check. Credit-based. Get a key at [my.sonjj.com](https://my.sonjj.com).

| Endpoint | Cost |
|---|---|
| General | 2 credits |
| Gmail | 0.5 credits |
| Microsoft | 0.5 credits |
| Disposable score only | 0.05 credits |

The API key is saved locally once entered. It loads on every run after that with no extra steps.

---

## Free access — how it works

No account. No sign up. Just run the script.

It uses the same relay that ychecker.com's own web frontend uses. Each check goes through a two-step token flow behind the scenes. You do not need to know or interact with any of that — it is handled automatically.

The limit is 100 checks per day per IP. It resets every 24 hours. The remaining count shows at the bottom of every bulk run.

Workers are capped at 5 in free mode to stay clean against the rate limit.

---

## Install

```bash
git clone https://github.com/Krainium/Email-validator-V2.git
cd Email-validator-v2
pip3 install requests rich or pip3 install requirements.txt
```

Python 3.10 or higher.

---

## Run

```bash
python3 emailchk.py
```

The menu opens straight away. No prompts before it.

---

## CLI — skip the menu

Check one address:
```bash
python3 emailchk.py someone@gmail.com
```

Check a list from a file:
```bash
python3 emailchk.py --file emails.txt --export results.csv
```

Force free mode even if a key is saved:
```bash
python3 emailchk.py --free --file emails.txt
```

Pass a key directly without saving it:
```bash
python3 emailchk.py --key YOUR_KEY --file emails.txt
```

Or set it as an environment variable:
```bash
SONJJ_API_KEY=YOUR_KEY python3 emailchk.py --file emails.txt
```

---

## Flags

| Flag | Short | What it does |
|---|---|---|
| `--file PATH` | `-f` | Load emails from a file, one per line |
| `--export PATH` | `-e` | Save results to a CSV file |
| `--key KEY` | | Use this API key for the session |
| `--free` | | Force free mode |
| `--mode MODE` | `-m` | Check mode: `auto` `general` `gmail` `microsoft` `disposable` |
| `--workers N` | `-w` | Parallel workers (default 5, max 20 for API key, max 5 for free) |

---

## Bulk check output -  DEMO

```
  [*] 5 email(s)  —  3 worker(s)  —  free mode (98 requests remaining today)

  Last: thomassmark51@gmail.com ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 5/5 0:00:01


  ──────────────────────────────────────────────────────────────
  Results  —  5 checked
  ──────────────────────────────────────────────────────────────

Email                    Type   Status     Disposable
─────────────────────────────────────────────────────
baronn2929@outlook.com   free   NotExist   No
sgsuuq8992@gmail.com     free   Disable    No
mamata920@aol.com        free   Ok         No
chloegriter@gmail.com    free   Ok         No
bammygerrado@gmail.com   free   Ok         No

  Valid/OK     4
  Invalid      1
  Disposable   0
  Errors       0

  [+] Results saved → results.csv

  Rate limit: used 5  —  93/100 remaining today
```

---

## Settings

Option 4 in the menu handles everything to do with the API key. Set it, clear it, switch between free mode. The key saves to `~/.emailchkrc`. Delete that file to reset.

---

## Status values

| Status | Meaning |
|---|---|
| Ok / Enable | Address exists, inbox is active |
| Disable | Address exists but inbox is disabled |
| NotExist | No record of this address at the provider |
| Not Found | Could not be verified |
| Unknown | Inconclusive result |

---

## Notes

Free mode sends two requests per check. One to get a signed token from ychecker.com, one to resolve it at the API. Both count toward the 100 per day limit. Running multiple workers in free mode is supported but keep it at 3–5 to stay clean.

API key mode has no hard rate limit — it is credit-based. Workers can go up to 20 without issues.

The config file at `~/.emailchkrc` stores your key in plain JSON. Do not commit it.
