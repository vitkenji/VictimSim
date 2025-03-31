# VictimSim

**VictimSim** is a simulator designed for testing search algorithms and other AI techniques in rescue scenarios. It is primarily used within the Artificial Intelligence course at UTFPR, Curitiba. This simulator allows the study of catastrophic scenarios within a 2D grid environment, where artificial agents embark on search and rescue missions to locate and assist victims.

## Key Features of the Simulator

### 1. **2D Grid Environment**
The environment consists of a 2D grid, indexed by coordinates (column, row) or (x, y). The origin is positioned at the upper-left corner, with the y-axis extending downward and the x-axis extending to the right. While the absolute coordinates are only accessible within the environment simulator, users are encouraged to define their own coordinate systems for agents.

### 2. **Cell Accessibility Values**
Each cell in the 2D grid is assigned an accessibility difficulty value ranging from greater than zero to 100. A value of 100 indicates an impassable wall, while higher values signify greater difficulty in accessing the cell. Conversely, values of one or less indicate easier access.

### 3. **Multiple Agents**
The simulator allows one or more agents to be present in the environment. Each agent can be customized with its own color, which is defined via configuration files.

### 4. **Collision Detection**
The simulator integrates collision detection to identify when agents collide with walls or reach the grid boundaries. This event is referred to as a "BUMPED" perception.

### 5. **Agent Perception**
Agents have the ability to detect obstacles and the grid boundaries within their immediate neighborhood, one step ahead of their current position.

### 6. **Multiple Agent Occupation**
Multiple agents can occupy the same cell simultaneously without any collisions occurring.

### 7. **Agent Scheduling and State Management**
The simulator schedules each agent based on its state, which can be ACTIVE, IDLE, ENDED, or DEAD. Only active agents are allowed to perform actions, and the simulator controls the execution time for each agent. Once an agent's allotted time expires, the agent is considered DEAD.
