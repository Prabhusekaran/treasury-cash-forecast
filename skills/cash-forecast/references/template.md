# The template and the result workbook

## The template: four tables

Sheets in one `.xlsx`, or four `.csv` files in one folder. Money in is positive, money
out is negative. One currency per file. Months are written `YYYY-MM`.

| Table | Columns |
|---|---|
| `inputs` | `key`, `value`: `currency`, `origin_month` (the last month of actuals), `data_kind` (`synthetic`, `actual`, `unspecified`); optional `model` and `minimum_cash` |
| `history` | The past cash-flow statement and the definition of every line: an `opening_cash` row, one row per line, a `closing_cash` row. Columns: `line_id`, `label`, `section` (`operating` / `investing` / `financing`), `treatment` (`forecast` / `known`), then one column per month |
| `known_events` | `line_id`, `month`, `amount`, optional `effect` (`replace` / `on top`), `known_from`, `note` |
| `scenarios` | `scenario`, `line_id`, `percent` or `amount`, optional `from_month`, `to_month`, `note` |

**Treatment.** `forecast`: a statistical model projects the line from its monthly
history. `known`: the user supplies the future amounts in `known_events`; nothing is
predicted, and a month without an amount is zero.

**Opening and closing cash.** The history carries the opening and closing cash of every
month. The check confirms each month ties (opening cash + all lines = closing cash, and
closing cash = next opening cash). The closing cash of `origin_month` becomes the
opening cash of the forecast.

**Known amounts on a forecast line.** `replace` (or empty) uses the user's amount instead
of the model's figure for that month. `on top` adds it to the model's figure, for
something new that the history does not contain. When the user's amounts cover the first
months of the forecast, the later months keep the model's pattern but start from the
level of the last amount.

**Scenarios.** `percent` changes the size of a line: `-4` on receipts means 4% lower
receipts, `4` on a payment line means 4% higher payments. It is taken from the line's
base-case figure for that month. In the Excel template the cell shows `-4` as -4%; the
cell still holds -4. A cell that Excel itself formats as a percentage (it holds 0.08 and
shows 8%) is read as 8, the figure on the screen. A plain number between -1 and 1, such as
`0.08`, is read as 0.08% and raises a warning. `amount` is a fixed sum per month. Empty `from_month`
and `to_month` mean all 12 months. A payment that arrives late is two `amount` rows:
minus the amount in the month it was due, plus the amount in the month it arrives. The
base case contains no scenario.

**`known_from`** is the month the user learned about an item. An amount learned after
`origin_month` is left out of every scenario and listed on the Summary sheet, because a
forecast as of a date uses only what was known then.

**`minimum_cash`** is the balance the user does not want to fall below. The result lists
the months below it and shows them in red.

**The example sheets** `known_events` and `scenarios` start with a red NOTE row. The
example's rows must be deleted before the user enters their own.

## The result: `cash_forecast.xlsx`

- **Summary**: the forecast identity (version, date and time of the run, model and its
  settings, input name, input fingerprint, libraries); closing cash by month for the base
  case and every scenario; the lowest point; months below zero or below the minimum cash;
  what was left out and why; what each scenario changes, with the row of the `scenarios`
  sheet behind each change.
- **How this is built**: one page in plain language for a reader who is not technical.
- **One sheet per scenario**: a cash-flow statement from opening cash to closing cash for
  the last 12 actual months and the 12 forecast months. Shading shows the source of each
  forecast cell: none = model, green = known amount, orange = model plus an amount on
  top, purple = changed by the scenario, grey = actuals.
- **Where numbers come from**: every forecast figure split into the model part, the known
  part and the scenario part, with a "Source row" column naming the rows of the input
  that produced it. The numbers are the row numbers Excel shows on that sheet of the
  template.
- **Notes**: identity again, what was left out, warnings, limits.

Every month, in every scenario:

```
operating + investing + financing = net cash flow
opening cash + net cash flow      = closing cash
closing cash (month N)            = opening cash (month N+1)
```

If anything does not tie, the run stops and nothing is written.

**The input fingerprint** is the first 12 characters of a SHA-256 checksum of the
headings and cells of the input tables. The same content gives the same fingerprint,
however often the file is saved; any changed cell gives a different one.

An `audit/<scenario>/` folder next to the workbook holds `forecast.md`, `cash_bridge.csv`,
`lines.csv` and `forecast.json` for each scenario.

## Models

| Model | Needs | Notes |
|---|---|---|
| `ets` (default) | 24 months | Holt-Winters, additive trend and seasonality |
| `sarima` | 36 months | Fixed (1,1,0)x(0,1,1,12); most reliable with five or more years |
| `baseline`, `seasonal_drift` | 24 months | Simple, transparent |
| `seasonal_naive` | 12 months | Same month last year |
| `previous_month` | 1 month | Sanity check, not a forecast |
| `chronos_2` (optional) | 1 month | Only if the user installed `chronos-forecasting` and the model themselves |

The four simple models give identical figures on every machine. ETS and SARIMA are fitted
numerically, so another machine or library version can differ by small amounts.

## Limits

- Monthly, 12 months ahead, one currency, one entity.
- No uncertainty range for closing cash.
- A forecast from thin or unrepresentative history will be poor, whatever the model.
- `data_kind` is the user's declaration; it is not verified.
- No claim is made about accuracy on any real company.
