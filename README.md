# NOVA Language — Python Prototype

An experimental Python implementation of a small command and scripting language for the Universal Dragon / NOVA tool environment.

## Current capabilities

The interpreter supports:

- text output with `say`
- variables with `set`
- bounded numeric calculations with `calc`
- equality and inequality conditions
- bounded repeat blocks from 0 to 100 iterations
- function definitions and calls with positional arguments
- notes, memory, history, and local backups
- project identity and host status commands

Files use the `.nova` extension. Examples and feature tests are included in the repository.

## Requirements

- Python 3
- Linux is recommended for the current `status` implementation

No third-party Python packages are required.

## Run

Show the command menu:

```bash
python3 nova.py
```

Run the included example:

```bash
python3 nova.py run main.nova
```

Other examples:

```bash
python3 nova.py version
python3 nova.py identity
python3 nova.py status
python3 nova.py note "example note"
python3 nova.py memory
python3 nova.py history
python3 nova.py backup
```

## Example NOVA file

```text
set name = "Dragon"
say "Hello $name"

calc total = 6 * 7
say "Result: $total"

repeat 3
  say "Step $i"
end
```

## Repository layout

- `nova.py` — interpreter and command-line entry point
- `*.nova` — examples and feature tests
- `memory/` — local notes and history used by the current prototype
- `backups/` — historical snapshots and generated backups

## Status

This is a development prototype, not a security sandbox. Review scripts before running them and do not treat the language runtime as an isolation boundary.
