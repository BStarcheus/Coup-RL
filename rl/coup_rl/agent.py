import random
import logging
from coup_rl.utils import *

logging.basicConfig()
logger = logging.getLogger('coup_rl')

class Agent:
    def __init__(self, id, env, qtable):
        '''
        id:     Agent id (1 or 2)
        env:    gym-coup env
        qtable: QTable object with table, learning params
        '''
        self.id = id
        self.env = env
        self.qtable = qtable
        self.learning_rate = self.qtable.learning_rate
        self.discount_factor = self.qtable.discount_factor
        self.epsilon = self.qtable.epsilon

        # State-action tuple from the last step that was at the beginning of turn
        self.prev_state_action = None
        # Reward accumulated since last beginning-of-turn
        self.reward = 0

        random.seed()

    def step(self):
        '''
        Take one action in the env
        '''
        valid_actions = self.env.get_valid_actions()
        is_p2 = self.id == 2
        obs = self.env.get_obs(p2_view=is_p2)
        state = convert_obs_to_q_index(obs)
        state_action = None

        if random.random() < self.epsilon:
            # Exploration
            action = random.choice(valid_actions)
        else:
            # Exploitation
            action = self.get_best_action(state, valid_actions, obs)
            state_action = tuple(state + [action])

        # Update Q values when prev_state_action has cell in QTable
        # (anything but exchange return).
        # Also, we view the opponent as the environment.
        if self.prev_state_action is not None and self.prev_state_action[-1] < 26:
            # Get Q value for previous state-action
            q_old = self.qtable.get(self.prev_state_action)

            # Get Q value for best action from new state
            if state_action is not None:
                q_max = self.qtable.get(state_action)
            else:
                # Random choice was selected above
                a = self.get_best_action(state, valid_actions, obs)
                state_action = tuple(state + [a])
                q_max = self.qtable.get(state_action)

            # Q Learning algorithm
            q_new = q_old + self.learning_rate * (self.reward + self.discount_factor * q_max - q_old)
            self.qtable.set(self.prev_state_action, q_new)

            # Store state and action that's about to be taken
            self.prev_state_action = tuple(state + [action])
            self.reward = 0

        # Take action
        logger.debug(f'P{self.id}: {self.env.actions[action]}')
        obs, reward, done, info = self.env.step(action)
        self.reward += reward

        return obs, reward, done, info

    def get_best_action(self, state, actions, obs):
        '''
        Choose the best action from the current state

        state: Current state in QTable index format
        actions: List of valid actions (integers)
        obs: Current state in original observation format
        '''
        if actions[0] < 26:
            # Actions stored in QTable

            if len(actions) == 1:
                # No need for other calculations, do the only action
                action = actions[0]
            else:
                possible_state_actions = [tuple(state + [a]) for a in actions]
                state_action = self.qtable.get_max_ind(possible_state_actions)
                # Best action from this state
                action = state_action[-1]
        else:
            # Actions not stored in QTable
            # Exchange Return
            # Get best Q values of state after each possible exchange return

            # Get states after each possible exchange return

            # Get best Q value from that state

            # x = argmax
            # action = actions[x]

            # TODO temp
            action = random.choice(actions)

        return action
