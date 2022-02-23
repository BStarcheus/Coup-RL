def convert_obs_to_q_index(obs):
    '''
    Convert a CoupEnv observation into the
    state portion of the state-action index to the QTable

    obs: CoupEnv Observation
    '''
    # Ignore any instances of a player having 4 cards.
    # This is not stored in the QTable.

    # Collapse the 2 elements for cards into a single element
    # with only 15 possibilities, not 5*5=25
    # which reduces the overall state space.

    # Go from 25 -> 15 indicies by removing where card1 > card2, since they are always sorted.
    # card1 * 5 + card2 - (card1 * (card1+1))/2
    c1 = obs[0]
    c2 = obs[1]
    p1_cards = c1 * 5 + c2 - (c1 * (c1+1))//2 # // for int
    c1 = obs[4]
    c2 = obs[5]
    p2_cards = c1 * 5 + c2 - (c1 * (c1+1))//2 # // for int

    p1_face_up = obs[8] * 2 + obs[9]
    p2_face_up = obs[12] * 2 + obs[13]

    return [p1_cards, p2_cards, p1_face_up, p2_face_up, obs[16], obs[17]]
