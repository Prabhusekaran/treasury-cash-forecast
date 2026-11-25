"""Treasury Cash Forecast: a 12-month monthly direct cash-flow forecast.

This is the engine of the Treasury Cash Forecast plugin, packaged as an agent skill that runs
in any assistant able to load a SKILL.md folder and run Python. It is a copy of
github.com/Prabhusekaran/hermes-treasury-cash-forecast at version 0.2.0 (commit c10a137). The
forecasting code, the reconciliation and both example companies are identical to that version.

Versions 0.2.1 to 0.2.3 of this package changed only the skill's instructions and the runner
script (the result names the user's own file instead of the upload's stored name). No figure
changed.

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

The arithmetic and the cash reconciliation run in code. No network calls, no credentials; it
reads only the input it is given and writes only where it is told to.
"""
__version__ = "0.2.3"
