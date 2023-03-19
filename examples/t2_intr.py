"""
GUI design for the T2 transport

        +-------+-------+  +-------------------------+
        |       |       |  |                         |
        | PAUSE |  PLAY |  |    <time in seconds>    |
        |       |       |  |                         |
        +-------+-------+  +-------------------------+

        +--------------------------------------------+
jog     |      ||                                    |
        +--------------------------------------------+

         2.0x   1.0x   0.5x   0.   0.5x   1.0x   2.0x
        +--------------------------------------------+
shuttle |                                  ||        |
        +--------------------------------------------+

"""

import tkinter as tk

# Create the main window
root = tk.Tk()
root.title("My GUI")

# Create a set of options and variable for the OptionMenu
options = ["Option 1", "Option 2", "Option 3"]
selected_option = tk.StringVar()
selected_option.set(options[0])

# Create a variable to store options for the Radiobuttons
radio_option = tk.IntVar()

###############################################################################
# Create widgets

# Create widgets
button = tk.Button(root, text="Button")
canvas = tk.Canvas(root, bg='white', width=50, height=50)
checkbutton = tk.Checkbutton(root, text="Checkbutton")
entry = tk.Entry(root, text="Entry", width=10)
frame = tk.Frame(root)
label = tk.Label(root, text="Label")
labelframe = tk.LabelFrame(root, text="LabelFrame", padx=5, pady=5)
listbox = tk.Listbox(root, height=3)
menu = tk.Menu(root)
# Menubutton: deprecated, use Menu instead
message = tk.Message(root, text="Message", width=50)
optionmenu = tk.OptionMenu(root, selected_option, *options)
panedwindow = tk.PanedWindow(root, sashrelief=tk.SUNKEN)
radiobutton_1 = tk.Radiobutton( root,
                                text="Option 1",
                                variable=radio_option,
                                value=1)
radiobutton_2 = tk.Radiobutton( root,
                                text="Option 2",
                                variable=radio_option,
                                value=2)
scale = tk.Scale(root, orient=tk.HORIZONTAL)
scrollbar = tk.Scrollbar(root)
spinbox = tk.Spinbox(root, values=(0, 2, 4, 10))
text = tk.Text(root, width=15, height=3)
toplevel = tk.Toplevel()

# Lay out widgets
button.pack(padx=5, pady=5)
canvas.pack(padx=5, pady=5)
checkbutton.pack(padx=5, pady=5)
entry.pack(padx=5, pady=5)
frame.pack(padx=5, pady=10)
label.pack(padx=5, pady=5)
labelframe.pack(padx=5, pady=5)
listbox.pack(padx=5, pady=5)
# Menu: See below for adding the menu bar at the top of the window
# Menubutton: deprecated, use Menu instead
message.pack(padx=5, pady=5)
optionmenu.pack(padx=5, pady=5)
panedwindow.pack(padx=5, pady=5)
radiobutton_1.pack(padx=5)
radiobutton_2.pack(padx=5)
scale.pack(padx=5, pady=5)
scrollbar.pack(padx=5, pady=5)
spinbox.pack(padx=5, pady=5)
text.pack(padx=5, pady=5)
# Toplevel: does not have a parent or geometry manager, as it is its own window

###############################################################################
# Add stuff to the widgets (if necessary)

# Draw something in the canvas
canvas.create_oval(5, 15, 35, 45, outline='blue')
canvas.create_line(10, 10, 40, 30, fill='red')

# Add a default value to the Entry widgets
entry.insert(0, "Entry")

# Create some useless buttons in the LabelFrame
button_yes = tk.Button(labelframe, text="YES")
button_no = tk.Button(labelframe, text="NO")
button_maybe = tk.Button(labelframe, text="MAYBE")

# Lay out buttons in the LabelFrame
button_yes.pack(side=tk.LEFT)
button_no.pack(side=tk.LEFT)
button_maybe.pack(side=tk.LEFT)

# Put some options in the Listbox
for item in ["Option 1", "Option 2", "Option 3"]:
    listbox.insert(tk.END, item)

# Add some options to the menu
menu.add_command(label="File")
menu.add_command(label="Edit")
menu.add_command(label="Help")

# Add the menu bar to the top of the window
root.config(menu=menu)

# Create some labels to add to the PanedWindow
label_left = tk.Label(panedwindow, text="LEFT")
label_right = tk.Label(panedwindow, text="RIGHT")

# Add the labels to the PanedWindow
panedwindow.add(label_left)
panedwindow.add(label_right)

# Put some default text into the Text widgets
text.insert(tk.END, "I am a\nText widget")

# Create some widgets to put in the Toplevel widget (window)
top_label = tk.Label(toplevel, text="A Toplevel window")
top_button = tk.Button(toplevel, text="OK", command=toplevel.destroy)

# Lay out widgets in the Toplevel pop-up window
top_label.pack()
top_button.pack()

###############################################################################
# Run!

root.mainloop()
