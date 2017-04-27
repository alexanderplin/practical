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
        self.alpha = None
        self.Q = None
        self.top_bin = None
        self.dist_bin = None

    def reset(self):
        self.last_state  = None
        self.last_action = None
        self.last_reward = None

    def to_tuple(self, state):
        '''
        Takes state from dictionary representation to tuple representation so that
        it can be hashed in our Q dictionary.
        returns new_state = (D, TD)
            D = binned distance from monkey to tree
            TD = binned difference between top of tree and top of monkey
        '''
        new_state = []

        new_state.append(int(state['tree']['dist'] / self.dist_bin))

        top_diff = state['tree']['top'] - state['monkey']['top']
        new_state.append(int(top_diff / self.top_bin))

        return tuple(new_state)

    def action_callback(self, state):
        '''
        Implement this function to learn things and take actions.
        Return 0 if you don't want to jump and 1 if you do.
        '''

        ## Q dictionary update
        # self.last_state = s, self.last_action = a, self.last_reward = r, state = s'
        if self.last_state is not None:
            # Convert to tuples
            last_state = self.to_tuple(self.last_state)
            current_state = self.to_tuple(state)

            # Update Q values
            Q_sa = self.Q[(last_state, self.last_action)]
            Q_sa = Q_sa + self.alpha*(self.last_reward + self.gamma*max(self.Q[(current_state, True)], self.Q[(current_state, False)]) - Q_sa)

            # Infer gravity: If the (post-binned) state is the same after you jump, likely means that you both jump slowly and fall slowly. Therefore, the monkey should NOT jump, since it's still falling slowly (unless it hits this threshold), and if it jumps slowly, then it might double jump and go very high and hit something.
            falling_threshold = 10
            if last_state == current_state:
                if state['monkey']['bot'] - state['tree']['bot'] >= falling_threshold:
                    self.last_action = False
                    return self.last_action

            # Beyond inferring gravity, some heurstics: if monkey is very close to the top, always swing; if monkey is very close to the bottom, always jump (also skewed towards swinging)
            if state['tree']['top'] - state['monkey']['top'] <= 75:
                self.last_action = False
                return self.last_action
            if state['monkey']['bot'] - state['tree']['bot'] <= 10:
                self.last_action = True
                return self.last_action
            

            ## Select best action based on max_a' Q(s', a') with greedy epsilon
            a_ = True
            if self.Q[(current_state, a_)] > self.Q[(current_state, not(a_))]:
                best_a = a_
            elif self.Q[(current_state, a_)] < self.Q[(current_state, not(a_))]:
                best_a = not(a_)
            else: # Tiebreak towards not jumping
                best_a = False

            if np.random.rand() >= self.epsilon:
                next_action = best_a
            else:
                next_action = not(best_a)

            ## Calculate probability based on Boltzmann distribution (softmax action selection)
            # Unsure how to determine annealing schedule ?? Didn't seem that much different than tweaking greedy epsilon
            # action_probs = []
            # for a_ in [False, True]:
            #     action_probs[a_] = np.exp(self.Q[(current_state, a_)]/self.temp)
            # action_probs = np.true_divide(action_probs, np.sum(action_probs))
            # print action_probs
            # if np.random.rand() <= action_probs[False]:
            #     next_action = False
            # else:
            #     next_action = True

        # If have not yet seen a state, choose to not jump
        else: 
            next_action = False

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

    # Initalize dictionary for storing Q values (default = random) and params
    Q = {}
    learner.Q = defaultdict(lambda: np.random.rand(), Q)
    learner.alpha = 0.2
    learner.gamma = 1
    learner.top_bin = 30
    learner.dist_bin = 30
    learner.epsilon = 0.1

    for ii in range(iters):
        # Make a new monkey object.
        swing = SwingyMonkey(sound=False,                  # Don't play sounds.
                             text="Epoch %d" % (ii),       # Display the epoch on screen.
                             tick_length = t_len,          # Make game ticks super fast.
                             action_callback=learner.action_callback,
                             reward_callback=learner.reward_callback)

        base_epsilon = 0.1
        learner.epsilon = base_epsilon * (1/float(ii + 1))

        # Loop until you hit something.
        while swing.game_loop():
            pass
        
        print ii, swing.score

        # Save score history.
        hist.append(swing.score)

        # Reset the state of the learner.
        learner.reset()
        
    return


if __name__ == '__main__':

	# Select agent.
	agent = Learner()

	# Empty list to save history.
	hist = []

	# Run games. 
	run_games(agent, hist, iters = 100, t_len = 1)

	# Save history. 
	np.savetxt('hist.csv', np.array(hist), fmt = '%u')


