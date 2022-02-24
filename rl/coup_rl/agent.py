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
        q_max = None

        if random.random() < self.epsilon:
            # Exploration
            action = random.choice(valid_actions)
        else:
            # Exploitation
            action, q_max = self.get_best_action(state, valid_actions, obs)

        state_action = tuple(state + [action])

        # Update Q values when prev_state_action has cell in QTable
        # (anything but exchange return).
        # Also, we view the opponent as the environment.
        if (self.prev_state_action is not None and
            self.prev_state_action[-1] < 26 and
            action < 26):
            # Get Q value for previous state-action
            q_old = self.qtable.get(self.prev_state_action)

            if q_max is None:
                # Random choice was selected above
                # Get Q value for best action from new state
                _, q_max = self.get_best_action(state, valid_actions, obs)

            # Q Learning algorithm
            q_new = q_old + self.learning_rate * (self.reward + self.discount_factor * q_max - q_old)
            self.qtable.set(self.prev_state_action, q_new)
            logger.debug('Updated Q-value')

            # Store state and action that's about to be taken
            self.prev_state_action = state_action
            self.reward = 0

        elif self.prev_state_action is None:
            # On first turn
            self.prev_state_action = state_action

        # Take action
        logger.debug(f'P{self.id}: {self.env.actions[action]}')
        obs, reward, done, info = self.env.step(action)
        self.reward += reward

        return obs, reward, done, info

    def get_best_action(self, state, actions, obs):
        '''
        Get the best action from the current state, and its Q-value

        state: Current state in QTable index format
        actions: List of valid actions (integers)
        obs: Current state in original observation format
        '''
        if actions[0] < 26:
            # Actions stored in QTable

            if len(actions) == 1:
                # No need for other calculations, do the only action
                action = actions[0]
                q_max = self.qtable.get(tuple(state + [action]))
            else:
                possible_state_actions = [tuple(state + [a]) for a in actions]
                state_action, q_max = self.qtable.get_max_ind(possible_state_actions)
                # Best action from this state
                action = state_action[-1]
        else:
            # Actions not stored in QTable
            # Exchange Return
            # Get best Q values of state after each possible exchange return

            # Get states after each possible exchange return
            # Then for each new state, get all possible actions
            # Each element of next_state_actions will be a list of state-actions for a single new state
            next_state_actions = []
            for a in actions:
                cards_remove = self.env.actions[a].split('_')[-1]
                # List of ints of indexes of cards to keep
                cards_keep = [i for i in range(4) if str(i+1) not in cards_remove]

                next_obs = list(obs)
                # Replace cards
                next_obs[0] = next_obs[cards_keep[0]]
                next_obs[1] = next_obs[cards_keep[1]]
                next_obs[2] = next_obs[3] = -1
                # Replace is card face up
                next_obs[8] = next_obs[8+cards_keep[0]]
                next_obs[9] = next_obs[8+cards_keep[1]]
                next_obs[10] = next_obs[11] = -1

                next_st = convert_obs_to_q_index(next_obs)
                next_state_actions.append(next_st)

            # Each possible state-action pair
            # All states will have same actions since
            # they have same number of coins
            curr_player_coins = obs[16]
            opp_player_coins = obs[17]
            valid = []
            if curr_player_coins >= 10:
                # Coup
                valid = [2]
            else:
                # Income FA Tax Exchange
                valid = [0, 1, 3, 5]
                if curr_player_coins >= 3:
                    # Assassinate
                    valid.append(4)
                if curr_player_coins >= 7:
                    # Coup
                    valid.append(2)
                if opp_player_coins > 0:
                    # Steal
                    valid.append(6)

            next_state_actions = [[next_st + [a] for a in valid] for next_st in next_state_actions]

            # Get best action for each new state
            q_vals = [[self.qtable.get(tuple(x)) for x in lst] for lst in next_state_actions]
            q_vals = [max(x) for x in q_vals]
            ind = q_vals.index(max(q_vals))
            action = actions[ind]
            # This is an estimate, so not a true Q-value. Leave empty.
            q_max = None

        return action, q_max
