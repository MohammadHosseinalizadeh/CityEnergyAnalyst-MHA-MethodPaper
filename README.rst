CEA Method Paper Fork
=====================

This fork contains the CEA settings used for the method-paper comparison.
The tracked ``cea/workflows/method_paper_full.yml`` workflow runs DAYSIM
radiation, occupancy, and demand. It uses area-based ventilation at
0.35 L/s/m2, MUBES hourly appliance profiles, and a 0.55 appliance
electricity-to-heat fraction. CRAX and photovoltaic generation are not
included in this workflow.

The CEA scenario folders and MUBES profiles are **not** part of this Git
repository. Obtain those inputs separately. From the repository root, run::

    pixi install
    pixi run setup-dev
    export MUBES_APPLIANCE_PROFILES_FOLDER="/path/to/SvB_Base/InputFiles"
    export METHOD_PAPER_SCENARIO="/path/to/CEA-project/SvB_Base"
    pixi run cea workflow --workflow "$PWD/cea/workflows/method_paper_full.yml"

For all standard scenarios in ``Base_21`` and ``Base_23``, set
``PROJECTS_ROOT`` to the directory containing those two project folders,
then run from the CEA repository root::

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

The loop skips the separate CRAX scenario. The full workflow recalculates
DAYSIM radiation for each standard scenario. If matching radiation results
already exist, the demand-only workflow can avoid that step. See the
`method-paper reproduction guide <README-method-paper.md>`_ for prerequisites,
output paths, and the demand-only option.

Original CEA Project
====================

|license| |repo_size| |zenodo|

.. |license| image:: https://img.shields.io/badge/License-MIT-blue.svg
    :alt: GitHub license
.. |repo_size| image:: https://img.shields.io/github/repo-size/architecture-building-systems/CityEnergyAnalyst
    :alt: Repo Size
.. |zenodo| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.14903253.svg
   :target: https://doi.org/10.5281/zenodo.14903253

.. image:: logo/cea_logo.png
    :scale: 25 %
    :alt: City Energy Analyst (CEA) logo
    :target: https://www.cityenergyanalyst.com

.. |repobeats| image:: https://repobeats.axiom.co/api/embed/31055fb15ba781904f1dcb1e51de1f17436a8816.svg
    :alt: Repo Contribuitions

.. |contrib.rocks| image:: https://contrib.rocks/image?repo=architecture-building-systems/CityEnergyAnalyst
    :target: https://github.com/architecture-building-systems/CityEnergyAnalyst/graphs/contributors
    :alt: Repo Contribuitions

.. |screenshot| image:: https://images.squarespace-cdn.com/content/v1/61e145bff396b63d6444554a/ac840e01-897b-49a5-bcf1-507bb7f51e7b/Screenshot+2025-03-13+at+16.40.31.jpg
    :target: https://github.com/architecture-building-systems/CityEnergyAnalyst-GUI
    :alt: CEA GUI Screenshot

City Energy Analyst (CEA)
--------------------------

The `City Energy Analyst (CEA) <https://www.cityenergyanalyst.com/>`_ is an urban building energy simulation platform and one of the first open-source initiatives of computation tools for the design of low-carbon and highly efficient cities. The CEA combines knowledge of urban planning and energy systems engineering in an integrated simulation platform. This allows to study of the effects, trade-offs, and synergies of urban design scenarios and energy infrastructure plans. At CEA we are committed to empowering practitioners and researchers to plan future low-carbon cities. 


* Click `here <https://city-energy-analyst.readthedocs.io/en/latest/index.html>`__  for our documentation

* Click `here <https://github.com/architecture-building-systems/CityEnergyAnalyst/issues>`__ to report an issue

* Click `here <https://www.cityenergyanalyst.com/contact>`__ to contact us


CEA Graphical User Interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
|screenshot|

Cite us
--------

The CEA Team. (2025). City Energy Analyst (v3.39.4). Zenodo. https://doi.org/10.5281/zenodo.14903253


Contributors
------------
|contrib.rocks|
|repobeats|
