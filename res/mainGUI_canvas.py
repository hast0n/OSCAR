# ==============================================================================
"""mainGUI : OSCAR project's Graphical User Interface"""
# ==============================================================================
__author__  = "Martin Devreese"
__version__ = "2.1"
__date__    = "2018/12/26"
# ------------------------------------------------------------------------------
from tkinter import (Frame, Tk, Button, Label, Scale, Canvas, Checkbutton,
    StringVar, filedialog as fd, IntVar, messagebox as ms, TclError, 
    LabelFrame, OptionMenu, _setit, Grid)
import res.core as c
from PIL import Image, ImageTk
from time import time
from os.path import split as os_split, isfile
# ==============================================================================
class main():

    def __init__(self, root, path):
        self.master = root
        self.master.bind('<space>', self.startstop)
        self.master.bind('<F5>', self.startstop)
        self.master.bind('<F6>', self.nextgen)
        # self.master.bind('<Enter>', self.debug)
        # self.master.bind('<Leave>', self.debug)
        self.master.resizable(False, False)
        self.master.minsize(350, 200)
        # ---
        self.bgcolor = 'white'
        self.master.title('OSCAR - Simulation tool')
        self.master.configure(bg=self.bgcolor)

        # Setup containers & image objects
        self.topFrame = Frame(self.master, height=150, bg=self.bgcolor)
        self.holderFrame = Frame(self.topFrame, bg=self.bgcolor)
        self.holderFrame2 = LabelFrame(self.topFrame, bg=self.bgcolor, bd=1, relief='sunken')
        self.startImage = ImageTk.PhotoImage(Image.open("./img/startimg.png").resize(
            (20,20), Image.ANTIALIAS))
        self.stopImage = ImageTk.PhotoImage(Image.open("./img/stopimg.png").resize(
            (20,20), Image.ANTIALIAS))
        self.resetImage = ImageTk.PhotoImage(Image.open("./img/resetimg.png").resize(
            (20,20), Image.ANTIALIAS))
        self.tickImage = ImageTk.PhotoImage(Image.open("./img/nextstepimg.png").resize(
            (20,20), Image.ANTIALIAS))
        self.openfileImage = ImageTk.PhotoImage(Image.open("./img/openfileimg.png").resize(
            (20,20), Image.ANTIALIAS))
        
        # Setup buttons, variables & label for 1st container
        self.StartStopButton = Button(
            self.holderFrame,
            bg       = self.bgcolor,
            relief   = 'raised',
            bd       = 1,
            text     = '  Start',
            command  = self.startstop,
            image    = self.startImage,
            compound = 'left'
            )
        self.ResetButton = Button(
            self.topFrame,
            bg       = self.bgcolor,
            relief   = 'raised',
            bd       = 1,
            text     = '  Reset',
            command  = self.reset,
            image    = self.resetImage,
            compound = 'left'
            )
        self.TickButton = Button(
            self.holderFrame,
            bg       = self.bgcolor,
            relief   = 'raised',
            bd       = 1,
            text     = '  Tick',
            command  = self.manualTick,
            image    = self.tickImage,
            compound = 'left'
            )
        self.OpenFileButton = Button(
            self.topFrame,
            bg       = self.bgcolor,
            relief   = 'raised',
            bd       = 1,
            text     = '  Open',
            command  = self.openfile,
            image    = self.openfileImage,
            compound = 'left'
            )
        self.FrameRateScale = Scale(
            self.topFrame,
            orient       = 'horizontal',
            sliderrelief = 'flat',
            resolution   = 10,
            length       = 300,
            label        = 'Tick every : (ms - 0 being compute time)',
            tickinterval = 200,
            from_        = 0,
            to           = 800,
            bg           = self.bgcolor,
            # takefocus    = True,
            bd = 1,
            highlightthickness = 0,
            relief='sunken'
            )
        self.StatusVar = StringVar(self.master)
        self.StatusVar.set('Status : Waiting for user input... (0)')
        self.statusLabel = Label(
            self.topFrame,
            textvariable = self.StatusVar,
            bg           = '#e6e6e6', 
            font         = 'Helvetica 8',
            justify      = 'left'
            )
        
        # Setup buttons for 2nd container
        self.EndedVar = IntVar()
        self.AgentVar = StringVar()
        self.AgentVar.set('All')
        self.EndedVar.set(0)
        self.EndCheckButton = Checkbutton(
            self.holderFrame2, 
            text     = 'Stop simulation when\n2 identical frames',
            variable = self.EndedVar,
            height   = 2,
            bg       = self.bgcolor,
            justify  = 'center',
            indicatoron = 0,
            bd       = 0,
            command  = self.onCheck,
            fg       = 'red'
            )
        self.HighlightAgentMenu = OptionMenu(
            self.holderFrame2,
            self.AgentVar,
            'None', # Temporary
            )
        self.HighlightAgentMenu.configure(
            bg       = self.bgcolor,
            highlightthickness = 0,
            relief   = 'flat',
            bd       = 0,
            width    = 5
            )

        # Apply layout on grid
        self.StartStopButton.grid(row=0, column=0, padx=0, 
            pady=5, ipadx=3, ipady=5)
        self.ResetButton.grid(row=0, column=1, padx=10, 
            pady=0, ipadx=40, ipady=5)
        self.TickButton.grid(row=0, column=2, padx=10, 
            pady=0, ipadx=3, ipady=5)
        self.FrameRateScale.grid(row=2, column=0, columnspan=2, 
            pady=10, padx=10, sticky='ew')
        self.OpenFileButton.grid(row=3, column=1, ipady=3,
            sticky='e', padx=10, pady=0, ipadx=5)
        self.statusLabel.grid(row=3, column=0, padx=10,
            sticky='w', columnspan=2)
        self.EndCheckButton.grid(row=0, column=0, padx=5, 
            pady=2, ipadx=3)
        Frame(self.holderFrame2, bd=0, bg='black', height=25, 
            width=1).grid(row=0, column=1)
        Label(self.holderFrame2, text='Agents to display :', 
            bg = self.bgcolor).grid(row=0, column=2, padx=3)
        self.HighlightAgentMenu.grid(row=0, column=3, padx=5)
        self.holderFrame.grid(row=0, column=0, padx=10) #, sticky='ew')
        self.holderFrame2.grid(row=1, column=0, padx=10, 
            columnspan=2) #, sticky='ew')
        self.topFrame.grid(row=0, column=1) #, sticky='ew')
        # ---
        Grid.columnconfigure(self.master, self.topFrame, weight=1)
        # ---
        if self.isFilePath(path) : 
            self.isGoodFile = self.loadFile(path)
        else : self.isGoodFile = False
        if self.isGoodFile : self.buildCanvas()
        else : 
            ms.showinfo(
                'Error - File error',
                'Unable to load file\n'\
                'Please, check file and retry'
                )
        # ---

    def isFilePath(self, path):
        if not isfile(path) :
            ms.showerror(
                'Error - File Not Found',
                'File not found.\nUnable to open...'
            )
            return False
        else :
            try : self.filename = os_split(path)[-1]
            except SyntaxError : self.filename = path
            return True

    def loadFile(self, path):
        try :             
            if hasattr(self, 'Canvas') :
                self.Canvas.destroy()
            self.initializeWorkspace(path)
            return True
        except Exception :
            ms.showerror(
                'File error',
                'Oops ! Something went bad... '\
                'Check config file or try another one'
            ); return False

    def openfile(self, event=None):
        self.iterate = True
        self.startstop()
        try : path = fd.askopenfilename()
        except FileNotFoundError : return
        if not path : return
        self.isGoodFile = self.isFilePath(path) and self.loadFile(path)
        if self.isGoodFile : self.buildCanvas()
        
    def initializeWorkspace(self, path):
        self.world = c.World(path); self.gridbg = self.world.color
        self.agents = [*list(self.world.defaultAgents), 0]
        self.cheight = (self.world.height)*10+1
        self.cwidth = (self.world.width)*10+1
        self.Canvas = Canvas(self.master, bg=self.gridbg,
            width=self.cwidth, height=self.cheight)
        self.Canvas.bind('<Leave>', self.onCanvasLeave)
        self.Canvas.bind('<B1-Motion>', self.DragAndFill)
        self.Canvas.bind('<Button-1>', self.alternate)
        self.Canvas.bind('<ButtonRelease-1>', self.wipeDragList)
        self.Canvas.bind('<Motion>', self.showAgent)
        self.Canvas.grid(row=1, column=1, padx=5, pady=10)
        self.generation = 0; self.dragList = []
        self.iterate = False; self.counter = 0
        self.HighlightAgentMenu['menu'].delete(0, 'end')
        if hasattr(self, 'traceID') :
            self.AgentVar.trace_remove('write', self.traceID)
        for agent in ['All', *self.world.types.keys()] :
            self.HighlightAgentMenu['menu'].add_command(
                label    = agent,
                command  = _setit(self.AgentVar, agent)
                )
        self.AgentVar.set('All')
        self.traceID = self.AgentVar.trace_add('write', self.updateGrid)
        self.AgentVar.trace_vdelete

    def startstop(self, event=None): 
        if (not self.iterate or event == 'start') and self.isGoodFile : 
            self.time = time()
            print(f"\n--- Running '{self.filename}' ---\n[START] : {self.time}")
            self.StartStopButton.configure(image=self.stopImage, text='  Stop')
            self.StatusVar.set(f'Status : Iterating... ({self.generation})')
            self.iterate = True; self.tick()
        elif self.iterate or event == 'stop':
            self.StartStopButton.configure(image=self.startImage, text='  Start')
            self.StatusVar.set(f'Status : Waiting for user input... ({self.generation})')
            self.iterate = False

    def reset(self):
        self.iterate = False; self.world.initialize(); self.updateGrid()
        self.StatusVar.set('Status : Waiting for user input... (0)')
        self.StartStopButton.configure(image=self.startImage, text='  Start')
        self.generation = 0

    def manualTick(self):
        if not self.iterate : self.nextgen()

    def buildCanvas(self):
        gridWidth, gridHeight = self.world.width, self.world.height
        self.cellList = [[[] for i in range(gridWidth)] for j in range(gridHeight)]
        for i in range(gridHeight) :
            for j in range(gridWidth) :
                y0, x0 = i*10+2, j*10+2; y1, x1 = i*10+12, j*10+12
                cell = self.Canvas.create_rectangle(x0,y0,x1,y1,outline=self.gridbg)
                self.cellList[i][j] = cell
        self.updateGrid()

    def DragAndFill(self, event=None):
        x, y = self.getcoor(event)
        if not [x,y] in self.dragList :
            self.dragList.append([x,y])
            self.alternate(event)

    def wipeDragList(self, event=None):
        self.dragList = []

    def alternate(self, event):
        x, y = self.getcoor(event)
        self.dragList.append([x,y])
        agent = self.world.matrix[x][y].type if self.world.matrix[x][y] else 0
        index = (self.agents.index(agent)+1)%len(self.agents)
        newAgent = self.agents[index]
        if newAgent :
            self.world.matrix[x][y] = c.Agent(
                self.world.defaultAgents[newAgent], newAgent)
        else : self.world.matrix[x][y] = 0
        if newAgent : newAgentString = f"agent '{newAgent}'"
        else : newAgentString = 'empty cell'
        self.StatusVar.set(
            f"Status : user set {newAgentString} "\
            f"at {x,y}"
            )
        # ---
        self.world.indexAgents()
        self.updateGrid()

    def showAgent(self, event):
        self.getcoor(event)
        if not self.iterate :
            x, y = self.getcoor(event)
            agent = f"agent '{self.world.matrix[x][y].type}'" if self.world.matrix[x][y] else 'empty cell'
            self.StatusVar.set(f"Pointing : {agent} at {x,y}")

    def onCanvasLeave(self, event):
        if not self.iterate :
            self.StatusVar.set(f"Status : Waiting for user input... ({self.generation})")
            self.statusLabel.update()

    def getcoor(self, event):
        """Get coordinates of cell clicked on"""
        x = int(event.x/self.cwidth*self.world.width)
        y = int(event.y/self.cheight*self.world.height)
        x = x if x < self.world.width else self.world.width-1
        y = y if y < self.world.height else self.world.height-1
        x = x if x >= 0 else 0; y = y if y >= 0 else 0
        return y, x

    def updateGrid(self, *args):
        for i in range (self.world.height) :
            for j in range (self.world.width):
                agent = self.world.matrix[i][j]
                agent_to_display = self.AgentVar.get()
                if agent_to_display != 'All' :
                    if agent and agent.type == agent_to_display :
                        color = agent.color if agent else self.world.color
                    else :
                        color = self.gridbg
                    self.Canvas.itemconfigure(self.cellList[i][j], fill=color)                  
                else :
                    color = agent.color if agent else self.world.color
                    self.Canvas.itemconfigure(self.cellList[i][j], fill=color)

    def nextgen(self, event=None):
        if self.world.live() == False and self.EndedVar.get() : self.startstop('stop'); return
        self.updateGrid()
        self.generation +=1
        if self.iterate : self.StatusVar.set(f"Status : iterating... ({self.generation})")
        else : self.StatusVar.set(f"Status : Waiting for user input... ({self.generation})")

    def tick(self, event=None):
        if not self.iterate :
            t = time()
            st = str(t-self.time).split('.')
            print(f'  [END] : {t}\n [TIME] : {st[0]}.{st[1][:2]} seconds')
            return
        if self.counter >= self.FrameRateScale.get() :
            self.nextgen()
            self.counter = 0
        else : self.counter += 10
        self.master.after(10, self.tick)

    def onCheck(self, event=None):
        _pass = self.EndedVar.get()
        self.EndCheckButton['fg'] = 'green' if _pass else 'red'
        
    def debug(self, event=None):
        print(event.type, event.widget)
# ==============================================================================
def launch(file): root = Tk(); main(root, file); root.mainloop()
# ==============================================================================