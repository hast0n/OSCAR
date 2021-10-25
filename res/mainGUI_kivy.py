# ==============================================================================
"""[WIP] mainGUI : OSCAR project's Graphical User Interface"""
# ==============================================================================
__author__  = "Martin Devreese"
__version__ = "0.2"
__date__    = "2018/12/18"
# ------------------------------------------------------------------------------
from kivy.app import App
from kivy.input.motionevent import MotionEvent
from kivy.clock import Clock
import kivy.graphics.texture as tex
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle
from kivy.uix.floatlayout import FloatLayout
import res.core as c
from PIL import Image, ImageTk
import time
import res.viewHelpers as vH
# ==============================================================================
class MySimuApp(App):

    def __init__(self, file):
        App.__init__(self)
        self.world = c.World(file); self.iterate = False
        self.FrameRate = 0; self.event = None
        self.textureWidget = MyTextureWidget(self.world.width, 
            self.world.height, self.world.matrix, self.world.colors, 300)
        self.textureWidget.bind(on_motion=self.on_motion)
        self.startstop()

    def startstop(self):
        if not self.iterate :
            if self.event : self.event()
            else : 
                self.event = Clock.schedule_interval(self.tick, self.FrameRate)
        else : self.event.cancel()

    def build(self):
        layout = FloatLayout()
        layout.add_widget(self.textureWidget)
        return layout

    def tick(self, event):
        self.world.live()
        self.textureWidget.reloadTexture(self.world.matrix, self.world.colors)

    def on_motion(self, etype, motionevent):
        # will (someday) receive all motion events
        print(etype, motionevent)

class MyTextureWidget(Widget) :
    
    def __init__(self, x_size, y_size, matrix, colors, cellHeight):
        Widget.__init__(self)
        self.texture = tex.texture_create(size=(x_size, y_size), colorfmt="rgb")
        self.texture.mag_filter = 'nearest'
        self.size = (x_size, y_size)
        self.initTexture(matrix, colors)
        width = (cellHeight/y_size) * x_size
        with self.canvas :
            Rectangle(texture=self.texture, pos=self.pos, size=(width, cellHeight))
        
    def reloadTexture(self, matrix, colors):
        arr = vH.getColorMatrix(matrix, colors)
        data = arr.tostring()
        self.texture.blit_buffer(data, bufferfmt="ubyte", colorfmt="rgb")
        self.canvas.ask_update()
    
    def initTexture(self, matrix, colors):
        arr = vH.getColorMatrix(matrix, colors)
        data = arr.tostring()
        self.texture.blit_buffer(data, bufferfmt="ubyte", colorfmt="rgb")
        

# ==============================================================================
def launch(file):
    OSCARSimu = MySimuApp(file); OSCARSimu.run()
# ==============================================================================