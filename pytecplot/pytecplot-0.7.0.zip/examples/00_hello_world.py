import tecplot

frame = tecplot.active_frame()
frame.add_text('Hello, World!', position=(36, 50), size=34)
tecplot.export.save_png('hello_world.png', 600)