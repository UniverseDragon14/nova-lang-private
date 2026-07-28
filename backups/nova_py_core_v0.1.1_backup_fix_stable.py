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
    print("NOVA Python Core v0.1")
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

def help_menu():
    print("NOVA Python Core Commands:")
    print("  nova version")
    print("  nova identity")
    print("  nova status")
    print("  nova note message")
    print("  nova memory")
    print("  nova history")
    print("  nova backup")

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
else:
    help_menu()
