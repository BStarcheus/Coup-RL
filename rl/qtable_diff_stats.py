import argparse
from coup_rl.utils import get_num_changed
from coup_rl.qtable import QTable
import numpy as np

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath1')
    parser.add_argument('filepath2')
    args = parser.parse_args()

    qtable1 = QTable()
    qtable1.load(args.filepath1)
    qtable2 = QTable()
    qtable2.load(args.filepath2)

    print(f'Num changed: {get_num_changed(qtable1.table, qtable2.table)}')

    abs_dif = np.absolute(qtable1.table - qtable2.table)
    print(f'Mean: {np.mean(abs_dif)}')
    print(f'Max diff: {np.amax(abs_dif)}')

    print(f'Num nonzero in file 1: {len(np.nonzero(qtable1.table)[0])}')
    print(f'Num nonzero in file 2: {len(np.nonzero(qtable2.table)[0])}')