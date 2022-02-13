import numpy as np
import logging

logging.basicConfig()
logger = logging.getLogger('coup_rl')

class QTable:
    '''
    Stores the necessary information for the Q-Learning algorithm
    Q-Table with indicies for each state-action pair
    Alg Parameters:
        Learning rate
        Discount factor
        Epsilon (e-greedy exploration)
    '''
    def __init__(self,
                 shape=None,
                 learning_rate=None,
                 discount_factor=None,
                 epsilon=None):
        '''
        Create a new QTable
        Either supply all args or none.
        All: creates a new empty QTable
        None: Load an existing QTable later using load()

        shape:           Tuple of ints for dimensions of table
        learning_rate:   Float (0, 1]
        discount_factor: Float [0, 1]
        epsilon:         Float [0, 1]
        '''
        self.table = None
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon

        if shape is not None:
            # Create a new QTable
            self.table = np.zeros(shape)

    def load(self, filename):
        '''
        Load QTable and parameters from a file
        '''
        with np.load(filename) as data:
            self.table = data.get('qtable')
            params = data.get('params')
            self.learning_rate = params[0]
            self.discount_factor = params[1]
            self.epsilon = params[2]
            logger.debug(f'Loaded QTable, LR {self.learning_rate}, DF {self.discount_factor}, Eps {self.epsilon}')

    def save(self, filename):
        '''
        Save QTable and parameters to a file
        '''
        logger.debug(f'Saving QTable to {filename}')
        np.savez_compressed(filename,
                            qtable=self.table,
                            params=[self.learning_rate, self.discount_factor, self.epsilon])

    def set(self, ind_tpl, val):
        '''
        Set a value for the given index of the QTable

        ind_tpl: Tuple, a multidimensioal index of the table for a single cell
        val:     Float value to set the table cell to
        '''
        if not isinstance(ind_tpl, tuple):
            raise TypeError('QTable must be indexed with tuple')

        self.table[ind_tpl] = val


    def get(self, ind_tpl):
        '''
        Get a value from the given index of the QTable

        ind_tpl: Tuple, a multidimensioal index of the table for a single cell
        '''
        if not isinstance(ind_tpl, tuple):
            raise TypeError('QTable must be indexed with tuple')

        return self.table[ind_tpl]

    def get_max_ind(self, ind_tpls):
        '''
        Get the Q-Table index with the largest Q-value
        Note: Returns the first max. Ignores other occurrences.

        ind_tpls: List of tuples, each for a single cell in the table
        '''
        ind = np.argmax([self.get(x) for x in ind_tpls])
        return ind_tpls[ind]