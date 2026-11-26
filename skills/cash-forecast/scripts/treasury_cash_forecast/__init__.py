"""Treasury Cash Forecast: a 12-month monthly direct cash-flow forecast.

This is the engine of the Treasury Cash Forecast plugin, packaged as an agent skill that runs
in any assistant able to load a SKILL.md folder and run Python. It is a copy of
github.com/Prabhusekaran/hermes-treasury-cash-forecast at version 0.2.0 (commit c10a137). The
forecasting code, the reconciliation and both example companies are identical to that version.

Versions 0.2.1 to 0.2.3 of this package changed only the skill's instructions and the runner
script (the result names the user's own file instead of the upload's stored name). Version
0.2.4 changed how scenario percentages are shown and read (points 6 and 7 below). No figure
changed for an input that was read correctly before.

Changes made to the copy, and nothing else:
  1. This file replaces the Hermes entry point; nothing is registered with a host application.
     The four actions are reached through scripts/cash_forecast.py.
  2. tools.py takes the version from this file instead of from plugin.yaml.
  3. Messages about a missing library say how to install it, instead of how to restart Hermes
     (tools.py, loader.py), and two "next step" hints name this copy's commands instead of the
     Hermes tool names (tools.py).
  4. The template's instructions say "tell the assistant which model to use" instead of
     "tell Hermes".
  5. schemas.py (the Hermes tool descriptions), the Hermes manifest and the tests are not copied.
  6. The template shows the percent column of the scenarios sheet with a % sign (-4 is shown as
     -4%). The cell still holds -4, so the content and its fingerprint are unchanged
     (template.py).
  7. A cell of that column which Excel formats as a percentage (it holds 0.08 and shows 8%) is
     read as 8, the figure on the screen, instead of 0.08. A plain number between -1 and 1 is
     still read as typed, with a warning (loader.py).

The arithmetic and the cash reconciliation run in code. No network calls, no credentials; it
reads only the input it is given and writes only where it is told to.
"""
__version__ = "0.2.4"
