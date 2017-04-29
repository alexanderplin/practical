# Imports.
import numpy as np
from collections import defaultdict

from SwingyMonkey import SwingyMonkey


class Learner(object):
    '''
    This agent jumps randomly.
    '''

    # Currently, the instance variables of the objects are in dictionary form, not tuple form

    def __init__(self):
        self.last_state  = None
        self.last_action = None
        self.last_reward = None
        self.epsilon = None
        self.eta = None
        self.Q = None
        self.C = None
        self.top_bin = None
        self.dist_bin = None
        self.gravity = None
        self.first = True
        self.counter = 0
        self.heurstics = 0
        self.last = None

    def reset(self):
        self.last_state  = None
        self.last_action = None
        self.last_reward = None
        self.first = True
        self.gravity = None
        self.counter = 0
        self.heurstics = 0
        self.last = None

    def to_tuple(self, state):
        '''
        Takes state from dictionary representation to tuple representation so that
        it can be hashed in our Q dictionary.
        returns new_state = (D, TD, G)
            D = binned distance from monkey to tree
            TD = binned difference between top of tree and top of monkey
            G = gravity
        '''
        new_state = []

        new_state.append(int(state['tree']['dist'] / self.dist_bin))

        top_diff = state['tree']['top'] - state['monkey']['top']
        new_state.append(int(top_diff / self.top_bin))
        new_state.append(state['monkey']['vel']/self.vel_bin)

        return tuple(new_state)

    def action_callback(self, state):
        '''
        Implement this function to learn things and take actions.
        Return 0 if you don't want to jump and 1 if you do.
        '''
        # Counting total number of actions in this epoch
        self.counter += 1
        ## Q dictionary update
        # self.last_state = s, self.last_action = a, self.last_reward = r, state = s'
        current_state = self.to_tuple(state)
        if self.last_state is not None:

            # Convert to tuples
            last_state = self.to_tuple(self.last_state)

            next_action = True if self.Q[current_state,True] > self.Q[current_state,False] else False

            # decrease epsilon by a proportion of the previous # of times that action was done
            if self.C[(current_state, next_action)] > 0:
                epsilon = self.epsilon/(self.C[(current_state, next_action)])
                eta=self.eta/(self.C[(last_state, last_state)]+1)
            else:
                epsilon=self.epsilon
                eta=self.eta

            if (np.random.uniform() < epsilon):
                if np.random.uniform() >= 0.95:
                    next_action=True
                else:
                    next_action=False

            # Update Q values
            self.Q[(last_state, self.last_action)] -= eta*(self.Q[(last_state, self.last_action)]-self.last_reward-self.gamma*max(self.Q[(current_state, True)], self.Q[(current_state, False)]))

        # If have not yet seen a state, randomly choose
        else:
            if np.random.uniform() >= 0.95:
                next_action=True
            else:
                next_action=False

        # Update last_action to the selected a'
        self.last_action = next_action
        # Update last_state to the current state s'
        self.last_state  = state
        self.C[(current_state,next_action)] += 1
        return self.last_action

    def reward_callback(self, reward):
        '''This gets called so you can see what reward you get.'''

        self.last_reward = reward


def run_games(learner, hist, top_bin_length, bot_bin_length, gamma, vel_bin, iters = 100, t_len = 100):
    '''
    Driver function to simulate learning by having the agent play a sequence of games.
    '''
    learner.vel_bin = vel_bin
    # Initalize dictionary for storing Q values and params
    Q = {}
    # # Q-values initialized to bias towards not jumping in low gravity and jumping in high gravity
    # for i in range(-100, 100):
    #     for j in range(-100, 100):
    #         Q[(i, j, 1), True] = -0.02
    #         Q[(i, j, 4), True] = -0.05
    learner.Q = defaultdict(int)
    learner.C = defaultdict(int)
    learner.top_bin = top_bin_length
    learner.dist_bin = bot_bin_length
    learner.gamma = gamma # Discount factor
    learner.epsilon = 0.001 # This percent of the time, choose a random action.
    learner.eta= 1 # learning rate

    for ii in range(iters):
        # Make a new monkey object.
        swing = SwingyMonkey(sound=False,                  # Don't play sounds.
                             text="Epoch %d" % (ii),       # Display the epoch on screen.
                             tick_length = t_len,          # Make game ticks super fast.
                             action_callback=learner.action_callback,
                             reward_callback=learner.reward_callback)

        # Loop until you hit something.
        while swing.game_loop():
            pass

        # print 'Iter {}: {} [{}] {}/{} last: {}'.format(ii, swing.score, learner.gravity, learner.heurstics, learner.counter, learner.last)

        # Save score history.
        hist.append(swing.score)

        # Reset the state of the learner.
        learner.reset()

    print 'Mean:', np.mean(hist)
    print 'Max:', np.max(hist)

    return np.mean(hist)


if __name__ == '__main__':

    # Select agent.
    agent = Learner()

    # Empty list to save history.
    hist = []

    # Run games.
    # top_bin_length_results = [[run_games(agent, hist, top_bin_length, 25, 0.25, iters = 50, t_len = 0) for top_bin_length in range(10,150,10)] for _ in range(0,5)]
    # print np.mean(np.array(top_bin_length_results), axis=0)

    # vert_bin_length_results = [[run_games(agent, hist, 110, vert_bin_length, 0.25, iters = 50, t_len = 0) for vert_bin_length in range(10,150,10)] for _ in range(0,5)]
    # print np.mean(np.array(vert_bin_length_results), axis=0)

    # gamma_results = [[run_games(agent, hist, 110, 130, gamma, iters = 50, t_len = 0) for gamma in [x/100.0 for x in range(0,201,5)]] for _ in range(0,5)]
    # print np.mean(np.array(gamma_results), axis=0)

    vel_bin_results = [[run_games(agent, hist, 110, 130, 0.25, vel_bin, iters = 50, t_len = 0) for vel_bin in range(1,101,10)] for _ in range(0,5)]
    print np.mean(np.array(vel_bin_results), axis=0)

    # Save history.
    np.savetxt('hist.csv', np.array(hist), fmt = '%u')
