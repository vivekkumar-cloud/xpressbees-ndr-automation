<<<<<<< HEAD
# Xpressbees NDR Automation 🚀

Automates the NDR (Non-Delivery Report) Re-Attempt push on the Xpressbees shipping panel.

## What it does
1. Logs into `ship.xpressbees.com`
2. Navigates to the NDR section
3. Sets per-page to 500 (max)
4. Selects all Action Required shipments
5. Clicks Bulk NDR → Re-Attempt
6. Enters remark "Reattempt" and submits

## Setup

```bash
pip install -r requirements.txt
```

Make sure **Google Chrome** is installed on your machine.

## Run

```bash
python ndr_automation.py
```

## Logs
All activity is logged to `ndr_automation.log` in the same folder.
=======
# xpressbees-ndr-automation
Automated NDR re-attempt pusher for Xpressbees panel
>>>>>>> e96c5d42322e734b30d3bf8c6ad660881b003b9d
