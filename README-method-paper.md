# Reproducing the method-paper CEA runs

This repository contains the CEA code changes and two run workflows:

- [`cea/workflows/method_paper_full.yml`](cea/workflows/method_paper_full.yml):
  DAYSIM radiation, occupancy, and demand for one scenario.
- [`cea/workflows/method_paper_demand.yml`](cea/workflows/method_paper_demand.yml):
  occupancy and demand only, when valid radiation results already exist.

Neither workflow calculates photovoltaic generation or runs CRAX. Both use the
same study settings for occupancy and demand.

## Inputs not included in this repository

- A CEA scenario directory with its `inputs/` folder, including building geometry,
  properties, databases, and `inputs/weather/weather.epw`.
- For the demand-only workflow, radiation results for that same scenario in
  `outputs/data/solar-radiation/`. The full workflow generates these results.
- The MUBES `InputFiles/` directory containing the 8,760-hour
  `BuildingN_winter.txt` appliance profiles. The corresponding
  `Building_*v*.pickle` files must be in the parent directory; CEA uses their
  UUID and heated-area metadata to map profiles to buildings.

The local `CityEnergyAnalyst-GUI/` checkout and its scenario data are intentionally
ignored by this repository. Obtain the same scenario, weather, and MUBES inputs
separately to reproduce the study. Keep a fixed copy and record its source.

## Install

From a clone of this repository, install CEA using the project's Pixi setup:

```bash
pixi install
pixi run setup-dev
```

## Run one scenario: radiation, occupancy, and demand

From the repository root, set the MUBES profile folder and scenario paths.
Replace both example paths with absolute paths on your machine:

```bash
export MUBES_APPLIANCE_PROFILES_FOLDER="/path/to/SvB_Base/InputFiles"
export METHOD_PAPER_SCENARIO="/path/to/CEA-project/SvB_Base"

pixi run cea workflow \
  --workflow "$PWD/cea/workflows/method_paper_full.yml"
```

Set `MUBES_APPLIANCE_PROFILES_FOLDER` and `METHOD_PAPER_SCENARIO` in each new
terminal session before running either workflow. They identify external data,
not numerical settings. Do not include `InputFiles/` in Git without checking
its size and redistribution rights.

## Run all standard scenarios in Base_21 and Base_23

Use this from the CEA repository root. Set `PROJECTS_ROOT` to the directory
containing `Base_21/` and `Base_23/`. The loop skips the separate `*_CRAX`
scenario so it is not accidentally rerun with DAYSIM:

```bash
export MUBES_APPLIANCE_PROFILES_FOLDER="/path/to/SvB_Base/InputFiles"
PROJECTS_ROOT="/path/to/CityEnergyAnalyst-GUI"
CEA_ROOT="$PWD"

for PROJECT in "$PROJECTS_ROOT/Base_21" "$PROJECTS_ROOT/Base_23"; do
  for SCENARIO in "$PROJECT"/SvB_*; do
    [ -d "$SCENARIO/inputs" ] || continue
    case "$SCENARIO" in *_CRAX) continue ;; esac

    echo "Running radiation, occupancy, and demand: $SCENARIO"
    if ! METHOD_PAPER_SCENARIO="$SCENARIO" pixi run cea workflow \
      --workflow "$CEA_ROOT/cea/workflows/method_paper_full.yml"; then
      echo "Failed: $SCENARIO"
      break 2
    fi
  done
done
```

The full workflow recalculates DAYSIM radiation for every scenario. This is
simple but can take several hours. To avoid repeating radiation for a scenario
that already has **complete, matching** radiation results, use the same command
with `method_paper_demand.yml` instead. Do not reuse radiation between scenarios
without checking geometry, weather, window-to-wall ratios, and surface optical
properties; some of the study scenarios differ in these inputs.

CEA writes radiation to `outputs/data/solar-radiation/` and per-building hourly
results to `outputs/data/occupancy/` and `outputs/data/demand/` within each
scenario. Rerunning a workflow replaces its generated results.

## Settings fixed by the workflow

| Setting | Value |
| --- | --- |
| Radiation method (full workflow) | DAYSIM |
| Roof / wall sensor grid | 10 m / 200 m |
| Terrain albedo | 0.2 |
| Ventilation basis | Area-based |
| Outdoor-air rate | 0.35 L/s per m2 of conditioned floor area (`Af`) |
| Appliance electricity schedule | MUBES hourly profiles, matched by building UUID |
| Appliance electricity converted to sensible heat | 0.55 |
| Subtract infiltration from ventilation | No |
| Dynamic infiltration | Off |
| Multiprocessing | On, with one CPU kept free |
| Debug mode | Off |

The workflows start from CEA's checked-in default configuration, select all
buildings, and leave the MUBES mapping CSV blank so the mapping comes from the
MUBES pickle metadata. The full workflow also pins the DAYSIM geometry and
ray-tracing parameters in its YAML file. Unlisted settings come from this
repository's `cea/default.config`, not a user's `~/cea.config`. For an exact
comparison, use the same code commit and input data.

For the profile conversion and mapping details, see
[`docs/mubes-appliance-profiles.md`](docs/mubes-appliance-profiles.md).
