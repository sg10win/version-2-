import tkinter as tk


class VerticalScrolledFrame(tk.Frame):
    """A pure Tkinter scrollable frame that actually works!

    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling
    """

    def __init__(self, parent, *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                           yscrollcommand=vscrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        vscrollbar.config(command=canvas.yview)

        def _on_mouse(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')

        canvas.bind_all('<MouseWheel>', _on_mouse)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = tk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=tk.NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())

        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())

        canvas.bind('<Configure>', _configure_canvas)


root = tk.Tk()
root.title("Scrollable Frame Demo")
root.configure(background="gray99")

scframe = VerticalScrolledFrame(root)
scframe.pack()

lis = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
for i, x in enumerate(lis):
    btn = tk.Button(scframe.interior, height=1, width=20, relief=tk.FLAT,
                    bg="gray99", fg="blue2",
                    font="Dosis", text='Button ' + lis[i],
                    command=lambda i=i, x=x: openlink(i))
    btn.pack(padx=10, pady=5, side=tk.TOP)


def openlink(i):
    print(lis[i])


root.mainloop()






















# -*-coding: utf8-*-
''' tk_Canvas_BGImage1.py
use a Tkinter canvas for a background image
for result see http://prntscr.com/12p9ux
'''
try:
    # Python2
    import Tkinter as tk
except ImportError:
    # Python3
    import tkinter as tk
root = tk.Tk()
root.title('background image')
# pick a .gif image file you have in the working directory
fname = r"pics\Andromeda-Galaxy.gif"
bg_image = tk.PhotoImage(file=fname)
# get the width and height of the image
w = bg_image.width()
h = bg_image.height()
# size the window so the image will fill it
root.geometry("%dx%d+50+30" % (w, h))
cv = tk.Canvas(width=w, height=h)
cv.pack(side='top', fill='both', expand='yes')
cv.create_image(0, 0, image=bg_image, anchor='nw')
# add canvas text at coordinates x=15, y=20
# anchor='nw' implies upper left corner coordinates
cv.create_text(15, 20, text="Python Greetings", fill="red", anchor='nw')
# now add some button widgets
btn1 = tk.Button(cv, text="Click")
btn1.pack(side='left', padx=10, pady=5, anchor='sw')
btn2 = tk.Button(cv, text="Quit", command=root.destroy)
btn2.pack(side='left', padx=10, pady=5, anchor='sw')
root.mainloop()