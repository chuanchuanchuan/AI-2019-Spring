import util, math, random
from collections import defaultdict
from util import ValueIteration
import copy
############################################################
# Problem 2a

# If you decide 2a is true, prove it in blackjack.pdf and put "return None" for
# the code blocks below.  If you decide that 2a is false, construct a counterexample.
class CounterexampleMDP(util.MDP):
    def startState(self):
        # BEGIN_YOUR_CODE (our solution is 1 line of code, but don't worry if you deviate from this)

        return 0
        # END_YOUR_CODE

    # Return set of actions possible from |state|.
    def actions(self, state):
        # BEGIN_YOUR_CODE (our solution is 1 line of code, but don't worry if you deviate from this)
        return [-1,1]
        #return [-1, 1] if state == 0 else [state]
        # END_YOUR_CODE

    # Return a list of (newState, prob, reward) tuples corresponding to edges
    # coming out of |state|.
    def succAndProbReward(self, state, action):
        # BEGIN_YOUR_CODE (our solution is 1 line of code, but don't worry if you deviate from this)

        if action == -1:
            return [(state - 1, 0.9, -10), (state + 1, 0.1, 10)] if state not in [-2, 2] else [(state, 1, 0)]
        else:
            return [(state - 1, 0.8, -10), (state + 1, 0.2, 10)] if state not in [-2, 2] else [(state, 1, 0)]

        #return [(-1, 0.9, 0), (1, 0.1, 100)] if state == 0 else [(state, 1, 0)]
        # END_YOUR_CODE

    def discount(self):
        # BEGIN_YOUR_CODE (our solution is 1 line of code, but don't worry if you deviate from this)
        return 1
        # END_YOUR_CODE

############################################################
# Problem 3a

class BlackjackMDP(util.MDP):
    def __init__(self, cardValues, multiplicity, threshold, peekCost):
        """
        cardValues: array of card values for each card type
        multiplicity: number of each card type
        threshold: maximum total before going bust
        peekCost: how much it costs to peek at the next card
        """
        self.cardValues = cardValues
        self.multiplicity = multiplicity
        self.threshold = threshold
        self.peekCost = peekCost

    # Return the start state.
    # Look at this function to learn about the state representation.
    # The first element of the tuple is the sum of the cards in the player's
    # hand.
    # The second element is the index (not the value) of the next card, if the player peeked in the
    # last action.  If they didn't peek, this will be None.
    # The final element is the current deck.
    def startState(self):
        return (0, None, (self.multiplicity,) * len(self.cardValues))  # total, next card (if any), multiplicity for each card

    # Return set of actions possible from |state|.
    # You do not need to modify this function.
    # All logic for dealing with end states should be done in succAndProbReward
    def actions(self, state):
        return ['Take', 'Peek', 'Quit']

    # Return a list of (newState, prob, reward) tuples corresponding to edges
    # coming out of |state|.  Indicate a terminal state (after quitting or
    # busting) by setting the deck to None. 
    # When the probability is 0 for a particular transition, don't include that 
    # in the list returned by succAndProbReward.
    def succAndProbReward(self, state, action):
        # BEGIN_YOUR_CODE (our solution is 53 lines of code, but don't worry if you deviate from this)
        #game over
        if state[2] == None: return []
        triples = []
        if action == 'Take':
            left_cards = sum(state[2])
            if state[1] != None:
                reward = 0
                new_deckCardCounts = list(copy.copy(state[2]))
                new_deckCardCounts[state[1]] = new_deckCardCounts[state[1]] - 1
                new_deckCardCounts = tuple(new_deckCardCounts)
                new_totalCardValueInHand = state[0] + self.cardValues[state[1]]
                new_nextCardIndexIfPeeked = None
                if sum(new_deckCardCounts) == 0:
                    new_deckCardCounts = None
                    reward = new_totalCardValueInHand
                if new_totalCardValueInHand > self.threshold:
                    new_deckCardCounts = None
                    reward = 0
                triples.append(((new_totalCardValueInHand, new_nextCardIndexIfPeeked, new_deckCardCounts),
                                    1, reward))
                return triples
            for i in range(len(state[2])):
                if state[2][i] == 0:continue
                reward = 0
                new_deckCardCounts = list(copy.copy(state[2]))
                new_deckCardCounts[i] = new_deckCardCounts[i] - 1
                new_deckCardCounts = tuple(new_deckCardCounts)
                new_totalCardValueInHand = state[0] + self.cardValues[i]
                new_nextCardIndexIfPeeked = None
                if sum(new_deckCardCounts) == 0:
                    new_deckCardCounts = None
                    reward = new_totalCardValueInHand
                if new_totalCardValueInHand > self.threshold:
                    new_deckCardCounts = None
                    reward = 0
                triples.append(((new_totalCardValueInHand,new_nextCardIndexIfPeeked,new_deckCardCounts),state[2][i]/float(left_cards),reward))
            return triples
        if action == 'Quit':
            triples.append(((state[0],None,None),1,state[0]))
            return triples
        if action == 'Peek':
            left_cards = sum(state[2])
            if state[1] != None:return triples
            for i in range(len(state[2])):
                if state[2][i] == 0:continue
                reward = self.peekCost
                new_nextCardIndexIfPeeked = i
                triples.append(((state[0],new_nextCardIndexIfPeeked,state[2]),state[2][i]/float(left_cards),-reward))
            return triples
        # END_YOUR_CODE

    def discount(self):
        return 1

############################################################
# Problem 3b

def peekingMDP():
    """
    Return an instance of BlackjackMDP where peeking is the optimal action at
    least 10% of the time.
    """
    # BEGIN_YOUR_CODE (our solution is 2 lines of code, but don't worry if you deviate from this)
    cardValues = [2,3,4,20]
    return BlackjackMDP(cardValues,4,20,1)
    # END_YOUR_CODE

############################################################
# Problem 4a: Q learning

# Performs Q-learning.  Read util.RLAlgorithm for more information.
# actions: a function that takes a state and returns a list of actions.
# discount: a number between 0 and 1, which determines the discount factor
# featureExtractor: a function that takes a state and action and returns a list of (feature name, feature value) pairs.
# explorationProb: the epsilon value indicating how frequently the policy
# returns a random action
class QLearningAlgorithm(util.RLAlgorithm):
    def __init__(self, actions, discount, featureExtractor, explorationProb=0.2):
        self.actions = actions
        self.discount = discount
        self.featureExtractor = featureExtractor
        self.explorationProb = explorationProb
        self.weights = defaultdict(float)
        self.numIters = 0

    # Return the Q function associated with the weights and features
    def getQ(self, state, action):
        score = 0
        for f, v in self.featureExtractor(state, action):
            score += self.weights[f] * v
        return score

    # This algorithm will produce an action given a state.
    # Here we use the epsilon-greedy algorithm: with probability
    # |explorationProb|, take a random action.
    def getAction(self, state):
        self.numIters += 1
        if random.random() < self.explorationProb:
            return random.choice(self.actions(state))
        else:
            return max((self.getQ(state, action), action) for action in self.actions(state))[1]

    # Call this function to get the step size to update the weights.
    def getStepSize(self):
        return 1.0 / math.sqrt(self.numIters)

    # We will call this function with (s, a, r, s'), which you should use to update |weights|.
    # Note that if s is a terminal state, then s' will be None.  Remember to check for this.
    # You should update the weights using self.getStepSize(); use
    # self.getQ() to compute the current estimate of the parameters.
    def incorporateFeedback(self, state, action, reward, newState):
        # BEGIN_YOUR_CODE (our solution is 12 lines of code, but don't worry if you deviate from this)
        newState_maxQ = 0
        if newState != None:
            newState_maxQ = max((self.getQ(newState, newaction), newaction) for newaction in self.actions(newState))[0]
        Q =  self.getQ(state, action)
        discount = self.discount
        difference = reward + discount * newState_maxQ - Q
        alpha = self.getStepSize()
        for f, v in self.featureExtractor(state, action):
            self.weights[f] = self.weights[f] + alpha * difference * v
        # END_YOUR_CODE

# Return a singleton list containing indicator feature for the (state, action)
# pair.  Provides no generalization.
def identityFeatureExtractor(state, action):
    featureKey = (state, action)
    featureValue = 1
    return [(featureKey, featureValue)]

############################################################
# Problem 4b: convergence of Q-learning
# Small test case
"""
smallMDP = BlackjackMDP(cardValues=[1, 5], multiplicity=2, threshold=10, peekCost=1)
alg = util.ValueIteration()
alg.solve(smallMDP, .0001)
pi = alg.pi
RL = QLearningAlgorithm(smallMDP.actions,smallMDP.discount(),identityFeatureExtractor)
util.simulate(smallMDP, RL, numTrials=30000, maxIterations=1000, verbose=False,sort=False)
RL.explorationProb = 0
piRL = {}
for state in smallMDP.states:
    piRL[state] = RL.getAction(state)
intersection = [1 if piRL[x] == pi[x] else 0 for x in piRL]
print(float(sum(intersection))/len(intersection))
"""
"""
# Large test case
largeMDP = BlackjackMDP(cardValues=[1, 3, 5, 8, 10], multiplicity=3, threshold=40, peekCost=1)
largeMDP.computeStates()
alg = util.ValueIteration()
alg.solve(largeMDP, .0001)
pi = alg.pi
RL = QLearningAlgorithm(largeMDP.actions,largeMDP.discount(),identityFeatureExtractor)
util.simulate(largeMDP, RL, numTrials=30000, maxIterations=1000, verbose=False,sort=False)
RL.explorationProb = 0
piRL = {}
for state in largeMDP.states:
    piRL[state] = RL.getAction(state)
intersection = [1 if piRL[x] == pi[x] else 0 for x in piRL]
print(float(sum(intersection))/len(intersection))
"""

############################################################
# Problem 4c: features for Q-learning.

# You should return a list of (feature key, feature value) pairs (see
# identityFeatureExtractor()).
# Implement the following features:
# - indicator on the total and the action (1 feature).
# - indicator on the presence/absence of each card and the action (1 feature).
#       Example: if the deck is (3, 4, 0 , 2), then your indicator on the presence of each card is (1,1,0,1)
#       Only add this feature if the deck != None
# - indicator on the number of cards for each card type and the action (len(counts) features).  Only add these features if the deck != None
def blackjackFeatureExtractor(state, action):
    total, nextCard, counts = state
    # BEGIN_YOUR_CODE (our solution is 9 lines of code, but don't worry if you deviate from this)
    result = []
    result.append(((total,action),1))
    if counts != None:
        presence = (1 if counts[i] else 0 for i in range(len(counts)))
        #just iterator
        result.append(((tuple(presence),action),1))
    if counts != None:
        for i in range(len(counts)):
            result.append(((i,counts[i],action),1))
    return result

    # END_YOUR_CODE

############################################################
# Problem 4d: What happens when the MDP changes underneath you?!

# Original mdp
"""
originalMDP = BlackjackMDP(cardValues=[1, 5], multiplicity=2, threshold=10, peekCost=1)
alg = util.ValueIteration()
alg.solve(originalMDP, .0001)
pi = alg.pi

# New threshold
newThresholdMDP = BlackjackMDP(cardValues=[1, 5], multiplicity=2, threshold=15, peekCost=1)
#rl = util.FixedRLAlgorithm(pi)
rl = QLearningAlgorithm(newThresholdMDP.actions,newThresholdMDP.discount(),identityFeatureExtractor)
rewards = util.simulate(newThresholdMDP, rl, numTrials=30000, maxIterations=1000, verbose=False,sort=False)
print rewards
"""