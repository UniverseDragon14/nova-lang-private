#!/usr/bin/env python3
import os
import sys
import tarfile
from datetime import datetime
from pathlib import Path

ROOT = Path.home() / "nova-lang"
MEMORY = ROOT / "memory" / "memory.txt"
HISTORY = ROOT / "memory" / "history.txt"
BACKUPS = ROOT / "backups"

for p in [ROOT, MEMORY.parent, BACKUPS]:
    p.mkdir(parents=True, exist_ok=True)

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log(msg):
    with open(HISTORY, "a", encoding="utf-8") as f:
        f.write(f"{now()} | {msg}\n")

def version():
    print("NOVA Python Core v0.6")
    print("Runtime: python nova.py")
    print("Mode: Universal Dragon tool-language core")

def identity():
    print("Universal Dragon = ecosystem")
    print("NOVA = language/core")
    print("EVE = control/doctor layer")
    print("Aslam = creator/builder")

def status():
    print("NOVA Python Status")
    print(f"Root: {ROOT}")
    print(f"User: {os.getenv('USER')}")
    print(f"PWD : {os.getcwd()}")
    os.system("uname -a")

def note(args):
    msg = " ".join(args).strip()
    if not msg:
        print("Use: nova note message")
        return
    with open(MEMORY, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    log("noted: " + msg)
    print("Noted.")

def memory():
    if MEMORY.exists():
        print(MEMORY.read_text(encoding="utf-8"))
    else:
        print("No memory yet.")

def history():
    if HISTORY.exists():
        print(HISTORY.read_text(encoding="utf-8"))
    else:
        print("No history yet.")

def backup():
    name = BACKUPS / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"
    with tarfile.open(name, "w:gz") as tar:
        for path in ROOT.rglob("*"):
            if path == BACKUPS or BACKUPS in path.parents:
                continue
            arcname = Path("nova-lang") / path.relative_to(ROOT)
            tar.add(path, arcname=str(arcname))
    log(f"backup created {name}")
    print(f"Backup created: {name}")



def clean_text(x):
    x = x.strip()
    if (x.startswith('"') and x.endswith('"')) or (x.startswith("'") and x.endswith("'")):
        return x[1:-1]
    return x

def render_text(text, vars_map):
    out = clean_text(text)
    for k, v in vars_map.items():
        out = out.replace("$" + k, v)
    return out

def calc_value(expr, vars_map):
    expr = render_text(expr, vars_map)

    allowed = set("0123456789+-*/%.() ")
    if not all(c in allowed for c in expr):
        raise ValueError("only numbers and math operators allowed")

    result = eval(expr, {"__builtins__": {}}, {})

    if isinstance(result, float) and result.is_integer():
        result = int(result)

    return str(result)

def execute_line(line, vars_map):
    if line.startswith("set ") and "=" in line:
        left, right = line[4:].split("=", 1)
        name = left.strip()
        value = clean_text(right.strip())

        if not name.replace("_", "").isalnum():
            print(f"NOVA variable error: bad name {name}")
            return

        vars_map[name] = value
        print(f"{name} = {value}")

    elif line.startswith("calc ") and "=" in line:
        left, right = line[5:].split("=", 1)
        name = left.strip()
        expr = right.strip()

        if not name.replace("_", "").isalnum():
            print(f"NOVA calc error: bad name {name}")
            return

        try:
            value = calc_value(expr, vars_map)
            vars_map[name] = value
            print(f"{name} = {value}")
        except Exception as e:
            print(f"NOVA calc error: {e}")

    elif line.startswith("say "):
        print(render_text(line[4:], vars_map))

    elif line.startswith("note "):
        note([render_text(line[5:], vars_map)])

    elif line == "vars":
        if vars_map:
            for k, v in vars_map.items():
                print(f"{k} = {v}")
        else:
            print("No variables set.")

    elif line == "identity":
        identity()

    elif line == "status":
        status()

    elif line == "memory":
        memory()

    elif line == "history":
        history()

    elif line == "backup":
        backup()

    else:
        print(f"NOVA does not understand: {line}")

def run_repeat(line, vars_map):
    # format: repeat 3 then say "hello"
    body = line[7:].strip()

    if " then " not in body:
        print(f"NOVA repeat error: missing then -> {line}")
        return

    count_text, action = body.split(" then ", 1)
    count_text = render_text(count_text.strip(), vars_map)
    action = action.strip()

    try:
        count = int(count_text)
    except:
        print(f"NOVA repeat error: bad count {count_text}")
        return

    if count < 0:
        print("NOVA repeat error: count cannot be negative")
        return

    if count > 100:
        print("NOVA repeat error: max repeat is 100")
        return

    for i in range(count):
        vars_map["i"] = str(i + 1)
        execute_line(action, vars_map)

def run_condition(line, vars_map):
    # format:
    # if name == value then say "text"
    # if name != value then note "text"

    body = line[3:].strip()

    if " then " not in body:
        print(f"NOVA if error: missing then -> {line}")
        return

    condition, action = body.split(" then ", 1)
    condition = condition.strip()
    action = action.strip()

    op = None
    if "==" in condition:
        op = "=="
    elif "!=" in condition:
        op = "!="
    else:
        print(f"NOVA if error: use == or != -> {line}")
        return

    left, right = condition.split(op, 1)
    left = left.strip()
    right = render_text(right.strip(), vars_map)

    left_value = vars_map.get(left, "")

    ok = False
    if op == "==":
        ok = left_value == right
    elif op == "!=":
        ok = left_value != right

    if ok:
        execute_line(action, vars_map)
    else:
        print(f"IF skipped: {left} {op} {right}")

def run_file(args):
    if not args:
        print("Use: nova run file.nova")
        return

    file = Path(args[0]).expanduser()

    if not file.exists():
        print(f"File not found: {file}")
        return

    vars_map = {}
    log(f"run file {file}")

    for raw in file.read_text(encoding="utf-8").splitlines():
        line = raw.strip()

        if not line or line.startswith("#"):
            continue

        if line.startswith("if "):
            run_condition(line, vars_map)
        elif line.startswith("repeat "):
            run_repeat(line, vars_map)
        else:
            execute_line(line, vars_map)

def help_menu():
    print("NOVA Python Core Commands:")
    print("  nova version")
    print("  nova identity")
    print("  nova status")
    print("  nova note message")
    print("  nova memory")
    print("  nova history")
    print("  nova backup")
    print("  nova run file.nova")
    print("  nova new file.nova")
    print("  NOVA file commands: say, note, set, calc, vars, if condition, repeat loop, identity, status, memory, history, backup")

cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
args = sys.argv[2:]

if cmd == "version":
    version()
elif cmd == "identity":
    identity()
elif cmd == "status":
    status()
elif cmd == "note":
    note(args)
elif cmd == "memory":
    memory()
elif cmd == "history":
    history()
elif cmd == "backup":
    backup()
elif cmd == "run":
    run_file(args)
elif cmd == "new":
    new_file(args)
else:
    help_menu()
