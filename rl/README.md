# Coup RL Agents and Algorithms

This module contains structures and algorithms required to train an agent, as well as save and load agents.

Human_v_Agent is used to test agents' skill against a humman in the desktop app.

SelfPlay is used to train an agent from scratch.

## Usage
To train via self-play, use the script `train_self_play.py` with the following arguments:
```
Coup RL Self-play Training

positional arguments:
  filepath              File path and name for agent to train
  episodes              Number of episodes to train for
  checkpoint            Number of episodes between saving the agent to a new
                        file

optional arguments:
  -h, --help            show this help message and exit
  --learning_rate LEARNING_RATE
                        Learning Rate (0, 1]
  --discount_factor DISCOUNT_FACTOR
                        Discount Factor [0, 1]
  --epsilon EPSILON     Ratio of exploration [0, 1]
  -d, --debug           Log at the debug level
  -t, --timer           Time the entire training session
```

Example of starting a new agent from scratch:
```bash
python rl/train_self_play.py new_agent_test.npz 1000000 100000 --learning_rate 0.1 --discount_factor 0.95 --epsilon 0.1
```