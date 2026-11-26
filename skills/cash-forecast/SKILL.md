---
name: cash-forecast
description: >
  Builds a 12-month monthly direct cash-flow forecast for a company from a filled Excel
  or CSV template, with a base case and what-if scenarios, and returns one reconciled
  Excel workbook. Use this skill when the user asks for a "cash forecast", "cash flow
  forecast", "12-month cash forecast", "liquidity forecast", "Treasury Cash Forecast",
  asks to "run the forecast", "check this cash forecast template", "create the cash
  forecast template", "create the hotel example" or "the manufacturer example", asks
  what happens to cash in a downside or other scenario, asks when cash falls below a
  minimum, asks to "compare the models", or asks where a figure in cash_forecast.xlsx
  comes from.
---

# Treasury Cash Forecast

A tested forecasting engine in `scripts/` does all the arithmetic. Your job is to pick
the command, pass the user's file to it, and explain the result in plain language.

**Never calculate, estimate, round or adjust a cash figure yourself.** Every number you
state must be copied from the command's output, digit for digit. If a number the user
wants is not in the output, say so; do not work it out.

That includes small sums that look harmless. Do not subtract, add, average or take a
percentage of figures from the output, and do not give an approximate version of one.
Write "lowest closing cash EUR 180,851.31, minimum cash EUR 150,000.00", not "about 31k
above the minimum": the gap is a number the engine did not produce. Totals and effects
that the output already contains (for example `total_effect_on_final_closing_cash` or a
line's `known_total`) may be quoted, because the engine calculated them.

## The four commands

The script is `scripts/cash_forecast.py` inside this skill's folder, the folder that holds
this SKILL.md. The commands below show it relative to that folder. Run it with its full
path, or from that folder; do not copy the script elsewhere.

```
python3 scripts/cash_forecast.py template --output-dir DIR [--example hotel] [--empty] [--format csv]
python3 scripts/cash_forecast.py validate INPUT
python3 scripts/cash_forecast.py run INPUT [--model MODEL] [--scenario NAME] [--base-only]
python3 scripts/cash_forecast.py compare INPUT [--model MODEL] [--scenario NAME]
```

`INPUT` is the filled template: one `.xlsx` workbook, or a folder with `inputs.csv`,
`history.csv`, `known_events.csv` and `scenarios.csv`. Each command prints one JSON
document. `"success": false` means nothing was forecast; show the user the `error` and
every entry of `problems` as written.

**The user's file name.** A file the user attaches is often stored under a random prefix,
for example `0bb90bb2-cash_forecast_example_hotel.xlsx`. Pass that path as it is; do not
copy or move the upload somewhere else first. The
script copies such an upload into `./cash_forecast_input/` under the user's own file name
and works on the copy, so the result workbook names the file the way the user knows it;
the output then carries an `input_note` saying so. When you mention the file to the user,
use their name for it, without the prefix. If the stored name has some other added prefix
or suffix the script did not remove, make that copy yourself before running.

| Command | What it does |
|---|---|
| `template` | Writes the template. Default: filled with a made-up manufacturer. `--example hotel`: a made-up 110-room hotel with seasonal cash. `--empty`: headings only. |
| `validate` | Checks a filled template. Forecasts nothing. Lists every problem and warning, and the known amounts and scenarios it found per line. |
| `run` | Runs the base case and every scenario, reconciles every month to the cent, writes `cash_forecast.xlsx` plus an audit folder. `--scenario` (repeatable) limits the scenarios; `--base-only` runs none. |
| `compare` | Runs several models on the same input and shows how far the results differ. Writes no files. It is not an accuracy test. |

Models: `ets` (default), `sarima`, `baseline`, `seasonal_drift`, `seasonal_naive`,
`previous_month`. `chronos_2` works only if the user has installed it themselves.

## Before the first command

The engine needs two Python libraries. Check once per session:

```
python3 -c "import statsmodels, openpyxl"
```

If that fails, install them, then continue:

```
pip install "statsmodels>=0.14,<1" "openpyxl>=3.1,<4"
```

If pip refuses because the environment is managed, add `--break-system-packages`. If the
install is not possible, tell the user plainly that the forecast cannot run here and why.
Do not switch to another method, model or file format to get around it.

## How to handle each request

**The user wants to see how it works, or asks for an example.** Run `template` with the
example they named (hotel if they work in hospitality or ask for the hotel; otherwise the
manufacturer). Give them the file. If they also asked to run it, continue with the next
case using that file.

**The user gives a filled template and wants the forecast.**

1. Run `validate` on their file.
2. If it fails, show every problem and stop. Offer to fix the file only if they ask.
3. If it passes, run `run` on the same file straight away. The user asked for the
   forecast, so do not stop to ask for confirmation. The one exception: if a warning says
   the history does not tie from opening to closing cash, show it and ask whether to go
   on. Every other warning is reported with the result (point 5 of the report).
4. Report the result as described below and give the user `cash_forecast.xlsx` (the
   `main_file` in the output).

**The user changed the file and asks to run it again.** Run `validate` and `run` on the
new file exactly as above. Say what changed in the result compared with the earlier run,
using only figures from the two outputs. Mention that the input fingerprint changed.

**The user asks how much the result depends on the model, or which model to trust.** Run
`compare`. Report final and lowest closing cash per model and the spread. Say it shows
sensitivity, not accuracy.

**The user has their own cash-flow spreadsheet, not the template.** Follow
`references/mapping.md`. Show the proposed mapping and wait for the user to confirm it
before writing anything.

**The user asks what a column or sheet of the template means.** Use
`references/template.md`.

**The user asks where a figure comes from.** Do not reconstruct it. Point them to the
sheet "Where numbers come from" in `cash_forecast.xlsx`: its last column, "Source row",
names the rows of their own input behind every forecast figure (for example
`history row 4; scenarios row 4`). You may read that sheet and quote the row for them.

**The user asks which run or which input a workbook belongs to.** Quote the
`forecast_identity` from the output, or the "Forecast identity" block at the top of the
Summary sheet.

## How to report a run

Keep it short and in this order. Use the currency from the output and copy every amount
exactly as it appears there.

Amounts in the output are signed: a minus sign means cash going out or a figure getting
smaller. Keep the sign and let it carry the direction. Write "effect on final closing
cash: EUR -45,000.00". Do not put a direction word around a signed amount ("EUR -45,000.00
lower", "costs EUR -60,000.00 more"): that states the direction twice and reads as the
opposite. To say what a scenario does in words, use the note the user wrote for it.

1. Opening cash, and the month it is the closing balance of.
2. Base case: lowest closing cash and its month, final closing cash, and any months below
   zero or below the minimum cash.
3. Each scenario in one or two sentences: what it changes (from the user's notes), months
   below the minimum or below zero, final closing cash.
4. Anything in `left_out_inputs`: always tell the user what was left out and why. An
   amount the user learned about after the forecast date is left out on purpose: a
   forecast as of a date uses only what was known then. Never suggest changing
   `known_from`, the date or `origin_month` to bring it in. If the user wants to see its
   effect, offer to add it as a scenario.
5. Any `warnings` and `model_notes`. One warning does not wait for point 5: if a warning
   says a percent "is read as" less than 1%, a scenario is probably a hundred times weaker
   than the user meant (0.08 typed where 8 was meant). Say so at the very top of the
   report, before point 1, and name the rows. The check also returns a reminder
   (`check_with_the_user`) to delete rows left over from the example. That reminder is
   for a user who has put their own data into the template. When `data_kind` is
   `synthetic`, the file is an example and its rows are the data: do not raise it.
6. One line: `Input fingerprint: <value>`, from `forecast_identity`.
7. Give the user the workbook file. Say it has a Summary, a plain-language page on how
   the forecast is built, one cash-flow statement per scenario, and a sheet that traces
   every figure to the row of their input.

Do not paste the JSON. Do not list all twelve months unless the user asks.

If you add suggestions for what to do next, keep them to these: fix a problem the check
reported, confirm a warning, add or change a scenario, compare the models, or trace a
figure. Do not suggest edits to the user's history or known amounts on your own judgement.

## Rules

- Write results in the working directory. Do not write into the folder the user's file
  came from. `run` already saves to `./cash_forecast_output/<input name>-<fingerprint>/`.
- Do not change the user's file. If they ask you to edit a scenario or an amount, make
  the edit in a copy, tell them exactly which cells changed, and give them the copy.
- A percentage in the `scenarios` sheet is written as the number of percent: 8% lower is
  `-8`, never `-0.08`. In the Excel template the cell shows it as -8%. When you write or
  change such a cell, write the number and leave the cell's format as it is.
- Do not choose a different model than the user or the template asked for.
- The example companies are invented. Never present their figures as real, and never
  claim the forecast is accurate for a real company.
- State the limits when they matter: monthly, 12 months ahead, one currency, one entity,
  no uncertainty range for closing cash.
