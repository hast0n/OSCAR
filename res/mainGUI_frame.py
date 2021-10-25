# ==============================================================================
"""
mainGUI : OSCAR project's Graphical User Interface

WARNING : 2018/12/22 - Discontinued since too ressource hungry
                     - Use mainGUI_canvas.py instead
"""
# ==============================================================================
__author__  = "Martin Devreese"
__version__ = "2.0"
__date__    = "2018/12/22"
# ------------------------------------------------------------------------------
from tkinter import (Frame, Tk, Button, Label, Scale, 
    StringVar, filedialog as fd, IntVar)
import res.core as c
from PIL import Image, ImageTk
# ==============================================================================
class main():

    def __init__(self, root, file):
        self.master = root; self.world = c.World(file)
        self.master.bind('<space>', self.startstop)
        self.master.bind('<F5>', self.startstop)
        self.master.bind('<F6>', self.nextgen)
        self.gridbg = self.world.color; self.generation = 0
        self.master.resizable(False, False); self.master.minsize(320, 300)
        self.agents =[*list(self.world.defaultAgents), 0]
        self.iterate = False; self.counter = 0
        # ---
        self.master.title('OSCAR - Simulation tool')
        self.master.configure(bg='white')
        # ---
        self.topFrame = Frame(self.master, height=150, bg='white')
        self.holderFrame = Frame(self.topFrame, bg='white')
        self.holderFrame2 = Frame(self.topFrame, bg='white')
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
        self.StartStopButton = Button(
            self.holderFrame,
            bg = 'white',
            relief = 'raised',
            bd = 1,
            text = '  Start',
            command = self.startstop,
            image=self.startImage,
            compound='left'
            )
        self.ResetButton = Button(
            self.topFrame,
            bg = 'white',
            relief = 'raised',
            bd = 1,
            text = '  Reset',
            command = self.reset,
            image=self.resetImage,
            compound='left'
            )
        self.TickButton = Button(
            self.holderFrame,
            bg = 'white',
            relief = 'raised',
            bd = 1,
            text = '  Tick',
            command = self.manualTick,
            image=self.tickImage,
            compound='left'
            )
        self.OpenFileButton = Button(
            self.topFrame,
            bg = 'white',
            relief = 'raised',
            bd = 1,
            text = '  Open',
            command = self.openfile,
            image=self.openfileImage,
            compound='left'
            )
        self.FrameRateScale = Scale(
            self.topFrame,
            orient='horizontal',
            sliderrelief='flat',
            resolution=10,
            length=300,
            label='Tick every : (ms - 0 being compute time)',
            tickinterval=200,
            from_=0, to=800,
            bg='white',
            takefocus=True
            )
        self.StatusVar = StringVar(self.master)
        self.StatusVar.set('Status : Waiting for user input... (0)')
        self.statusLabel = Label(
            self.topFrame,
            textvariable=self.StatusVar,
            bg='#e6e6e6', font='Helvetica 8',
            justify='left'
            )
        # ---
        self.StartStopButton.grid(row=0, column=0, padx=0, 
            pady=5, ipadx=3, ipady=5)
        self.ResetButton.grid(row=0, column=1, padx=10, 
            pady=0, ipadx=40, ipady=5)
        self.TickButton.grid(row=0, column=2, padx=10, 
            pady=0, ipadx=3, ipady=5)
        self.FrameRateScale.grid(row=2, column=0,
            columnspan=2, padx=10, pady=10, ipadx=1)
        self.OpenFileButton.grid(row=3, column=1, ipady=3,
            sticky='e', padx=10, pady=0, ipadx=5)
        self.statusLabel.grid(row=3, column=0, padx=10,
            sticky='w', columnspan=2)
        self.holderFrame.grid(row=0, column=0, padx=10)
        self.holderFrame2.grid(row=1, column=0, padx=10)
        self.topFrame.grid(row=0, column=0)
        # ---
        self.GridFrame = Frame(self.master, bg=self.gridbg)
        self.GridFrame.bind('<Leave>', self.onGridLeave)
        self.GridFrame.grid(row=1, column=0, padx=5, pady=10)
        # ---
        self.buildFrame()
        # ---

    def openfile(self):
        try :
            path = fd.askopenfilename(); self.GridFrame.destroy()
            self.world = c.World(path); self.gridbg = self.world.color
            self.agents =[*list(self.world.defaultAgents), 0]
            self.GridFrame = Frame(self.master, bg=self.gridbg)
            self.GridFrame.grid(row=1, column=0, padx=5, pady=10)
            self.buildFrame(); self.GridFrame.configure(bg=self.gridbg)
            self.StartStopButton.configure(image=self.startImage, text='  Start')
            self.StatusVar.set('Status : Waiting for user input... (0)')
            self.iterate = False; self.generation = 0
        except FileNotFoundError : return

    def startstop(self, event=None): 
        if not self.iterate or event == 'start' : 
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

    def buildFrame(self):
        gridWidth, gridHeight = self.world.width, self.world.height
        self.cellList = [[[] for i in range(gridWidth)] for j in range(gridHeight)]
        for i in range (gridHeight) :
            for j in range (gridWidth) :
                cell = Frame(self.GridFrame, height=10, width=10)
                cell.bind('<Button-1>', self.alternate)
                cell.bind('<Enter>', self.showAgent)
                self.cellList[i][j] = cell
                cell.grid(row=i, column=j, padx=1, pady=1)
        self.updateGrid()

    def alternate(self, event):
        x, y = self.getcoor(event)
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
        if not self.iterate :
            x, y = self.getcoor(event)
            agent = f"agent '{self.world.matrix[x][y].type}'" if self.world.matrix[x][y] else 'empty cell'
            self.StatusVar.set(f"Pointing : {agent} at {x,y}")

    def onGridLeave(self, event):
        if not self.iterate :
            self.StatusVar.set(f"Status : Waiting for user input... ({self.generation})")
            self.statusLabel.update()

    def getcoor(self, event):
        """Get index of column clicked on"""
        try : x = int(event.widget._name.replace('!frame', '')) -1
        except ValueError : x = 0
        return x//self.world.width, x%self.world.width

    def updateGrid(self):
        for i in range (self.world.height) :
            for j in range (self.world.width):
                agent = self.world.matrix[i][j]
                color = agent.color if agent else self.world.color
                self.cellList[i][j]['bg'] = color
        self.master.update()

    def nextgen(self, event=None):
        self.world.live(); self.updateGrid()
        self.generation +=1
        if self.iterate : self.StatusVar.set(f"Status : iterating... ({self.generation})")
        else : self.StatusVar.set(f"Status : Waiting for user input... ({self.generation})")

    def tick(self, event=None):
        if not self.iterate : return
        if self.counter >= self.FrameRateScale.get() :
            self.nextgen()
            self.counter = 0
        else : self.counter += 10
        self.master.after(10, self.tick)
# ==============================================================================
def launch(file): root = Tk(); main(root, file); root.mainloop()
# ==============================================================================