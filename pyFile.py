from tkinter import *
def a ():
    pass
root = Tk()
submit_Button = Button(root, text='submit',width=25,bg="DodgerBlue2", command=a)
submit_Button.grid(row=5,column=1, sticky="e")
root.mainloop()