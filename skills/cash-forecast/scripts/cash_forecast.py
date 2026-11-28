#!/usr/bin/env python3
"""Run the Treasury Cash Forecast engine from the command line.

    python3 cash_forecast.py template --output-dir DIR [--example manufacturer|hotel] [--empty] [--format xlsx|csv]
    python3 cash_forecast.py validate INPUT
    python3 cash_forecast.py run INPUT [--model MODEL] [--scenario NAME ...] [--base-only] [--output-dir DIR]
    python3 cash_forecast.py compare INPUT [--model MODEL ...] [--scenario NAME]

INPUT is the filled template: one .xlsx workbook, or a folder holding inputs.csv,
history.csv, known_events.csv and scenarios.csv.

Every command prints one JSON document. "success": true means the figures in it come
from the engine and are reconciled; "success": false means nothing was forecast and
"error" (and "problems") say why in plain language. The exit code is 0 or 1 to match.

This script calculates nothing itself. It only passes the request to the engine in the
folder next to it. It makes no network calls.
"""
import argparse
import importlib.util
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIBRARIES = {"statsmodels": "statsmodels>=0.14,<1", "openpyxl": "openpyxl>=3.1,<4"}
MODELS = ["ets", "sarima", "baseline", "seasonal_drift", "seasonal_naive", "previous_month", "chronos_2"]
UPLOAD_PREFIX = re.compile(r"^[0-9a-f]{8}-(?P<name>.+)$")
MINIMUM_PYTHON = (3, 9)
UPLOAD_FOLDERS = (Path("/mnt/user-data/uploads"),)      # where chat uploads are kept, when the host has one


def missing_libraries():
    missing = []
    for name in LIBRARIES:
        try:
            found = importlib.util.find_spec(name) is not None
        except (ImportError, ValueError):
            found = False
        if not found:
            missing.append(name)
    return missing


def parser():
    top = argparse.ArgumentParser(prog="cash_forecast.py", description="12-month monthly direct cash-flow forecast.")
    commands = top.add_subparsers(dest="command", required=True)

    template = commands.add_parser("template", help="write the input template, filled with an example or empty")
    template.add_argument("--output-dir", required=True, help="folder where the template is saved")
    template.add_argument("--example", choices=["manufacturer", "hotel"], default="manufacturer",
                          help="which made-up example company to include (default: manufacturer)")
    template.add_argument("--empty", action="store_true", help="headings only, no example company")
    template.add_argument("--format", choices=["xlsx", "csv"], default="xlsx", help="one workbook (default) or a CSV folder")

    for name, text in (("validate", "check a filled template; forecasts nothing"), ("check", "same as validate")):
        check = commands.add_parser(name, help=text)
        check.add_argument("input", help="the .xlsx workbook or the folder of CSV files")

    run = commands.add_parser("run", help="run the base case and the scenarios and write the result workbook")
    run.add_argument("input", help="the .xlsx workbook or the folder of CSV files")
    run.add_argument("--model", choices=MODELS, help="model for the forecast lines (default: the template's, else ets)")
    run.add_argument("--scenario", action="append", default=None,
                     help="a scenario to run next to the base case; repeat for several (default: all)")
    run.add_argument("--base-only", action="store_true", help="run the base case without any scenario")
    run.add_argument("--output-dir", help="where to save the result (default: ./cash_forecast_output/<input name>-<fingerprint>)")

    compare = commands.add_parser("compare", help="run several models on the same input and show how far they differ")
    compare.add_argument("input", help="the .xlsx workbook or the folder of CSV files")
    compare.add_argument("--model", action="append", default=None, choices=MODELS,
                         help="a model to include; repeat for several (default: the six built-in models)")
    compare.add_argument("--scenario", help="compare on this scenario instead of the base case")
    return top


def under_the_users_own_name(input_path):
    """Return (path to use, note). An uploaded workbook is copied so the result names the user's file.

    A chat upload is stored as "<8 random characters>-<the user's file name>" in a folder called
    uploads. The result workbook states the name of its input, and it should state the name the
    user knows. So such a file is copied, unchanged, into ./cash_forecast_input/ under its own
    name and the copy is used. The same is done for a copy of an upload that was put somewhere
    else under its stored name, as long as the upload is still in its uploads folder. Nothing
    else is renamed, and the upload itself is never touched.
    """
    source = Path(input_path)
    found = UPLOAD_PREFIX.match(source.name)
    if not (found and source.is_file()):
        return input_path, None
    if "uploads" not in source.parts and not any((folder / source.name).is_file() for folder in UPLOAD_FOLDERS):
        return input_path, None
    folder = Path.cwd() / "cash_forecast_input"
    folder.mkdir(parents=True, exist_ok=True)
    copy = folder / found["name"]
    shutil.copyfile(source, copy)
    return str(copy), (f"The upload '{source.name}' was copied to '{copy}' so that the result shows the "
                       f"user's own file name, '{copy.name}'. The upload itself was not changed.")


def default_output_dir(input_path, loader):
    """A folder in the working directory, named after the input and its content.

    The input may sit in a folder that cannot be written to (an upload), so the result does
    not go next to it. A changed input gets a new folder; the same input reuses its own.
    """
    source = Path(input_path).expanduser()
    stem = source.stem if source.is_file() else source.name
    try:
        mark = loader.load_inputs(input_path).fingerprint[:8]
    except Exception:
        mark = "result"          # the run itself will report what is wrong with the input
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in stem) or "input"
    return Path.cwd() / "cash_forecast_output" / f"{safe}-{mark}"


def main(argv=None):
    args = parser().parse_args(argv)
    if tuple(sys.version_info[:2]) < MINIMUM_PYTHON:
        print(json.dumps({
            "success": False,
            "error": "This needs Python %d.%d or newer, and this is Python %d.%d. Nothing was run."
                     % (MINIMUM_PYTHON + tuple(sys.version_info[:2])),
            "next_step": "Run the same command with a newer Python, for example python3.11 in place of python3. "
                         "If none is installed, tell the user that the forecast cannot run here and why.",
        }, indent=2))
        return 1
    missing = missing_libraries()
    if missing:
        install = "python3 -m pip install " + " ".join(f'"{LIBRARIES[name]}"' for name in LIBRARIES)
        print(json.dumps({
            "success": False,
            "error": "Python cannot load " + " and ".join(missing) + " in this session. Nothing was run.",
            "install_command": install,
            "next_step": "Run the install command once, then run this command again unchanged. If pip refuses "
                         "because the environment is managed, add --break-system-packages. Use the same Python for pip and for this script.",
        }, indent=2))
        return 1

    sys.path.insert(0, str(HERE))
    from treasury_cash_forecast import loader, tools

    def absolute(path):
        """Paths in the output are always complete, so they can be used from any folder."""
        return str(Path(path).expanduser().resolve())

    note = None
    if getattr(args, "input", None):
        args.input, note = under_the_users_own_name(absolute(args.input))
    if getattr(args, "output_dir", None):
        args.output_dir = absolute(args.output_dir)

    if args.command == "template":
        reply = tools.cash_forecast_template({"output_dir": args.output_dir, "format": args.format,
                                              "with_example": not args.empty, "example": args.example})
    elif args.command in ("validate", "check"):
        reply = tools.cash_forecast_validate({"input_path": args.input})
    elif args.command == "run":
        request = {"input_path": args.input,
                   "output_dir": args.output_dir or str(default_output_dir(args.input, loader))}
        if args.model:
            request["model"] = args.model
        if args.base_only:
            request["scenarios"] = []
        elif args.scenario:
            request["scenarios"] = args.scenario
        reply = tools.cash_forecast_run(request)
    else:
        request = {"input_path": args.input}
        if args.model:
            request["models"] = args.model
        if args.scenario:
            request["scenario"] = args.scenario
        reply = tools.cash_forecast_compare(request)

    result = json.loads(reply)
    if note:
        result = {**result, "input_note": note}
        reply = json.dumps(result, indent=2, default=str)
    print(reply)
    return 0 if result.get("success") else 1


if __name__ == "__main__":
    sys.exit(main())
