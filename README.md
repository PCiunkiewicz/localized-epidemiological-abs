# Localized Epidemiological Agent-Based Simulation (ABS)

P. Ciunkiewicz, W. Brooke, M. Rogers, and S. Yanushkevich, “Agent-based epidemiological modeling of COVID-19 in localized environments,” Computers in Biology and Medicine, vol. 144, p. 105396, May 2022, doi: [10.1016/j.compbiomed.2022.105396](10.1016/j.compbiomed.2022.105396).

Epidemiological modeling is used, under certain assumptions, to represent the spread of a disease within a population. Information generated by these models can then be applied to inform public health practices and mitigate risk. To provide useful and actionable preparedness information to administrators and policy makers, epidemiological models must be formulated to model highly localized environments such as office buildings, campuses, or long-term care facilities. In this paper, a highly configurable agent-based simulation (ABS) framework designed for localized environments is proposed. This ABS provides information about risk and the effects of both pharmacological and non-pharmacological interventions, as well as detailed control over the rapidly evolving epidemiological characteristics of COVID-19. Simulation results can inform decisions made by facility administrators and be used as inputs for a complementary decision support system. The application of our ABS to our research lab environment as a proof of concept demonstrates the configurability and insights achievable with this form of modeling, with future work focused on extensibility and integration with decision support.

## Agent-Based Model Simulation notes

### Directory Structure

```bash
src/
├── benchmark.py
├── bulk-stats.sh
├── experiment.ipynb
├── experiment.py
├── export.py
├── launch.py
├── multirun.sh
├── exports/
│   └── exported animations and images
├── mapfiles/
│   └── scenario maps as RGB png files
├── outputs/
│   └── simulation results as hdf5 files
├── scenarios/
│   └── scenario configurations as json files
├── simulation/
│   ├── agent.py
│   ├── model.py
│   ├── publisher.py
│   ├── scenario.py
│   ├── utils.py
│   └── writer.py
└── tools/
    ├── animation.py
    ├── snapshot.py
    └── utils.py
```

### Example Script Invocations

#### Launch

```bash
python launch.py --help
python launch.py run-sim scenarios/eng301.json
python launch.py run-parallel scenarios/eng301.json
```

#### Export

```bash
python export.py --help
python export.py snapshot outputs/simulation_0.hdf5 mapfiles/eng301.png
python export.py animation outputs/simulation_0.hdf5 mapfiles/eng301.png
python export.py stats scenarios/eng301.json 10
```
