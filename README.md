# Treasury Cash Forecast

A 12-month monthly cash-flow forecast for corporate treasury, packaged as a plugin for AI
assistants.

It uses the direct method: receipts and payments by type, from opening cash to closing
cash. You fill one Excel template with your past cash-flow statement, the future payments
you already know, and your what-if scenarios. The assistant checks the file, runs the
forecast and returns one Excel workbook: a summary comparing the base case with every
scenario, and a cash-flow statement per scenario showing your last 12 actual months
followed by the 12 forecast months, tied to the cent.

**The language model never calculates the forecast.** It picks the step and explains the
result. Every figure in the workbook comes from a tested forecasting engine that ships
inside the plugin.

## Where it runs

| Assistant | Status | How to get it |
|---|---|---|
| Claude (chat, Cowork, Claude Code) | Tested | See "Install in Claude" below |
| Hermes Agent | Tested, listed in the Hermes Marketplace | `hermes plugins install treasury-cash-forecast` ([its own repository](https://github.com/Prabhusekaran/hermes-treasury-cash-forecast)) |
| ChatGPT and Codex | Built to the documented plugin format, not yet run there, not in the directory | See "ChatGPT and Codex" below |
| DeepSeek Harness | Built to the documented skill format, not yet run there | See "DeepSeek Harness" below |

The forecasting engine, the two example companies and the result workbook are the same
everywhere.

## Install in Claude

In the Claude app:

1. Open **Customize**, then **Plugins**.
2. Choose **Add**, then **Add marketplace**.
3. Paste `https://github.com/Prabhusekaran/treasury-cash-forecast` and confirm.
4. Install **Treasury Cash Forecast** from the list.
5. Start a new chat. A plugin loads when a chat starts.

In Claude Code:

```
/plugin install treasury-cash-forecast --marketplace Prabhusekaran/treasury-cash-forecast
```

## ChatGPT and Codex

The package follows the layout OpenAI documents for a skills-only plugin, with its listing
details in `.codex-plugin/plugin.json`. It is not in the ChatGPT directory: on
25 November 2026 OpenAI's submission portal was not accepting skills-only plugins. It has
not been run in ChatGPT.

To try the skill in Codex on your own computer, copy it into your skills folder:

```
git clone https://github.com/Prabhusekaran/treasury-cash-forecast
mkdir -p ~/.agents/skills
cp -r treasury-cash-forecast/skills/cash-forecast ~/.agents/skills/
pip install "statsmodels>=0.14,<1" "openpyxl>=3.1,<4"
```

## DeepSeek Harness

DeepSeek Harness loads skills from `~/.agents/skills`. The same four commands as above
install it; then restart `dsh`. It has not been run in DeepSeek Harness yet.

## Use it

Ask in plain words. For example:

- "Create the hotel example for the cash forecast." You get a filled template for an
  invented hotel, so you can see what the forecast needs.
- Attach a filled template and say "Check this cash forecast template and run the
  forecast." Any problems are listed first; then you get `cash_forecast.xlsx`.
- Change a scenario in your file, attach it again and say "Run it again."
- "Compare the models on the base case." This shows how far the result depends on the
  forecasting model.
- "Where does this figure come from?" You are pointed to the sheet that names the row of
  your input behind every forecast figure.

## What you get

- **Summary**: closing cash by month for the base case and every scenario, the lowest
  point, any month below zero or below your minimum cash, what was left out and why.
- **How this is built**: one page in plain language for a reader who is not technical.
- **One cash-flow statement per scenario**, actuals then forecast, shaded by source.
- **Where numbers come from**: every forecast figure with the rows of your input that
  produced it, for example `history row 4; scenarios row 4`.
- **Forecast identity**: the version, the time of the run, the model, and a fingerprint
  of your input, so two people can confirm they are looking at the same forecast.

Every month, in every scenario, opening cash plus net cash flow equals closing cash. If
anything does not tie, nothing is written.

## What is inside

One skill, `cash-forecast`, and the engine it runs: four actions (template, validate,
run, compare), six built-in statistical models (ETS by default), and two invented example
companies, a manufacturer and a hotel with seasonal cash.

## Data

The plugin sends nothing anywhere. It reads only the file you give the assistant and
writes the result in the assistant's working folder. It makes no network calls, needs no
account and stores no credentials. See [PRIVACY.md](PRIVACY.md).

It needs two open-source Python libraries, `statsmodels` and `openpyxl`. If they are not
already present where the assistant runs code, the assistant installs them from the
Python Package Index with `pip install "statsmodels>=0.14,<1" "openpyxl>=3.1,<4"`.
Nothing else is downloaded.

## Limits

- Monthly, 12 months ahead, one currency, one entity.
- No uncertainty range for closing cash.
- The example companies are invented. No claim is made about accuracy on a real company.

## A person decides

This plugin is a forecasting aid, not financial advice. It moves no money and takes no
action on any account. A forecast continues the past and adds what you told it; it can be
wrong. A qualified person must review the result before any decision is based on it.

## If something does not work

- **"Python cannot load statsmodels" or "openpyxl".** The two libraries are missing where
  the assistant runs code. Ask the assistant to install them and run the step again. If
  code execution is switched off in your assistant, the plugin cannot run there.
- **"The input has problems. Nothing was forecast."** The check lists every problem with
  the sheet and the row number as Excel shows it. Fix those rows and run it again.
- **"The history does not tie."** Opening cash plus all lines does not equal closing cash
  in the months named. A line is usually missing, or an amount is wrong.
- **The assistant answers without using the plugin.** Start a new chat, and name it:
  "Use the Treasury Cash Forecast plugin."
- **A figure looks wrong.** Open the sheet "Where numbers come from" in the workbook. Its
  "Source row" column names the rows of your input behind that figure.

## Support

Questions, problems and security concerns: open an issue at
https://github.com/Prabhusekaran/treasury-cash-forecast/issues

## Where it comes from

The engine is the same code as the Treasury Cash Forecast plugin for Hermes Agent
(github.com/Prabhusekaran/hermes-treasury-cash-forecast, version 0.2.0), and gives the
same figures. The few wording changes made for this package are listed at the top of
`skills/cash-forecast/scripts/treasury_cash_forecast/__init__.py`.

## Licence and terms

MIT. See [LICENSE](LICENSE) and the short [terms of use](TERMS.md).
