#!/usr/bin/env python3
import os
import sys
import shlex
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
    print("NOVA Python Core v0.9")
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
    for k in sorted(vars_map.keys(), key=len, reverse=True):
        out = out.replace("$" + k, vars_map[k])
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

def condition_ok(condition, vars_map):
    condition = condition.strip()

    if "==" in condition:
        op = "=="
    elif "!=" in condition:
        op = "!="
    else:
        print(f"NOVA if error: use == or != -> {condition}")
        return False

    left, right = condition.split(op, 1)
    left = left.strip()
    right = render_text(right.strip(), vars_map)
    left_value = vars_map.get(left, "")

    if op == "==":
        return left_value == right
    return left_value != right

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


def find_block_end(lines, start):
    depth = 0
    for i in range(start, len(lines)):
        line = lines[i].strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("define "):
            depth += 1
        elif line.startswith("repeat ") and " then " not in line:
            depth += 1
        elif line.startswith("if ") and " then " not in line:
            depth += 1
        elif line == "end":
            if depth == 0:
                return i
            depth -= 1

    return -1

def execute_lines(lines, vars_map, functions=None, start=0, end=None):
    if functions is None:
        functions = {}

    if end is None:
        end = len(lines)

    i = start

    while i < end:
        line = lines[i].strip()

        if not line or line.startswith("#"):
            i += 1
            continue

        if line == "end":
            return i

        if line.startswith("define "):
            name = line[7:].strip()

            if not name.replace("_", "").isalnum():
                print(f"NOVA function error: bad name {name}")
                i += 1
                continue

            block_end = find_block_end(lines, i + 1)

            if block_end == -1:
                print(f"NOVA function error: missing end for {name}")
                return i

            functions[name] = lines[i + 1:block_end]
            print(f"function {name} defined")

            i = block_end + 1
            continue

        if line.startswith("call "):
            raw_call = line[5:].strip()

            try:
                parts = shlex.split(raw_call)
            except Exception as e:
                print(f"NOVA call error: {e}")
                i += 1
                continue

            if not parts:
                print("NOVA call error: missing function name")
                i += 1
                continue

            name = parts[0]
            call_args = [render_text(x, vars_map) for x in parts[1:]]

            if name not in functions:
                print(f"NOVA function not found: {name}")
                i += 1
                continue

            old_args = {}
            for k in list(vars_map.keys()):
                if k == "argc" or (k.startswith("arg") and k[3:].isdigit()):
                    old_args[k] = vars_map[k]
                    del vars_map[k]

            vars_map["argc"] = str(len(call_args))
            for idx, value in enumerate(call_args, start=1):
                vars_map[f"arg{idx}"] = value

            execute_lines(functions[name], vars_map, functions)

            for k in list(vars_map.keys()):
                if k == "argc" or (k.startswith("arg") and k[3:].isdigit()):
                    del vars_map[k]

            vars_map.update(old_args)

            i += 1
            continue

        if line == "functions":
            if functions:
                for name in functions:
                    print(f"function {name}")
            else:
                print("No functions defined.")
            i += 1
            continue

        if line.startswith("repeat "):
            body = line[7:].strip()

            if " then " in body:
                count_text, action = body.split(" then ", 1)
                count_text = render_text(count_text.strip(), vars_map)

                try:
                    count = int(count_text)
                except:
                    print(f"NOVA repeat error: bad count {count_text}")
                    i += 1
                    continue

                if count < 0 or count > 100:
                    print("NOVA repeat error: count must be 0..100")
                    i += 1
                    continue

                for n in range(count):
                    vars_map["i"] = str(n + 1)
                    execute_line(action.strip(), vars_map)

                i += 1
                continue

            count_text = render_text(body, vars_map)

            try:
                count = int(count_text)
            except:
                print(f"NOVA repeat error: bad count {count_text}")
                i += 1
                continue

            if count < 0 or count > 100:
                print("NOVA repeat error: count must be 0..100")
                i += 1
                continue

            block_end = find_block_end(lines, i + 1)

            if block_end == -1:
                print("NOVA repeat error: missing end")
                return i

            for n in range(count):
                vars_map["i"] = str(n + 1)
                execute_lines(lines, vars_map, functions, i + 1, block_end)

            i = block_end + 1
            continue

        if line.startswith("if "):
            body = line[3:].strip()

            if " then " in body:
                condition, action = body.split(" then ", 1)

                if condition_ok(condition, vars_map):
                    execute_line(action.strip(), vars_map)
                else:
                    print(f"IF skipped: {condition.strip()}")

                i += 1
                continue

            block_end = find_block_end(lines, i + 1)

            if block_end == -1:
                print("NOVA if error: missing end")
                return i

            if condition_ok(body, vars_map):
                execute_lines(lines, vars_map, functions, i + 1, block_end)
            else:
                print(f"IF skipped: {body}")

            i = block_end + 1
            continue

        execute_line(line, vars_map)
        i += 1

    return i

def run_file(args):
    if not args:
        print("Use: nova run file.nova")
        return

    file = Path(args[0]).expanduser()

    if not file.exists():
        print(f"File not found: {file}")
        return

    vars_map = {}
    functions = {}
    log(f"run file {file}")

    lines = file.read_text(encoding="utf-8").splitlines()
    execute_lines(lines, vars_map, functions)

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
    print("  NOVA file commands: say, note, set, calc, vars, define/call function with args, if/end block, repeat/end block, identity, status, memory, history, backup")

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
