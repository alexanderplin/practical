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

        new_state.append(int(self.gravity))

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
        if self.last_state is not None:

            # Infer gravity: if monkey moves much more than velocity suggests, then gravity is higher
            if self.first == True:
                self.gravity = state['monkey']['top'] - self.last_state['monkey']['top'] - state['monkey']['vel']
                self.first = False

            # Convert to tuples
            last_state = self.to_tuple(self.last_state)
            current_state = self.to_tuple(state)

            # Update Q values
            Q_sa = self.Q[(last_state, self.last_action)]
            Q_sa = Q_sa - self.eta*(Q_sa - (self.last_reward + self.gamma*max(self.Q[(current_state, True)], self.Q[(current_state, False)])))

            # Some heurstics: if monkey is very close to the top, always swing; if monkey is very close to the bottom, always jump (also skewed towards swinging)
            if state['tree']['top'] - state['monkey']['top'] <= 75:
                self.heurstics += 1
                self.last = 'heurstic'
                self.last_action = False
                return self.last_action
            if state['monkey']['bot'] - state['tree']['bot'] <= 10:
                self.heurstics += 1
                self.last = 'heurstic'
                self.last_action = True
                return self.last_action

            self.last = 'not heurstic'

            ## Select best action based on max_a' Q(s', a') with greedy epsilon
            a_ = True
            if self.Q[(current_state, a_)] > self.Q[(current_state, not(a_))]:
                best_a = a_
            elif self.Q[(current_state, a_)] < self.Q[(current_state, not(a_))]:
                best_a = not(a_)
            else: # Tiebreak randomly
                best_a = np.random.rand() >= 0.5

            if np.random.rand() >= self.epsilon:
                next_action = best_a
            else:
                next_action = not(best_a)

        # If have not yet seen a state, randomly choose
        else: 
            next_action = np.random.rand() >= 0.5

        # Update last_action to the selected a'
        self.last_action = next_action
        # Update last_state to the current state s'
        self.last_state  = state

        return self.last_action

    def reward_callback(self, reward):
        '''This gets called so you can see what reward you get.'''

        self.last_reward = reward


def run_games(learner, hist, iters = 100, t_len = 100):
    '''
    Driver function to simulate learning by having the agent play a sequence of games.
    '''

    # Initalize dictionary for storing Q values and params
    Q = {}
    # # Q-values initialized to bias towards not jumping in low gravity and jumping in high gravity
    # for i in range(-100, 100):
    #     for j in range(-100, 100):
    #         Q[(i, j, 1), True] = -0.02
    #         Q[(i, j, 4), True] = -0.05
    learner.Q = defaultdict(lambda: np.random.rand(), Q)
    learner.eta = 0.2
    learner.gamma = 1
    learner.top_bin = 20
    learner.dist_bin = 30

    for ii in range(iters):
        # Make a new monkey object.
        swing = SwingyMonkey(sound=False,                  # Don't play sounds.
                             text="Epoch %d" % (ii),       # Display the epoch on screen.
                             tick_length = t_len,          # Make game ticks super fast.
                             action_callback=learner.action_callback,
                             reward_callback=learner.reward_callback)

        base_epsilon = 0.05
        learner.epsilon = base_epsilon * (1/float(ii/10.0 + 1))

        # Loop until you hit something.
        while swing.game_loop():
            pass
        
        print 'Iter {}: {} [{}] {}/{} last: {}'.format(ii, swing.score, learner.gravity, learner.heurstics, learner.counter, learner.last) 

        # Save score history.
        hist.append(swing.score)

        # Reset the state of the learner.
        learner.reset()

    print 'Mean:', np.mean(hist)
    print 'Max:', np.max(hist)
        
    return


if __name__ == '__main__':

    # Select agent.
    agent = Learner()

    # Empty list to save history.
    hist = []

    # Run games. 
    run_games(agent, hist, iters = 100, t_len = 10)

    # Save history. 
    np.savetxt('hist.csv', np.array(hist), fmt = '%u')


