# Switching ventilation between area and people

Run `cea workflow --workflow cea/workflows/area_ventilation.yml` from the source repository with your target scenario selected. Existing radiation results are required.

```yaml
- script: occupancy
  parameters:
    ventilation-mode: area  # area or people
    ventilation-area-rate-lpsm2: 0.35
- script: demand
```

CEA stores typed defaults in `cea/default.config`; YAML workflows pass these parameters to occupancy generation. The default is `people`, preserving existing behaviour. The same options are available in the occupancy tool through the CLI / dashboard.

`people`: hourly scheduled occupants multiplied by the building's `Ve_lsp` [L/s/person].

`area`: constant `ventilation-area-rate-lpsm2` [L/s/m²] multiplied by CEA conditioned floor area `Af` [m²], including unoccupied hours. At 1500 m² and 0.35 L/s/m², the requirement is 525 L/s. It does not add a per-person component or alter occupant heat gains. Rates and areas must be finite and non-negative.

Regenerate occupancy schedules and then run demand for every baseline and retrofit scenario to compare them consistently. Changing the setting without regenerating schedules has no effect on demand.

This changes the outdoor-air **requirement**, not the infiltration model. By default CEA subtracts infiltration when calculating mechanical ventilation; set `demand:subtract-infiltration-from-ventilation=false` to treat infiltration as an additional load. Neither option guarantees the same mechanical airflow as MUBES. CEA's Af may also differ from MUBES's ventilated area. No simulation outputs are changed until you rerun the tools.
