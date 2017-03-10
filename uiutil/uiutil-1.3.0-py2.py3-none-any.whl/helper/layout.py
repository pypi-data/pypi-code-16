
def nice_grid(parent):

    cols, rows = parent.grid_size()

    for col in range(0, cols):
        parent.columnconfigure(col, weight=1)

    for row in range(0, rows):
        parent.rowconfigure(row, weight=1)
