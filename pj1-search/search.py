# search.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


"""
In search.py, you will implement generic search algorithms which are called by
Pacman agents (in searchAgents.py).
"""

import util
class node:
    """define node"""

    def __init__(self,state,parent,path_cost,action):
        self.state = state
        self.parent = parent
        self.path_cost = path_cost
        self.action = action



def solution(in_state,node):
    path = []
    while(node.state != in_state):
        path.append(node.action)
        node = node.parent
    path = path[::-1]
    return path
#node class
class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()


def tinyMazeSearch(problem):
    """
    Returns a sequence of moves that solves tinyMaze.  For any other maze, the
    sequence of moves will be incorrect, so only use this for tinyMaze.
    """
    from game import Directions
    s = Directions.SOUTH
    w = Directions.WEST
    return  [s, s, w, s, w, w, s, w]

def depthFirstSearch(problem):
    """
    Search the deepest nodes in the search tree first.

    Your search algorithm needs to return a list of actions that reaches the
    goal. Make sure to implement a graph search algorithm.

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print "Start:", problem.getStartState()
    print "Is the start a goal?", problem.isGoalState(problem.getStartState())
    print "Start's successors:", problem.getSuccessors(problem.getStartState())
    """
    node_start = node(problem.getStartState(),'',0,'')
    frontier = util.Stack()
    frontier.push(node_start.state)
    explored = []
    node_dic = {}
    node_iter = node_start
    node_dic[node_iter.state] = node_iter
    """
    if problem.isGoalState(node_iter.state):
        return solution(problem.getStartState(), node_iter)
    """
    while not frontier.isEmpty():
        state_iter = frontier.pop()
        node_iter = node_dic[state_iter]
        if problem.isGoalState(node_iter.state):
            return solution(problem.getStartState(), node_iter)
        if state_iter not in explored:
            explored.append(state_iter)
            successors = problem.getSuccessors(state_iter)
            for successror in successors:
                child_node = node(successror[0],node_iter,node_iter.path_cost+successror[2],successror[1])
                if child_node.state not in explored:
                    node_dic[child_node.state] = child_node
                    frontier.push(child_node.state)
                """
                if problem.isGoalState(child_node.state):
                    return solution(problem.getStartState(),child_node)
                """


def breadthFirstSearch(problem):
    
    node_start = node(problem.getStartState(),'',0,[])
    frontier = util.Queue()
    frontier.push(node_start)
    explored = []
    node_dic = {}
    node_iter = node_start

    
    while not frontier.isEmpty():
        iter = frontier.pop()
        state = iter.state
        path_cost = iter.path_cost
        action = iter.action

        if problem.isGoalState(state):
            return action
        if state not in explored:
            explored.append(state)
            successors = problem.getSuccessors(state)
            for successror in successors:
                child_node = node(successror[0],state,path_cost+successror[2],action+[successror[1]])
                frontier.push(child_node)
                


def uniformCostSearch(problem):
    """Search the node of least total cost first."""
    node_start = node(problem.getStartState(), '', 0, [])
    frontier = util.PriorityQueue()
    frontier.push(node_start,node_start.path_cost)
    explored = []
    node_dic = {}
    node_iter = node_start
    while not frontier.isEmpty():
        node_iter = frontier.pop()
        state = node_iter.state
        path_cost = node_iter.path_cost
        action = node_iter.action

        if problem.isGoalState(state):
            return action
        if state not in explored:
            explored.append(state)
            successors = problem.getSuccessors(state)
            for successror in successors:
                child_node = node(successror[0], state, path_cost + successror[2], action+[successror[1]])
                frontier.push(child_node,path_cost + successror[2])

def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0

def aStarSearch(problem, heuristic=nullHeuristic):
    """Search the node that has the lowest combined cost and heuristic first."""
    node_start = node(problem.getStartState(), '', heuristic(problem.getStartState(),problem), [])
    frontier = util.PriorityQueue()
    frontier.push(node_start,heuristic(problem.getStartState(),problem))
    explored = []
    node_iter = node_start
    while not frontier.isEmpty():
        node_iter = frontier.pop()
        state = node_iter.state
        path_cost = node_iter.path_cost
        action = node_iter.action
        if problem.isGoalState(state):
            return action
        if state not in explored:
            explored.append(state)
            successors = problem.getSuccessors(state)
            for successror in successors:
                child_node = node(successror[0], state, path_cost + successror[2], action+[successror[1]])
                frontier.push(child_node, child_node.path_cost + heuristic(child_node.state,problem))


# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
