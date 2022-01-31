# Coup RL Gym Environment

gym-coup contains the Coup game logic and the [OpenAI Gym](https://gym.openai.com/) environment to simulate a complete 2-player game.

## Usage
In a python file:
```python
import gym
import gym_coup
env = gym.make('coup-v0')
env.reset()
```
Then you can take `.step()`'s with each player's actions in the game.
There are 18 actions [defined here](https://github.com/BStarcheus/coup-rl/blob/main/gym-coup/gym_coup/envs/coup_env.py#L16).

For example:
```python
env.step(0)  # P1 takes 1 coin of income
env.step(6) # P2 attempts to steal
env.step(13) # P1 passes, allowing the steal to happen
```