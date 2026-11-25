# Mapping a company's own cash-flow spreadsheet into the template

Use this when the user has their own cash-flow file (Excel or CSV) and wants a 12-month
cash forecast from it. Your job is the mapping. The numbers are the engine's job: never
calculate, estimate or adjust a cash figure yourself.

## Steps

1. Run `template` so you and the user can see the target format (`--example hotel` if
   the user works in hospitality, otherwise the default manufacturer). Read the user's
   file.
2. Propose a mapping table and show it to the user before writing anything:

   | Their row | line_id | section | treatment | Why |
   |---|---|---|---|---|

   Lines are defined in the `history` sheet (line_id, label, section, treatment, then
   the months). Every known line needs its future amounts in `known_events`.

3. Wait for the user to confirm or correct the mapping. Do not continue on your own
   judgement; a wrong treatment changes the forecast.
4. Write the filled template (four tables) from their data, copying amounts exactly as
   they appear. Start from an empty template (`template --empty`) so no rows of the
   example company are left behind.
5. Run `validate`. Show every problem and warning to the user. Also show the known
   amounts and scenarios it lists per line and ask whether all of them still apply;
   delete the rows that do not.
6. When validation passes and the user agrees, run `run`. It runs the base case and
   every scenario in one go.
7. Report as described in SKILL.md.

## How to choose section and treatment

- **section**: operating (day-to-day business), investing (capex, acquisitions,
  disposals), financing (debt, equity, dividends, interest on debt if the user books it
  there). At least one line per section is required; if the user has none for a section,
  add one line and leave it empty.
- **forecast**: recurring flows with at least 24 months of monthly history and no fixed
  schedule, such as customer receipts or supplier payments.
- **known**: flows fixed by contract or already decided, such as rent, tax instalments,
  loan repayments, approved capex. The user supplies the amounts. A line the business
  never had before is also known: a model has no history to learn from.
- A line can mix both. If the user knows the next month or two exactly and wants the
  model after that (salaries are typical), make the line `forecast` and add the known
  months to `known_events` with effect `replace`. Use effect `on top` only for something
  new that the history does not contain.

## Rules that protect the result

- Skip subtotal and formula rows (EBITDA, "total operating cash flow", cash period end).
  The engine derives every total. Mapping a subtotal as a line counts it twice.
- Skip non-cash rows (depreciation, provisions, accruals) and balance-sheet balances.
  Only cash movements belong in the template.
- Money in is positive, money out is negative. If the user's file shows payments as
  positive numbers, ask before flipping the sign.
- A known amount with effect `on top` is added to the model's figure, so the same kind
  of item must not also be inside that line's history. Ask the user which effect they
  mean; never choose `on top` yourself.
- If the file is an indirect cash-flow statement (it starts from profit or EBITDA and
  adjusts for working capital), say so. This template is a direct statement of receipts
  and payments, and a line-by-line mapping from an indirect statement needs the user's
  decisions, not yours.
- One currency per template. Do not convert currencies.
- If the user gives known amounts for the first months of a forecast line, the later
  months start from the level of the last one. A one-off (a bonus, a back-payment) must
  therefore go on its own known line, not into such a row.
- An amount the user learned about after `origin_month` is left out by design. Say so,
  and offer to add it as a scenario if they want to see its effect.
- Ask whether the user has a minimum cash balance; if so, set `minimum_cash`.
- The history sheet is the user's past cash-flow statement: an `opening_cash` row, one
  row per line, a `closing_cash` row. Copy their balances; never calculate a balance
  yourself. If validation says the history does not tie, show the user the months and
  amounts and ask what is missing (often FX effect on cash or an unmapped row). Do not
  plug the difference.
- Scenarios are percentages of a line (`-5` = 5% lower receipts, `5` on a payment line =
  5% higher payments). Ask the user for the percentages; do not invent them. Use `amount`
  for a fixed monthly sum such as a contingency.
- Set `data_kind` to what the user tells you (synthetic, actual, unspecified).

## What to say about limits

- ETS needs 24 months of history; SARIMA needs 36.
- There is no uncertainty range for closing cash.
- `compare` shows how much the result depends on the model. It is not an accuracy test.
