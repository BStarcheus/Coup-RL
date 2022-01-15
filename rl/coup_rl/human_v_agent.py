import random
import gym
import gym_coup

class Human_v_Agent:
    def __init__(self):
        self.env = gym.make('coup-v0')
        self.env.reset()

    def step(self, action):
        '''
        Take one action for the human player,
        and as many agent actions until it is the human's turn again.
        '''
        print('you:', action)
        obs, reward, done, info = self.env.step(action)

        while not done and self.env.game.whose_action != 0:
            self.agent_step()

    def agent_step(self):
        # Temp random agent
        agent_action = random.choice(self.env.get_valid_actions())
        print('agent:', self.env.actions[agent_action])
        obs2, reward2, done2, info2 = self.env.step(agent_action)
