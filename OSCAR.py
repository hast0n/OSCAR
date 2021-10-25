# ==============================================================================
"""mainGUI : OSCAR project's Graphical User Interface"""
# ==============================================================================
__author__  = "Martin Devreese"
__version__ = "1.0"
__date__    = "2018.12.12"
# ------------------------------------------------------------------------------
# import res.mainGUI_frame as GAME # Discontinued
import res.mainGUI_canvas as GAME
# import res.mainGUI_kivy as GAME
# ------------------------------------------------------------------------------
game_config = {
    # 'file' : 'config/gameoflife.cfg',   # Conway's Game of Life
    # 'file' : 'config/forestfire.cfg',   # Forest Fire
     'file' : 'config/wireworld.cfg',    # Silverman's Wireworld cellular automata
    # 'file' : 'config/phototropism.cfg', # PhotoTropism
    # 'file' : 'config/sugarscape.cfg',   # Sugarscape System
    # 'file' : 'config/segregation.cfg'
}
GAME.launch(
    game_config['file']
)
# ==============================================================================