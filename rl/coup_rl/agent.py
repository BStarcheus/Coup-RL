import random
import logging

logging.basicConfig()
logger = logging.getLogger('coup_rl')

class Agent:
    def __init__(self, id, env, qtable):
        '''
        id: Agent id (1 or 2)
        env: gym-coup env
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

        if random.random() < self.epsilon:
            # Explore
            action = random.choice(valid_actions)
        else:
            # Choose best action
            if 0 in valid_actions:
                # Beginning of turn. All possible actions are found directly in QTable
                is_p2 = self.id == 2
                state = list(self.env.get_obs(p2_view=is_p2))[:6]
                possible_state_actions = [tuple(state + [a]) for a in valid_actions]
                state_action = self.qtable.argmax(possible_state_actions)
                action = state_action[-1]

            elif len(valid_actions) == 1:
                # No need for other calculations, do the only action
                action = valid_actions[0]

            else:
                # Actions not found in QTable
                # Need to look at possible next states
                ...

        # In Coup, turn sub-states and sub-actions are not stored in the QTable
        # so we can only update Q values when we are at the beginning of a turn.
        # Also, we view the opponent as the environment.
        if 0 in valid_actions:
            # Beginning of turn
            # Update Q Table

            # Get Q value for previous state-action
            q_old = self.qtable.get(self.prev_state_action)

            # Get Q value for best action from new state
            try:
                q_max = self.qtable.get(state_action)
            except NameError:
                # state_action doesn't exist. Random choice was selected above.
                is_p2 = self.id == 2
                state = list(self.env.get_obs(p2_view=is_p2))[:6]
                possible_state_actions = [tuple(state + [a]) for a in valid_actions]
                state_action = self.qtable.argmax(possible_state_actions)
                q_max = self.qtable.get(state_action)

            # Q Learning algorithm
            q_new = q_old + self.learning_rate * (self.reward + self.discount_factor * q_max - q_old)
            self.qtable.set(self.prev_state_action, q_new)

            self.prev_state_action = state_action
            self.reward = 0


        # Take action
        logger.debug(f'P{self.id}: {self.env.actions[action]}')
        obs, reward, done, info = self.env.step(action)
        self.reward += reward
