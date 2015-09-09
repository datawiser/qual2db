# Taken from:
# https://www.daniweb.com/software-development/python/code/234888/tooltip-box#post1032380
from Tkinter import *
tipwindow = None
def ToolTip( widget, text ):
    # Creates a tooptip box for a widget.
    def enter( event ):
        global tipwindow
        x = y = 0
        if tipwindow or not text:
            return
        x, y, cx, cy = widget.bbox( "insert" )
        x += widget.winfo_rootx() + 27
        y += widget.winfo_rooty() + 27
        # Creates a toplevel window
        tipwindow = tw = Toplevel( widget )
        # Leaves only the label and removes the app window
        tw.wm_overrideredirect( 1 )
        tw.wm_geometry( "+%d+%d" % ( x, y ) )
        label = Label( tw, text = text, justify = LEFT,
                       background = "#ffffe0", relief = SOLID, borderwidth = 1,
                       font = ( "tahoma", "8", "normal" ) )
        label.pack( ipadx = 1 )
        
    def close( event ):
        global tipwindow
        tw = tipwindow
        tipwindow = None
        if tw:
            tw.destroy()
            
    widget.bind( "<Enter>", enter )
    widget.bind( "<Leave>", close )
