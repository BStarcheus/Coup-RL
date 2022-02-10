import random
import logging
import re
import gym
import gym_coup
from coup_rl.qtable import QTable
from coup_rl.agent import Agent

logging.basicConfig()
logger = logging.getLogger('coup_rl')

class Human_v_Agent:
    def __init__(self,
                 p_first_turn,
                 filepath,
                 is_training,
                 learning_rate=None,
                 discount_factor=None,
                 epsilon=None,
                 log_level=None):
        '''
        p_first_turn:    Which player goes first, 0-indexed
        filepath:        Path for file ending in .npz
        is_training:     True if creating new save file after game
        learning_rate:   Used for creating new QTable. Float (0, 1]
        discount_factor: Used for creating new QTable. Float [0, 1]
        epsilon:         Used for creating new QTable. Float [0, 1] 
        log_level:       coup_rl log level
        '''
        self.filepath = filepath
        self.is_training = is_training

        # Make the gym env
        self.env = gym.make('coup-v0', num_human_players=1, p_first_turn=p_first_turn)
        self.env.reset()

        if log_level is not None:
            # Set the logging level of this package
            logger.setLevel(log_level)
            # and the gym env
            logging.getLogger('gym_coup').setLevel(log_level)

        self.env.render()
        
        if (learning_rate is not None and
            discount_factor is not None and
            epsilon is not None):
            # Create new Q Table
            s_shape = [x+1 for x in self.env.observation_space.high]
            a_shape = [self.env.action_space.n + 1]
            shape = tuple(s_shape[:6] + a_shape)
            self.qtable = QTable(shape, learning_rate, discount_factor, epsilon)
        else:
            # Try to load existing Q Table
            try:
                self.qtable = QTable()
                self.qtable.load(self.filepath)
            except:
                raise RuntimeError('Agent file does not exist, and not enough information was provided to create a new agent')

        self.agent = Agent(2, self.env, self.qtable)

        random.seed()

    def step(self, action):
        '''
        Take one action for the human player,
        and as many agent actions until it is the human's turn again.
        '''
        logger.debug(f'you: {action}')
        obs, reward, done, info = self.env.step(action)
        self.env.render()

        while not done and self.env.game.whose_action != 0:
            obs2, reward2, done, info2 = self.agent.step()
            self.env.render()

        if done:
            self.finish_game()

    def finish_game(self):
        if self.is_training:
            logger.debug('Saving QTable to file')
            # All saved agent files must end with _000000.npz
            # with number of episodes it's trained on
            fp_split = self.filepath.split('/')
            file = fp_split[-1]
            suf = re.search('_\d\d\d\d\d\d.npz', file)
            if suf:
                start = suf.start() + 1
                end = suf.end() - 4
                num_ep = int(file[start:end]) + 1
                num_ep = str(num_ep)
                num_ep = (6-len(num_ep)) * '0' + num_ep
                file = file[:start]
            else:
                # When creating new, user likely wont enter number
                # But .npz will be there
                file = file[:-4] + '_'
                num_ep = '000001'

            new_file = file + num_ep + '.npz'
            fp_split[-1] = new_file
            new_fp = '/'.join(fp_split)

            self.qtable.save(new_fp)

    def agent_random_step(self):
        # Temp random agent
        agent_action = random.choice(self.env.get_valid_actions())
        logger.debug(f'agent: {self.env.actions[agent_action]}')
        return self.env.step(agent_action)
