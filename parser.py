#!/usr/bin/env python3
"""
Parser for quantum chemistry .out files.

Phase 1 (implemented):
  • Extract the Cartesian geometry block and write it to geometry.txt,
    replacing atomic symbols with their integer masses while preserving the
    original column alignment for the remainder of each line.

Planned (scaffold only; not implemented yet):
  • Excited states matrix extraction → excited_states_matrix.txt
  • Excitation energies extraction → excitation_energies.txt

Usage
-----
python parse_out_to_files.py /path/to/file.out [--outdir DIR] [--strict]

Notes
-----
• Geometry block is detected starting two lines after the header line that
  contains the literal text "CARTESIAN COORDINATES (ANGSTROEM)" and ends at
  the first subsequent blank line.
• Only the *first* token of each geometry-row is replaced when it is an
  atomic symbol among {N, C, O, H}. All subsequent columns and spacing are
  preserved.
• If a line's first token is not one of the listed symbols, it is left as-is
  and a WARNING is logged (use --strict to raise an error instead).
"""
from __future__ import annotations

import argparse
import logging
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple


# ---------------------------- Configuration ---------------------------------

# Symbol → integer mass mapping (as requested by the user)
MASS_BY_SYMBOL = {
    "N": 14,
    "C": 12,
    "O": 16,
    "H": 1,
}

GEOM_HEADER_PATTERN = re.compile(r"CARTESIAN\s+COORDINATES\s*\(ANGSTROEM\)", re.IGNORECASE)

# Capture the first non-whitespace token and preserve everything that follows
FIRST_TOKEN_RE = re.compile(r"^(?P<lead_ws>\s*)(?P<tok>\S+)(?P<rest>.*)$")


# ------------------------------ Data types ----------------------------------

@dataclass
class GeometryBlock:
    start_line: int  # inclusive index of the first data line
    end_line: int    # exclusive index (one past the last geometry line)
    lines: List[str]


# ------------------------------ Core logic ----------------------------------

def find_geometry_block(lines: Sequence[str]) -> Optional[GeometryBlock]:
    """Locate and return the geometry block.

    The geometry block starts two lines *after* the header line matching
    GEOM_HEADER_PATTERN and continues until (but not including) the first
    blank line.
    """
    header_idx: Optional[int] = None
    for i, line in enumerate(lines):
        if GEOM_HEADER_PATTERN.search(line):
            header_idx = i
            break

    if header_idx is None:
        logging.info("Geometry header not found.")
        return None

    # Start two lines after the header line
    start = header_idx + 2
    if start >= len(lines):
        return None

    # Consume until first blank line
    end = start
    while end < len(lines) and lines[end].strip():
        end += 1

    if end <= start:
        return None

    block_lines = list(lines[start:end])
    return GeometryBlock(start_line=start, end_line=end, lines=block_lines)


def symbol_to_mass_token(token: str, strict: bool = False) -> str:
    """Map an atomic symbol to its integer mass string if known.

    If token is a known symbol, return its mass as a string. Otherwise,
    return the token unchanged and optionally warn/raise when strict=True.
    """
    if token in MASS_BY_SYMBOL:
        return str(MASS_BY_SYMBOL[token])

    if strict:
        raise ValueError(
            f"Unrecognized atomic symbol '{token}' in geometry block; "
            f"supported: {sorted(MASS_BY_SYMBOL)}"
        )
    logging.warning(
        "Unrecognized first token '%s' in geometry row; leaving unchanged.", token
    )
    return token


def transform_geometry_lines(raw_lines: Iterable[str], strict: bool = False) -> List[str]:
    """Replace first token (atomic symbol) with mass while preserving spacing.

    For example:  "N   1   1   1"  →  "14   1   1   1".
    Leading whitespace and the remainder of the line are preserved exactly.
    """
    out_lines: List[str] = []
    for line in raw_lines:
        m = FIRST_TOKEN_RE.match(line.rstrip("\n"))
        if not m:
            # Unlikely due to regex, but handle gracefully
            out_lines.append(line)
            continue
        lead_ws = m.group("lead_ws")
        tok = m.group("tok")
        rest = m.group("rest")
        new_tok = symbol_to_mass_token(tok, strict=strict)
        out_lines.append(f"{lead_ws}{new_tok}{rest}\n")
    return out_lines


# ----------------------------- I/O Utilities --------------------------------

def read_text_lines(path: Path, encoding: str = "utf-8", errors: str = "replace") -> List[str]:
    with path.open("r", encoding=encoding, errors=errors) as f:
        return f.readlines()


def write_text_lines(path: Path, lines: Iterable[str], encoding: str = "utf-8") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding=encoding, newline="\n") as f:
        for ln in lines:
            f.write(ln)


# ------------------------------ Orchestration -------------------------------

def generate_geometry_file(inp: Path, outdir: Path, strict: bool = False) -> Path:
    """Parse the geometry block from *inp* and write geometry.txt to *outdir*.

    Returns the output path.
    """
    all_lines = read_text_lines(inp)
    block = find_geometry_block(all_lines)
    if block is None:
        raise RuntimeError(
            "Failed to locate geometry block starting two lines after the "
            "'CARTESIAN COORDINATES (ANGSTROEM)' header."
        )

    transformed = transform_geometry_lines(block.lines, strict=strict)
    out_path = outdir / "geometry.txt"
    write_text_lines(out_path, transformed)
    logging.info("Wrote geometry: %s (\u2192 %d lines)", out_path, len(transformed))
    return out_path


# --------------------------- Future placeholders ----------------------------

def generate_excited_states_matrix(inp: Path, outdir: Path) -> Path:
    """Scaffold: parse excited states matrix (not yet implemented)."""
    raise NotImplementedError(
        "Excited states matrix extraction is not yet implemented."
    )


def generate_excitation_energies(inp: Path, outdir: Path) -> Path:
    """Scaffold: parse excitation energies (not yet implemented)."""
    raise NotImplementedError(
        "Excitation energies extraction is not yet implemented."
    )


# ---------------------------------- CLI -------------------------------------

def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=(
            "Extract geometry (and later excited-state data) from a .out file."
        )
    )
    p.add_argument(
        "input",
        type=Path,
        help="Path to the .out file to parse.",
    )
    p.add_argument(
        "--outdir",
        type=Path,
        default=Path.cwd(),
        help="Directory for generated outputs (default: current directory).",
    )
    p.add_argument(
        "--strict",
        action="store_true",
        help=(
            "Treat unknown first tokens in geometry rows as errors instead of "
            "leaving them unchanged."
        ),
    )
    p.add_argument(
        "--log",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level (default: INFO).",
    )
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)

    logging.basicConfig(
        level=getattr(logging, args.log),
        format="[%(levelname)s] %(message)s",
    )

    if not args.input.exists():
        logging.error("Input file not found: %s", args.input)
        return 2

    try:
        geom_path = generate_geometry_file(args.input, args.outdir, strict=args.strict)
        logging.info("Geometry saved to: %s", geom_path)
    except Exception as exc:
        logging.exception("Failed to generate geometry.txt: %s", exc)
        return 1

    # Placeholders for future phases (disabled by default to avoid surprises)
    # When ready, uncomment these and implement the corresponding generators.
    # try:
    #     mat_path = generate_excited_states_matrix(args.input, args.outdir)
    #     logging.info("Excited states matrix saved to: %s", mat_path)
    # except NotImplementedError:
    #     logging.info("Excited states matrix extraction is not implemented yet.")
    # except Exception as exc:
    #     logging.exception("Failed to generate excited states matrix: %s", exc)
    #     return 1

    # try:
    #     ener_path = generate_excitation_energies(args.input, args.outdir)
    #     logging.info("Excitation energies saved to: %s", ener_path)
    # except NotImplementedError:
    #     logging.info("Excitation energies extraction is not implemented yet.")
    # except Exception as exc:
    #     logging.exception("Failed to generate excitation energies: %s", exc)
    #     return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
