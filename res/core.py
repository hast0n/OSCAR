# ==============================================================================
"""Classes : OSCAR project's functionnal module"""
# ==============================================================================
__author__  = "Martin Devreese"
__version__ = "0.5"
__date__    = "2018.12.11"
# ------------------------------------------------------------------------------
import res.myparser as myparser
import random as r
from copy import deepcopy
from math import sqrt
# ------------------------------------------------------------------------------
class World():

    def __init__(self, file):
        """Initialization if variables"""
        self.gameData = myparser.Parser(file).gameData
        self.color = self.gameData['world']['color']
        self.height, self.width = map(int, 
            (self.gameData['world']['height'], self.gameData['world']['width'])
        )
        # ---
        self.indexAttr()
        # ---
        self.isFilled = {}
        self.initialize()

    def initialize(self):
        """Set initial layout of grid"""
        self.matrix = [[0 for j in range(self.width)] for i in range(self.height)]
        self.nextmatrix = [[0 for j in range(self.width)] for i in range(self.height)]
        to_fill_with = ''
        if 'agent' in self.gameData : # If not, user can create its own config in grid
            
            # Randomization needs to come first before coordinates assignments
            for key, values in self.gameData['agent'].items() :
                if key == 'random' : self.randomize(values)

            # Assign coordinates to agents in grid
            for agent, values in self.gameData['agent'].items():
                if values == 'fill' : to_fill_with = agent; continue
                elif agent == 'random' : continue

                for coor in values :
                    if not coor[1] in range(self.width) or not coor[0] in range(self.height) :
                        print(f"invalid coordinates ({coor[0]},{coor[1]}) : "\
                            f"must fit the grid layout (height:{self.height}, width: {self.width})")
                    else :
                        self.matrix[coor[0]][coor[1]] = Agent(
                            self.defaultAgents[agent], agent)
        # ---
        if to_fill_with : self.fill(to_fill_with)
        self.indexAgents()

    def fill(self, to_fill_with):
        """Fill empty cells of grid with on agent"""
        self.isFilledWith = {'agent':to_fill_with}
        for i in range(self.height) :
            for j in range(self.width) :
                if not self.matrix[i][j] : 
                    self.matrix[i][j] = Agent(
                        self.gameData[self.types[to_fill_with]][to_fill_with], 
                        to_fill_with)

    def randomize(self, dic):
        """Randomize agents in grid"""
        for values in dic.values() :
            if values['coords'] == 'fill' :
                for i in range(self.height) :
                    for j in range(self.width) : self.getRandAgent(i,j, values)
            else :
                for i, j in values['coords'] : self.getRandAgent(i,j, values)

    def getRandAgent(self, i, j, values):
        """Return a random agent name among agents to randomize"""
        agent = values['agents'][
            r.randint(0, len(values['agents'])-1)
            ]
        if agent == 'empty' : self.matrix[i][j] = 0
        else :
            self.matrix[i][j] = Agent(
                self.gameData[self.types[agent]][agent], 
                agent)

    def indexAttr(self):
        """Index agents attributs like type or fields for easier access"""
        # ---
        self.types = {}; self.defaultAgents = {}
        for key, value in self.gameData.items() :
            if key in ('world', 'agent') : continue
            for key2, rules in value.items() : 
                self.types[key2] = key
                self.defaultAgents[key2] = rules
        # ---
        self.fields = {}
        for rules in self.defaultAgents.values():
            if 'field' in rules :
                varName = rules['field'][0]['FieldName']
                self.fields[varName] = rules['field'][0]
                for dic in rules['var'] :
                    if varName in dic.values() :
                        InitValue = dic['Value']
                self.fields[varName]['Value'] = InitValue

        # =============== FOR KIVY ONLY =======================
        self.colors = {}
        for agent, values in self.defaultAgents.items() :
            self.colors[agent] = self.HextoRGB(values['color'])
        self.colors['empty'] = self.HextoRGB(self.color)
        # =====================================================

    def indexAgents(self):
        """
        Index all agents in grid to avoid browsing all the grid
        at each iteration
        """
        self.index = {}
        for i in range(self.height) :
            for j in range(self.width) :
                if not self.matrix[i][j] : continue
                if not self.matrix[i][j].type in self.index :
                    self.index[self.matrix[i][j].type] = [[i,j]]
                else : self.index[self.matrix[i][j].type].append([i,j])
        for a in self.defaultAgents :
            if not a in self.index : self.index[a] = []

    # ================= FOR KIVY ONLY =====================
    def HextoRGB(self, hex):
        """Return rgb value of pseudo hexa color"""
        hex = hex.lstrip('#')
        return tuple(int(hex[i], 16)*17 for i in (0, 1, 2))
    # =====================================================

    def live(self):
        """Run evolution for each agent in grid."""
        for coords in self.index.values() :
            for row, col in coords :
                self.evolve(self.matrix[row][col], row, col)
        if self.ended() : return False
        self.matrix = [[agent for agent in row] for row in self.nextmatrix]
        self.nextmatrix = [[0 for j in range(self.width)] for i in range(self.height)]
        # ---
        self.indexAgents()

    def evolve(self, agent, row, col):
        """Initiate computation of each attributs of one agent"""
        self.checkSensors(agent, row, col)
        self.handleBirth(agent, row, col)
        self.handleStatus(agent, row, col)
        self.handleMove(agent, row, col)
        self.updateVars(agent)
        # self.handleTraces # TO DO

    def checkSensors(self, agent, row, col):
        """Update sensors value for 1 iteration"""
        if agent.sensors is not None :
            for sensor in agent.sensors :
                s = self.sum_fields(sensor['SensitivityValue'], row, col)
                tmp = sensor['ScaleValue'] * s
                agent.vars[sensor['SensorName']]['Value'] = tmp

    def handleBirth(self, agent, row, col):
        """Handle birth state for animal and vegetal agents"""
        if (self.types[agent.type] in ('animal', 'vegetal'))\
        and agent.birth is not None :
            b = agent.birth[0]; newA = b['NewAgentStatusName']; to_eval = ''
            if bool(b["condition"]) :
                varName = b['VariableName']; aff = b['Affinity']; tsv = b['ThresholdValue']
                varValue = agent.vars[varName]['Value']
                if aff == '=' : aff = '=='
                to_eval = f"{varValue} {aff} {tsv}"
                if (to_eval and eval(to_eval)) :
                    cell = self.getBestAdjCell(row, col, agent)
                    if cell :
                        x, y = cell
                        self.setNewAgent(x, y, newA)

    def handleStatus(self, agent, row, col):
        """Update agent's status according to rules""" 
        if agent.status is not None :
            for s in agent.status :
                newA = s['NewBornStatusName']; to_eval = ''
                if bool(s['condition']) : # if has condition
                    varName = s['VariableName']; aff = s['Affinity']
                    tsv = s['ThresholdValue']
                    varValue = agent.vars[varName]['Value']
                    if aff == '=' : aff = '=='
                    to_eval = f"{varValue} {aff} {tsv}"
                    _pass = to_eval and eval(to_eval)
                    if _pass : 
                        if newA == 'death' :
                            self.nextmatrix[row][col] = 0
                        elif self.types[agent.type] != 'mineral' :
                            agent.type = newA
                            agent.merge(self.defaultAgents[newA])
                            self.nextmatrix[row][col] = agent
                        else : 
                            self.setNewAgent(row, col, newA)
                        return
                    else :
                        self.nextmatrix[row][col] = agent
                elif newA == agent.type : # no condition & same agent
                    self.nextmatrix[row][col] = agent
                    return
                elif not bool(s["condition"]) : # no condition & different agent
                    self.setNewAgent(row, col, newA)
                    return

    def handleMove(self, agent, row, col):
        """Make animal agents move"""
        if self.types[agent.type] == 'animal' :
            cell = self.getBestAdjCell(row, col, agent)
            if cell :
                x, y = cell
                self.nextmatrix[row][col] = 0
                self.nextmatrix[x][y] = agent

    def updateVars(self, agent):
        """Update agent's vars"""
        if agent.vars is not None :
            for varName, values in agent.vars.items() :
                if bool(values['TimeStepValue']) :
                    agent.vars[varName]['Value'] += values['TimeStepValue']

    def getBestAdjCell(self, x, y, agent):
        """Return adjacent cell with maximum field capacity""" 
        coeffs = [
            [-1, -1], [-1, 0], [-1, 1], 
            [0, -1],           [0, 1], 
            [1, -1],  [1, 0],  [1, 1]
        ]
        freeCells = [
            [i+x,j+y] for i,j in coeffs \
            if self.isInGrid(i+x,j+y)   \
            and self.isFree(i+x,j+y)
        ]
        if agent.sensors is None :
            try : return freeCells[r.randint(0, len(freeCells)-1)]
            except (ValueError, IndexError) : return None
            return None
        else :
            adjCells = {}
            for nx, ny in freeCells :
                tmp = 0
                for sensor in agent.sensors :
                    s = self.sum_fields(sensor['SensitivityValue'], nx, ny)
                    tmp += sensor['ScaleValue'] * s
                adjCells[f'{nx} {ny}'] = tmp
            if adjCells :
                maxValue = adjCells[max(adjCells, key=adjCells.get)]
                if maxValue < 0 : func = max # Negative impact on agent
                else : func = min            # Positive impact on agent
                cells = [c for c in adjCells if adjCells[c] == maxValue]
                if len(cells) > 1 :
                    cell = cells[r.randint(0, len(cells)-1)]
                    # cell = self.nearest(x, y, cells, func)
                else : cell = cells[0]
                return map(int, cell.split())
            else : return None

    def sum_fields(self, field, row, col) :
        """Return sum of fields at one location of grid"""
        fsum = 0; fieldAttr = self.fields[field]
        agent_emitting_field = [
            a for a, v in self.defaultAgents.items() \
            if ('field' in v and field in v['field'][0].values())
        ]
        for aef in agent_emitting_field :
            for i, j in self.index[aef] :
                if not (i,j) == (row,col) :
                    dist = max((abs(row-i), abs(col-j)))
                    fvalue = fieldAttr['Value'] + dist*fieldAttr['DistanceStepValue']
                    fvalue = 0 if fvalue < 0 else fvalue
                    fsum += fvalue
        return fsum

    def isInGrid(self, x, y):
        """Return a True if coordinates are in grid else False"""
        return (x in range(self.height)) and (y in range(self.width))

    def isFree(self, x, y):
        """Return True if cell can be populated"""
        return not self.matrix[x][y] and not self.nextmatrix[x][y]

    def setNewAgent(self, row, col, agent, layer1=False):
        """Place new agent in grid"""
        if layer1 :
            self.matrix[row][col] = Agent(self.defaultAgents[agent], agent)
        else :
            self.nextmatrix[row][col] = Agent(self.defaultAgents[agent], agent)

    def ended(self):
        """Return True if last iteration was the same (agent's type wise)"""
        for i in range(self.height):
            for j in range(self.width):
                a1 = self.matrix[i][j]
                a1 = a1.type if a1 else 0
                a2 = self.nextmatrix[i][j]
                a2 = a2.type if a2 else 0
                if a1 != a2 : return False
        return True

    def nearest(self, x, y, cells, func=min):
        """
        [NONSENS AND USELESS]
        Get nearest/farthest adjacent cell using euclidian distance
        """
        dist = {i:self.eclid_dist(x,y,*map(int,i.split())) for i in cells}
        value = dist[func(dist, key=dist.get)]
        tup = [i for i in dist if dist[i]==value]
        if len(tup) > 1 : return tup[r.randint(0, len(tup)-1)]
        else : return tup[0]

    def eclid_dist(self, x1, y1, x2, y2):
        """Return euclidian distance between to points in grid"""
        return sqrt((x2 - x1)**2 + (y2 - y1)**2)
# ------------------------------------------------------------------------------
class Agent():

    def __init__(self, mrules, agent):
        """Initiate agent object"""
        rules = deepcopy(mrules)
        self.type = agent
        self.color = rules['color'] if 'color' in rules else None
        self.vars = {var['VariableName']:var for var in rules['var']}\
                    if 'var' in rules else None
        self.sensors = rules['sensor'] if 'sensor' in rules else None
        self.field = rules['field'][0] if 'field' in rules else None
        self.birth = rules['birth'] if 'birth' in rules else None
        self.trace = rules['trace'] if 'trace' in rules else None
        if not 'status' in rules :
            self.status = [{
                'NewBornStatusName' : self.type,
                "condition" : False
            }]
        else : 
            self.status = rules['status']

    def merge(self, mrules):
        """
        [Experimental] :
        When animal or vegetal agent turn into another agent :
        new agent adds vars of last state with current values 
        to its new state
        """
        rules = deepcopy(mrules)
        # ---
        self.color = rules['color'] if 'color' in rules else None
        # ---
        newVars =  {var['VariableName']:var for var in rules['var']}\
            if 'var' in rules else None
        if newVars is not None : self.vars.update(newVars)
        else : self.vars = newVars
        # ---
        self.status = rules['status'] if 'status' in rules else None
        self.sensors = rules['sensor'] if 'sensor' in rules else None
        self.birth = rules['birth'] if 'birth' in rules else None
        self.trace = rules['trace'] if 'trace' in rules else None
        # ---
        self.field = rules['field'][0] if 'field' in rules else None
# ------------------------------------------------------------------------------