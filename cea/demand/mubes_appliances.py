import csv
import pickletools
import re
from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional

import numpy as np

from cea.constants import HOURS_IN_YEAR


MUBES_IDF_APPLIANCE_WM2 = 0.01
MUBES_PROFILE_PATTERN = re.compile(r"Building(\d+)_winter\.txt$")
MUBES_PICKLE_PATTERN = re.compile(r"Building_(\d+)v\d+\.pickle$")


def normalize_building_uuid(building_name: str) -> str:
    """CEA zone names sometimes prefix UUIDs with B to satisfy shapefile naming constraints."""
    name = str(building_name)
    if name.startswith("B") and re.fullmatch(r"[0-9a-fA-F-]{36}", name[1:]):
        return name[1:]
    return name


def load_mubes_profile_for_building(building_name: str, profiles_folder: str, profile_map_path: str = "") -> Optional[Dict]:
    if not profiles_folder:
        return None

    profiles_folder_path = Path(profiles_folder).expanduser()
    if not profiles_folder_path.exists():
        raise FileNotFoundError(f"MUBES appliance profile folder does not exist: {profiles_folder_path}")

    building_uuid = normalize_building_uuid(building_name)
    profile_map = _load_profile_map(profile_map_path, profiles_folder_path)
    row = profile_map.get(building_uuid)
    if row is None:
        return None

    profile_path = Path(row["profile_path"])
    if not profile_path.is_absolute():
        profile_path = profiles_folder_path / profile_path

    profile = np.loadtxt(profile_path, delimiter=",")
    if len(profile) != HOURS_IN_YEAR:
        raise ValueError(f"MUBES profile {profile_path} has {len(profile)} rows, expected {HOURS_IN_YEAR}.")

    heated_area_m2 = float(row["heated_area_m2"])
    hourly_watts = profile * MUBES_IDF_APPLIANCE_WM2 * heated_area_m2

    return {
        "profile_path": str(profile_path),
        "mubes_building_number": int(row["mubes_building_number"]),
        "heated_area_m2": heated_area_m2,
        "hourly_watts": hourly_watts,
        "epc_electricity_kwhyr": float(row["epc_electricity_kwhyr"]) if row.get("epc_electricity_kwhyr") else None,
    }


def _load_profile_map(profile_map_path: str, profiles_folder: Path) -> Dict[str, Dict[str, str]]:
    return _load_profile_map_cached(
        str(Path(profile_map_path).expanduser()) if profile_map_path else "",
        str(profiles_folder))


@lru_cache(maxsize=8)
def _load_profile_map_cached(profile_map_path: str, profiles_folder: str) -> Dict[str, Dict[str, str]]:
    profiles_folder_path = Path(profiles_folder)
    if profile_map_path:
        return _read_profile_map_csv(Path(profile_map_path), profiles_folder_path)
    return _build_profile_map_from_mubes_pickles(profiles_folder_path)


def _read_profile_map_csv(profile_map_path: Path, profiles_folder: Path) -> Dict[str, Dict[str, str]]:
    if not profile_map_path.exists():
        raise FileNotFoundError(f"MUBES appliance profile map does not exist: {profile_map_path}")

    with profile_map_path.open(newline="") as f:
        rows = list(csv.DictReader(f))

    required_columns = {"name", "mubes_building_number", "heated_area_m2", "profile_path"}
    missing = required_columns - set(rows[0].keys() if rows else [])
    if missing:
        raise ValueError(f"MUBES appliance profile map is missing required columns: {sorted(missing)}")

    result = {}
    for row in rows:
        uuid = normalize_building_uuid(row["name"])
        if not row.get("profile_path"):
            row["profile_path"] = f"Building{int(row['mubes_building_number'])}_winter.txt"
        result[uuid] = row
    return result


def _build_profile_map_from_mubes_pickles(profiles_folder: Path) -> Dict[str, Dict[str, str]]:
    mubes_results_folder = profiles_folder.parent
    pickle_paths = sorted(mubes_results_folder.glob("Building_*v*.pickle"))
    if not pickle_paths:
        raise FileNotFoundError(
            "No MUBES Building_*v*.pickle files found next to appliance profile folder. "
            "Provide occupancy:mubes-appliance-profile-map to avoid auto-discovery."
        )

    result = {}
    for pickle_path in pickle_paths:
        metadata = _read_mubes_pickle_metadata(pickle_path)
        if metadata is None:
            continue

        profile_path = Path(metadata["profile_path"])
        if profile_path.name and not profile_path.is_absolute():
            profile_path = profiles_folder / profile_path.name

        result[metadata["uuid"]] = {
            "name": metadata["uuid"],
            "mubes_building_number": str(metadata["mubes_building_number"]),
            "heated_area_m2": str(metadata["heated_area_m2"]),
            "profile_path": str(profile_path),
            "epc_electricity_kwhyr": str(metadata["epc_electricity_kwhyr"] or ""),
        }
    return result


def _read_mubes_pickle_metadata(pickle_path: Path) -> Optional[Dict]:
    m = MUBES_PICKLE_PATTERN.match(pickle_path.name)
    if not m:
        return None
    mubes_building_number = int(m.group(1))

    values = {}
    operations = list(pickletools.genops(pickle_path.read_bytes()))
    for index, (opcode, arg, _pos) in enumerate(operations):
        if opcode.name not in {"SHORT_BINUNICODE", "BINUNICODE", "UNICODE"}:
            continue
        if arg == "BuildID":
            next_arg = _next_value(operations, index)
            if isinstance(next_arg, str) and re.fullmatch(r"[0-9a-fA-F-]{36}", next_arg):
                values["uuid"] = next_arg
        elif arg == "DB_Surf":
            next_arg = _next_value(operations, index)
            if isinstance(next_arg, (int, float)):
                values["heated_area_m2"] = float(next_arg)
        elif arg == "IntLoad":
            next_arg = _next_value(operations, index)
            if isinstance(next_arg, str):
                values["profile_path"] = next_arg
        elif arg in {"BuildingLev", "HousholdLev", "OperationLev"}:
            next_arg = _next_value(operations, index)
            values[arg] = float(next_arg) if isinstance(next_arg, (int, float)) else 0.0

    if not {"uuid", "heated_area_m2", "profile_path"} <= set(values):
        return None

    profile_name = Path(values["profile_path"]).name
    profile_match = MUBES_PROFILE_PATTERN.match(profile_name)
    if profile_match and int(profile_match.group(1)) != mubes_building_number:
        raise ValueError(
            f"MUBES pickle/profile mismatch: {pickle_path.name} points to {profile_name}."
        )

    values["mubes_building_number"] = mubes_building_number
    values["epc_electricity_kwhyr"] = values.get("BuildingLev", 0.0) + values.get("HousholdLev", 0.0) + values.get("OperationLev", 0.0)
    return values


def _next_value(operations, index):
    for opcode, arg, _pos in operations[index + 1:index + 5]:
        if opcode.name in {"MEMOIZE", "BINPUT", "LONG_BINPUT"}:
            continue
        return arg
    return None
