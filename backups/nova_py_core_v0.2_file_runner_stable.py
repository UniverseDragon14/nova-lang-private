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
    print("NOVA Python Core v0.2")
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

def run_file(args):
    if not args:
        print("Use: nova run file.nova")
        return

    file = Path(args[0]).expanduser()

    if not file.exists():
        print(f"File not found: {file}")
        return

    log(f"run file {file}")

    for raw in file.read_text(encoding="utf-8").splitlines():
        line = raw.strip()

        if not line or line.startswith("#"):
            continue

        if line.startswith("say "):
            print(clean_text(line[4:]))
        elif line.startswith("note "):
            note([clean_text(line[5:])])
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
else:
    help_menu()
