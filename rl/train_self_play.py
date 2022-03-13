import logging
import argparse
import time
from coup_rl import SelfPlay

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
        description='Coup RL Self-play Training\nCreate new agent: New filename, and add LR, DR, Epsilon\nUse existing: Existing filename\nModify existing: Existing filename, and add any param you want to change mid-training (LR, DF, Epsilon)')
    parser.add_argument('filepath', help='File path and name for agent to train')
    parser.add_argument('episodes', type=int, help='Number of episodes to train for')
    parser.add_argument('checkpoint', type=int, help='Number of episodes between saving the agent to a new file')
    parser.add_argument('--conv_eps', type=float, default=0.01, help='Convergence epsilon: Max average difference for convergence')
    parser.add_argument('--learning_rate', type=float, help='Learning Rate (0, 1]')
    parser.add_argument('--discount_factor', type=float, help='Discount Factor [0, 1]')
    parser.add_argument('--epsilon', type=float, help='Ratio of exploration [0, 1]')
    parser.add_argument('-d', '--debug', action='store_true', help='Log at the debug level')
    parser.add_argument('-t', '--timer', action='store_true', help='Time the entire training session')
    args = parser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.INFO

    sp = SelfPlay(args.filepath,
                  learning_rate=args.learning_rate,
                  discount_factor=args.discount_factor,
                  epsilon=args.epsilon,
                  log_level=log_level)

    if args.timer:
        start = time.time()

    sp.train(args.episodes, args.checkpoint, args.conv_eps)

    if args.timer:
        delta = time.time() - start
        print(f'Total training time for {args.episodes} episodes: {delta} seconds')
