# VictimSim

**VictimSim** is a simulator designed for testing search algorithms and other AI techniques in rescue scenarios. It is primarily used in the Artificial Intelligence course at UTFPR, Curitiba. This simulator provides a platform for studying catastrophic scenarios within a 2D grid environment, where artificial agents perform search and rescue missions to locate and assist victims.

## Key Features

### 1. **2D Grid Environment**
The environment consists of a 2D grid composed of free cells and obstacles, indexed by (x, y) coordinates. The coordinate system's origin (0,0) is the base of the agents. Each cell is assigned a value representing its accessibility difficulty (or traversal cost). Multiple agents can occupy the same cell simultaneously without collision.

### 2. **Multiple Agents**
The simulator supports multiple agents, defaulting to four explorers and four rescuers. The simulator schedules agents based on their state (e.g., ACTIVE, DEAD). Only ACTIVE agents can perform actions. Each agent has a limited execution time; once this time expires, the agent's state changes to DEAD.

#### Explorer Agent
The explorer agent's primary goal is to find victims and build a map detailing the locations of victims, obstacles, and free cells. Each explorer is assigned a "favorite" direction to encourage the exploration of different regions. Explorers cannot communicate with each other.

#### Rescuer Agent
A central "master" controller (or a designated rescuer) aggregates the maps from all explorers. This master agent then assigns victims to the individual rescuer agents. Each rescuer plans the most efficient order and path to save their assigned victims and return to the base.

### 3. **Victims**
Each victim is characterized by a set of vital signs (e.g., systolic pressure, diastolic pressure, pulse, heart rate). These vitals are first read by an explorer agent. Subsequently, a rescuer agent can provide a first-aid kit to the victim.

## AI Techniques Implemented

### 1. A* Search
A* is the primary pathfinding algorithm used in the simulator. It is employed by agents to:
* Find the shortest path back to the base (e.g., when the battery is low).
* Find the shortest path to a non-adjacent unvisited cell during backtracking.
* Calculate the optimal path for a rescuer to save assigned victims and return to the base.

### 2. Online Depth-First Search (DFS)
Online DFS is the main exploration algorithm. The explorer agent prioritizes moving to unvisited adjacent cells. If all adjacent cells have been visited, it backtracks (using A*) to find a path to the nearest unvisited cell elsewhere.

### 3. K-Means Clustering
The K-Means algorithm clusters victims based on their (x, y) coordinates. This is used by the master agent to assign a group of nearby victims to each rescuer.

### 4. Genetic Algorithm
Once a rescuer is assigned a cluster of victims, a genetic algorithm is used to determine a near-optimal order in which to visit them. The fitness function considers the victims' coordinates, predicted gravity, and classification.

### 5. Victim Classifier (Random Forest)
A `RandomForestClassifier` model predicts a victim's triage category (a value from 1 to 4).

### 6. Gravity Regressor (Gradient Boosting)
A `GradientBoostingRegressor` model predicts a victim's "gravity" (a severity score ranging from 0 to 100).

## Results
Simulation results can be found in the `results` folder.

## Requirements
Ensure you have Python 3 and the following libraries installed:
* `pygame`
* `numpy`
* `matplotlib`
* `sklearn`

You can install them using pip:
```bash
pip install pygame numpy matplotlib sklearn
```

## Running

Run the following command:

- `python3 main.py`

## Collaborators:
- Vitor Kenji Zoppo Yamada
- Professor César Tacla
