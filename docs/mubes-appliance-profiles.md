# MUBES Appliance Profiles

CEA can optionally replace its generated appliance electricity schedule with MUBES 8,760-hour profiles.
This is intended for local comparison studies against MUBES. Normal CEA runs are unchanged unless the
option is enabled.

## Enable

Run occupancy with the MUBES profile folder:

```bash
cea occupancy \
  --scenario /Users/alizad/PycharmProjects/CityEnergyAnalyst/CityEnergyAnalyst-GUI/SvB_CEA_Sim/SvB_Base \
  --use-mubes-appliance-profiles true \
  --mubes-appliance-profiles-folder /Users/alizad/PycharmProjects/NewWorking-MUBES/examples/1965-1975/Final_Sim_Results/SvB_Base/InputFiles
```

Then run demand with the desired appliance heat-gain fraction:

```bash
cea demand \
  --scenario /Users/alizad/PycharmProjects/CityEnergyAnalyst/CityEnergyAnalyst-GUI/SvB_CEA_Sim/SvB_Base \
  --appliance-heat-gain-fraction 0.55
```

The imported MUBES appliance profile is written into the normal CEA occupancy output column:

```text
outputs/data/occupancy/<building>.csv: Ea_W
```

Rerunning `cea occupancy` with `--use-mubes-appliance-profiles true` regenerates the imported profile.
Rerunning occupancy without the option restores the standard CEA appliance schedule.

## Reproducible CEA Workflow

The tracked workflow `cea/workflows/method_paper_demand.yml` runs occupancy and demand with
area-based ventilation (0.35 L/s/m2), MUBES appliance profiles, and a 0.55 appliance
electricity-to-heat fraction. It also turns off debug mode. Radiation results must already
exist in the selected scenario.

From the CEA repository root, point to the external MUBES data and select a scenario:

```bash
export MUBES_APPLIANCE_PROFILES_FOLDER=/path/to/SvB_Base/InputFiles
export METHOD_PAPER_SCENARIO=/path/to/CEA/scenario
cea workflow \
  --workflow cea/workflows/method_paper_demand.yml
```

The workflow starts from the repository defaults and applies the versioned
settings; it does not inherit the user's `~/cea.config` settings.
The MUBES `BuildingN_winter.txt` profiles and adjacent `Building_*v*.pickle` files are
external inputs and are not included in the CEA repository. Keep a fixed copy of those
inputs for a reproducible study. The workflow uses the pickle metadata for UUID mapping;
it deliberately clears any locally configured mapping CSV path.

## Mapping And Scaling

CEA maps buildings by UUID, not row order. CEA building names may have a leading `B` prefix, so
`B784b8bb9-c90d-4c2f-b2eb-3e07d745f8ad` maps to MUBES UUID
`784b8bb9-c90d-4c2f-b2eb-3e07d745f8ad`.

If no explicit map is provided, CEA reads the MUBES `Building_*v*.pickle` files next to the `InputFiles`
folder using `pickletools` metadata inspection. It reads:

```text
BuildID / 50A_UUID
DB_Surf
IntLoad
EPCMeters / ElecLoad
```

The hourly CEA appliance watts are calculated as:

```text
Ea_W[t] = BuildingN_winter[t] * 0.01 W/m2 * DB_Surf
```

This matches the MUBES IDF `ElectricEquipment` scaling:

```text
Watts per Zone Floor Area = 0.01
Schedule Name = LoadSchedule
```

## Explicit Map

For a deployed or multi-user setup, prefer an explicit CSV instead of auto-discovering local MUBES files:

```csv
name,mubes_building_number,heated_area_m2,profile_path,epc_electricity_kwhyr
B784b8bb9-c90d-4c2f-b2eb-3e07d745f8ad,0,2225,/path/to/Building0_winter.txt,99235
```

Enable it with:

```bash
cea occupancy \
  --scenario <scenario> \
  --use-mubes-appliance-profiles true \
  --mubes-appliance-profiles-folder <InputFiles folder> \
  --mubes-appliance-profile-map <mapping csv>
```

Auto-discovery is convenient for local one-user work. The explicit CSV is better for repeatable shared
runs because it avoids scanning external folders during each occupancy run.
