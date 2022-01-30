import random
import logging
import gym
import gym_coup

logging.basicConfig()
logger = logging.getLogger('coup_rl')

class Human_v_Agent:
    def __init__(self, p_first_turn, log_level=None):
        '''
        p_first_turn: Which player goes first, 0-indexed
        log_level: coup_rl log level
        '''
        # Make the gym env
        self.env = gym.make('coup-v0', num_human_players=1, p_first_turn=p_first_turn)

        if log_level is not None:
            # Set the logging level of this package
            logger.setLevel(log_level)
            # and the gym env
            logging.getLogger('gym_coup').setLevel(log_level)

        self.env.reset()

    def step(self, action):
        '''
        Take one action for the human player,
        and as many agent actions until it is the human's turn again.
        '''
        logger.debug(f'you: {action}')
        obs, reward, done, info = self.env.step(action)

        while not done and self.env.game.whose_action != 0:
            obs2, reward2, done, info2 = self.agent_step()

    def agent_step(self):
        # Temp random agent
        agent_action = random.choice(self.env.get_valid_actions())
        logger.debug(f'agent: {self.env.actions[agent_action]}')
        return self.env.step(agent_action)
