# myTeam.py
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


from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first='DummyAgent', second='DummyAgent'):
    """
    This function should return a list of two agents that will form the
    team, initialized using firstIndex and secondIndex as their agent
    index numbers.  isRed is True if the red team is being created, and
    will be False if the blue team is being created.

    As a potentially helpful development aid, this function can take
    additional string-valued keyword arguments ("first" and "second" are
    such arguments in the case of this function), which will come from
    the --redOpts and --blueOpts command-line arguments to capture.py.
    For the nightly contest, however, your team will be created without
    any extra arguments, so you should make sure that the default
    behavior is what you want for the nightly contest.
    """

    # The following line is an example only; feel free to change it.
    # return [eval("TrainAgent")(index = firstIndex,extractor = "MyFeatureExtractor"), eval(second)(index = secondIndex)]
    return [eval(first)(index=firstIndex), eval(second)(index=secondIndex)]


##########
# Agents #
##########



class DummyAgent(CaptureAgent):
    """
    A Dummy agent to serve as an example of the necessary agent structure.
    You should look at baselineTeam.py for more details about how to
    create an agent as this is the bare minimum.
    """

    def initCapsules(self, gameState):
        self.OpCapsules = self.getCapsules(gameState)
        self.DeCapsules = self.getCapsulesYouAreDefending(gameState)

    def registerInitialState(self, gameState):
        """
        This method handles the initial setup of the
        agent to populate useful fields (such as what team
        we're on).

        A distanceCalculator instance caches the maze distances
        between each pair of positions, so your agents can use:
        self.distancer.getDistance(p1, p2)

        IMPORTANT: This method may run for at most 15 seconds.
        """
        self.walls = gameState.getWalls().data
        self.initCapsules(gameState)
        self.goHome = False
        self.stage = 0
        self.startPostion = gameState.getInitialAgentPosition(self.index)

        self.width = gameState.getWalls().width
        self.height = gameState.getWalls().height
        self.foodNum = len(self.getFood(gameState).asList())

        self.bePersuitedTime = 0
        self.teamMap = {}
        self.teamMap[0] = 2
        self.teamMap[1] = 3
        self.teamMap[2] = 0
        self.teamMap[3] = 1

        '''
        Make sure you do not delete the following line. If you would like to
        use Manhattan distances instead of maze distances in order to save
        on initialization time, please take a look at
        CaptureAgent.registerInitialState in captureAgents.py.
        '''

        CaptureAgent.registerInitialState(self, gameState)

        self.weights = util.Counter()
        self.weights["can_be_captured"] = -2580.941410881
        self.weights["closest-food"] = -258.941410881
        self.weights["bias"] = -258.941410881
        self.weights["eats-food"] = 147.237783878
        self.weights["#-of-ghosts-1-step-away"] = -2580.941410881
        # self.weights["team_dis"] = -256.941410881
        self.weights["from_mid"] = -25.941410881

        self.verticleDirection = set([Directions.NORTH, Directions.SOUTH, Directions.STOP])

        self.northEntrance = self.getNorthEntrance()
        self.southEntrance = self.getSouthEntrance()
        # self.weights2 = util.Counter()
        # self.weights2["closest-food"] = -258.941410881
        # self.weights2["bias"] = -258.941410881

        '''
        Your initialization code goes here, if you need any.
        '''

        self.caveDis = {}

        self.caveSet = set()
        self.caveEntry = set()
        # self.caveExit =set()

        for i in range(len(self.walls)):
            for j in range(len(self.walls[0])):
                if not self.walls[i][j]:
                    self.myHandle(i, j)

        for i in range(len(self.walls)):
            for j in range(len(self.walls[0])):
                if not self.walls[i][j]:
                    self.myBFS2(i, j)

        for c in list(self.caveSet):
            if (c[0] - 1, c[1]) not in self.caveSet and not self.walls[c[0] - 1][c[1]]:
                self.caveEntry.add(c)
                continue
            if (c[0] + 1, c[1]) not in self.caveSet and not self.walls[c[0] + 1][c[1]]:
                self.caveEntry.add(c)
                continue
            if (c[0], c[1] - 1) not in self.caveSet and not self.walls[c[0]][c[1] - 1]:
                self.caveEntry.add(c)
                continue
            if (c[0], c[1] + 1) not in self.caveSet and not self.walls[c[0]][c[1] + 1]:
                self.caveEntry.add(c)
                continue

        for c in list(self.caveEntry):
            self.tempset = set()
            self.tempcount = 0
            self.myBFS(c[0], c[1], 1, c)
            # util.raiseNotDefined()

    def myHandle(self, x, y):
        self.target = (x, y)

        self.tempset = set()
        self.tempcount = 0
        if not self.myDFS(x, y - 1):
            return

        self.tempset = set()
        self.tempcount = 0
        if not self.myDFS(x, y + 1):
            return

        self.tempset = set()
        self.tempcount = 0
        if not self.myDFS(x - 1, y):
            return

        self.tempset = set()
        self.tempcount = 0
        if not self.myDFS(x + 1, y):
            return

        self.caveSet.add((x, y))

    def myBFS2(self, i, j):
        pre = set([(i, j)])
        tempss = set()
        while len(pre) > 0:
            temp = set()
            for c in list(pre):
                if self.walls[c[0]][c[1]]:
                    continue
                if c in self.caveSet:
                    continue
                tempss.add(c)
                if self.isInMyArea(c):
                    return
                temp.add((c[0], c[1] - 1))
                temp.add((c[0], c[1] + 1))
                temp.add((c[0] - 1, c[1]))
                temp.add((c[0] + 1, c[1]))

            pre = temp - tempss
        self.caveSet.add((i,j))

    def myBFS(self, i, j, distance, caveEntry):
        pre = set([(i, j)])
        while len(pre) > 0:
            temp = set()
            for c in list(pre):
                if c not in self.caveSet:
                    continue
                if c in self.tempset:
                    continue
                self.tempset.add(c)
                self.caveDis[c[0], c[1]] = (distance, caveEntry)
                temp.add((c[0], c[1] - 1))
                temp.add((c[0], c[1] + 1))
                temp.add((c[0] - 1, c[1]))
                temp.add((c[0] + 1, c[1]))
            pre = temp
            distance += 1

    def myDFS(self, i, j):
        if self.walls[i][j]:
            return True
        if (i, j) == self.target:
            self.tempcount += 1
            if self.tempcount == 2:
                return False
            return True
        if (i, j) in self.tempset:
            return True
        self.tempset.add((i, j))
        if not self.myDFS(i + 1, j):
            return False
        if not self.myDFS(i, j + 1):
            return False
        if not self.myDFS(i - 1, j):
            return False
        if not self.myDFS(i, j - 1):
            return False
        return True

    def handleState(self, state):
        ghostIndexList = self.getOpponents(state)
        myPos = state.getAgentPosition(self.index)
        if self.getDistanceFromGhost(state, myPos, ghostIndexList) > 6:
            self.goHome = False
            self.bePersuitedTime = 0
        else:
            self.bePersuitedTime += 1

        if self.index > 1:
            if self.index == 2:
                temp = 0
            else:
                temp = 1
            if self.getMazeDistance(myPos, state.getAgentPosition(temp)) <= 1 and not self.isInMyArea(myPos):
                self.goHome = True

    def getLineDefenceAction(self, state):
        actions = state.getLegalActions(self.index)
        return max([[self.getDefendActionValue(state, action), action] for action in actions])[1]

    def chooseAction(self, gameState):
        """
        Picks among actions randomly.
        """
        # print gameState.getAgentDistances()
        foods = self.getFoodYouAreDefending(gameState)


        self.handleState(gameState)
        currentPos = gameState.getAgentPosition(self.index)
        ghostIndexList = self.getOpponents(gameState)

        if self.getDisFromMid(currentPos[0]) ==1:
            self.stage = 1
        teampos =gameState.getAgentPosition(self.teamMap[self.index])
        if self.canOberserveOppo(gameState, currentPos, ghostIndexList):
            if self.index <2 and self.canOberserveOppo(gameState,teampos , ghostIndexList):
                self.stage = 0
            else:
                if self.isInMyArea(currentPos):
                    return self.getLineDefenceAction(gameState)

        actions = gameState.getLegalActions(self.index)
        # print [[self.getQValue(gameState, action), action] for action in actions]
        action = max([[self.getQValue(gameState, action), action] for action in actions])[1]
        return action

    def getDefendAction(self, state):
        actions = state.getLegalActions(self.index)
        return max([[self.getDefendActionValue(state, action), action] for action in actions])[1]

    def getDefendActionValue(self, state, action):
        x, y = state.getAgentPosition(self.index)
        dx, dy = Actions.directionToVector(action)
        nextPos = (int(x + dx), int(y + dy))
        if self.isInMyArea(nextPos):
            return self.getWeights2() * self.getFeatures2(state, action)
        else:
            return -100000

    def canOberserveOppo(self, state, nextPos, ghostIndexList):
        result = 10
        for gindex in ghostIndexList:
            if state.getAgentState(gindex).scaredTimer > 1:
                continue
            g = state.getAgentPosition(gindex)
            if g == None:
                continue
            result = min(result, self.getMazeDistance(g, nextPos))
        return result < 6

    def isInMyArea(self, pos):
        # print pos,self.width,self.red
        if self.red:
            return pos[0] < self.width / 2
        else:
            return pos[0] >= self.width / 2

    def getDisFromMid(self, x):
        if self.red:
            return abs(x - self.width / 2 + 1) + 1
        else:
            return abs(x - self.width / 2) + 1

    def getFeatures2(self, state, action):
        # extract the grid of food and wall locations and get the ghost locations
        foods = self.getFoodYouAreDefending(state)
        x, y = state.getAgentPosition(self.index)
        dx, dy = Actions.directionToVector(action)
        next_x, next_y = int(x + dx), int(y + dy)

        walls = state.getWalls()
        opposIndex = self.getOpponents(state)
        oppoPostions = [state.getAgentPosition(c) for c in opposIndex]

        features = util.Counter()

        features["bias"] = 1.0

        features["from_mid"] = self.getDisFromMid(next_x)

        for oppo in oppoPostions:
            if oppo == None:
                continue
            else:
                if self.isInMyArea(oppo):
                    temp = self.getMazeDistance((next_x, next_y), oppo)
                    features["closest-food"] = float(temp) / (walls.width * walls.height)
                    break
        else:
            temp = [self.getMazeDistance((next_x, next_y), food) for food in foods.asList()]
            if len(temp) != 0:
                features["closest-food"] = float(min(temp)) / (walls.width * walls.height)

        next_x, next_y = int(x + dx), int(y + dy)
        if (next_x, next_y) in self.caveDis:
            caveDis, caveEntry = self.caveDis[next_x, next_y]
            for ghost in opposIndex:
                if state.getAgentPosition(ghost) != None:
                    if state.getAgentState(self.index).scaredTimer > 0:
                        if caveDis >= self.getMazeDistance(state.getAgentPosition(ghost), caveEntry) - 2:
                            features["can_be_captured"] = 1
                            break
            else:
                features["can_be_captured"] = 0
        if state.getAgentState(self.index).scaredTimer > 0:
            features["#-of-ghosts-1-step-away"] = sum(
                (next_x, next_y) in Actions.getLegalNeighbors(g, walls) for g in oppoPostions if g != None)

        return features

    def getWeights2(self):
        return self.weights


    def getQValue(self, state, action):
        result = self.getWeights() * self.getFeatures(state, action)
        # print(action,self.getFeatures(state, action))
        return result

    def getWeights(self):
        return self.weights

    def getDistanceFromGhost(self, state, nextPos, ghostIndexList):
        result = 10
        for gindex in ghostIndexList:
            if state.getAgentState(gindex).scaredTimer > 1:
                continue
            g = state.getAgentPosition(gindex)
            if g == None:
                continue
            result = min(result, self.getMazeDistance(g, nextPos))
        return result

    def getFeatures(self, state, action):
        # print self.caveEntry
        # print (23,4) in self.caveSet
        # extract the grid of food and wall locations and get the ghost locations
        food = self.getFood(state)
        x, y = state.getAgentPosition(self.index)
        dx, dy = Actions.directionToVector(action)
        next_x, next_y = int(x + dx), int(y + dy)

        walls = state.getWalls()
        ghostIndexList = self.getOpponents(state)
        ghostPositions = [state.getAgentPosition(g) for g in ghostIndexList]

        features = util.Counter()

        features["bias"] = 1.0

        # compute the location of pacman after he takes the x

        if (next_x, next_y) in self.caveDis:
            caveDis, caveEntry = self.caveDis[next_x, next_y]
            for ghost in ghostIndexList:
                temp = state.getAgentPosition(ghost)
                if  temp != None:
                    if state.getAgentState(ghost).scaredTimer < 5:
                        if self.getMazeDistance((next_x,next_y),temp) > 5:
                            continue

                        if caveDis >= self.getMazeDistance(temp, caveEntry) - 2:
                            features["can_be_captured"] = 1
                            break
            else:
                features["can_be_captured"] = 0

        # count the number of ghosts 1-step away
        features["#-of-ghosts-1-step-away"] = 0
        for ghost in ghostIndexList:
            if state.getAgentPosition(ghost) != None:
                if state.getAgentState(ghost).scaredTimer < 3:
                    if (next_x, next_y) in Actions.getLegalNeighbors(state.getAgentPosition(ghost), walls):
                        if not self.isInMyArea((next_x, next_y)):
                            features["#-of-ghosts-1-step-away"] += 1
                        else:
                            if state.getAgentState(self.index).scaredTimer > 0:
                                features["#-of-ghosts-1-step-away"] += 1


        if not features["can_be_captured"] and food[next_x][next_y]:
            features["eats-food"] = 1.0
        if len(food.asList()) < 3:
            features["eats-food"] = 1.0

        if self.goHome:
            features["closest-food"] = self.getHomeDis((next_x, next_y), walls)
        elif state.data.timeleft < 80:
            self.goHome = True
            features["closest-food"] = self.getHomeDis((next_x, next_y), walls)
        elif self.bePersuitedTime > 20:
            # print (next_x,next_y),self.getHomeDis((next_x, next_y), walls),features
            features["closest-food"] = self.getHomeDis((next_x, next_y), walls)
        else:
            if self.index < 2:
                if self.isInMyArea((next_x, next_y)) and self.stage == 0:
                    dist = self.getMazeDistance((next_x,next_y),self.southEntrance)
                else:
                    dist = self.SouthClosestFood((next_x, next_y), food, walls)
                if dist is not None:
                    # make the distance a number less than one otherwise the update
                    # will diverge wildly
                    features["closest-food"] = float(dist) / (walls.width * walls.height)

            else:
                # if self.isInMyArea((next_x, next_y)) and self.stage == 0:
                #     dist = self.getMazeDistance((next_x, next_y), self.southEntrance)
                # else:
                dist = self.NorthClosestFood((next_x, next_y), food, walls)
                if dist is not None:
                    # make the distance a number less than one otherwise the update
                    # will diverge wildly
                    features["closest-food"] = float(dist) / (walls.width * walls.height)

        features.divideAll(10.0)
        return features

    def getSouthEntrance(self):
        if self.red:
            for y in range(self.height):
                if not self.walls[self.width / 2][y]:
                    return (self.width / 2, y)
        else:
            for y in range(self.height):
                if not self.walls[self.width / 2 - 1][y]:
                    return (self.width / 2 - 1, y)

    def getNorthEntrance(self):
        if self.red:
            for y in range(self.height - 1, -1, -1):
                if not self.walls[self.width / 2][y]:
                    return (self.width / 2, y)
        else:
            for y in range(self.height - 1, -1, -1):
                if not self.walls[self.width / 2 - 1][y]:
                    return (self.width / 2 - 1, y)

    def predictTeamMemberPos(self, state):
        temp = self.index
        self.index = self.teamMap[temp]
        tempaction = self.chooseAction(state)
        x, y = state.getAgentPosition(self.index)
        dx, dy = Actions.directionToVector(tempaction)
        next_x, next_y = int(x + dx), int(y + dy)
        self.index = temp
        return (next_x, next_y)

    def SouthClosestFood(self, pos, food, walls):
        if isinstance(food, tuple):
            return self.getMazeDistance(pos, food)
        foods = food.asList()
        if len(foods) < 3:
            return self.getHomeDis(pos, walls)
        temp = [self.getMazeDistance(pos, food) for food in foods if food[1] < walls.height / 2]
        if len(temp) == 0:
            return self.NorthClosestFood(pos, food, walls)
        return min(temp)

    def NorthClosestFood(self, pos, food, walls):
        if isinstance(food, tuple):
            return self.getMazeDistance(pos, food)
        foods = food.asList()
        if len(foods) < 3:
            return self.getHomeDis(pos, walls)
        temp = [self.getMazeDistance(pos, food) for food in foods if food[1] >= walls.height / 2]
        if len(temp) == 0:
            return self.SouthClosestFood(pos, food, walls)
        return min(temp)

    # def getHomeDis(self, pos, walls):
    #     if self.red:
    #         x = self.width / 2 - 1
    #     else:
    #         x = self.width / 2
    #
    #     return min([self.getMazeDistance(pos, (x, y)) for y in range(0, walls.height) if not walls[x][y]])

    def getHomeDis(self, pos, walls):
        if self.red:
            x = self.width / 2 - 1
        else:
            x = self.width / 2

        if self.index > 1:
            h2 = 7*walls.height/8
            h1 = 5*walls.height/8
        else:
            h1 = walls.height/8
            h2 = 3*walls.height/8

        temp = [self.getMazeDistance(pos, (x, y)) for y in range(h1,h2) if not walls[x][y]]
        if len(temp) == 0:
            return min([self.getMazeDistance(pos, (x, y)) for y in range(0, walls.height) if not walls[x][y]])
        return min(temp)


    def closestFood(self, pos, food, walls):
        """
        closestFood -- this is similar to the function that we have
        worked on in the search project; here its all in one place
        """
        fringe = [(pos[0], pos[1], 0)]
        expanded = set()
        while fringe:
            pos_x, pos_y, dist = fringe.pop(0)
            if (pos_x, pos_y) in expanded:
                continue
            expanded.add((pos_x, pos_y))
            # if we find a food at this location then exit
            if food[pos_x][pos_y]:
                return dist
            # otherwise spread out from the location to its neighbours
            nbrs = Actions.getLegalNeighbors((pos_x, pos_y), walls)
            for nbr_x, nbr_y in nbrs:
                fringe.append((nbr_x, nbr_y, dist + 1))
        # no food found
        return None


class DefendAgent(CaptureAgent):
    """
    A Dummy agent to serve as an example of the necessary agent structure.
    You should look at baselineTeam.py for more details about how to
    create an agent as this is the bare minimum.
    """

    def registerInitialState(self, gameState):
        """
        This method handles the initial setup of the
        agent to populate useful fields (such as what team
        we're on).

        A distanceCalculator instance caches the maze distances
        between each pair of positions, so your agents can use:
        self.distancer.getDistance(p1, p2)

        IMPORTANT: This method may run for at most 15 seconds.
        """

        '''
        Make sure you do not delete the following line. If you would like to
        use Manhattan distances instead of maze distances in order to save
        on initialization time, please take a look at
        CaptureAgent.registerInitialState in captureAgents.py.
        '''
        CaptureAgent.registerInitialState(self, gameState)

        '''
        Your initialization code goes here, if you need any.
        '''

    def chooseAction(self, gameState):
        """
        Picks among actions randomly.
        """
        actions = gameState.getLegalActions(self.index)

        '''
        You should change this in your own agent.
        '''

        return random.choice(actions)


class Actions:
    """
    A collection of static methods for manipulating move actions.
    """
    # Directions
    _directions = {Directions.NORTH: (0, 1),
                   Directions.SOUTH: (0, -1),
                   Directions.EAST: (1, 0),
                   Directions.WEST: (-1, 0),
                   Directions.STOP: (0, 0)}

    _directionsAsList = _directions.items()

    TOLERANCE = .001

    def reverseDirection(action):
        if action == Directions.NORTH:
            return Directions.SOUTH
        if action == Directions.SOUTH:
            return Directions.NORTH
        if action == Directions.EAST:
            return Directions.WEST
        if action == Directions.WEST:
            return Directions.EAST
        return action

    reverseDirection = staticmethod(reverseDirection)

    def vectorToDirection(vector):
        dx, dy = vector
        if dy > 0:
            return Directions.NORTH
        if dy < 0:
            return Directions.SOUTH
        if dx < 0:
            return Directions.WEST
        if dx > 0:
            return Directions.EAST
        return Directions.STOP

    vectorToDirection = staticmethod(vectorToDirection)

    def directionToVector(direction, speed=1.0):
        dx, dy = Actions._directions[direction]
        return (dx * speed, dy * speed)

    directionToVector = staticmethod(directionToVector)

    def getPossibleActions(config, walls):
        possible = []
        x, y = config.pos
        x_int, y_int = int(x + 0.5), int(y + 0.5)

        # In between grid points, all agents must continue straight
        if (abs(x - x_int) + abs(y - y_int) > Actions.TOLERANCE):
            return [config.getDirection()]

        for dir, vec in Actions._directionsAsList:
            dx, dy = vec
            next_y = y_int + dy
            next_x = x_int + dx
            if not walls[next_x][next_y]: possible.append(dir)

        return possible

    getPossibleActions = staticmethod(getPossibleActions)

    def getLegalNeighbors(position, walls):
        x, y = position
        x_int, y_int = int(x + 0.5), int(y + 0.5)
        neighbors = []
        for dir, vec in Actions._directionsAsList:
            dx, dy = vec
            next_x = x_int + dx
            if next_x < 0 or next_x == walls.width: continue
            next_y = y_int + dy
            if next_y < 0 or next_y == walls.height: continue
            if not walls[next_x][next_y]: neighbors.append((next_x, next_y))
        return neighbors

    getLegalNeighbors = staticmethod(getLegalNeighbors)

    def getSuccessor(position, action):
        dx, dy = Actions.directionToVector(action)
        x, y = position
        return (x + dx, y + dy)

    getSuccessor = staticmethod(getSuccessor)
