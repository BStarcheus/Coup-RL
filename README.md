# Coup RL

Coup RL is a reinforcement learning agent that learns to play the deception-based board game Coup.

Coup RL consists of several submodules:
- OpenAI Gym Environment
- Desktop application
- Reinforcement learning agent
    - Self-play training algorithm

## Setup
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

Build and install the gym environment:
```bash
$ pip install -e ./gym-coup
```

## Run the Desktop App
```bash
$ cd coup-rl/app
$ python main.py
```

## Use the Gym Environment
In a python file:
```python
import gym
import gym_coup
env = gym.make('coup-v0')
```
