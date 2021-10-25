# ==============================================================================
"""MyParser : Parse specifically designed data to project"""
# ==============================================================================
__author__  = "Martin Devreese"
__version__ = "1.1"
__date__    = "2018.12.22"
# ------------------------------------------------------------------------------
#pyParsing
from ast import literal_eval as l_e
import re
# ------------------------------------------------------------------------------
class Parser():

    def __init__(self, file):
        self.file = open(file, 'r')
        self.text = self.file.read()
        self.lines = self.text.split('\n')
        self.fileLength = len(self.lines)
        # ---
        self.gameData = self.readData()
        # ---
        self.file.close()

    def isValidHexa(self, string): # Unused
        return True if re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', string) else False

    def num(self, s):
        try : return int(s)
        except ValueError : return float(s)
        else : raise ValueError(f'wrong argument : {s}')

    def getSliceCoord(self, regex, data):
        coords = []
        try :
            exp = list(re.findall(
                r"\((\d+)?:?(\d+)?,(\d+)?:?(\d+)?\)", regex
            )[0])
            if exp[1] : # multiline x coordinates
                x1 = int(exp[0]) if exp[0] else 0
                x2 = int(exp[1]) if exp[1] else int(data['world'][1])
            elif exp[0] : x = int(exp[0])
            if exp[3] : # multiline y coordinates
                y1 = int(exp[2]) if exp[2] else 0
                y2 = int(exp[3]) if exp[3] else int(data['world'][2])
            elif exp[2] : y = int(exp[2])
            if not (exp[1] or exp[3]) :
                coords.append((x,y))
            elif exp[1] and exp[3] :
                for i in range(x1, x2):
                    for j in range(y1,y2):
                        coords.append((i,j))
            elif exp[1] and not exp[3] :
                for i in range(x1,x2):
                    coords.append((i,y))
            elif exp[3] and not exp[1] :
                for i in range(y1,y2):
                    coords.append((x,i))
            else :
                coords = 'fill'
        except ValueError : 
            print(f"invalid entry : {regex}, ignoring")
        except IndexError : pass
        return coords

    def readData(self):
        context, subContext = '', ''
        blocks = {}; layout = False
        # ---
        for line in self.lines :
            # Keep meaningful infos -------------------------------
            line = line.strip() # remove spaces
            if not line or (line and line[0] == '#') : continue
            if not True in [i in line for i in ('world', 'mineral', 'vegetal', 'animal')] :
                try : line = line[0:line.index("#")]
                except ValueError : pass # line does not include '#'
            line = [item for item in line.split(' ') if item != '']
            # List items in line ----------------------------------
            if not line : continue
            elif line[0] in ('world', 'agent', 'mineral', 'vegetal', 'animal') : 
                context, subContext = line[0].lower(), line[1].lower()
            if context == 'agent' :
                if not context in blocks :
                    blocks[context] = {}
                if not subContext in blocks[context] : 
                    blocks[context][subContext] = []
                blocks[context][subContext].append(line)
            elif context == 'world' : blocks[context.lower()] = line
            else :
                if not context in blocks : 
                    blocks[context] = {}
                if not subContext in blocks[context] : 
                    blocks[context][subContext] = []
                blocks[context][subContext].append(line)
        # ---
        return self.sortData(blocks)

    def sortData(self, dic): 
        data = {}
        for context, subContext in dic.items() :
            if context  == 'world' : 
                data[context] = {
                    "height" : subContext[1],
                    "width" : subContext[2],
                    "color" : subContext[3]
                }; continue
            data[context] = {}
            for key, lines in subContext.items() :
                data[context][key] = {} if context  != 'agent' else []
                for line in lines :
                    if line[0] == context and context  != 'agent' :
                        data[context][key]["color"] = line[2]; continue
                    if context  == 'agent' :
                        if re.match(r'choice\(([0-9a-z]+\,?)+\)', key) :
                            a = key[7:-1].split(','); coords = []
                            if '' in a : a.remove('')
                            for expr in line[2:] :
                                coords += self.getSliceCoord(expr, data)
                            if 'fill' in line[2:] or 'fill' in coords or not line[2:]: 
                                coords = 'fill'
                            d = {key:{'coords':coords, 'agents':a}}
                            if 'random' in data['agent'] :
                                data['agent']['random'] = {
                                    **data['agent']['random'], **d
                                }
                            else :
                                data['agent']['random'] = d
                            if key in data['agent'] : 
                                del data['agent'][key]
                        else :
                            for p in line[2:] :
                                if p == 'fill' :
                                    data['agent'][key] = p; break
                                elif re.match(r"\((\d+)?:?(\d+)?,(\d+)?:?(\d+)?\)", p) :
                                    coords = self.getSliceCoord(p, data)
                                    if isinstance(coords, list) :
                                        data['agent'][key] += coords
                                    else : data['agent'][key] = coords
                                else : print(f"invalid entry : {p}, ignoring")
                            if isinstance(data['agent'][key], list) :
                                data['agent'][key] = list(set(data['agent'][key]))
                    else :
                        var = line[0]; attributes = line[1:]
                        if not var in data[context][key] : 
                            data[context][key][var] = [attributes]
                        else : data[context][key][var].append(attributes)
        # ---
        return self.computeData(data)

    def computeData(self, data):
        for context, value in data.items() :
            if context in ('agent', 'world') : continue
            for agentType, attributes in value.items() :
                for varType, params in attributes.items() :
                    if varType == 'color' : continue
                    tmp2 = []
                    for attr in params :
                        try :
                            # ------------------------------------------------------------------
                            if varType == 'sensor' : # can be multiple
                                tmp = {
                                    "SensorName" : attr[0],
                                    "SensitivityValue" : attr[1],
                                    "ScaleValue" : self.num(attr[2]) if len(attr) >= 3 else 1
                                }
                            # ------------------------------------------------------------------
                            elif varType == 'var' : # can be multiple
                                tmp = {
                                    "VariableName" : attr[0],
                                    "Value" : self.num(attr[1]) if len(attr) >= 2 else 0,
                                    "TimeStepValue" : self.num(attr[2]) if len(attr) >= 3 else 0
                                }
                            # ------------------------------------------------------------------
                            elif varType == 'field' :
                                tmp = {
                                    "FieldName" : attr[0],
                                    "DistanceStepValue" : self.num(attr[1])\
                                    if self.num(attr[1]) <= 0 else None
                                }
                                if None in tmp.values(): raise ValueError(
                                    "field step can not be positive"
                                    )
                            # ------------------------------------------------------------------
                            elif varType == 'birth' :
                                if len(attr) == 1 : 
                                    tmp = {
                                        'NewAgentStatusName' : attr[0],
                                        "condition" : False
                                    }
                                else :
                                    tmp = {
                                        "VariableName" : attr[0],
                                        "Affinity" : attr[1] if attr[1] in ('<','>','=') else None,
                                        "ThresholdValue" : self.num(attr[2]),
                                        "NewAgentStatusName" : attr[3],
                                        "condition" : True
                                    }
                                if None in tmp.values() : 
                                    raise ValueError(f'wrong comparator : {attr[1]}')
                            # ------------------------------------------------------------------
                            elif varType == 'trace' :
                                tmp = {
                                    "VariableName" : attr[0],
                                    "Affinity" : attr[1] if attr[1] in ('<','>','=') else None,
                                    "ThresholdValue" : self.num(attr[2]),
                                    "NewTraceStatusName" : attr[3]
                                }
                                if None in tmp.values() : 
                                    raise ValueError(f'wrong comparator : {attr[1]}')
                            # ------------------------------------------------------------------
                            elif varType == 'status' : # Order in file matters
                                if len(attr) == 1 : 
                                    tmp = {
                                        'NewBornStatusName' : attr[0],
                                        "condition" : False
                                    }
                                else :
                                    tmp = {
                                        "VariableName" : attr[0],
                                        "Affinity" : attr[1] if attr[1] in ('<','>','=') else None,
                                        "ThresholdValue" : self.num(attr[2]),
                                        "NewBornStatusName" : attr[3],
                                        "condition" : True
                                    }
                                if None in tmp.values() : 
                                    raise ValueError(f'wrong comparator : {attr[1]}')
                            # ------------------------------------------------------------------
                            tmp2.append(tmp)
                        except IndexError : raise IndexError(
                                f'Rule file not valid : {context} {agentType} '\
                                f'{varType} missing arguments')
                    data[context][agentType][varType] = tmp2
        return data

    def savePattern(self, pattern): # Not working
        try : 
            p = re.search(r"BEGLAYOUT(.*)ENDLAYOUT", self.text)
            self.text.replace(
                f"BEGLAYOUT{p}ENDLAYOUT", 
                f"BEGLAYOUT{pattern}ENDLAYOUT"
                )
        except AttributeError : pass
# ------------------------------------------------------------------------------