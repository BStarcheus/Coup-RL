<p align="center">
    <img src="./img/Coup-RL-logo-dark.png#gh-light-mode-only" width="200px"/>
    <img src="./img/Coup-RL-logo-light.png#gh-dark-mode-only" width="200px"/>
</p>

# Coup RL

Coup RL is a reinforcement learning agent that learns to play the deception-based board game Coup.

Learn the rules of Coup [here](https://www.ultraboardgames.com/coup/game-rules.php).

Coup RL consists of several submodules:
- [OpenAI Gym Environment](./gym-coup): Contains the Coup game logic and the environment to simulate a complete 2-player game.
- [Desktop app](./app): Humans can play against an RL agent with this simple app.
- [Reinforcement learning agent & algorithms](./rl): Contains the structures and algorithms required to train an agent, as well as save and load agents.

## Requirements
The project can run on any OS with [Python 3](https://www.python.org/) installed that also supports [OpenAI Gym](https://gym.openai.com/) and [PyQt6](https://doc.qt.io/qtforpython/).
Developed and tested on macOS with Python 3.9.

## Installation
First create a virtual environment:
```bash
$ cd coup-rl
$ virtualenv env
$ source env/bin/activate
```

Then install the dependencies:
```bash
$ pip install -r app/requirements.txt
$ pip install -r gym-coup/requirements.txt
```

Build and install the gym environment and RL agents:
```bash
$ pip install -e ./gym-coup
$ pip install -e ./rl
```

## Usage
### Run the Desktop App
```bash
$ python app/main.py
```

For further usage documentation see the individual modules:
- Gym Environment - [gym-coup](./gym-coup/README.md)
- Desktop app - [app](./app/README.md)
- Reinforcement learning agent & algorithms - [rl](./rl/README.md)

## FAQ
### Do I need to install everything?
No. If you aren't going to use the desktop app, you don't need to install PyQt6 and its dependencies. You can ignore the command from above:
```bash
$ pip install -r app/requirements.txt
```

