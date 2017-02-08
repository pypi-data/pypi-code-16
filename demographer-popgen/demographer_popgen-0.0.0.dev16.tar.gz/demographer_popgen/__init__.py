#!/usr/bin/python

from __future__ import division
from copy import deepcopy
from mpmath import *
import numpy as np
import numpy.matlib as mtlb
from scipy import special
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
#from matplotlib import pyplot as plt
import matplotlib.patches as ptchs
from matplotlib.lines import Line2D
from scipy.optimize import minimize
import ast
import json
from PIL import Image, ImageTk


#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

import sys
if sys.version_info[0] < 3:
    import Tkinter as tk
else:
    import tkinter as tk
    
import Tkconstants, tkFileDialog

from Tkinter import INSERT
#from Tkinter import Menu
import ttk
import copy




class DemoGrapher:
    def __init__(self):
        #root = tk.Tk()
        self.root = tk.Tk()
        self.root.withdraw()
        #self.root.wm_title("Setup") 
        #self.root.geometry('+%d+%d' % (0, 0))
        #self.win_pos_x = self.root.winfo_x()
        #self.win_pos_y = self.root.winfo_y()
        #self.win_width = self.root.winfo_width()
        #self.win_height = self.root.winfo_height()
        #self.root.wm_title("DemoGrapher 1.0")       
        
        #logo_image_path = "/Users/ethan/Dropbox/Berkeley/Projects/DemoGrapher/PythonDemographer/DraggablePopHistoryDevelopment/DemoGrapherLogo2.tif"
        #logo_image = ImageTk.PhotoImage(Image.open(logo_image_path))
        #self.logo = tk.Label(self.root, image = logo_image)
        #self.logo.grid(row = 19, column = 1, sticky = tk.W)
                
        self.reset_menubar(0)

        self.file_opt = None

        self.old_units = 'Coalescent units'
        self.new_units = None
        
        self.stat_drop_menu_exists = None        
                        
        self.new_command_window = None
        self.new_command_app = None
        self.nuref = None
        self.maxnes = None
        self.nus = None
        self.ts = None
        self.expmat = None
        self.migs = None
        self.ns = None
        self.maxt = None
        self.nentries = None
        self.which_pops = None

        self.full_boxes = False
        self.jsfs_object = None
        self.jsfs = None
                
        self.plotdt = None
        self.tubd = None
        self.Ent_sum_maxn = None
        self.save_jusfs_path = None
        self.save_session_path = None
        self.load_session_path = None
        #self.maxt_plot = None
        self.jusfs_to_plot_path = None
        self.jusfs_to_plot = None
        
        self.get_JSFS = None
                        
        self.Nref = 10000
        self.years_per_gen = None
        self.maxnes_display = None
        self.maxt_display = None
        self.nus_display = None
        self.ts_display = None
        self.migs_display = None
        self.max_popsize = None
        self.npops = None
        
        self.momi_dir_path = None

        #self.output_box = tk.Text(master = self.root, height = 10, width = 95, fg = "blue")
        #self.output_box.grid(row = 14, column = 1, rowspan = 5, columnspan = 4)

        self.JUSFS_plot = None
        self.JSFS_plot = None

        self.fst_computed_before = False        
        self.fst = None
        self.compute_fst_button_exists = False
        
        self.full_boxes_hist = None
        self.full_boxes_plot = None
        
        self.hist = None
        
        self.fig1 = None
        self.fig2 = None
        self.ax1 = None
        self.ax2 = None
        
        self.save_button_exists = False
        
        self.observer_ind = None
        
        self.hist_window_dim = [350,170]
        self.hist_window_pos = [0,0]
        self.ms_command_window_dim = [350,395]
        self.ms_command_window_pos = [0,215]
        self.scrm_command_window_dim = [350,315]
        self.scrm_command_window_pos = [0,215]
        self.output_box_window_dim = [400,400]
        self.output_box_window_pos = [1000,0]
        self.stat_visualization_window_dim = [400,150]
        self.stat_visualization_window_pos = [1000,450]
        self.test = 1        
        
        #Make a setup window
        #Generate a history window and fill display boxes
        self.new_setup_window = tk.Toplevel(self.root)
        self.app_setup_window = setup_window(self.new_setup_window, self)


    def on_setup_ms_simulator_menu_option(self):
        self.new_command_window = tk.Toplevel(self.root)
        self.app_command_window = ms_sim_command_window(self.new_command_window, self,(self.ms_command_window_dim[0],self.ms_command_window_dim[1],self.ms_command_window_pos[0],self.ms_command_window_pos[1]))
        return
    
    def on_setup_scrm_simulator_menu_option(self):
        self.new_command_window = tk.Toplevel(self.root)
        self.app_command_window = scrm_sim_command_window(self.new_command_window, self,(self.scrm_command_window_dim[0],self.scrm_command_window_dim[1],self.scrm_command_window_pos[0],self.scrm_command_window_pos[1]))
        return

    def reset_menubar(self,val):

        self.menubar = tk.Menu(self.root)

        # create the app menu (only for mac)
        appmenu = tk.Menu(self.menubar, name='apple')
        appmenu.add_command(label='About DemoGrapher')
        self.menubar.add_cascade(menu=appmenu)
        
        # create a file menu, and add it to the menu bar
        filemenu = tk.Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="New History", command=self.on_new_hist_menu_option)
        #filemenu.add_command(label="Open History", command=self.root.quit)
        filemenu.add_separator()
        filemenu.add_command(label="Save History", command=self.on_save_session_menu_call)
        filemenu.add_separator()
        filemenu.add_command(label="Quit", command=self.root.quit)
        self.menubar.add_cascade(label="File", menu=filemenu)        
                
        # Option menu
        optionmenu = tk.Menu(self.menubar, tearoff=0)
        simulatormenu = tk.Menu(self.menubar, tearoff=0)
        optionmenu.add_cascade(label="Change Units", command=self.on_change_units_menu_option)
        optionmenu.add_cascade(label="Simulator", menu=simulatormenu)
        simulatormenu.add_cascade(label="ms", command=self.on_setup_ms_simulator_menu_option)
        simulatormenu.add_cascade(label="scrm", command=self.on_setup_scrm_simulator_menu_option)
        #simulatormenu.add_cascade(label="ms", command=self.temp1)
        #simulatormenu.add_cascade(label="scrm", command=self.temp2)
        optionmenu.add_cascade(label="Set momi directory", command=self.on_setup_momi_dir_menu_option)
        #optionmenu.add_cascade(label="Get Command", command=self.root.quit)
        #filemenu.add_separator()
        #optionmenu.add_cascade(label="Inference", command=self.root.quit)
        #filemenu.add_separator()
        #optionmenu.add_command(label="History Diagram", command=self.root.quit)
        #optionmenu.add_separator()
        #optionmenu.add_command(label="Clear Background Variables", command=self.on_clear_hist_button_call)
        #optionmenu.add_separator()
        self.menubar.add_cascade(label="Option", menu=optionmenu)
        
        # Window menu
        winmenu = tk.Menu(self.menubar, name='window')
        winmenu.add_command(label='Something')
        self.menubar.add_cascade(menu=winmenu, label='Window')
        
        # Help menu
        #helpmenu = tk.Menu(self.menubar, tearoff=0)
        #helpmenu.add_command(label="About", command=self.root.quit)
        #self.menubar.add_cascade(label="Help", menu=helpmenu)
        
        # display the menu
        self.root.config(menu=self.menubar)
        self.root.createcommand('tk::mac::ShowPreferences', self.preferences_dialog)
        #tk.update()
        #self.root.mainloop()

    def preferences_dialog(self):
        print ">>>>>>>>>>>>>>>>>>>>>> DIALOG WORKING"
        return    


    def on_change_units_menu_option(self):
        self.change_units_window = tk.Toplevel(self.root)
        self.change_units_window = update_units_window(self.change_units_window, self)


    def on_new_hist_menu_option(self):
        self.new_setup_window = tk.Toplevel(self.root)
        self.new_setup_window = setup_window(self.new_setup_window, self)
        
    def on_setup_momi_dir_menu_option(self):
        #if self.momi_dir_path is None:
        momi_dir_opt = options = {}
        options["title"] = "Specify momi Directory"
        self.momi_dir_path = tkFileDialog.askdirectory(**momi_dir_opt)
    

                                                                                                                                
    def change_units(self):
        if self.new_units == self.old_units:
            self.new_units = None
            return
        else:
            if self.new_units == 'Coalescent units':
                #self.maxne_label = tk.Label(self.root, text = "Max population sizes (nu)")
                #self.nus_label = tk.Label(self.root, text="Sizes (nu)")
                #self.ts_label = tk.Label(self.root, text="Epoch bds (2*Nref gens)")
                #self.maxt_label = tk.Label(self.root, text="Max time (2*Nref gens)") 
                
                if not (self.maxnes is None):
                    self.maxnes_display = deepcopy(self.maxnes)
                else:
                    self.maxnes_display = None
                if not (self.maxt is None):
                    self.maxt_display = deepcopy(self.maxt)
                else:
                    self.maxt_display = None
                if not (self.nus is None):
                    self.nus_display = deepcopy(self.nus)
                else:
                    self.nus_display = None
                if not (self.ts is None):
                    self.ts_display = deepcopy(self.ts)
                else:
                    self.ts_display = None
                if not (self.migs is None):
                    self.migs_display = deepcopy(self.migs)
                else:
                    self.migs_display = None
            elif self.new_units == 'Ne/generations':                
                if not (self.maxnes is None):
                    self.maxnes_display = deepcopy(self.maxnes)
                    for i in range(0,len(self.maxnes_display)):
                        self.maxnes_display[i] = self.maxnes[i] * self.Nref
                else:
                    self.maxnes_display = None
                if not (self.maxt is None):
                    self.maxt_display = self.maxt * 2 * self.Nref
                else:
                    self.maxt_display = None
                if not (self.nus is None):
                    self.nus_display = deepcopy(self.nus)
                    for i in range(0,len(self.nus_display)):
                        for j in range(0,len(self.nus_display[i])):
                            self.nus_display[i][j] = self.nus[i][j] * self.Nref
                else:
                    self.nus_display = None
                if not (self.ts is None):
                    self.ts_display = deepcopy(self.ts)
                    for i in range(0,len(self.ts_display)):
                        for j in range(0,len(self.ts_display[i])):
                            self.ts_display[i][j] = self.ts[i][j] * 2 * self.Nref
                else:
                    self.ts_display = None
                if not (self.migs is None):
                    self.migs_display = deepcopy(self.migs)
                    for i in range(0,len(self.migs_display)):
                        self.migs_display[i][0] = self.migs[i][0] * 2 * self.Nref
                        self.migs_display[i][4] = self.migs[i][4] * 2 * self.Nref
                else:
                    self.migs_display = None
            elif self.new_units == 'Ne/years':
                if not (self.maxnes is None):
                    self.maxnes_display = deepcopy(self.maxnes)
                    for i in range(0,len(self.maxnes_display)):
                        self.maxnes_display[i] = self.maxnes[i] * self.Nref
                else:
                    self.maxnes_display = None
                if not (self.maxt is None):
                    self.maxt_display = self.maxt * 2 * self.Nref * self.years_per_gen
                else:
                    self.maxt_display = None
                if not (self.nus is None):
                    self.nus_display = deepcopy(self.nus)
                    for i in range(0,len(self.nus_display)):
                        for j in range(0,len(self.nus_display[i])):
                            self.nus_display[i][j] = self.nus[i][j] * self.Nref
                else:
                    self.nus_display = None
                if not (self.ts is None):
                    self.ts_display = deepcopy(self.ts)
                    for i in range(0,len(self.ts_display)):
                        for j in range(0,len(self.ts_display[i])):
                            self.ts_display[i][j] = self.ts[i][j] * 2 * self.Nref * self.years_per_gen
                else:
                    self.ts_display = None
                if not (self.migs is None):
                    self.migs_display = deepcopy(self.migs)
                    for i in range(0,len(self.migs_display)):
                        self.migs_display[i][0] = self.migs[i][0] * 2 * self.Nref  * self.years_per_gen
                        self.migs_display[i][4] = self.migs[i][4] * 2 * self.Nref  * self.years_per_gen
                else:
                    self.migs_display = None
            else:
                print "ERROR: Invalid units were chosen !!!!!!!!!!!!!!!!!!!!"
                return
            

            for i in range(0,len(self.maxnes_display)):
                self.maxnes_display[i] = round(self.maxnes_display[i],4)
            self.app_hist_window.maxne_ent.delete(0, tk.END)
            if type(self.maxnes_display).__module__ == 'numpy':                
                self.app_hist_window.maxne_ent.insert(0, json.dumps(self.maxnes_display.tolist()))
            else:
                self.app_hist_window.maxne_ent.insert(0, json.dumps(self.maxnes_display))
                        

            for i in range(0,len(self.nus_display)):
                for j in range(0,len(self.nus_display[i])):
                    self.nus_display[i][j] = round(self.nus_display[i][j],4)
            self.app_hist_window.nus_ent.delete(0, tk.END)
            if type(self.nus_display).__module__ == 'numpy':
                self.app_hist_window.nus_ent.insert(0, json.dumps(self.nus_display.tolist()))
            else:
                self.app_hist_window.nus_ent.insert(0, json.dumps(self.nus_display))
            
            
            for i in range(0,len(self.ts_display)):
                for j in range(0,len(self.ts_display[i])):
                    self.ts_display[i][j] = round(self.ts_display[i][j],4)
            self.app_hist_window.ts_ent.delete(0, tk.END)
            if type(self.ts_display).__module__ == 'numpy':
                self.app_hist_window.ts_ent.insert(0, json.dumps(self.ts_display.tolist()))
            else:
                self.app_hist_window.ts_ent.insert(0, json.dumps(self.ts_display))
            
            
            for i in range(0,len(self.migs_display)):
                self.migs_display[i][0] = round(self.migs_display[i][0],4)
                self.migs_display[i][3] = round(self.migs_display[i][3],4)
                self.migs_display[i][4] = round(self.migs_display[i][4],4)
            self.app_hist_window.mig_ent.delete(0, tk.END)
            if type(self.migs_display).__module__ == 'numpy':
                self.app_hist_window.mig_ent.insert(0, json.dumps(self.migs_display.tolist()))
            else:
                self.app_hist_window.mig_ent.insert(0, json.dumps(self.migs_display))


            self.old_units = self.new_units + '' #Copy by value            
            self.new_units = None



    def on_save_session_menu_call(self):
        self.save_session_path = tkFileDialog.asksaveasfilename(**self.file_opt)        
        #np.save(self.save_session_path,[self.nuref, self.maxnes, self.nus, self.ts, self.expmat, self.migs, self.ns, self.maxt, self.nentries, self.which_pops, self.plotdt, self.tubd, self.Ent_sum_maxn, self.save_jusfs_path, self.save_session_path, self.load_session_path, self.get_JSFS, self.Nref, self.years_per_gen, self.maxnes_display, self.maxt_display, self.nus_display, self.ts_display, self.migs_display, self.max_popsize, self.npops])        
        np.save(self.save_session_path, [self.hist.units, self.hist.maxnes, self.hist.nus, self.hist.ts, self.hist.expmat, self.hist.migs, self.ns, self.hist.maxt, self.hist.Nref, self.hist.years_per_gen, self.hist.npops, self.hist.plotdt])        


    def load_session(self):
        if self.load_session_path is not None:
            data = np.load(self.load_session_path)
                        
            self.old_units = data[0]
            self.maxnes = data[1]
            self.nus = data[2]
            self.ts = data[3]
            self.expmat = data[4]
            self.migs = data[5]
            self.ns = data[6]
            self.maxt = data[7]
            self.Nref = data[8]
            self.years_per_gen = data[9]
            self.npops = data[10]
            self.plotdt = data[11]*10
            
            ##self.hist.units = data[0]
            ##self.hist.maxnes = data[1]
            #self.fig1 = plt.figure(facecolor = 'white')
            #self.ax1 = self.fig1.add_subplot(111)  
            #self.ax1.cla()
            #self.hist = DraggablePopHistory(self,self.fig1, self.ax1, deepcopy(self.ts), deepcopy(self.nus), deepcopy(self.expmat), deepcopy(self.migs), deepcopy(self.maxnes), deepcopy(self.maxt), deepcopy(self.plotdt)/10, self.old_units, self.Nref, self.years_per_gen)
            
            self.maxnes_display = self.maxnes
            self.maxt_display = self.maxt
            self.nus_display = self.nus
            self.ts_display = self.ts
            self.migs_display = self.migs
            if self.old_units == 'Ne/generations':
                for i in range(0,len(self.maxnes)):
                    self.maxnes_display[i] = self.maxnes[i] * self.Nref
                self.maxt_display = self.maxt * 2 * self.Nref
                for i in range(0,len(self.nus)):
                    for j in range(0,len(self.nus[i])):
                        self.nus_display[i][j] = self.nus[i][j] * self.Nref
                        self.ts_display[i][j] = self.ts[i][j] * 2 * self.Nref
                for i in range(0,len(self.migs)):
                    self.migs_display[i][0] = self.migs[i][0] * 2 * self.Nref
                    self.migs_display[i][4] = self.migs[i][4] * 2 * self.Nref
            elif self.old_units == 'Ne/years':
                for i in range(0,len(self.maxnes)):
                    self.maxnes_display[i] = self.maxnes[i] * self.Nref
                self.maxt_display = self.maxt * 2 * self.Nref * self.years_per_gen
                for i in range(0,len(self.nus)):
                    for j in range(0,len(self.nus[i])):
                        self.nus_display[i][j] = self.nus[i][j] * self.Nref
                        self.ts_display[i][j] = self.ts[i][j] * 2 * self.Nref * self.years_per_gen
                for i in range(0,len(self.migs)):
                    self.migs_display[i][0] = self.migs[i][0] * 2 * self.Nref * self.years_per_gen
                    self.migs_display[i][4] = self.migs[i][4] * 2 * self.Nref * self.years_per_gen
                
            
            #Reset other variables
            self.new_units = None
            self.get_JSFS = None
            self.JUSFS_plot = None
            self.JSFS_plot = None
            self.fst_computed_before = None
            self.fst = None
            self.compute_fst_button_exists = None
            self.hist = None      
            self.save_session_path = None
            self.load_session_path = None



    def load_session_old(self):
        if self.load_session_path is not None:
            data = np.load(self.load_session_path)
                        
            self.nuref = data[0]
            self.maxnes = data[1]
            self.nus = data[2]
            self.ts = data[3]
            self.expmat = data[4]
            self.migs = data[5]
            self.ns = data[6]
            self.maxt = data[7]
            self.nentries = data[8]
            self.which_pops = data[9]
            self.plotdt = data[10]
            self.tubd = data[11]
            self.Ent_sum_maxn = data[12]
            self.save_jusfs_path = data[13]
            #self.save_session_path = data[14]
            #self.load_session_path = data[15]
            #self.get_JSFS = data[16]
            self.Nref = data[17]
            self.years_per_gen = data[18]
            self.maxnes_display = data[19]
            self.maxt_display = data[20]
            self.nus_display = data[21]
            self.ts_display = data[22]
            self.migs_display = data[23]
            self.max_popsize = data[24]
            self.npops = data[25]
            #self.JUSFS_plot = data[26]
            #self.JSFS_plot = data[27]
            #self.fst_computed_before = data[28]
            #self.fst = data[29]
            #self.compute_fst_button_exists = data[30]
            #self.hist = data[31]
            
            #Reset other variables
            self.get_JSFS = None
            self.JUSFS_plot = None
            self.JSFS_plot = None
            self.fst_computed_before = None
            self.fst = None
            self.compute_fst_button_exists = None
            self.hist = None      
            self.save_session_path = None
            self.load_session_path = None
            
            

    def setup_session(self,npops,maxne):
        self.nuref = 1
        self.npops = npops
        self.max_popsize = maxne+0 #Copy by value
        
        self.maxnes = [self.max_popsize] * self.npops
        self.nus = np.array([[self.max_popsize/2]] * self.npops)
        self.maxt = 5*2*self.nus[0][0]
        self.ts = [[0]]*self.npops
        self.expmat = [[0]]*self.npops
        self.migs = []
        self.plotdt = self.maxt/1000
        self.tubd = copy.deepcopy(self.maxt)
        self.Ent_sum_maxn = 100
        self.ns = [10] * self.npops
            
        self.maxnes_display = copy.deepcopy(self.maxnes)
        for i in range(0,len(self.maxnes)):
            self.maxnes_display[i] = round(self.maxnes[i],4)
        self.maxt_display = round(self.maxt,4)
        self.nus_display = copy.deepcopy(self.nus)
        for i in range(0,len(self.nus)):
            for j in range(0,len(self.nus[i])):
                self.nus_display[i][j] = round(self.nus[i][j],4)
        self.ts_display = copy.deepcopy(self.ts)
        for i in range(0,len(self.ts)):
            for j in range(0,len(self.ts[i])):
                self.ts_display[i][j] = round(self.ts[i][j],4)
        self.migs_display = copy.deepcopy(self.migs)
        for i in range(0,len(self.migs)):
            self.migs_display[i][0] = round(self.migs[i][0],4)
            self.migs_display[i][3] = round(self.migs[i][3],4)
            self.migs_display[i][4] = round(self.migs[i][4],4)
            
        #Set other variables
        self.get_JSFS = None
        self.JUSFS_plot = None
        self.JSFS_plot = None
        self.fst_computed_before = None
        self.fst = None
        self.compute_fst_button_exists = None
        self.hist = None      
        self.save_session_path = None
        self.load_session_path = None
        
        
            
            
        ##Generate a history window and fill display boxes
        #self.new_hist_window = tk.Toplevel(self.root)
        #self.app_hist_window = hist_window(self.new_hist_window, self)
        
        #Generate plotting window
        #self.new_hist_plot_window = tk.Toplevel(self.root)
        #self.app_hist_plot_window = hist_plot_window(self.new_hist_plot_window, self)



    def on_create_hist_button_call(self):                

        self.tubd = self.maxt
                        
        self.fig1 = plt.figure(facecolor = 'white')
        self.ax1 = self.fig1.add_subplot(111)  
        self.ax1.cla()
        
        self.app_hist_window.get_values()

        self.hist = DraggablePopHistory(self,self.fig1, self.ax1, deepcopy(self.ts), deepcopy(self.nus), deepcopy(self.expmat), deepcopy(self.migs), deepcopy(self.maxnes), deepcopy(self.maxt), deepcopy(self.plotdt)/10, self.old_units, self.Nref, self.years_per_gen)

        #Bind movement in this plot to movement of the history plot, and store the index of the observer in DraggablePopHistory
        self.observer_ind = self.hist.bind_observer([self.prepare_to_update_values,self.update_values,self.end_update_values])            
            
        self.hist.connect()
        plt.ion()
        plt.show()
        
            
        #self.root.config(menu=self.menubar)
        #self.root.createcommand('tk::mac::ShowPreferences', self.preferences_dialog)
        




                                
    def on_save_stat_button_call(self):
        #Check if all the boxes are full or not
        self.full_boxes_save = True
        if self.save_jusfs_ent.get():       
            filepath = self.save_jusfs_ent.get()
            #if filepath[-1] != '/':
            #    filepath = filepath + '/'
        else:
            self.full_boxes_inf = False
        
        if self.full_boxes_save:
            if self.stat_to_plot.get() == 'JUSFS':
                npJUSFSplot = np.array(self.jsfs.JUSFS.tolist(),dtype=np.float64)
                strJUSFS = json.dumps(npJUSFSplot.tolist())
                filepath = filepath + 'JUSFS.csv'

                out_file = open(filepath, "w")
                out_file.write(strJUSFS)
                out_file.close()
            if self.stat_to_plot.get() == 'JSFS':
                npJSFSplot = np.array(self.jsfs.JSFS.tolist(),dtype=np.float64)
                strJSFS = json.dumps(npJSFSplot.tolist())
                out_file = open(filepath, "w")
                out_file.write(strJSFS)
                out_file.close()
                                   


    def prepare_to_update_values(self):
        return
    def update_values(self):
        return
    def end_update_values(self):
        
        self.maxnes = self.hist.maxnes
        self.nus = self.hist.nus
        self.ts = self.hist.ts
        self.expmat = self.hist.expmat
        self.migs = self.hist.migs
        self.maxt = self.hist.maxt     
        
        self.maxnes_display = deepcopy(self.maxnes)
        for i in range(0,len(self.maxnes)):            
            if (self.old_units == 'Ne/generations') or (self.old_units == 'Ne/years'):
                self.maxnes_display[i] = self.maxnes[i] * self.Nref
            elif self.old_units == 'Coalescent units':
                self.maxnes_display[i] = self.maxnes[i]*1
        self.nus_display = deepcopy(self.nus)
        for i in range(0,len(self.nus)):            
            for j in range(0,len(self.nus[i])):
                if (self.old_units == 'Ne/generations') or (self.old_units == 'Ne/years'):
                    self.nus_display[i][j] = self.nus[i][j] * self.Nref
                elif self.old_units == 'Coalescent units':
                    self.nus_display[i][j] = self.nus[i][j]*1
        self.ts_display = deepcopy(self.ts)
        for i in range(0,len(self.ts)):            
            for j in range(0,len(self.ts[i])):
                if (self.old_units == 'Ne/generations'):
                    self.ts_display[i][j] = self.ts[i][j] * (2 * self.Nref)
                if (self.old_units == 'Ne/years'):
                    self.ts_display[i][j] = self.ts[i][j] * (2 * self.Nref * self.years_per_gen)
                elif self.old_units == 'Coalescent units':
                    self.ts_display[i][j] = self.ts[i][j] * 1
        self.migs_display = deepcopy(self.migs)
        for i in range(0,len(self.migs)):            
            if (self.old_units == 'Ne/generations'):
                self.migs_display[i][0] = self.migs[i][0] * (2 * self.Nref)
                self.migs_display[i][4] = self.migs[i][4] * (2 * self.Nref)
            if (self.old_units == 'Ne/years'):
                self.migs_display[i][0] = self.migs[i][0] * (2 * self.Nref * self.years_per_gen)
                self.migs_display[i][4] = self.migs[i][4] * (2 * self.Nref * self.years_per_gen)
            elif self.old_units == 'Coalescent units':
                self.migs_display[i][0] = self.migs[i][0] * 1
                self.migs_display[i][4] = self.migs[i][4] * 1
        if (self.old_units == 'Ne/generations'):
            self.maxt_display = self.maxt * (2*self.Nref)
        elif (self.old_units == 'Ne/years'):
            self.maxt_display = self.maxt * (2*self.Nref*self.years_per_gen)
        elif self.old_units == 'Coalescent units':
            self.maxt_display = self.maxt * 1


        for i in range(0,len(self.maxnes_display)):
            self.maxnes_display[i] = round(self.maxnes_display[i],4)
            
        for i in range(0,len(self.nus_display)):
            for j in range(0,len(self.nus_display[i])):
                self.nus_display[i][j] = round(self.nus_display[i][j],4)
            
        for i in range(0,len(self.ts_display)):
            for j in range(0,len(self.ts_display[i])):
                self.ts_display[i][j] = round(self.ts_display[i][j],4)
            
        for i in range(0,len(self.hist.expmat)):
            for j in range(0,len(self.hist.expmat[i])):
                if self.hist.expmat[i][j] is not None:
                    self.hist.expmat[i][j] = round(self.hist.expmat[i][j],4)
            
        for i in range(0,len(self.migs_display)):
            self.migs_display[i][0] = round(self.migs_display[i][0],4)
            self.migs_display[i][3] = round(self.migs_display[i][3],4)
            self.migs_display[i][4] = round(self.migs_display[i][4],4)
            
        self.maxt_display = round(self.maxt_display,4)        
        
        self.app_hist_window.maxne_ent.delete(0, tk.END)
        self.app_hist_window.maxne_ent.insert(0, json.dumps(np.array(self.maxnes_display).tolist()))
        self.app_hist_window.nus_ent.delete(0, tk.END)
        self.app_hist_window.nus_ent.insert(0, json.dumps(np.array(self.nus_display).tolist()))   
        self.app_hist_window.ts_ent.delete(0, tk.END)
        self.app_hist_window.ts_ent.insert(0, json.dumps(np.array(self.ts_display).tolist())) 
        self.app_hist_window.expmat_ent.delete(0, tk.END)
        self.app_hist_window.expmat_ent.insert(0, json.dumps(np.array(self.hist.expmat).tolist()))
        self.app_hist_window.mig_ent.delete(0, tk.END)
        self.app_hist_window.mig_ent.insert(0, json.dumps(np.array(self.migs_display).tolist()))


    def on_compute_fst_button_call(self):
        #if not self.fst_computed_before:
            #self.fst = FSTprecise(self.hist, self.tubd, self.ns, self.nuref, None)
        self.fst = FSTprecise(self.hist, self.tubd, self.ns, self.nuref, None)
        self.fst.get_FST()
        self.output_box.insert(INSERT,'\n\n')
        self.output_box.insert(INSERT,'FST: ')
        self.output_box.insert(INSERT,str(self.fst.FST))
        self.output_box.insert(INSERT,'\n\n')
        self.output_box.see(tk.END)
        
        self.fst_computed_before = True


    def on_clear_hist_button_call(self):                
        self.maxnes = None
        self.nus = None
        self.ts = None
        self.expmat = None
        self.migs = None
        self.ns = None
        self.maxt = None
        self.nentries = None
        #self.nuref = 1
        self.which_pops = None
        self.obs_jusfs = None
        #self.x0 = None
        self.full_boxes = False
        #self.num_x0 = False
        self.jsfs = None
        #self.jsfs_opt = None
        
        self.plotdt = 0.005
        self.tubd = None
        self.Ent_sum_maxn = 5
        self.save_jusfs_path = None
        #self.maxt_plot = None

        #self.obs_jusfs_path = None  
        #self.obsJSFS = None      
        #self.maxt_inf = None
        #self.maxnes_inf = None
        #self.nuref_inf = None
        #self.nus_inf = None
        #self.ts_inf = None
        #self.migs_inf = None
        #self.ns_inf = None
        #self.nentries_inf = None
        #self.expmat_inf = None
        
        self.get_JSFS = True
        
        #self.hist_inf = None
        #self.JUSFS_inf = None
        #self.JSFS_inf = None
        
        self.JUSFS_plot = None
        self.JSFS_plot = None

        #self.fst_computed_before = False        
        #self.fst = None
        #self.compute_fst_button_exists = False
        
        self.full_boxes_hist = None
        self.full_boxes_plot = None
        #self.full_boxes_inf = None
        
        self.hist = None
        
        self.fig1 = None
        self.fig2 = None
        self.ax1 = None
        self.ax2 = None
        
        self.save_button_exists = False
        
        self.observer_ind = None
          
                
                                
        
    def _quit(self):
        self.root.quit()     # stops mainloop
        self.root.destroy()  # this is necessary on Windows to prevent
                            # Fatal Python Error: PyEval_RestoreThread: NULL tstate        
        


    def new_inference_window(self):
        if self.hist is not None:
            self.newWindow = tk.Toplevel(self.root)
            self.app = inference_window(self.newWindow, self)
            self.output_box.insert(INSERT,'\n\n\n INFRENCE INSTRUCTIONS:\n ')
            self.output_box.insert(INSERT,'   - Replace a value by ? to infer it.\n ')
            self.output_box.insert(INSERT,'   - Replace one or more migration strengths by the same negative integer j satisfying\n ')
            self.output_box.insert(INSERT,'     j<-1 to infer them while constraining their values to be equal.\n ')
            self.output_box.insert(INSERT,'   - Replace an epoch boundary time and a migration time by the same negative integer j\n ')
            self.output_box.insert(INSERT,'     satisfying j<-1 to infer them while constraining their values to be equal.\n ')
            self.output_box.insert(INSERT,'   - Replace one or more population sizes by the same negative integer j satisfying\n ')
            self.output_box.insert(INSERT,'     j<-1 to infer them while constraining their values to be equal (j even) or to\n ')
            self.output_box.insert(INSERT,'     constraining their values to change exponentially from the first size down to\n ')
            self.output_box.insert(INSERT,'     the size of the epoch folowing the last constrained epoch (j odd).\n ')
            self.output_box.insert(INSERT,'   - Specify bounds (lbd,ubd) on a migration time by replacing ? with [?,lbd,ubd].\n ')
            self.output_box.see(tk.END)
        else:
            self.output_box.insert(INSERT,'Must click "Draw History" to generate a history to infer. \n\n ')
            self.output_box.see(tk.END)


    
    def new_sim_command_window(self):
        if self.hist is not None:
            self.new_command_window = tk.Toplevel(self.root)
            self.command_app = sim_command_window(self.new_command_window, self)
        else:
            self.output_box.insert(INSERT,'Must click "Draw History" to generate a history. \n\n ')
            self.output_box.see(tk.END)



class setup_window:
    def __init__(self, root, demog_main):
        self.root = root
        self.demog_main = demog_main
        self.frame = tk.Frame(self.root)
        
        self.root.geometry('+%d+%d' % (self.root.winfo_screenwidth()/3,self.root.winfo_screenheight()/3))
        #self.root.geometry('+%d+%d' % (root.winfo_screenwidth()/2-100*self.root.winfo_width()/2,root.winfo_screenheight()/2-self.root.winfo_height()/2))
        self.root.wm_title("Setup")
        
        #Set up labels
        self.new_hist_label = tk.Label(self.root, text = "Create a New History:")
        self.npops_label = tk.Label(self.root, text = "Number of Populations")
        self.max_popsize_label = tk.Label(self.root, text = "Max Population Size")
        self.maxt_label = tk.Label(self.root, text="Max time")
        self.load_hist_label = tk.Label(self.root, text = "Or Load History from File:")
        self.years_per_gen_label = tk.Label(self.root, text="Years/gen")
        self.Nref_label = tk.Label(self.root, text="Reference Eff. Size")

        self.npops_ent = tk.Entry(self.root)
        self.max_popsize_ent = tk.Entry(self.root)
        self.load_session_ent = tk.Entry(self.root)
        self.years_per_gen_ent = tk.Entry(self.root)
        self.Nref_ent = tk.Entry(self.root)
        
        self.npops_ent.delete(0, tk.END)
        self.npops_ent.insert(0, "2")
        self.max_popsize_ent.delete(0, tk.END)
        self.max_popsize_ent.insert(0, "3")     
        self.years_per_gen_ent.delete(0, tk.END)
        self.years_per_gen_ent.insert(0, "30")
        self.Nref_ent.delete(0, tk.END)
        self.Nref_ent.insert(0, "10000")
        
        self.demog_main.new_units = 'Units'        
        self.Nref_ent_exists = None
        self.years_per_gen_ent_exists = None

        self.new_hist_label.grid(row = 1, column = 1, sticky = tk.W)
        #self.new_units = 'Coalescent units'        
        self.new_units = 'Units'
        self.units_list = ['Coalescent units','Eff. Size and Generations','Eff. Size and Years']
        self.units = tk.StringVar()
        self.units.set('Units')
        self.units_menu = tk.OptionMenu(root,self.units,*self.units_list, command = self.update_units_textboxes)
        self.units_menu.grid(row = 1, column = 2, sticky = tk.EW)
        self.npops_label.grid(row = 4, column = 1, sticky = tk.E)
        self.max_popsize_label.grid(row = 5, column = 1, sticky = tk.E)
        
        self.npops_ent.grid(row = 4, column = 2, sticky = tk.E)
        self.max_popsize_ent.grid(row = 5, column = 2, sticky = tk.E)
                          
        self.load_hist_label.grid(row = 6, column = 1, sticky = tk.W)
        self.load_session_ent.grid(row = 6, column = 2, sticky = tk.E)
        
        self.demog_main.file_opt = options = {}
        options["defaultextension"] = ".npy"
        self.browse_hist_button = tk.Button(master=self.root, text="Browse", command=self.askopenfilename)
        self.browse_hist_button.grid(row = 7, column = 2, sticky = tk.W)
                
        self.load_hist_button = tk.Button(master=self.root, text="Initialize History", command=self.on_load_session_button_call)        
        self.load_hist_button.grid(row = 8, column = 2, sticky = tk.W)

                                                                
    def update_units_textboxes(self,val):
        self.new_units = self.units.get()
        if self.new_units == 'Coalescent units':
            if self.Nref_ent_exists is not None:
                self.Nref_ent.grid_remove()
                self.Nref_label.grid_remove()
                self.Nref_ent_exists = None
            if self.years_per_gen_ent_exists is not None:
                self.years_per_gen_ent.grid_remove()
                self.years_per_gen_label.grid_remove()
                self.years_per_gen_ent_exists = None
            self.max_popsize_ent.delete(0, tk.END)
            self.max_popsize_ent.insert(0, "3") 
        elif self.new_units == 'Eff. Size and Generations':
            if self.years_per_gen_ent_exists is not None:
                self.years_per_gen_ent.grid_remove()
                self.years_per_gen_label.grid_remove()
                self.years_per_gen_ent_exists = None
            if self.Nref_ent_exists is None:
                self.Nref_label.grid(row=2, column=1, sticky=tk.E)
                self.Nref_ent.grid(row = 2, column = 2, sticky = tk.W)
                self.Nref_ent_exists = 1
            self.max_popsize_ent.delete(0, tk.END)
            self.max_popsize_ent.insert(0, "30000") 
        elif self.new_units == 'Eff. Size and Years':
            if self.Nref_ent_exists is None:
                self.Nref_label.grid(row=2, column=1, sticky=tk.E)
                self.Nref_ent.grid(row = 2, column = 2, sticky = tk.W)
                self.Nref_ent_exists = 1
            if self.years_per_gen_ent_exists is None:
                self.years_per_gen_label.grid(row=3, column=1, sticky=tk.E)
                self.years_per_gen_ent.grid(row = 3, column = 2, sticky = tk.W)
                self.years_per_gen_ent_exists = 1
            self.max_popsize_ent.delete(0, tk.END)
            self.max_popsize_ent.insert(0, "30000")
            

    def askopenfilename(self):
        self.load_session_path = tkFileDialog.askopenfilename(**self.demog_main.file_opt)
        self.load_session_ent.delete(0, tk.END)
        self.load_session_ent.insert(0, self.load_session_path)
        return


    def on_load_session_button_call(self):
        if self.new_units == 'Units':
            print "\n\nERROR: Must specify units, max sizes, and number of populations (or load an existing history).\n"
            return
        if self.new_units == 'Coalescent units':            
            self.demog_main.new_units = 'Coalescent units'
        elif self.new_units == 'Eff. Size and Generations':
            self.demog_main.new_units = 'Ne/generations'
            if self.Nref_ent.get():
                self.demog_main.Nref = ast.literal_eval(self.Nref_ent.get())
            else:
                print "\n\nERROR: Must specify reference effective population size.\n"
                return
        elif self.new_units == 'Eff. Size and Years':
            self.demog_main.new_units = 'Ne/years'
            if self.Nref_ent.get():
                self.demog_main.Nref = ast.literal_eval(self.Nref_ent.get())
            else:
                print "\n\nERROR: Must specify reference effective population size.\n"
                return
            if self.years_per_gen_ent.get():
                self.demog_main.years_per_gen = ast.literal_eval(self.years_per_gen_ent.get())
            else:
                print "\n\nERROR: Must specify years per generation.\n"
                return
        
        if self.load_session_ent.get():            
            self.demog_main.load_session_path = self.load_session_ent.get()
        
        if self.demog_main.load_session_path is not None:
            self.demog_main.load_session()
            #self.demog_main.old_units = self.demog_main.new_units
            #self.demog_main.new_units = self.new_units
        else:
            self.npops = None
            if self.npops_ent.get():
                self.npops = ast.literal_eval(self.npops_ent.get())
            else:
                print "\n\nERROR: Must specify number of populations.\n"
                return
            if self.max_popsize_ent.get():
                self.max_popsize = ast.literal_eval(self.max_popsize_ent.get())
            else:
                print "\n\nERROR: Must specify number of population size.\n"
                return
            self.demog_main.old_units = 'Coalescent units'

            if (self.demog_main.new_units == 'Ne/generations') or (self.demog_main.new_units == 'Ne/years'):
                self.max_popsize = self.max_popsize/self.demog_main.Nref
                
            self.demog_main.setup_session(self.npops,self.max_popsize)

        #Generate a history window and fill display boxes
        self.demog_main.new_hist_window = tk.Toplevel(self.demog_main.root)
        self.demog_main.app_hist_window = hist_window(self.demog_main.new_hist_window, self.demog_main,(self.demog_main.hist_window_dim[0],self.demog_main.hist_window_dim[1],self.demog_main.hist_window_pos[0],self.demog_main.hist_window_pos[1]))
                        
        self.demog_main.new_command_window = tk.Toplevel(self.demog_main.root)
        self.demog_main.app_command_window = ms_sim_command_window(self.demog_main.new_command_window, self.demog_main,(self.demog_main.ms_command_window_dim[0],self.demog_main.ms_command_window_dim[1],self.demog_main.ms_command_window_pos[0],self.demog_main.ms_command_window_pos[1]))

        self.demog_main.new_output_box_window = tk.Toplevel(self.demog_main.root)
        self.demog_main.app_output_box_window = output_box_window(self.demog_main.new_output_box_window, self.demog_main,(self.demog_main.output_box_window_dim[0],self.demog_main.output_box_window_dim[1],self.demog_main.output_box_window_pos[0],self.demog_main.output_box_window_pos[1]))
                        
        self.demog_main.new_stat_visualization_window = tk.Toplevel(self.demog_main.root)
        self.demog_main.app_stat_visualization_window = statistic_visualization_window(self.demog_main.new_stat_visualization_window, self.demog_main,(self.demog_main.stat_visualization_window_dim[0],self.demog_main.stat_visualization_window_dim[1],self.demog_main.stat_visualization_window_pos[0],self.demog_main.stat_visualization_window_pos[1]))

        self.demog_main.app_output_box_window.output_box.insert(INSERT,'INSTRUCTIONS: \n')
        self.demog_main.app_output_box_window.output_box.insert(INSERT,'  -Click "Draw History" to draw the population. \n')
        self.demog_main.app_output_box_window.output_box.insert(INSERT,'  -Drag circles to move epochs and migrations. \n')
        self.demog_main.app_output_box_window.output_box.insert(INSERT,'  -Hold "n" while clicking on a population to draw \n')
        self.demog_main.app_output_box_window.output_box.insert(INSERT,'   a new epoch. \n')
        self.demog_main.app_output_box_window.output_box.insert(INSERT,'  -Hold "m" while clicking/dragging from one \n')
        self.demog_main.app_output_box_window.output_box.insert(INSERT,'   population to another to draw a migration. \n')
        self.demog_main.app_output_box_window.output_box.insert(INSERT,'  -Hold "d" while clicking on a circle to delete \n')
        self.demog_main.app_output_box_window.output_box.insert(INSERT,'   object. \n')
        self.demog_main.app_output_box_window.output_box.insert(INSERT,'  -Hold "e" while clicking on an epoch circle to \n')
        self.demog_main.app_output_box_window.output_box.insert(INSERT,'   toggle exponential growth. \n')
        self.demog_main.app_output_box_window.output_box.insert(INSERT,'  -Hold "v" while clicking on an epoch circle to \n')
        self.demog_main.app_output_box_window.output_box.insert(INSERT,'   edit its numerical value. \n')
        self.demog_main.app_output_box_window.output_box.see(tk.END)

                
        self.demog_main.change_units()
        
        self.root.withdraw()
        
        #Generate plotting window
        #self.new_hist_plot_window = tk.Toplevel(self.root)
        #self.app_hist_plot_window = hist_plot_window(self.new_hist_plot_window, self)




class hist_window:
    def __init__(self, root, demog_main, hwxy):
        self.root = root
        self.demog_main = demog_main
        self.frame = tk.Frame(self.root)
        self.root.bind('<Button-1>',self.demog_main.reset_menubar)        
        
        self.root.geometry('%dx%d+%d+%d' % hwxy)
        self.root.wm_title("History")
        
        #Set up labels
        #self.hist_title_label = tk.Label(self.root, text = "Population history:")
        self.maxne_label = tk.Label(self.root, text = "Max Population Sizes")
        self.nus_label = tk.Label(self.root, text="Population Sizes")
        self.ts_label = tk.Label(self.root, text="Epoch Boundaries")
        self.expmat_label = tk.Label(self.root, text="Growth Rates")
        self.mig_label = tk.Label(self.root, text="Migration events")
        #self.ns_label = tk.Label(self.root, text="Numbers of samples")
        #self.nentries_label = tk.Label(self.root, text="Entries to compute")
        #self.nuref_label = tk.Label(self.root, text="Reference Ne")
        #self.which_pops_label = tk.Label(self.root, text="Which pops?")
        #self.years_per_gen_label = tk.Label(self.root, text="Years/gen")
        #self.Nref_label = tk.Label(self.root, text="Nref")
        #self.save_jusfs_label = tk.Label(self.root, text="Save JSFS path")
        #self.jusfs_to_plot_label = tk.Label(self.root, text="SFS to plot path")
        
        #Set up entries
        self.maxne_ent = tk.Entry(self.root)
        self.nus_ent = tk.Entry(self.root)
        self.ts_ent = tk.Entry(self.root)
        self.expmat_ent = tk.Entry(self.root)
        self.mig_ent = tk.Entry(self.root)
        #self.ns_ent = tk.Entry(self.root)
        
        #Fill entries from loaded data
        self.maxne_ent.delete(0, tk.END)
        self.maxne_ent.insert(0, json.dumps(np.array(self.demog_main.maxnes_display).tolist()))
        self.nus_ent.delete(0, tk.END)
        self.nus_ent.insert(0, json.dumps(np.array(self.demog_main.nus_display).tolist()))   
        self.ts_ent.delete(0, tk.END)
        self.ts_ent.insert(0, json.dumps(np.array(self.demog_main.ts_display).tolist())) 
        self.expmat_ent.delete(0, tk.END)
        self.expmat_ent.insert(0, json.dumps(np.array(self.demog_main.expmat).tolist()))
        self.mig_ent.delete(0, tk.END)
        self.mig_ent.insert(0, json.dumps(np.array(self.demog_main.migs_display).tolist()))
        #self.ns_ent.delete(0, tk.END)
        #self.ns_ent.insert(0, json.dumps(np.array(self.demog_main.ns).tolist()))
        
        #Make the window
        #self.hist_title_label.grid(row = 0, column = 1, sticky = tk.W)
        self.maxne_label.grid(row = 1, column = 1, sticky = tk.E)
        self.nus_label.grid(row = 2, column = 1, sticky = tk.E)
        self.ts_label.grid(row = 3, column = 1, sticky = tk.E)
        self.expmat_label.grid(row = 4, column = 1, sticky = tk.E)
        self.mig_label.grid(row = 5, column = 1, sticky = tk.E)
        #self.ns_label.grid(row = 6, column = 1, sticky = tk.E)
        
        self.maxne_ent.grid(row = 1, column = 2, sticky = tk.W)
        self.nus_ent.grid(row = 2, column = 2, sticky = tk.W)
        self.ts_ent.grid(row = 3, column = 2, sticky = tk.W)
        self.expmat_ent.grid(row = 4, column = 2, sticky = tk.W)
        self.mig_ent.grid(row = 5, column = 2, sticky = tk.W)                                
        #self.ns_ent.grid(row = 6, column = 2, sticky = tk.W)
        
        self.new_hist_button = tk.Button(master = self.root, text="Draw History", command = self.demog_main.on_create_hist_button_call)
        self.new_hist_button.grid(row = 6, column = 2, sticky = tk.W)
        
        #self.new_reset_menubar_button = tk.Button(master = self.root, text="Reset Menubar", command = self.demog_main.reset_menubar)
        #self.new_reset_menubar_button.grid(row = 6, column = 1, sticky = tk.E)

    def get_values(self):
        if self.maxne_ent.get():
            maxnes_unsc = np.array(ast.literal_eval(self.maxne_ent.get()))
            if self.demog_main.old_units == 'Coalescent units':
                self.demog_main.maxnes = maxnes_unsc
            elif self.demog_main.old_units == 'Ne/generations':
                self.demog_main.maxnes = maxnes_unsc / self.demog_main.Nref
            elif self.demog_main.old_units == 'Ne/years':
                self.demog_main.maxnes = maxnes_unsc / self.demog_main.Nref            
        else:
            self.demog_main.output_box.insert(INSERT,'ERROR: Specify max sizes.\n')
            self.demog_main.output_box.see(tk.END)
            return
        
        if self.nus_ent.get():
            nus_unsc = np.array(ast.literal_eval(self.nus_ent.get()))            
            if self.demog_main.old_units == 'Coalescent units':
                self.demog_main.nus = nus_unsc
            elif self.demog_main.old_units == 'Ne/generations':
                for i in range(0,len(self.demog_main.nus)):
                    for j in range(0,len(self.demog_main.nus[i])):
                        self.demog_main.nus[i][j] = nus_unsc[i][j] / self.demog_main.Nref
            elif self.demog_main.old_units == 'Ne/years':
                for i in range(0,len(self.demog_main.nus)):
                    for j in range(0,len(self.demog_main.nus[i])):
                        self.demog_main.nus[i][j] = nus_unsc[i][j] / self.demog_main.Nref
        else:
            self.demog_main.output_box.insert(INSERT,'ERROR: Specify population sizes.\n')
            self.demog_main.output_box.see(tk.END)
            return        
            
        if self.ts_ent.get():
            ts_unsc = np.array(ast.literal_eval(self.ts_ent.get()))
            if self.demog_main.old_units == 'Coalescent units':
                self.demog_main.ts = ts_unsc
            elif self.demog_main.old_units == 'Ne/generations':
                for i in range(0,len(self.demog_main.ts)):
                    for j in range(0,len(self.demog_main.ts[i])):
                        self.demog_main.ts[i][j] = ts_unsc[i][j] / (2 * self.demog_main.Nref)
            elif self.demog_main.old_units == 'Ne/years':
                for i in range(0,len(self.demog_main.ts)):
                    for j in range(0,len(self.demog_main.ts[i])):
                        self.demog_main.ts[i][j] = ts_unsc[i][j] / (2 * self.demog_main.Nref * self.demog_main.years_per_gen)
        else:
            self.demog_main.output_box.insert(INSERT,'ERROR: Specify epoch boundary times.\n')
            self.demog_main.output_box.see(tk.END)
            return
            

        if self.expmat_ent.get():
            self.demog_main.expmat = np.array(ast.literal_eval(self.expmat_ent.get().replace("null","None")))
        else:
            self.demog_main.output_box.insert(INSERT,'ERROR: Specify growth rates.\n')
            self.demog_main.output_box.see(tk.END)
            return


        if self.mig_ent.get():
            migs_unsc = np.array(ast.literal_eval(self.mig_ent.get()))
            if self.demog_main.old_units == 'Coalescent units':
                self.demog_main.migs = migs_unsc
            elif self.demog_main.old_units == 'Ne/generations':
                for j in range(0,len(migs_unsc)):
                    migs_unsc[j][0] = migs_unsc[j][0] / (2 * self.demog_main.Nref)
                    migs_unsc[j][4] = migs_unsc[j][4] / (2 * self.demog_main.Nref)
                self.demog_main.migs = migs_unsc
            elif self.demog_main.old_units == 'Ne/years':
                for j in range(0,len(migs_unsc)):
                    migs_unsc[j][0] = migs_unsc[j][0] / (2 * self.demog_main.Nref * self.demog_main.years_per_gen)
                    migs_unsc[j][4] = migs_unsc[j][4] / (2 * self.demog_main.Nref * self.demog_main.years_per_gen)
                self.demog_main.migs = migs_unsc
        else:
            self.demog_main.output_box.insert(INSERT,'ERROR: Specify migration rates.\n')
            self.demog_main.output_box.see(tk.END)
            return
                

class output_box_window:
    def __init__(self, root, demog_main,hwxy):
        self.root = root
        self.demog_main = demog_main
        self.frame = tk.Frame(self.root)
        self.root.bind('<Button-1>',self.demog_main.reset_menubar)        
        
        self.root.geometry('%dx%d+%d+%d' % hwxy)
        self.root.wm_title("Output")
        
        self.output_box = tk.Text(master = self.root, height = 24, width = 55, fg = "blue")
        self.output_box.grid(row = 0, column = 0, rowspan = 1, columnspan = 1)
        

class hist_plot_window:
    def __init__(self, root, demog_main,hwxy):
        self.root = root
        self.demog_main = demog_main
        self.frame = tk.Frame(self.root)
        
        self.root.geometry('%dx%d+%d+%d' % hwxy)
        self.root.wm_title("History Diagram")
        
        self.fig1 = plt.figure(figsize=(7, 5), facecolor = 'white', edgecolor = 'none')
        self.ax1 = self.fig1.add_subplot(111)
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=self.root)
        
        self.canvas1.show(block = False)
        self.canvas1.get_tk_widget().grid(row = 0, column = 0, columnspan = 2)


class update_units_window:
    def __init__(self, root, demog_main):
        self.root = root
        self.demog_main = demog_main
        self.frame = tk.Frame(self.root)
        
        self.root.geometry('+%d+%d' % (root.winfo_screenwidth()/3,root.winfo_screenheight()/3))        
        self.root.wm_title("Units")

        self.new_units = 'Units'
        self.units_list = ['Coalescent units','Eff. Size and Generations','Eff. Size and Years']
        self.units = tk.StringVar()
        self.units.set('Units')
        self.units_menu = tk.OptionMenu(root,self.units,*self.units_list, command = self.update_units_textboxes)
        self.units_menu.grid(row = 1, column = 2, sticky = tk.EW)        

        self.years_per_gen_label = tk.Label(self.root, text="Years/gen")
        self.Nref_label = tk.Label(self.root, text="Reference Eff. Size")
        
        self.years_per_gen_ent = tk.Entry(self.root)
        self.Nref_ent = tk.Entry(self.root)
                
        self.years_per_gen_ent.delete(0, tk.END)
        self.years_per_gen_ent.insert(0, "30")
        self.Nref_ent.delete(0, tk.END)
        self.Nref_ent.insert(0, "10000")
        
        self.demog_main.new_units = 'Units'
        self.Nref_ent_exists = None
        self.years_per_gen_ent_exists = None
        
        self.update_units_button = tk.Button(master=self.root, text="Update Units", command=self.on_update_units_button_press)
        self.update_units_button.grid(row = 4, column = 2, sticky = tk.W)
        

    def update_units_textboxes(self,val):
        self.new_units = self.units.get()
        if self.new_units == 'Coalescent units':
            if self.Nref_ent_exists is not None:
                self.Nref_ent.grid_remove()
                self.Nref_label.grid_remove()
                self.Nref_ent_exists = None
            if self.years_per_gen_ent_exists is not None:
                self.years_per_gen_ent.grid_remove()
                self.years_per_gen_label.grid_remove()
                self.years_per_gen_ent_exists = None
        elif self.new_units == 'Eff. Size and Generations':
            if self.years_per_gen_ent_exists is not None:
                self.years_per_gen_ent.grid_remove()
                self.years_per_gen_label.grid_remove()
                self.years_per_gen_ent_exists = None
            if self.Nref_ent_exists is None:
                self.Nref_label.grid(row=2, column=1, sticky=tk.E)
                self.Nref_ent.grid(row = 2, column = 2, sticky = tk.W)
                self.Nref_ent_exists = 1
        elif self.new_units == 'Eff. Size and Years':
            if self.Nref_ent_exists is None:
                self.Nref_label.grid(row=2, column=1, sticky=tk.E)
                self.Nref_ent.grid(row = 2, column = 2, sticky = tk.W)
                self.Nref_ent_exists = 1
            if self.years_per_gen_ent_exists is None:
                self.years_per_gen_label.grid(row=3, column=1, sticky=tk.E)
                self.years_per_gen_ent.grid(row = 3, column = 2, sticky = tk.W)
                self.years_per_gen_ent_exists = 1


    def on_update_units_button_press(self):
        if self.new_units == 'Coalescent units':
            self.demog_main.new_units = 'Coalescent units'
        elif self.new_units == 'Eff. Size and Generations':
            if self.Nref_ent.get():
                Nref = ast.literal_eval(self.Nref_ent.get())
                if np.array(Nref).dtype.char == 'S':
                    self.demog_main.output_box.insert(INSERT,'ERROR: Specify numeric value for reference size.\n')
                    self.demog_main.output_box.see(tk.END)
                    return
                else:
                    self.demog_main.Nref = Nref
                    self.demog_main.new_units = 'Ne/generations'
        elif self.new_units == 'Eff. Size and Years':
            if self.Nref_ent.get():
                Nref = ast.literal_eval(self.Nref_ent.get())
                if np.array(Nref).dtype.char == 'S':
                    self.demog_main.output_box.insert(INSERT,'ERROR: Specify numeric value for reference size.\n')
                    self.demog_main.output_box.see(tk.END)
                    return
                else:
                    self.demog_main.Nref = Nref
            if self.years_per_gen_ent.get():
                years_per_gen = ast.literal_eval(self.years_per_gen_ent.get())
                if np.array(years_per_gen).dtype.char == 'S':
                    self.demog_main.output_box.insert(INSERT,'ERROR: Specify numeric value for years.\n')
                    self.demog_main.output_box.see(tk.END)
                    return
                else:
                    self.demog_main.years_per_gen =years_per_gen
            self.demog_main.new_units = 'Ne/years'
        
        self.demog_main.change_units()
        self.root.withdraw()


class inference_window:
    def __init__(self, root, demog_main, hwxy):
        self.root = root
        self.demog_main = demog_main
        self.frame = tk.Frame(self.root)
        
        self.root.geometry('%dx%d+%d+%d' % hwxy)
        self.root.wm_title("Inference")

        self.obs_jusfs_label = tk.Label(self.root, text="Obs JSFS path")
        self.num_x0_label = tk.Label(self.root, text="Num random start values")
        self.maxne_inf_label = tk.Label(self.root, text="Max population sizes")
        #self.nuref_inf_label = tk.Label(self.root, text="Reference Ne")
        self.nus_inf_label = tk.Label(self.root, text="Population sizes")
        self.ts_inf_label = tk.Label(self.root, text="Epoch boundaries")
        self.expmat_inf_label = tk.Label(self.root, text="Expmat")
        self.mig_inf_label = tk.Label(self.root, text="Migration events")
        self.ns_inf_label = tk.Label(self.root, text="Numbers of samples")
        self.nentries_inf_label = tk.Label(self.root, text="Entries to compute")
        self.maxt_inf_label = tk.Label(self.root, text="Max time")
        
        self.obs_jusfs_ent = tk.Entry(self.root)
        self.num_x0_ent = tk.Entry(self.root)
        self.maxne_inf_ent = tk.Entry(self.root)
        #self.nuref_inf_ent = tk.Entry(self.root)
        self.nus_inf_ent = tk.Entry(self.root)
        self.ts_inf_ent = tk.Entry(self.root)
        self.expmat_inf_ent = tk.Entry(self.root)
        self.mig_inf_ent = tk.Entry(self.root)
        self.ns_inf_ent = tk.Entry(self.root)
        self.nentries_inf_ent = tk.Entry(self.root)
        self.maxt_inf_ent = tk.Entry(self.root)                        
        
        for i in range(0,len(self.demog_main.maxnes_display)):
            self.demog_main.maxnes_display[i] = round(self.demog_main.maxnes_display[i],4)
            
        for i in range(0,len(self.demog_main.nus_display)):
            for j in range(0,len(self.demog_main.nus_display[i])):
                self.demog_main.nus_display[i][j] = round(self.demog_main.nus_display[i][j],4)
            
        for i in range(0,len(self.demog_main.ts_display)):
            for j in range(0,len(self.demog_main.ts_display[i])):
                self.demog_main.ts_display[i][j] = round(self.demog_main.ts_display[i][j],4)
            
        #for i in range(0,len(self.demog_main.expmat_display)):
        #    for j in range(0,len(self.demog_main.expmat_display[i])):
        #        if self.demog_main.expmat_display[i][j] is not None:
        #            self.demog_main.expmat_display[i][j] = round(self.demog_main.expmat_display[i][j],4)
            
        for i in range(0,len(self.demog_main.migs_display)):
            self.demog_main.migs_display[i][0] = round(self.demog_main.migs_display[i][0],4)
            self.demog_main.migs_display[i][3] = round(self.demog_main.migs_display[i][3],4)
            self.demog_main.migs_display[i][4] = round(self.demog_main.migs_display[i][4],4)            
            
        self.demog_main.maxt_display = round(self.demog_main.maxt_display,4)

        self.maxt_inf_ent.delete(0, tk.END)
        self.maxt_inf_ent.insert(0, json.dumps(self.demog_main.maxt_display))
        #self.maxt_plot_ent.delete(0, tk.END)
        #self.maxt_plot_ent.insert(0, "0.5")
        self.num_x0_ent.delete(0, tk.END)
        self.num_x0_ent.insert(0,"5")
        self.obs_jusfs_ent.delete(0, tk.END)
        self.obs_jusfs_ent.insert(0,"/Users/ethan/Desktop/JSFS.csv") 
        self.maxne_inf_ent.delete(0, tk.END)
        self.maxne_inf_ent.insert(0, json.dumps(self.demog_main.maxnes_display.tolist()))
        #self.nuref_inf_ent.delete(0, tk.END)
        #self.nuref_inf_ent.insert(0, "1")
        self.nus_inf_ent.delete(0, tk.END)
        self.nus_inf_ent.insert(0, json.dumps(self.demog_main.nus_display.tolist()))     
        self.ts_inf_ent.delete(0, tk.END)
        self.ts_inf_ent.insert(0, json.dumps(self.demog_main.ts_display.tolist()))
        self.expmat_inf_ent.delete(0, tk.END)
        self.expmat_inf_ent.insert(0, json.dumps(np.array(self.demog_main.expmat).tolist()))
        self.mig_inf_ent.delete(0, tk.END)
        self.mig_inf_ent.insert(0, json.dumps(self.demog_main.migs_display.tolist()))
        self.ns_inf_ent.delete(0, tk.END)
        self.ns_inf_ent.insert(0, json.dumps(np.array(self.demog_main.ns).tolist()))
        self.nentries_inf_ent.delete(0, tk.END)
        self.nentries_inf_ent.insert(0, json.dumps(self.demog_main.nentries.tolist()))       
                        
                
        self.obs_jusfs_label.grid(row = 1, column = 3, sticky = tk.E)
        self.maxt_inf_label.grid(row = 2, column = 3, sticky = tk.E)
        self.maxne_inf_label.grid(row = 3, column = 3, sticky = tk.E)
        #self.nuref_inf_label.grid(row = 4, column = 3, sticky = tk.E)
        self.nus_inf_label.grid(row = 5, column = 3, sticky = tk.E)
        self.ts_inf_label.grid(row = 6, column = 3, sticky = tk.E)
        self.expmat_inf_label.grid(row = 7, column = 3, sticky = tk.E)        
        self.mig_inf_label.grid(row = 8, column = 3, sticky = tk.E)
        self.ns_inf_label.grid(row = 9, column = 3, sticky = tk.E)
        self.num_x0_label.grid(row = 10, column = 3, sticky = tk.E)
        self.nentries_inf_label.grid(row = 11, column = 3, sticky = tk.E)                    
        
        self.obs_jusfs_ent.grid(row = 1, column = 4, sticky = tk.W)
        self.maxt_inf_ent.grid(row = 2, column = 4, sticky = tk.W)
        self.maxne_inf_ent.grid(row = 3, column = 4, sticky = tk.W)
        #self.nuref_inf_ent.grid(row = 4, column = 4, sticky = tk.W)
        self.nus_inf_ent.grid(row = 5, column = 4, sticky = tk.W)
        self.ts_inf_ent.grid(row = 6, column = 4, sticky = tk.W)
        self.expmat_inf_ent.grid(row = 7, column = 4, sticky = tk.W)
        self.mig_inf_ent.grid(row = 8, column = 4, sticky = tk.W)
        self.ns_inf_ent.grid(row = 9, column = 4, sticky = tk.W)
        self.num_x0_ent.grid(row = 10, column = 4, sticky = tk.W)
        self.nentries_inf_ent.grid(row = 11, column = 4, sticky = tk.W)          

        self.obs_jusfs = None
        self.x0 = None
        self.num_x0 = False
        self.jsfs_opt = None

        self.nuref_inf = 1
        self.obs_jusfs_path = None
        self.obsJSFS = None
        self.maxt_inf = None
        self.maxnes_inf = None
        self.nus_inf = None
        self.ts_inf = None
        self.migs_inf = None
        self.ns_inf = None
        self.nentries_inf = None
        self.expmat_inf = None
        
        self.maxt_inf_display = None
        self.maxnes_inf_display = None
        self.nus_inf_display = None
        self.ts_inf_display = None
        self.migs_inf_display = None
                
        self.to_infer_list = ['JSFS','JUSFS']
        self.stat_to_infer = tk.StringVar()
        self.stat_to_infer.set('Statistics to infer')
        self.stat_drop_menu_infer = tk.OptionMenu(root,self.stat_to_infer,*self.to_infer_list)
        self.stat_drop_menu_infer.grid(row = 12, column = 4, sticky = tk.EW)        
        
        self.hist_inf = None
        self.JUSFS_inf = None
        self.JSFS_inf = None
        
        self.full_boxes_inf = None
        self.hist_inferred = None
                        
        self.optimize_hist_button = tk.Button(master = self.root, text="Optimize History", command = self.on_optimize_hist_button_call)
        self.optimize_hist_button.grid(row = 13, column = 4, sticky = tk.W)
        
        self.optimize_hist_button = tk.Button(master = self.root, text="Update graphic hist. vals", command = self.on_update_demog_main_hist_button_call)
        self.optimize_hist_button.grid(row = 14, column = 4, sticky = tk.W)      
        
        self.quit_button = tk.Button(master = self.root, text="Close optimizer", command = self.close_window)
        self.quit_button.grid(row = 15, column = 4, sticky = tk.W)
        

                                        
    def close_window(self):        
        self.root.destroy()


    def on_optimize_hist_button_call(self):
                
        #Check if all the boxes are full or not
        self.full_boxes_inf = True
        if self.obs_jusfs_ent.get():       
            filepath = self.obs_jusfs_ent.get()
        else:
            self.full_boxes_inf = False
        if self.maxt_inf_ent.get():
            self.maxt_inf_display = np.array(ast.literal_eval(self.maxt_inf_ent.get()))
        else:
            self.full_boxes_inf = False
        if self.maxne_inf_ent.get():
            self.maxnes_inf_display = np.array(ast.literal_eval(self.maxne_inf_ent.get()))
            if len(self.maxnes_inf_display) == 0:
                self.full_boxes_inf = False
        else:
            self.full_boxes_inf = False
        #if self.nuref_inf_ent.get():       
        #    self.nuref_inf = np.array(ast.literal_eval(self.nuref_inf_ent.get()))
        #    if self.nuref_inf is None:
        #        self.full_boxes_inf = False
        #else:
        #    self.full_boxes_inf = False
        if self.nus_inf_ent.get():
            self.nus_inf_display = ast.literal_eval(self.nus_inf_ent.get().replace("?","None"))
            if len(self.nus_inf_display) == 0:
                self.full_boxes_inf = False
        else:
            self.full_boxes_inf = False
        if self.ts_inf_ent.get():
            self.ts_inf_display = ast.literal_eval(self.ts_inf_ent.get().replace("?","None"))
            if len(self.ts_inf_display) == 0:
                self.full_boxes_inf = False
        else:
            self.full_boxes_inf = False
        if self.mig_inf_ent.get():       
            self.migs_inf_display = np.array(ast.literal_eval(self.mig_inf_ent.get().replace("?","None")))
        else:
            self.full_boxes_inf = False
        if self.ns_inf_ent.get():
            self.ns_inf = np.array(ast.literal_eval(self.ns_inf_ent.get()))
            if len(self.ns_inf) == 0:
                self.full_boxes_inf = False
        else:
            self.full_boxes_inf = False
        if self.num_x0_ent.get():       
            self.num_x0 = ast.literal_eval(self.num_x0_ent.get())
        if self.nentries_inf_ent.get():       
            self.nentries_inf = np.array(ast.literal_eval(self.nentries_inf_ent.get()))
            if self.nentries_inf is None:
                self.full_boxes_inf = False
        else:
            self.full_boxes_inf = False  
        if self.expmat_inf_ent.get():
            self.expmat_inf = ast.literal_eval(self.expmat_inf_ent.get().replace("null","None"))
            if len(self.expmat_inf) == 0:
                self.full_boxes_inf = False
        else:
            self.full_boxes_inf = False
        
        #print "migs inf read in >>>>>>>>>>>>>>>"
        #print self.migs_inf_display

        #Convert units if need be
        if (self.demog_main.new_units == 'Ne/years') or (self.demog_main.new_units == 'Ne/generations'):
            self.demog_main.Nref = np.array(ast.literal_eval(self.demog_main.Nref_ent.get()))
        if self.demog_main.new_units == 'Ne/years':
            self.demog_main.years_per_gen = np.array(ast.literal_eval(self.demog_main.years_per_gen_ent.get()))
        
        self.maxnes_inf = deepcopy(self.maxnes_inf_display)
        for i in range(0,len(self.maxnes_inf)):
            if (self.demog_main.new_units == 'Ne/generations') or (self.demog_main.new_units == 'Ne/years'):
                if not (self.maxnes_inf[i] is None):
                    self.maxnes_inf[i] = self.maxnes_inf[i] / self.demog_main.Nref                
        self.nus_inf = deepcopy(self.nus_inf_display)
        for i in range(0,len(self.nus_inf)):
            for j in range(0,len(self.nus_inf[i])):
                if (self.demog_main.new_units == 'Ne/generations') or (self.demog_main.new_units == 'Ne/years'):
                    if not (self.nus_inf[i][j] is None):
                        self.nus_inf[i][j] = self.nus_inf[i][j] / self.demog_main.Nref
        self.ts_inf = deepcopy(self.ts_inf_display)
        for i in range(0,len(self.ts_inf)):
            for j in range(0,len(self.ts_inf[i])):
                if (self.demog_main.new_units == 'Ne/generations'):
                    if not (self.ts_inf[i][j] is None):
                        self.ts_inf[i][j] = self.ts_inf[i][j] / (2 * self.demog_main.Nref)
                if (self.demog_main.new_units == 'Ne/years'):
                    if not (self.ts_inf[i][j] is None):
                        self.ts_inf[i][j] = self.ts_inf[i][j] / (2 * self.demog_main.Nref * self.demog_main.years_per_gen)
        self.migs_inf = deepcopy(self.migs_inf_display)
        for i in range(0,len(self.migs_inf)):
            if hasattr(self.migs_inf[i][0],"__len__"):
                self.migs_inf[i][0] = self.migs_inf[i][0][0]
                if (self.demog_main.new_units == 'Ne/generations'):
                    if self.migs_inf_display[i][0][1] is not None:
                        self.migs_inf_display[i][0][1] = self.migs_inf_display[i][0][1] / (2 * self.demog_main.Nref)
                    if self.migs_inf_display[i][0][2] is not None:
                        self.migs_inf_display[i][0][2] = self.migs_inf_display[i][0][2] / (2 * self.demog_main.Nref)
                elif (self.demog_main.new_units == 'Ne/years'):
                    if self.migs_inf_display[i][0][1] is not None:
                        self.migs_inf_display[i][0][1] = self.migs_inf_display[i][0][1] / (2 * self.demog_main.Nref * self.demog_main.years_per_gen)
                    if self.migs_inf_display[i][0][2] is not None:
                        self.migs_inf_display[i][0][2] = self.migs_inf_display[i][0][2] / (2 * self.demog_main.Nref * self.demog_main.years_per_gen)
        for i in range(0,len(self.migs_inf)):
            if (self.demog_main.new_units == 'Ne/generations'):
                if not (self.migs_inf[i][0] is None):
                    self.migs_inf[i][0] = self.migs_inf[i][0] / (2 * self.demog_main.Nref)
                if not (self.migs_inf[i][4] is None):
                    self.migs_inf[i][4] = self.migs_inf[i][4] / (2 * self.demog_main.Nref)
            if (self.demog_main.new_units == 'Ne/years'):
                if not (self.migs_inf[i][0] is None):
                    self.migs_inf[i][0] = self.migs_inf[i][0] / (2 * self.demog_main.Nref * self.demog_main.years_per_gen)
                if not (self.migs_inf[i][4] is None):
                    self.migs_inf[i][4] = self.migs_inf[i][4] / (2 * self.demog_main.Nref * self.demog_main.years_per_gen)
        self.maxt_inf = deepcopy(self.maxt_inf_display)
        if (self.demog_main.new_units == 'Ne/generations'):
            self.maxt_inf = self.maxt_inf / (2*self.demog_main.Nref)
        elif (self.demog_main.new_units == 'Ne/years'):
            self.maxt_inf = self.maxt_inf / (2 * self.demog_main.Nref * self.demog_main.years_per_gen)

        
        if not self.full_boxes_inf:
            self.demog_main.output_box.insert(INSERT,'ERROR: All inference text fields must be properly specified.\n')
            self.demog_main.output_box.see(tk.END)
        else:
            #Find out what we need to infer and initialize the history
            #If we haven't drawn a history yet, these might not be specified yet
            if self.demog_main.plotdt is None:
                self.demog_main.plotdt = 0.005
            self.demog_main.maxt = self.maxt_inf
            self.demog_main.maxt_ent.delete(0, tk.END)
            self.demog_main.maxt_ent.insert(0, self.maxt_inf_ent.get())
            
            nu_2infer = []
            t_2infer = []
            #self.expmat_inf = deepcopy(self.nus_inf)
            for i in range(0,len(self.nus_inf)):
                nuvec = self.nus_inf[i]
                tvec = self.ts_inf[i]
                for j in range(0,len(nuvec)):
                    #self.expmat_inf[i][j] = 0
                    if self.nus_inf[i][j] is None: #Then we infer it, and it's not constrained
                        nu_2infer = nu_2infer + [[i,j]]
                        self.nus_inf[i][j] = self.maxnes_inf[i]/2 #Set the dummy variable to the max size over two
                    elif self.nus_inf[i][j] < -1: #Then we infer it and other sizes in the population are constrained to it
                        val = self.nus_inf[i][j]
                        #print "line 1454 >>>>>>>>>>>>>>>>>>>>>"                        
                        #print val
                        cons_list = [i,j]
                        grow_indic = None
                        if abs(np.mod(val,2)) == 1: #Then it's growth
                            #cons_list = cons_list + [None]
                            grow_indic = None
                        else:
                            #cons_list = cons_list + [1]
                            grow_indic = 1
                        self.nus_inf[i][j] = self.maxnes_inf[i]/2
                        num_cons_epochs = 0
                        cons_epochs = []
                        for ep_epind in range(j+1,len(self.nus_inf[i])):
                            if self.nus_inf[i][ep_epind] == val:
                                #cons_list = cons_list + [ep_epind]
                                cons_epochs = cons_epochs + [ep_epind]
                                num_cons_epochs = num_cons_epochs + 1
                                self.nus_inf[i][ep_epind] = self.nus_inf[i][j] #In the case of exp growth, this size should be exponentially changing, but the optimizer takes care of it and we don't know the next popsize to set it here. So set all equal                                
                        if num_cons_epochs > 0:
                            cons_list = cons_list + [grow_indic]
                            cons_list = cons_list + cons_epochs  
                        nu_2infer = nu_2infer + [cons_list]
                    if (self.ts_inf[i][j] is None) or (self.ts_inf[i][j] < -1):
                        #print 'Got to line 1442>>>>>>>>>>>>>>>>>'
                        val = self.ts_inf[i][j]                        
                        if j == 0:
                            self.demog_main.output_box.insert(INSERT,'ERROR: Cannot infer time at t=0.\n')
                            self.demog_main.output_box.see(tk.END)
                            return
                        elif j < len(nuvec) - 1:
                            lbd = tvec[j-1]
                            ubd = tvec[j+1]
                            k = j+2
                            while ubd is None and k < len(tvec):
                                ubd = tvec[k]
                                k = k+1
                            if ubd is None: #Then all entries from j up to the last are None
                                ubd = (lbd + self.maxt_inf)/2 #Set the ubd to the mipoint
                            self.ts_inf[i][j] = (lbd + ubd)/2 #Set the dummy time to the midpoint of lbd and ubd
                        else:
                            lbd = tvec[j-1]
                            ubd = self.maxt_inf
                            self.ts_inf[i][j] = (lbd + ubd)/2
                        migcons = []
                        if val < -1:
                            #print 'Got to line 1464>>>>>>>>>>>>>>>>>'
                            for migind in range(0,len(self.migs_inf)):
                                if self.migs_inf[migind][0] == val:
                                    #print 'Got to line 1467>>>>>>>>>>>>>>>>>'
                                    migcons = migcons + [migind]
                                    self.migs_inf[migind][0] = self.ts_inf[i][j]
                                    #print migcons
                                    #print self.ts_inf[i][j]
                                    
                        t_2infer = t_2infer + [[i,j]+migcons]
                        #print 't2infer >>>>>>>>>>>>>>>>>>>>'
                        #print t_2infer

                            
                        
            #print "nu 2 infer >>>>>>>>>>>>>>>>"
            #print nu_2infer
            #print ' migs inf 1  >>>>>>>>>>>>>>>>>>'
            #print self.migs
            #print self.migs_inf
                                                                                                            
            mig_t_2infer = []
            mig_mag_2infer = []
            for i in range(0,len(self.migs_inf)):
                if self.migs_inf[i][0] is None:
                    mtlbd = 0
                    mtubd = self.maxt_inf*1
                    if hasattr(self.migs_inf_display[i][0],"__len__"):
                        if self.migs_inf_display[i][0][1] is not None:
                            mtlbd = self.migs_inf_display[i][0][1]
                        if self.migs_inf_display[i][0][2] is not None:
                            mtubd = self.migs_inf_display[i][0][2]
                    mig_t_2infer = mig_t_2infer + [[i,mtlbd,mtubd]]
                    self.migs_inf[i][0] = np.random.uniform(low=mtlbd, high=mtubd, size=None)
                if self.migs_inf[i][3] is None:
                    mig_mag_2infer = mig_mag_2infer + [i]
                    self.migs_inf[i][3] = np.random.uniform(low=0, high=1, size=None)
                #elif isinstance(self.migs_inf[i][3],str):
                elif self.migs_inf[i][3] < -1:
                    val = self.migs_inf[i][3]
                    temp_mag = [i]
                    rnd = np.random.uniform(low=0, high=1, size=None)
                    self.migs_inf[i][3] = rnd
                    for i2 in range(i+1,len(self.migs_inf)):
                        #if isinstance(self.migs_inf[i2][3],str):
                        if self.migs_inf[i2][3] < -1:
                            if val == self.migs_inf[i2][3]:
                                temp_mag = temp_mag + [i2]
                                self.migs_inf[i2][3] = rnd
                    mig_mag_2infer = mig_mag_2infer + [temp_mag]
            
            #print "migs inf 2 >>>>>>>>>>>>>>>>>>>"
            #print self.migs_inf
            
            #print "migmags 2infer >>>>>>>>>>>>>>>"
            #print mig_mag_2infer
                            
            
            #print 'MIGS (optimizie history button: after computing mig2infer): '
            #print self.migs
            #print self.migs_inf
            
            #print 'MIG T TO INFER: ---------------'
            #print mig_t_2infer
            #print 'MIG MAG TO INFER: -------------'
            #print mig_mag_2infer
                                                                                                                                                                                                                                                                                                                                                                                                                        
            #self.output_box.insert(INSERT,'STATUS: All values read.\n')
            #self.output_box.insert(INSERT,'maxt: \n')
            #self.output_box.insert(INSERT,str(self.maxt_inf))
            #self.output_box.insert(INSERT,'\n\n')
            #self.output_box.insert(INSERT,'nus: \n')
            #self.output_box.insert(INSERT,json.dumps(self.nus_inf))
            #self.output_box.insert(INSERT,'\n\n')
            #self.output_box.insert(INSERT,'ts: \n')
            #self.output_box.insert(INSERT,json.dumps(self.ts_inf))
            #self.output_box.insert(INSERT,'\n\n')
            #self.output_box.insert(INSERT,'expmat: \n')
            #self.output_box.insert(INSERT,json.dumps(self.expmat_inf))
            #self.output_box.insert(INSERT,'\n\n')
            #self.output_box.insert(INSERT,'migs: \n')
            #self.output_box.insert(INSERT,json.dumps(self.migs_inf.tolist()))
            #self.output_box.insert(INSERT,'\n\n')
            #self.output_box.insert(INSERT,'num start posits: \n')
            #self.output_box.insert(INSERT, str(self.num_x0))
            #self.output_box.insert(INSERT,'\n\n')
            #self.output_box.see(tk.END)
            #self.output_box.insert(INSERT,'nu2infer: \n')
            #self.output_box.insert(INSERT, str(nu_2infer))
            #self.output_box.insert(INSERT,'\n\n')
            #self.output_box.insert(INSERT,'t2infer: \n')
            #self.output_box.insert(INSERT, str(t_2infer))
            #self.output_box.insert(INSERT,'\n\n')
            #self.output_box.insert(INSERT,'mig_t_2infer: \n')
            #self.output_box.insert(INSERT, str(mig_t_2infer))
            #self.output_box.insert(INSERT,'\n\n')
            #self.output_box.insert(INSERT,'mig_mag_2infer: \n')
            #self.output_box.insert(INSERT, str(mig_mag_2infer))
            #self.output_box.insert(INSERT,'\n\n')
                                                
            #print 'MIGS (optimizie history button: after setting box values): >>>>>>>>>>>>>>>>>>>>>>>>>'
            #print self.migs
            #print self.migs_inf                                                                        
                                                                                                                                                            
            #Draggable pop history requires a figure. If we don't have it, make it
            if self.demog_main.fig1 is None:
                self.demog_main.fig1 = plt.figure(facecolor = 'white')
                self.demog_main.ax1 = self.demog_main.fig1.add_subplot(111)
                self.demog_main.ax1.cla()                
            self.demog_main.hist = DraggablePopHistory(self.demog_main,self.demog_main.fig1, self.demog_main.ax1, self.ts_inf, self.nus_inf, self.expmat_inf, self.migs_inf, self.maxnes_inf, self.maxt_inf, copy.deepcopy(self.demog_main.plotdt), self.old_units, self.Nref, self.years_per_gen)
            
            #Read in the JUSFS
            #if filepath.find('.csv') >= 0:
            #    #Then it's a file of sequences and we need to compute the sfs
            #    #Assume the file rows correspond to individuals, cols to snps. 
            #    #Derived snps are 1, ancestral are 0
            #    #The first n_1 rows correspond to haplotypes from population 1, the next n_2 rows to haplotypes from population 2, etc.
            #    #self.obs_jsfs = np.zeros(tuple(self.demog_main.ns))
            #    sums = []
            #    f = open(filepath, 'rb') # opens the csv file
            #    try:
            #        reader = csv.reader(f)  # creates the reader object
            #        for i in range(0,len(self.demog_main.ns)):
            #            row = np.array(next(reader))
            #            for j in range(1,self.demog_main.ns[i]):
            #                row = row + np.array(next(reader))
            #            sums = sums + [row.tolist()]
            #    finally:
            #        f.close()
            #    self.obs_jsfs = np.zeros(tuple(np.array(self.demog_main.ns)+1))
            #    for i in range(0,len(sums[0])):
            #        
            #else:
            #    infile = open(filepath, "r")
            #    jsfs_str = infile.read()
            #    infile.close()
            #    self.obs_jsfs = np.array(ast.literal_eval(jsfs_str))
            
                #Then it's a file of sequences and we need to compute the sfs
                #Assume the file rows correspond to individuals, cols to snps. 
                #Derived snps are 1, ancestral are 0
                #The first n_1 rows correspond to haplotypes from population 1, the next n_2 rows to haplotypes from population 2, etc.
                
            infile = open(filepath, "r")
            jsfs_str = infile.read()
            infile.close()
            self.obs_jsfs = np.array(ast.literal_eval(jsfs_str))                
            
            #print 'MIGS (optimizie history button: after creating draggable hist): '
            #print self.migs
            #print self.migs_inf
            #print self.hist.migs
            
            self.obs_jsfs = np.array(ast.literal_eval(jsfs_str))
            self.demog_main.jsfs = JUSFSprecise(self.demog_main.hist, self.nentries_inf, self.nuref_inf, self.ns_inf, self.maxt_inf, self.demog_main.Ent_sum_maxn, True, None)
            self.demog_main.jsfs.get_JUSFS_point_migrations()
            
            #print 'MIGS (optimizie history button: after computing JUSFSprecise): '
            #print self.migs
            #print self.migs_inf
            #print self.jsfs.migs
                    
            use_jsfs = False
            if self.stat_to_infer.get() == 'JSFS':
                use_jsfs = True
            self.jsfs_opt = JUSFS_optimizer(self.demog_main.jsfs, self.obs_jsfs, nu_2infer, t_2infer, mig_mag_2infer, mig_t_2infer, self.maxnes_inf, self.maxt_inf, self.num_x0, use_jsfs)

            #print 'MIGS (optimizie history button: after initializing optimizer): '
            #print self.migs
            #print self.migs_inf                
                                                
            self.demog_main.output_box.insert(INSERT, 'Starting optimization.\n')
            self.demog_main.output_box.see(tk.END)
            
            self.jsfs_opt.optimize_jusfs()
            
            self.demog_main.output_box.insert(INSERT,'Optimization done!\n')
            self.demog_main.output_box.see(tk.END)

            #print 'MIGS (optimizie history button: after optimiziation): '
            #print self.migs
            #print self.migs_inf
            
            #Write all optimized values to file
            out_filepath = filepath[0:-4] + '_opt.csv'
            #out_file = open(out_filepath, "w")
            outmat = deepcopy(self.jsfs_opt.xmins.tolist())
            for i in range(0,len(outmat)):
                outmat[i] = [self.jsfs_opt.fvals[i]] + outmat[i].tolist()
            np.savetxt(out_filepath,np.array(outmat))
            #out_file.write(str(outmat))
            #out_file.close()
            
            #Find the most optimal value                        
            min_ind = self.jsfs_opt.fvals.argmin()
            xmin = self.jsfs_opt.xmins[min_ind]
            
            #print "t 2 infer>>>>>>>>>>>>>>>>>>>>>>>"
            #print t_2infer
            
            #Record the inferred parameters
            j = 0
            for i in range(0,len(t_2infer)):
                popind = t_2infer[i][0]
                epind = t_2infer[i][1]
                self.ts_inf[popind][epind] = xmin[j]
                for migind in range(2,len(t_2infer[i])):
                    self.migs_inf[t_2infer[i][migind]][0] = xmin[j]
                j = j + 1
                
                
            #print "and we got here, too >>>>>>>>>>>>>>>>>"
            
            for i in range(0,len(nu_2infer)):
                popind = nu_2infer[i][0]
                epind = nu_2infer[i][1]
                self.nus_inf[popind][epind] = xmin[j]
                if len(nu_2infer[i]) > 2:
                    
                    #print "LINE 1707: Constraint exp or const >>>>>>>>>>>>>>>>>>"
                    
                    if nu_2infer[i][2] is not None: #Then sizes are constrained to be equal
                        #print "Got to 1711 >>>>>>>>>>>>>>>>"
                        for q in range(3,len(nu_2infer[i])):
                            ep_epind = nu_2infer[i][q]
                            self.nus_inf[popind][ep_epind] = xmin[j]
  		    else: #Then sizes are constrained to change exponentially
  		        #print "Got to 1709 >>>>>>>>>>>>>>>>>>>>"
                        next_epind = nu_2infer[i][-1]+1 #Index of the epoch following the last constrained epoch
                        nu_inf_ind = None
                        for q in range(0,len(nu_2infer)):
                            if popind == nu_2infer[q][0] and next_epind == nu_2infer[q][1]: #Then we infer its size
                                nu_inf_ind = q
                        t_inf_ind = None
                        for q in range(0,len(t_2infer)):
                            if popind == t_2infer[q][0] and next_epind == t_2infer[q][1]: #Then we infer its time
                                t_inf_ind = q
                        nuval = None #nu in the following epoch
                        if nu_inf_ind is None:
                            nuval = self.nus_inf[popind][next_epind]
                        else:
                            nuval = xmin[len(t_2infer) + nu_inf_ind]
                        tval = None #Time at which the following epoch begins
                        if t_inf_ind is None:
                            tval = self.ts_inf[popind][next_epind]
                        else:
                            tval = xmin[t_inf_ind]
                        tstart = self.ts_inf[popind][epind]
                        nustart = self.nus_inf[popind][epind]
                        gam = (1 / (tval - tstart)) * log(nuval/nustart)
                        
                        #print "tstart, tend, nustart, nuend, gamma >>>>>>>>>>>>>"
                        #print tstart, tval, nustart, nuval, gam
                        
                        for q in range(3,len(nu_2infer[i])):
                            ep_epind = nu_2infer[i][q]
                            tep = self.ts_inf[popind][ep_epind]
                            ep_nu = nustart * exp(gam * (tep - tstart))
                            self.nus_inf[popind][ep_epind] = ep_nu
                        
                j = j + 1
            
            #print 'LENGTH MIG MAG 2 INFER: -----'
            #print len(mig_mag_2infer)
            #print 'MIG MAG 2 INFER: -----'
            #print mig_mag_2infer
            #print 'MIGS INF: ----------'
            #print self.migs_inf
            for i in range(0,len(mig_mag_2infer)):
                miginds = mig_mag_2infer[i]
                if not (hasattr(miginds, "__len__")):
                    self.migs_inf[miginds][3] = xmin[j]-0 #Copy by value
                else:
                    for k in range(0,len(miginds)):
                        self.migs_inf[miginds[k]][3] = xmin[j]-0
                j = j + 1
            
            for i in range(0,len(mig_t_2infer)):
                migind = mig_t_2infer[i][0]
                self.migs_inf[migind][0] = xmin[j]-0 #Copy by value
                j = j + 1

            #print 'MIGS (optimizie history button: after recording values): '
            #print self.migs
            #print self.migs_inf
            
            self.hist_inferred = True

            
    def on_update_demog_main_hist_button_call(self):
        if self.hist_inferred:
            self.demog_main.maxnes = deepcopy(self.maxnes_inf)
            self.demog_main.nus = deepcopy(self.nus_inf)
            self.demog_main.ts = deepcopy(self.ts_inf)
            self.demog_main.expmat = deepcopy(self.expmat_inf)
            self.demog_main.migs = deepcopy(self.migs_inf)
            self.demog_main.maxt = self.maxt_inf+0
            
            
            self.demog_main.maxnes_display = deepcopy(self.demog_main.maxnes)
            for i in range(0,len(self.demog_main.maxnes)):
                if (self.demog_main.new_units == 'Ne/generations') or (self.demog_main.new_units == 'Ne/years'):
                    self.demog_main.maxnes_display[i] = self.demog_main.maxnes[i] * self.demog_main.Nref 
            
            self.demog_main.nus_display = deepcopy(self.demog_main.nus)               
            for i in range(0,len(self.demog_main.nus)):
                for j in range(0,len(self.demog_main.nus[i])):
                    if (self.demog_main.new_units == 'Ne/generations') or (self.demog_main.new_units == 'Ne/years'):
                        self.demog_main.nus_display[i][j] = self.demog_main.nus[i][j] * self.demog_main.Nref
            
            self.demog_main.ts_display = deepcopy(self.demog_main.ts)               
            for i in range(0,len(self.demog_main.ts)):
                for j in range(0,len(self.demog_main.ts[i])):
                    if (self.demog_main.new_units == 'Ne/generations'):
                        self.demog_main.ts_display[i][j] = self.demog_main.ts[i][j] * (2 * self.demog_main.Nref)
                    if (self.demog_main.new_units == 'Ne/years'):
                        self.demog_main.ts_display[i][j] = self.demog_main.ts[i][j] * (2 * self.demog_main.Nref * self.demog_main.years_per_gen)
            
            self.demog_main.migs_display = deepcopy(self.demog_main.migs)               
            for i in range(0,len(self.demog_main.migs)):
                if (self.demog_main.new_units == 'Ne/generations'):
                    self.demog_main.migs_display[i][0] = self.demog_main.migs[i][0] * (2 * self.demog_main.Nref)
                    self.demog_main.migs_display[i][4] = self.demog_main.migs[i][4] * (2 * self.demog_main.Nref)
                if (self.demog_main.new_units == 'Ne/years'):
                    self.demog_main.migs_display[i][0] = self.demog_main.migs[i][0] * (2 * self.demog_main.Nref * self.demog_main.years_per_gen)
                    self.demog_main.migs_display[i][4] = self.demog_main.migs[i][4] * (2 * self.demog_main.Nref * self.demog_main.years_per_gen)
            
            self.demog_main.maxt_display = deepcopy(self.demog_main.maxt)               
            if (self.demog_main.new_units == 'Ne/generations'):
                self.demog_main.maxt_display = self.demog_main.maxt * (2*self.demog_main.Nref)
            elif (self.demog_main.new_units == 'Ne/years'):
                self.demog_main.maxt_display = self.demog_main.maxt * (2 * self.demog_main.Nref * self.demog_main.years_per_gen)            

                
            for i in range(0,len(self.demog_main.nus_display)):
                for j in range(0,len(self.demog_main.nus_display[i])):
                    self.demog_main.nus_display[i][j] = round(self.demog_main.nus_display[i][j],4)
                
            for i in range(0,len(self.demog_main.ts_display)):
                for j in range(0,len(self.demog_main.ts_display[i])):
                    self.demog_main.ts_display[i][j] = round(self.demog_main.ts_display[i][j],4)
                
            #for i in range(0,len(self.demog_main.expmat_display)):
            #    for j in range(0,len(self.demog_main.expmat_display[i])):
            #        if self.demog_main.expmat_display[i][j] is not None:
            #            self.demog_main.expmat_display[i][j] = round(self.demog_main.expmat_display[i][j],4)
                
            for i in range(0,len(self.demog_main.migs_display)):
                self.demog_main.migs_display[i][0] = round(self.demog_main.migs_display[i][0],4)
                self.demog_main.migs_display[i][3] = round(self.demog_main.migs_display[i][3],4)
                self.demog_main.migs_display[i][4] = round(self.demog_main.migs_display[i][4],4)            
                
            self.demog_main.maxt_display = round(self.demog_main.maxt_display,4)

            #Update the history text boxes
            self.demog_main.maxne_ent.delete(0, tk.END)
            self.demog_main.maxne_ent.insert(0, json.dumps(np.array(self.demog_main.maxnes_display).tolist()))
            #self.demog_main.nus = self.nus_inf
            self.demog_main.nus_ent.delete(0, tk.END)
            self.demog_main.nus_ent.insert(0, json.dumps(np.array(self.demog_main.nus_display).tolist()))
            #self.demog_main.ts = self.ts_inf
            self.demog_main.ts_ent.delete(0, tk.END)
            self.demog_main.ts_ent.insert(0, json.dumps(np.array(self.demog_main.ts_display).tolist()))
            #self.demog_main.expmat = self.expmat_inf
            self.demog_main.expmat_ent.delete(0, tk.END)
            self.demog_main.expmat_ent.insert(0, json.dumps(np.array(self.demog_main.expmat).tolist()))
            #self.demog_main.migs = deepcopy(self.migs_inf)
            self.demog_main.mig_ent.delete(0, tk.END)
            self.demog_main.mig_ent.insert(0, json.dumps(np.array(self.demog_main.migs_display).tolist()))
            #self.demog_main.maxt = self.maxt_inf
            self.demog_main.maxt_ent.delete(0, tk.END)
            self.demog_main.maxt_ent.insert(0, str(self.demog_main.maxt_display))
            
            #print 'MIGS (optimizie history button: after updating text boxes): '
            #print self.migs
            #print self.migs_inf
        else:
            self.demog_main.output_box.insert(INSERT,'\n\n ERROR: You must infer a history first.\n\n')
            self.demog_main.output_box.see(tk.END)



class CreateToolTip(object): #Tooltip class from http://stackoverflow.com/questions/3221956/what-is-the-simplest-way-to-make-tooltips-in-tkinter
    """
    create a tooltip for a given widget
    """
    def __init__(self, widget, wrap_len, text='widget info'):
        self.waittime = 500     #miliseconds
        self.wraplength = wrap_len   #pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify='left',
                       background="#ffffff", relief='solid', borderwidth=1,
                       wraplength = self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()



class popup_epoch_textfield:
    def __init__(self,demog_main,popind,epind,x_loc,y_loc): 
        self.demog_main = demog_main
        #self.root = demog_main.root
        self.toplevel = tk.Toplevel(self.demog_main.root)
        self.toplevel.geometry('+%d+%d' % (x_loc,y_loc))
        self.toplevel.wm_title("Specify size and time")
        
        self.popind = popind
        self.epind = epind
        
        self.N_label = tk.Label(self.toplevel, text="Size")
        if self.demog_main.hist.units == 'Coalescent units':   
            self.N_label_ttp = CreateToolTip(self.N_label, 200, 'Population size in coalescent units.')
        elif self.demog_main.hist.units == 'Ne/generations':
            self.N_label_ttp = CreateToolTip(self.N_label, 200, 'Population size in coalescent units.')
        elif self.demog_main.hist.units == 'Ne/years':
            self.N_label_ttp = CreateToolTip(self.N_label, 200, 'Population size in diploid individuals.')
        self.t_label = tk.Label(self.toplevel, text="Time")
        if self.demog_main.hist.units == 'Coalescent units':   
            self.t_label_ttp = CreateToolTip(self.t_label, 200, 'Epoch boundary time in units of 2Nref generations.')
        elif self.demog_main.hist.units == 'Ne/generations':
            self.t_label_ttp = CreateToolTip(self.t_label, 200, 'Epoch boundary time in units of generations.')
        elif self.demog_main.hist.units == 'Ne/years':
            self.t_label_ttp = CreateToolTip(self.t_label, 200, 'Epoch boundary time in years.')
        
        self.N_ent = tk.Entry(self.toplevel)
        self.t_ent = tk.Entry(self.toplevel)
        
        self.N = self.demog_main.hist.nus[popind][epind]+0 #Copy by value
        self.t = self.demog_main.hist.ts[popind][epind]+0 #Copy by value
                
        self.N_ent.delete(0, tk.END)
        self.t_ent.delete(0, tk.END)
        if self.demog_main.hist.units == 'Coalescent units':
            self.t_ent.insert(0, str(self.t))
            self.N_ent.insert(0, str(self.N))
        elif self.demog_main.hist.units == 'Ne/generations':
            self.t_ent.insert(0, str(2 * self.demog_main.hist.Nref * self.t))
            self.N_ent.insert(0, str(self.demog_main.hist.Nref * self.N))
        elif self.demog_main.hist.units == 'Ne/years':
            self.t_ent.insert(0, str(2 * self.demog_main.hist.Nref * self.demog_main.hist.years_per_gen * self.t))
            self.N_ent.insert(0, str(self.demog_main.hist.Nref * self.N))
        
        self.N_label.grid(row = 1, column = 1, sticky = tk.E)
        self.t_label.grid(row = 2, column = 1, sticky = tk.E)
        
        self.N_ent.grid(row = 1, column = 2, sticky = tk.W)
        self.t_ent.grid(row = 2, column = 2, sticky = tk.W)
        
        self.get_command_button = tk.Button(master = self.toplevel, text="Set Values", command = self.on_set_values_button_call)
        self.get_command_button.grid(row = 3, column = 2, sticky = tk.W)
        

    def on_set_values_button_call(self):
        if self.N_ent.get():       
            self.N = np.array(ast.literal_eval(self.N_ent.get()))
            if self.N is not None:
                if self.N.dtype.char == 'S':
                    self.demog_main.app_output_box_window.output_box.insert(INSERT,'\n\nERROR: Must specify population size.\n\n')
                    self.demog_main.app_output_box_window.output_box.see(tk.END)
                    return
        else:
            self.demog_main.app_output_box_window.output_box.insert(INSERT,'\n\nERROR: Must specify population size.\n\n')
            self.demog_main.app_output_box_window.output_box.see(tk.END)
            self.N = None
            return
        
        if self.t_ent.get():       
            self.t = np.array(ast.literal_eval(self.t_ent.get()))
            if self.t is not None:
                if self.t.dtype.char == 'S':
                    self.demog_main.app_output_box_window.output_box.insert(INSERT,'\n\nERROR: Must specify epoch boundary time.\n\n')
                    self.demog_main.app_output_box_window.output_box.see(tk.END)
                    return
        else:
            self.demog_main.app_output_box_window.output_box.insert(INSERT,'\n\nERROR: Must specify epoch boundary time.\n\n')
            self.demog_main.app_output_box_window.output_box.see(tk.END)
            self.t = None
            return
        

        if self.demog_main.hist.units == 'Ne/generations':
            self.N = self.N / self.demog_main.hist.Nref #Copy by value
            self.t = self.t / (2 * self.demog_main.hist.Nref)
        elif self.demog_main.hist.units == 'Ne/years':
            self.N = self.N / self.demog_main.hist.Nref #Copy by value
            self.t = self.t / (2 * self.demog_main.hist.Nref * self.demog_main.hist.years_per_gen)
        
        self.N = max(0,min(self.N,self.demog_main.hist.maxnes[self.popind]))
        if self.epind > 0:
            self.t = max(self.demog_main.hist.ts[self.popind][self.epind-1],self.t)
            self.t = min(self.t,self.demog_main.hist.maxt)
            if self.epind < len(self.demog_main.hist.ts[self.popind]) - 1:
                self.t = min(self.t,self.demog_main.hist.ts[self.popind][self.epind+1])

        self.demog_main.hist.nus[self.popind][self.epind] = self.N+0 #Copy by value
        if self.epind > 0:
            self.demog_main.hist.ts[self.popind][self.epind] = self.t+0 #Copy by value                

        #Redraw DraggablePopHistory            
        self.demog_main.hist.animate_canvas()
        self.demog_main.hist.fig.canvas.draw()
        self.background = self.demog_main.hist.fig.canvas.copy_from_bbox(self.demog_main.hist.ax.bbox)
        #Tell observers we're about to move
        for callback in self.demog_main.hist._observers:
            callback[0]()
        
        self.demog_main.hist.update_cts_mig_graphics()
        self.demog_main.hist.update_mig_graphics()        
        self.demog_main.hist.update_histline(self.popind, self.epind)
        if self.epind > 0:
            self.demog_main.hist.update_histline(self.popind, self.epind-1)

        self.demog_main.hist.update_rects_circles(self.popind ,self.epind)

        self.demog_main.hist.redraw_canvas()   
        self.demog_main.hist.fig.canvas.restore_region(self.background)
	self.demog_main.hist.fig.canvas.blit(self.demog_main.hist.ax.bbox) 

        #Update each observer by passing the history to the observer
        for callback in self.demog_main.hist._observers:
            callback[1]()                        

        self.demog_main.hist.unanimate_canvas()
        self.demog_main.hist.fig.canvas.draw()
        self.background = None
        for callback in self.demog_main.hist._observers:
            callback[2]() 

        self.toplevel.destroy()
        
        
  
        
class popup_migration_textfield:
    def __init__(self,demog_main,migind,x_loc,y_loc): 
        self.demog_main = demog_main
        self.toplevel = tk.Toplevel(self.demog_main.root)
        self.toplevel.geometry('+%d+%d' % (x_loc,y_loc))
        self.toplevel.wm_title("Specify Migration")
        
        self.migind = migind
        
        self.t_label = tk.Label(self.toplevel, text="Start Time")
        if self.demog_main.hist.units == 'Coalescent units':   
            self.t_label_ttp = CreateToolTip(self.t_label, 200, 'Migration start time in units of 2Nref generations.')
        elif self.demog_main.hist.units == 'Ne/generations':
            self.t_label_ttp = CreateToolTip(self.t_label, 200, 'Migration start time in units of generations.')
        elif self.demog_main.hist.units == 'Ne/years':
            self.t_label_ttp = CreateToolTip(self.t_label, 200, 'Migration start time in years.')
            
        self.m_label = tk.Label(self.toplevel, text="Rate")
        self.m_label_ttp = CreateToolTip(self.m_label, 200, 'Migration rate: fraction (f) of lineages in the arrow base population that migrate to the arrow tip population in each generation (going backward in time). If migration duration is 0 then this is a pulse migration (a fraction f of lineages in the base population migrate instantaneously to the tip population). If the migration duration is >0, then f is the fraction that migrate each generation.')

        self.dur_label = tk.Label(self.toplevel, text="Duration")
        if self.demog_main.hist.units == 'Coalescent units':   
            self.dur_label_ttp = CreateToolTip(self.dur_label, 200, 'Migration duration in units of 2Nref generations.')
        elif self.demog_main.hist.units == 'Ne/generations':
            self.dur_label_ttp = CreateToolTip(self.dur_label, 200, 'Migration duration in units of generations.')
        elif self.demog_main.hist.units == 'Ne/years':
            self.dur_label_ttp = CreateToolTip(self.dur_label, 200, 'Migration duration in years.')

        
        self.t_ent = tk.Entry(self.toplevel)
        self.m_ent = tk.Entry(self.toplevel)
        self.dur_ent = tk.Entry(self.toplevel)
        
        self.t = self.demog_main.hist.migs[self.migind][0]+0 #Copy by value
        self.m = self.demog_main.hist.migs[self.migind][3]+0 #Copy by value
        self.dur = self.demog_main.hist.migs[self.migind][4]+0 #Copy by value
        
        self.t_ent.delete(0, tk.END)
        self.dur_ent.delete(0, tk.END)
        self.m_ent.delete(0, tk.END)
        if self.demog_main.hist.units == 'Coalescent units':
            self.t_ent.insert(0, str(self.t))
            self.m_ent.insert(0, str(self.m))
            self.dur_ent.insert(0, str(self.dur))
        elif self.demog_main.hist.units == 'Ne/generations':
            self.t_ent.insert(0, str(2 * self.demog_main.hist.Nref * self.t))
            self.m_ent.insert(0, str(self.m))
            self.dur_ent.insert(0, str(2 * self.demog_main.hist.Nref * self.dur))
        elif self.demog_main.hist.units == 'Ne/years':
            self.t_ent.insert(0, str(2 * self.demog_main.hist.Nref * self.demog_main.hist.years_per_gen * self.t))
            self.m_ent.insert(0, str(self.m))
            self.dur_ent.insert(0, str(2 * self.demog_main.hist.Nref * self.demog_main.hist.years_per_gen * self.dur))
        
        self.t_label.grid(row = 1, column = 1, sticky = tk.E)
        self.m_label.grid(row = 2, column = 1, sticky = tk.E)
        self.dur_label.grid(row = 3, column = 1, sticky = tk.E)
        
        self.t_ent.grid(row = 1, column = 2, sticky = tk.W)
        self.m_ent.grid(row = 2, column = 2, sticky = tk.W)
        self.dur_ent.grid(row = 3, column = 2, sticky = tk.W)
        
        self.get_command_button = tk.Button(master = self.toplevel, text="Set Values", command = self.on_set_values_button_call)
        self.get_command_button.grid(row = 4, column = 2, sticky = tk.W)
        

    def on_set_values_button_call(self):
        
        if self.t_ent.get():       
            self.t = np.array(ast.literal_eval(self.t_ent.get()))
            if self.t is not None:
                if self.t.dtype.char == 'S':
                    self.demog_main.app_output_box_window.output_box.insert(INSERT,'\n\nERROR: Must specify migration start time.\n\n')
                    self.demog_main.app_output_box_window.output_box.see(tk.END)
                    return
        else:
            self.demog_main.app_output_box_window.output_box.insert(INSERT,'\n\nERROR: Must specify migration start time.\n\n')
            self.demog_main.app_output_box_window.output_box.see(tk.END)
            self.t = None
            return
        
        if self.m_ent.get():       
            self.m = np.array(ast.literal_eval(self.m_ent.get()))
            if self.m is not None:
                if self.m.dtype.char == 'S':
                    self.demog_main.app_output_box_window.output_box.insert(INSERT,'\n\nERROR: Must specify migration rate.\n\n')
                    self.demog_main.app_output_box_window.output_box.see(tk.END)
                    return
        else:
            self.demog_main.app_output_box_window.output_box.insert(INSERT,'\n\nERROR: Must specify migration rate.\n\n')
            self.demog_main.app_output_box_window.output_box.see(tk.END)
            self.m = None
            return
            
        if self.dur_ent.get():       
            self.dur = np.array(ast.literal_eval(self.dur_ent.get()))
            if self.dur is not None:
                if self.dur.dtype.char == 'S':
                    self.demog_main.app_output_box_window.output_box.insert(INSERT,'\n\nERROR: Must specify migration duration.\n\n')
                    self.demog_main.app_output_box_window.output_box.see(tk.END)
                    return
        else:
            self.demog_main.app_output_box_window.output_box.insert(INSERT,'\n\nERROR: Must specify migration duration.\n\n')
            self.demog_main.app_output_box_window.output_box.see(tk.END)
            self.dur = None
            return

                
        if self.demog_main.hist.units == 'Ne/generations':
            self.t = self.t / (2 * self.demog_main.hist.Nref)
            self.m = self.m+0 #Copy by value
            self.dur = self.dur / (2 * self.demog_main.hist.Nref)
        elif self.demog_main.hist.units == 'Ne/years':
            self.t = self.t / (2 * self.demog_main.hist.Nref * self.demog_main.hist.years_per_gen)
            self.m = self.m+0 #Copy by value
            self.dur = self.dur / (2 * self.demog_main.hist.Nref * self.demog_main.hist.years_per_gen)

        self.t = max(0,min(self.t,self.demog_main.hist.maxt))
        self.m = self.m
        self.dur = max(0,min(self.dur,self.demog_main.hist.maxt - self.t))
        self.demog_main.hist.migs[self.migind][0] = self.t+0 #Copy by value
        self.demog_main.hist.migs[self.migind][3] = self.m+0 #Copy by value
        self.demog_main.hist.migs[self.migind][4] = self.dur+0 #Copy by value
                                
        #Redraw DraggablePopHistory            
        self.demog_main.hist.animate_canvas()
        self.demog_main.hist.fig.canvas.draw()
        self.background = self.demog_main.hist.fig.canvas.copy_from_bbox(self.demog_main.hist.ax.bbox)
        #Tell observers we're about to move
        for callback in self.demog_main.hist._observers:
            callback[0]()
        
        self.demog_main.hist.update_cts_mig_graphics()
        self.demog_main.hist.update_mig_graphics()        

        self.demog_main.hist.redraw_canvas()   
        self.demog_main.hist.fig.canvas.restore_region(self.background)
	self.demog_main.hist.fig.canvas.blit(self.demog_main.hist.ax.bbox) 

        #Update each observer by passing the history to the observer
        for callback in self.demog_main.hist._observers:
            callback[1]()                        

        self.demog_main.hist.unanimate_canvas()
        self.demog_main.hist.fig.canvas.draw()
        self.background = None
        for callback in self.demog_main.hist._observers:
            callback[2]() 

        self.toplevel.destroy()

      



class ms_sim_command_window:
    def __init__(self, root, demog_main,hwxy):
        self.root = root
        self.frame = tk.Frame(self.root)        
        self.demog_main = demog_main
        self.root.bind('<Button-1>',self.demog_main.reset_menubar)        

        self.root.geometry('%dx%d+%d+%d' % hwxy)
        self.root.wm_title("Simulation Command (ms)")
        
        self.Nref = None
        self.rec_rate = None
        self.mut_rate = None
        self.num_seqs = None
        self.num_bases = None
        self.geneconv_g = None
        self.geneconv_lambda = None
        self.fixed_num_segsites = None
        self.seed = None
        self.digits = None
        self.outf_path = None

        self.Nref_label = tk.Label(self.root, text="Nref")
        self.Nref_label_ttp = CreateToolTip(self.Nref_label, 250, \
        'Required (e.g., 10000): Reference effective size. Output times will be in units of 4Nref generations.')
        self.rec_rate_label = tk.Label(self.root, text="Recombination rate")
        self.rec_rate_label_ttp = CreateToolTip(self.rec_rate_label, 250, \
        'Optional (e.g., 0.00000001): Per base, per generation probability of recombination.')
        self.mut_rate_label = tk.Label(self.root, text="Mutation rate")
        self.mut_rate_label_ttp = CreateToolTip(self.mut_rate_label, 250, \
        'Optional, but required for simulating sequences (e.g., 0.001): Per generation mutation rate for the full locus.')
        self.num_seqs_label = tk.Label(self.root, text="Number of sequences")
        self.num_seqs_label_ttp = CreateToolTip(self.num_seqs_label, 250, \
        'Required (e.g., [10,31]): Number of sequences sampled from each population. Should be a vector of length equal to the number of populations.')
        self.num_bases_label = tk.Label(self.root, text="Sequence length")
        self.num_bases_label_ttp = CreateToolTip(self.num_bases_label, 250, \
        'Optional, but required for recombination (e.g., 1000000): Number of bases per locus.')
        self.num_loci_label = tk.Label(self.root, text="Number of loci")
        self.num_loci_label_ttp = CreateToolTip(self.num_loci_label, 250, \
        'Required (e.g., 3): number of identical independent replicate loci to simulate with the given parameters.')
        self.geneconv_f_label = tk.Label(self.root, text="Gene conv. f")
        self.geneconv_f_label_ttp = CreateToolTip(self.geneconv_f_label, 250, \
        'Optional (e.g., 2): Gene conversion parameter f = g/r, where g is the probability that gene conversion initiates, per site, in each generation and r is the probability of a gene conversion recombination, per-site, per-generation. To simulate gene conversion without recombination, set the recombination rate to 0 and set Gene conv. f to g (defined above).')
        self.geneconv_lambda_label = tk.Label(self.root, text="Gene conv. lambda")
        self.geneconv_lambda_label_ttp = CreateToolTip(self.geneconv_lambda_label, 250, \
        'Optional (e.g., 1000): Expected length of converted region in gene conversion event.')
        self.fixed_num_segsites_label = tk.Label(self.root, text="Number of sites")
        self.fixed_num_segsites_label_ttp = CreateToolTip(self.fixed_num_segsites_label, 250, \
        'Optional (e.g., 25): Specify this to fix an integer number of segregating sites.')
        self.seed_label = tk.Label(self.root, text="Random seeds")
        self.seed_label_ttp = CreateToolTip(self.seed_label, 250, \
        'Optional (e.g., [123,536,134]): Three-element vector specifying the seed.')
        self.digits_label = tk.Label(self.root, text="Digits in output")
        self.digits_label_ttp = CreateToolTip(self.digits_label, 250, \
        'Optional (e.g., 5): Number of significant digits in output values.')
        self.outf_path_label = tk.Label(self.root, text="Output file path")
        self.outf_path_label_ttp = CreateToolTip(self.outf_path_label, 250, \
        'Optional (e.g., ~/Desktop/output.txt): Path for simulation output.')

        self.Nref_ent = tk.Entry(self.root)
        self.rec_rate_ent = tk.Entry(self.root)
        self.mut_rate_ent = tk.Entry(self.root)
        self.num_seqs_ent = tk.Entry(self.root)
        self.num_bases_ent = tk.Entry(self.root)
        self.num_loci_ent = tk.Entry(self.root)
        self.geneconv_f_ent= tk.Entry(self.root)
        self.geneconv_lambda_ent = tk.Entry(self.root)
        self.fixed_num_segsites_ent = tk.Entry(self.root)
        self.seed_ent = tk.Entry(self.root)
        self.digits_ent = tk.Entry(self.root)
        self.outf_path_ent = tk.Entry(self.root)


        self.Nref_ent.delete(0, tk.END)
        self.Nref_ent.insert(0, "")
        self.rec_rate_ent.delete(0, tk.END)
        self.rec_rate_ent.insert(0, "")
        self.mut_rate_ent.delete(0, tk.END)
        self.mut_rate_ent.insert(0, "")
        self.num_seqs_ent.delete(0, tk.END)
        #self.num_seqs_ent.insert(0, str(self.demog_main.ns))
        self.num_seqs_ent.insert(0, "")
        self.num_bases_ent.delete(0, tk.END)
        self.num_bases_ent.insert(0, "")
        self.num_loci_ent.delete(0, tk.END)
        self.num_loci_ent.insert(0, "")
        self.geneconv_f_ent.delete(0, tk.END)
        self.geneconv_f_ent.insert(0, "")
        self.geneconv_lambda_ent.delete(0, tk.END)
        self.geneconv_lambda_ent.insert(0, "")
        self.fixed_num_segsites_ent.delete(0, tk.END)
        self.fixed_num_segsites_ent.insert(0, "")
        self.seed_ent.delete(0, tk.END)
        self.seed_ent.insert(0, "")
        self.digits_ent.delete(0, tk.END)
        self.digits_ent.insert(0, "")
        self.outf_path_ent.delete(0, tk.END)
        self.outf_path_ent.insert(0, "")

        self.Nref_label.grid(row = 1, column = 1, sticky = tk.E)
        self.rec_rate_label.grid(row = 2, column = 1, sticky = tk.E)
        self.mut_rate_label.grid(row = 3, column = 1, sticky = tk.E)
        self.num_seqs_label.grid(row = 4, column = 1, sticky = tk.E)
        self.num_bases_label.grid(row = 5, column = 1, sticky = tk.E)
        self.num_loci_label.grid(row = 6, column = 1, sticky = tk.E)
        self.geneconv_f_label.grid(row = 7, column = 1, sticky = tk.E)
        self.geneconv_lambda_label.grid(row = 8, column = 1, sticky = tk.E)
        self.fixed_num_segsites_label.grid(row = 9, column = 1, sticky = tk.E)
        self.seed_label.grid(row = 10, column = 1, sticky = tk.E)
        self.digits_label.grid(row = 11, column = 1, sticky = tk.E)
        self.outf_path_label.grid(row = 12, column = 1, sticky = tk.E)
        
        self.Nref_ent.grid(row = 1, column = 2, sticky = tk.E)
        self.rec_rate_ent.grid(row = 2, column = 2, sticky = tk.E)
        self.mut_rate_ent.grid(row = 3, column = 2, sticky = tk.E)
        self.num_seqs_ent.grid(row = 4, column = 2, sticky = tk.E)
        self.num_bases_ent.grid(row = 5, column = 2, sticky = tk.E)
        self.num_loci_ent.grid(row = 6, column = 2, sticky = tk.E)
        self.geneconv_f_ent.grid(row = 7, column = 2, sticky = tk.E)
        self.geneconv_lambda_ent.grid(row = 8, column = 2, sticky = tk.E)
        self.fixed_num_segsites_ent.grid(row = 9, column = 2, sticky = tk.E)
        self.seed_ent.grid(row = 10, column = 2, sticky = tk.E)
        self.digits_ent.grid(row = 11, column = 2, sticky = tk.E)
        self.outf_path_ent.grid(row = 12, column = 2, sticky = tk.E)
        
        self.comm_out_stat_list = ['Sequences','Sequences (cleaned,csv)','Trees (Newick format)','Tree length (units of 4Nref generations)']
        self.comm_out_stat = tk.StringVar()
        self.comm_out_stat.set('Output')
        self.comm_out_stat_menu = tk.OptionMenu(root,self.comm_out_stat,*self.comm_out_stat_list)
        self.comm_out_stat_menu.grid(row = 13, column = 2, sticky = tk.EW)
        self.comm_stat = None
        
        self.grep_comm = ''
        
        self.command = None

        self.get_command_button = tk.Button(master = self.root, text="Get command", command = self.on_get_command_button_call)
        self.get_command_button.grid(row = 14, column = 2, sticky = tk.W)          
        
        self.full_boxes_command = None


    def close_window(self):        
        self.root.destroy()


    def on_get_command_button_call(self):
        
        self.demog_main.app_hist_window.get_values()
        
        if self.demog_main.hist is None:
            self.demog_main.fig1 = plt.figure(facecolor = 'white')
            self.demog_main.ax1 = self.demog_main.fig1.add_subplot(111)  
            self.demog_main.ax1.cla()
            self.demog_main.hist = DraggablePopHistory(self.demog_main,self.demog_main.fig1, self.demog_main.ax1, deepcopy(self.demog_main.ts), deepcopy(self.demog_main.nus), deepcopy(self.demog_main.expmat), deepcopy(self.demog_main.migs), deepcopy(self.demog_main.maxnes), deepcopy(self.demog_main.maxt), deepcopy(self.demog_main.plotdt)/10, self.demog_main.old_units, self.demog_main.Nref, self.demog_main.years_per_gen)

        if self.Nref_ent.get():       
            self.Nref = np.array(ast.literal_eval(self.Nref_ent.get()))
            if self.Nref is not None:
                if self.Nref.dtype.char == 'S':
                    self.Nref = None
        else:
            self.Nref = None

        if self.rec_rate_ent.get():       
            self.rec_rate = np.array(ast.literal_eval(self.rec_rate_ent.get()))
            if self.rec_rate is not None:
                if self.rec_rate.dtype.char == 'S':
                    self.rec_rate = None
        else:
            self.rec_rate = None
            
        if self.mut_rate_ent.get():       
            self.mut_rate = np.array(ast.literal_eval(self.mut_rate_ent.get()))
            if self.mut_rate is not None:
                if self.mut_rate.dtype.char == 'S':
                    self.mut_rate = None
        else:
            self.mut_rate = None
                
        if self.num_seqs_ent.get():
            self.num_seqs = np.array(ast.literal_eval(self.num_seqs_ent.get()))
            if self.num_seqs is not None:
                temp = self.num_seqs_ent.get()
                if not temp.startswith('['):
                    temp = '[' + temp
                if not temp.endswith(']'):
                    temp = temp + ']'
                self.num_seqs = np.array(ast.literal_eval(temp))
                if self.num_seqs.dtype.char == 'S':
                    self.num_seqs = None
                if len(self.num_seqs) == 1 and self.demog_main.npops > 1:
                    self.num_seqs = str([self.num_seqs[0]]*self.demog_main.npops)
                    self.num_seqs = np.array(ast.literal_eval(self.num_seqs))
        else:
            self.num_seqs = None

        if self.num_bases_ent.get():       
            self.num_bases = np.array(ast.literal_eval(self.num_bases_ent.get()))
            if self.num_bases is not None:
                if self.num_bases.dtype.char == 'S':
                    self.num_bases = None
        else:
            self.num_bases = None
            
        if self.num_loci_ent.get():       
            self.num_loci = np.array(ast.literal_eval(self.num_loci_ent.get()))
            if self.num_loci is not None:
                if self.num_loci.dtype.char == 'S':
                    self.num_loci = None
        else:
            self.num_loci = None

        if self.geneconv_f_ent.get():
            self.geneconv_f = np.array(ast.literal_eval(self.geneconv_f_ent.get()))
            if self.geneconv_f is not None:
                if self.geneconv_f.dtype.char == 'S':
                    self.geneconv_f = None
        else:
            self.geneconv_f = None

        if self.geneconv_lambda_ent.get():
            self.geneconv_lambda = np.array(ast.literal_eval(self.geneconv_lambda_ent.get()))
            if self.geneconv_lambda is not None:
                if self.geneconv_lambda.dtype.char == 'S':
                    self.geneconv_lambda = None
        else:
            self.geneconv_lambda = None
            
        if self.geneconv_f is not None:
            if (self.geneconv_lambda is None) or (self.rec_rate is None):
                self.demog_main.app_output_box_window.output_box.insert(INSERT,'\n\nERROR: Must specify all of f, lambda, and reocombination rate for gene conversion. For gene conversion without recombination, set the recombination rate to 0 and set Gene conv. f to g, where g is the probability that gene conversion initiates per site per generation. \n\n')
                self.demog_main.app_output_box_window.output_box.see(tk.END)
                return                

        if self.fixed_num_segsites_ent.get():
            self.fixed_num_segsites = np.array(ast.literal_eval(self.fixed_num_segsites_ent.get()))
            if self.fixed_num_segsites is not None:
                if self.fixed_num_segsites.dtype.char == 'S':
                    self.fixed_num_segsites = None
        else:
            self.fixed_num_segsites = None        
            
        if self.seed_ent.get():       
            self.seed = np.array(ast.literal_eval(self.seed_ent.get()))
            if self.seed is not None:
                if self.seed.dtype.char == 'S':
                    self.seed = None
        else:
            self.seed = None
            
        if self.outf_path_ent.get():       
            self.outf_path = self.outf_path_ent.get()
        else:
            self.outf_path = None
            #self.demog_main.app_output_box_window.output_box.insert(INSERT,'\n\nWARNING: No output file specified.\n')
            #self.demog_main.app_output_box_window.output_box.insert(INSERT,'         Output will be printed to console.\n\n')
            #self.demog_main.app_output_box_window.output_box.see(tk.END)
            
        self.grep_comm = ''
        
        self.comm_stat = self.comm_out_stat.get()
        
        if self.comm_stat == 'Output':
            self.demog_main.app_output_box_window.output_box.insert(INSERT,'\n\nERROR: Must select output statistic.\n\n')
            self.demog_main.app_output_box_window.output_box.see(tk.END)
            return        
 
        if self.num_seqs is not None:
            nhap = np.sum(self.num_seqs)
        else:
            self.demog_main.app_output_box_window.output_box.insert(INSERT,'\n\nERROR: Must specify number of sequences.\n\n')
            self.demog_main.app_output_box_window.output_box.see(tk.END)
            return
            
        if self.num_loci is not None:
            nrep = self.num_loci * 1 #Copy by value
        else:
            self.demog_main.app_output_box_window.output_box.insert(INSERT,'\n\nERROR: Must specify number of replicate loci.\n\n')
            self.demog_main.app_output_box_window.output_box.see(tk.END)
            return
            
        self.command = 'ms ' + str(nhap) + ' ' + str(nrep) + ' '
        
        if self.seed is not None:
            self.command = self.command + '-seed ' + str(self.seed) + ' '
        
        if self.digits is not None:
            self.command = self.command + '-p ' + str(self.digits) + ' '

        if self.comm_stat == 'Sequences':
            if self.mut_rate is None:
                if self.fixed_num_segsites is None:
                    self.demog_main.app_output_box_window.output_box.insert(INSERT,'\n\nERROR: For "Sequences", you must specify the mutation rate or a fixed number of segregating sites.\n\n')
                    self.demog_main.app_output_box_window.output_box.see(tk.END)
                    return
                else:
                    self.command = self.command + '-s ' + str(self.fixed_num_segsites) + ' '
            else:
                theta = 4 * self.Nref * self.mut_rate
                self.command = self.command + '-t ' + str(theta) + ' '
                if self.fixed_num_segsites is not None: #if self.fixed_num_segsites is specified, then ms will also print out the probability of observing this number of seg sites.
                    self.command = self.command + '-s ' + str(self.fixed_num_segsites) + ' '
        if self.comm_stat == 'Sequences (cleaned,csv)':
            if self.mut_rate is None:
                if self.fixed_num_segsites is None:
                    self.demog_main.app_output_box_window.output_box.insert(INSERT,'\n\nERROR: For "Sequences", you must specify the mutation rate or a fixed number of segregating sites.\n\n')
                    self.demog_main.app_output_box_window.output_box.see(tk.END)
                    return
                else:
                    self.command = self.command + '-s ' + str(self.fixed_num_segsites) + ' '
            else:
                theta = 4 * self.Nref * self.mut_rate
                self.command = self.command + '-t ' + str(theta) + ' '
            self.grep_comm = self.grep_comm + ' | grep -v .*ms | grep -v -e "[2-9]" | grep -v -e "^[[:space:]]*$" | grep -v // | grep -v segsites: | grep -v positions: | sed -e "s/0/0,/g" | sed -e "s/1/1,/g" | sed -e "s/,$//g" '
        elif self.comm_stat == 'Trees (Newick format)':
            self.command = self.command + '-T ' + ' '
            if (self.geneconv_f is not None) or (self.geneconv_lambda is not None):
                self.demog_main.app_output_box_window.output_box.insert(INSERT,'\n\nWARNING: Cannot output trees with gene conversion. Ignoring gene conversion parameters.\n\n')
                self.demog_main.app_output_box_window.output_box.see(tk.END)
                self.geneconv_f = None
                self.geneconv_lambda = None
        elif self.comm_stat == 'Tree length (units of 4Nref generations)':
            self.command = self.command + '-L ' + ' '
            if (self.geneconv_f is not None) or (self.geneconv_lambda is not None):
                self.demog_main.app_output_box_window.output_box.insert(INSERT,'\n\nWARNING: Cannot output tree lengths with gene conversion. Ignoring gene conversion parameters.\n\n')
                self.demog_main.app_output_box_window.output_box.see(tk.END)
                self.geneconv_f = None
                self.geneconv_lambda = None
        
        if self.rec_rate is not None:
            if self.num_bases is not None:
                r = self.rec_rate * 4 * self.Nref * (self.num_bases - 1)
                #Just a note: this is how Hudson calculates r in ms.
                #However, he defines r as 4 * Nref * rho where rho is the probability of a cross-over between the ends
                #of the locus each generation. Because he says the positions of the recombination events are uniformly distributed
                #along the sequence and he's using the infinite sites model, I assume that the number of recombination events
                #is drawn from a Poisson distribution. In this case, rec_rate * (num_bases - 1) is just the first term in the
                #Taylor approximation of rho, and the correct value of rho should actually be
                #   rho = 1 - exp( - num_bases * rec_rate * 1 generation)
                #which gives
                #   r = 4 * Nref * rho
                #However, because Hudson defines rho = rec_rate * (num_bases - 1) in the ms documentation, I have used his formula here.
                self.command = self.command + '-r ' + str(r) + ' ' + str(self.num_bases) + ' '
            else:
                self.demog_main.app_output_box_window.output_box.insert(INSERT,'\n\nERROR: Must specify number of bases to simulate recombination.\n\n')
                self.demog_main.app_output_box_window.output_box.see(tk.END)
                return

        if self.geneconv_f is not None:
            if self.rec_rate > 0:
                self.command = self.command + '-c ' + str(self.geneconv_f) + ' ' + str(self.geneconv_lambda) + ' '
            elif self.rec_rate == 0:
                self.command = self.command + '-c ' + str(4 * self.Nref * self.geneconv_f) + ' ' + str(self.geneconv_lambda) + ' '
            else:
                self.demog_main.app_output_box_window.output_box.insert(INSERT,'\n\nERROR: Must specify gene conversion lambda.\n\n')
                self.demog_main.app_output_box_window.output_box.see(tk.END)
                return        
                
        npop = np.array(self.demog_main.npops * 1).astype(int)
        self.command = self.command + '-I ' + str(npop) + ' '
        for i in range(0,self.demog_main.npops):
            nhap = np.array(self.num_seqs[i] * 1).astype(int)
            self.command = self.command + str(nhap) + ' '
            
        
        for i in range(0,self.demog_main.hist.npops):
            ind = np.array(i * 1).astype(int)
            sz = self.demog_main.hist.nus[i][0] * 1
            self.command = self.command + '-n ' + str(ind+1) + ' ' + str(sz) + ' '
            if self.demog_main.hist.gammas[i][0] != 0:
                g = -2*self.demog_main.hist.gammas[i][0] * 1 #Demographer measures time in units of 2Nref generations. ms measures it in units of 4Nref generations. So we scale g by 2 when passing it to ms. Also, we scale by -1 because ms defines the rate to have the opposite sign.
                self.command = self.command + '-g ' + str(ind+1) + ' ' + str(g) + ' '

        #Set up vectors that store all events in sequential order
        event_type_vec = []
        event_time_vec = []
        event_index_vec = []
        for i in range(0,len(self.demog_main.hist.ts)):
            for j in range(0,len(self.demog_main.hist.ts[i])):
                event_type_vec = event_type_vec + [1]
                event_time_vec = event_time_vec + [np.array(self.demog_main.hist.ts[i][j]).tolist()]
                event_index_vec = event_index_vec + [[i,j]]
        
        for i in range(0,len(self.demog_main.hist.migs)):
            time = self.demog_main.hist.migs[i][0]
            ind = np.sum(np.array(event_time_vec) <= time) #index to insert at
            event_type_vec.insert(ind,2)
            event_time_vec.insert(ind,time)
            event_index_vec.insert(ind,i)            
            if self.demog_main.hist.migs[i][4] > 0: #If it's continuous migration
                time = self.demog_main.hist.migs[i][0] + self.demog_main.hist.migs[i][4]
                ind = np.sum(np.array(event_time_vec) <= time) #index to insert at
                event_type_vec.insert(ind,3)
                event_time_vec.insert(ind,time)
                event_index_vec.insert(ind,i)
        
        event_time_vec = (np.array(event_time_vec) / 2).tolist() #Time is in units of 2*Nref generations, so we convert to 4Nref gens.
                
        #Set up all size change and migration events
        pop_ct = np.array(copy.deepcopy(self.demog_main.npops)).astype(int)
        for i in range(0,len(event_type_vec)):
            time = event_time_vec[i]
            if event_type_vec[i] == 1: #It's a size change
                if time > 0:
                    popind = np.array(event_index_vec[i][0]).astype(int)
                    epind = event_index_vec[i][1]
                    sz = self.demog_main.hist.nus[popind][epind] * 1
                    self.command = self.command + '-en ' + str(time) + ' ' + str(popind+1) + ' ' + str(sz) + ' '
                    #if self.demog_main.hist.expmat[popind][epind] is None:
                    gam = -2*self.demog_main.hist.gammas[popind][epind] #Demographer measures time in units of 2Nref generations. ms measures it in units of 4Nref generations. So we scale g by 2 when passing it to ms. Also, we scale by -1 because ms defines the rate to have the opposite sign.
                    self.command = self.command + '-eg ' + ' ' + str(time) + ' ' + str(popind+1) + ' ' + str(gam) + ' '
            elif event_type_vec[i] == 2: #It's a migration start
                migind = event_index_vec[i]
                if self.demog_main.hist.migs[migind][3] >= 0:
                    startpop = np.array(self.demog_main.hist.migs[migind][1]).astype(int)
                    stoppop = np.array(self.demog_main.hist.migs[migind][2]).astype(int)
                    frac = self.demog_main.hist.migs[migind][3]
                else:
                    startpop = np.array(self.demog_main.hist.migs[migind][2]).astype(int)
                    stoppop = np.array(self.demog_main.hist.migs[migind][1]).astype(int)
                    frac = -self.demog_main.hist.migs[migind][3]
                dur = self.demog_main.hist.migs[migind][4]
                if dur == 0:
                    self.command = self.command + '-es ' + str(time) + ' ' + str(startpop) + ' ' + str(1-frac) + ' '
                    pop_ct = pop_ct + 1
                    self.command = self.command + '-ej ' + str(time) + ' ' + str(pop_ct) + ' ' + str(stoppop) + ' '
                else:
                    self.command = self.command + '-em ' + str(time) + ' ' + str(startpop) + ' ' + str(stoppop) + ' ' + str(4*frac*self.Nref) + ' '
            elif event_type_vec[i] == 3: #It's a migration stop
                migind = event_index_vec[i]
                if self.demog_main.hist.migs[migind][3] >= 0:
                    startpop = np.array(self.demog_main.hist.migs[migind][1]).astype(int)
                    stoppop = np.array(self.demog_main.hist.migs[migind][2]).astype(int)
                else:
                    startpop = np.array(self.demog_main.hist.migs[migind][2]).astype(int)
                    stoppop = np.array(self.demog_main.hist.migs[migind][1]).astype(int)
                    frac = -self.demog_main.hist.migs[migind][3]
                self.command = self.command + '-em ' + str(time) + ' ' + str(startpop) + ' ' + str(stoppop) + ' ' + str(0) + ' '
        
            
        self.command = self.command + self.grep_comm
        if self.outf_path is not None:
            self.command = self.command + '> ' + self.outf_path
        

        self.demog_main.app_output_box_window.output_box.insert(INSERT,'\n\n>>> ms command: \n' + self.command + '\n')
        self.demog_main.app_output_box_window.output_box.see(tk.END)






class scrm_sim_command_window:
    def __init__(self, root, demog_main,hwxy):
        self.root = root
        self.frame = tk.Frame(self.root)
        self.demog_main = demog_main
        self.root.bind('<Button-1>',self.demog_main.reset_menubar)

        self.root.geometry('%dx%d+%d+%d' % hwxy)
        self.root.wm_title("Simulation Command (scrm)")
        
        self.rec_rate = None
        self.mut_rate = None
        self.num_seqs = None
        self.num_bases = None
        self.seed = None
        self.digits = 5
        self.outf_path = None
        

        self.Nref_label = tk.Label(self.root, text="Nref")
        self.Nref_label_ttp = CreateToolTip(self.Nref_label, 250, \
        'Required (e.g., 10000): Reference effective size. Output times will be in units of 4Nref generations.')
        self.rec_rate_label = tk.Label(self.root, text="Recombination rate")
        self.rec_rate_label_ttp = CreateToolTip(self.rec_rate_label, 250, \
        'Optional (e.g., 5): Expected number of recombination events per generation in the full locus.')
        self.mut_rate_label = tk.Label(self.root, text="Mutation rate")
        self.mut_rate_label_ttp = CreateToolTip(self.mut_rate_label, 250, \
        'Optional (e.g., 5): Expected number of mutations per generation in the full locus.')
        self.num_seqs_label = tk.Label(self.root, text="Number of sequences")
        self.num_seqs_label_ttp = CreateToolTip(self.num_seqs_label, 250, \
        'Required (e.g., [10,21,4,5]): Number of sequences sampled from each population. Should be a vector with length equal to the number of populations.')
        self.num_bases_label = tk.Label(self.root, text="Sequence length")
        self.num_bases_label_ttp = CreateToolTip(self.num_bases_label, 250, \
        'Optional (e.g., 1000): Length of the locus in bases.')
        self.num_loci_label = tk.Label(self.root, text="Number of loci")
        self.num_loci_label_ttp = CreateToolTip(self.num_loci_label, 250, \
        'Required (e.g., 23): Number of replicate loci to simulate.')
        self.seed_label = tk.Label(self.root, text="Random seed")
        self.seed_label_ttp = CreateToolTip(self.seed_label, 250, \
        'Optional (e.g., 12345): Seed for the random number generator. Leave blank to choose a random seed.')
        self.digits_label = tk.Label(self.root, text="Digits in output")
        self.digits_label_ttp = CreateToolTip(self.digits_label, 250, \
        'Optional (e.g., 5): Number of significant figures for output values. Default is 5.')
        self.outf_path_label = tk.Label(self.root, text="Output file path")
        self.outf_path_label_ttp = CreateToolTip(self.outf_path_label, 250, \
        'Optional (e.g., ~/Desktop/output_file.txt): Path specifying the simulation output file. If path si unspecified, output will be printed to the screen.')

        self.Nref_ent = tk.Entry(self.root)
        self.rec_rate_ent = tk.Entry(self.root)
        self.mut_rate_ent = tk.Entry(self.root)
        self.num_seqs_ent = tk.Entry(self.root)
        self.num_bases_ent = tk.Entry(self.root)
        self.num_loci_ent = tk.Entry(self.root)
        self.seed_ent = tk.Entry(self.root)
        self.digits_ent = tk.Entry(self.root)
        self.outf_path_ent = tk.Entry(self.root)


        self.Nref_ent.delete(0, tk.END)
        self.Nref_ent.insert(0, "")
        self.rec_rate_ent.delete(0, tk.END)
        self.rec_rate_ent.insert(0, "")
        self.mut_rate_ent.delete(0, tk.END)
        self.mut_rate_ent.insert(0, "")
        self.num_seqs_ent.delete(0, tk.END)
        self.num_seqs_ent.insert(0, "")
        self.num_bases_ent.delete(0, tk.END)
        self.num_bases_ent.insert(0, "")
        self.num_loci_ent.delete(0, tk.END)
        self.num_loci_ent.insert(0, "")
        self.seed_ent.delete(0, tk.END)
        self.seed_ent.insert(0, "")
        self.digits_ent.delete(0, tk.END)
        self.digits_ent.insert(0, "")
        self.outf_path_ent.delete(0, tk.END)
        self.outf_path_ent.insert(0, "")

        self.Nref_label.grid(row = 2, column = 1, sticky = tk.E)
        self.rec_rate_label.grid(row = 3, column = 1, sticky = tk.E)
        self.mut_rate_label.grid(row = 4, column = 1, sticky = tk.E)
        self.num_seqs_label.grid(row = 5, column = 1, sticky = tk.E)
        self.num_bases_label.grid(row = 6, column = 1, sticky = tk.E)
        self.num_loci_label.grid(row = 7, column = 1, sticky = tk.E)
        self.seed_label.grid(row = 8, column = 1, sticky = tk.E)
        self.digits_label.grid(row = 9, column = 1, sticky = tk.E)
        self.outf_path_label.grid(row = 10, column = 1, sticky = tk.E)
        
        self.Nref_ent.grid(row = 2, column = 2, sticky = tk.W)
        self.rec_rate_ent.grid(row = 3, column = 2, sticky = tk.W)
        self.mut_rate_ent.grid(row = 4, column = 2, sticky = tk.W)
        self.num_seqs_ent.grid(row = 5, column = 2, sticky = tk.W)
        self.num_bases_ent.grid(row = 6, column = 2, sticky = tk.W)
        self.num_loci_ent.grid(row = 7, column = 2, sticky = tk.W)
        self.seed_ent.grid(row = 8, column = 2, sticky = tk.W)
        self.digits_ent.grid(row = 9, column = 2, sticky = tk.W)
        self.outf_path_ent.grid(row = 10, column = 2, sticky = tk.W)
        
        self.comm_out_stat_list = ['Sequences','Sequences (cleaned,csv)','Trees (Newick format)','Trees (Oriented Forest format)','Local tree length (units of 4Nref generations)','SFS']
        self.comm_out_stat = tk.StringVar()
        self.comm_out_stat.set('Output')
        self.comm_out_stat_menu = tk.OptionMenu(root,self.comm_out_stat,*self.comm_out_stat_list)
        self.comm_out_stat_menu.grid(row = 11, column = 2, sticky = tk.EW)
        self.comm_stat = None
        
        self.grep_comm = ''
        
        self.command = None

        self.get_command_button = tk.Button(master = self.root, text="Get command", command = self.on_get_command_button_call)
        self.get_command_button.grid(row = 12, column = 2, sticky = tk.W)          
        
        #self.quit_button = tk.Button(master = self.root, text="Quit", command = self.close_window)
        #self.quit_button.grid(row = 11, column = 2, sticky = tk.W)
        
        #self.output_box = tk.Text(master = self.root, height = 10, width = 50, fg = "grey")
        #self.output_box.grid(row = 7, column = 1, rowspan = 4, columnspan = 2)
        
        self.full_boxes_command = None


    def close_window(self):        
        self.root.destroy()


    def on_get_command_button_call(self):
        
        self.demog_main.app_hist_window.get_values()
        
        if self.demog_main.hist is None:
            self.demog_main.fig1 = plt.figure(facecolor = 'white')
            self.demog_main.ax1 = self.demog_main.fig1.add_subplot(111)  
            self.demog_main.ax1.cla()
            self.demog_main.hist = DraggablePopHistory(self.demog_main,self.demog_main.fig1, self.demog_main.ax1, deepcopy(self.demog_main.ts), deepcopy(self.demog_main.nus), deepcopy(self.demog_main.expmat), deepcopy(self.demog_main.migs), deepcopy(self.demog_main.maxnes), deepcopy(self.demog_main.maxt), deepcopy(self.demog_main.plotdt)/10, self.demog_main.old_units, self.demog_main.Nref, self.demog_main.years_per_gen)

        if self.Nref_ent.get():       
            self.Nref = np.array(ast.literal_eval(self.Nref_ent.get()))
            if self.Nref is not None:
                if self.Nref.dtype.char == 'S':
                    self.Nref = None
        else:
            self.Nref = None
            
        self.demog_main.Nref

        if self.rec_rate_ent.get():       
            self.rec_rate = np.array(ast.literal_eval(self.rec_rate_ent.get()))
            if self.rec_rate is not None:
                if self.rec_rate.dtype.char == 'S':
                    self.rec_rate = None
        else:
            self.rec_rate = None
            
        if self.mut_rate_ent.get():       
            self.mut_rate = np.array(ast.literal_eval(self.mut_rate_ent.get()))
            if self.mut_rate is not None:
                if self.mut_rate.dtype.char == 'S':
                    self.mut_rate = None
        else:
            self.mut_rate = None
                
        if self.num_seqs_ent.get():       
            self.num_seqs = np.array(ast.literal_eval(self.num_seqs_ent.get()))
            if self.num_seqs is not None:
                temp = self.num_seqs_ent.get()
                if not temp.startswith('['):
                    temp = '[' + temp
                if not temp.endswith(']'):
                    temp = temp + ']'
                self.num_seqs = np.array(ast.literal_eval(temp))
                if self.num_seqs.dtype.char == 'S':
                    self.num_seqs = None
                if len(self.num_seqs) == 1 and self.demog_main.npops > 1:
                    self.num_seqs = str([self.num_seqs[0]]*self.demog_main.npops)
                    self.num_seqs = np.array(ast.literal_eval(self.num_seqs))
                #elif hasattr(self.num_seqs, "__len__"):
                #    if len(self.num_seqs) == 1 and self.demog_main.npops > 1:
                #        self.num_seqs = str([self.num_seqs[0]]*self.demog_main.npops)
                #elif (not hasattr(self.num_seqs, "__len__")):
                #    self.num_seqs = str([self.num_seqs]*self.demog_main.npops)
        else:
            self.num_seqs = None
            
        self.demog_main.ns = self.num_seqs

        if self.num_bases_ent.get():       
            self.num_bases = np.array(ast.literal_eval(self.num_bases_ent.get()))
            if self.num_bases is not None:
                if self.num_bases.dtype.char == 'S':
                    self.num_bases = None
        else:
            self.num_bases = None
            
        if self.num_loci_ent.get():       
            self.num_loci = np.array(ast.literal_eval(self.num_loci_ent.get()))
            if self.num_loci is not None:
                if self.num_loci.dtype.char == 'S':
                    self.num_loci = None
        else:
            self.num_loci = None
            
        if self.seed_ent.get():       
            self.seed = np.array(ast.literal_eval(self.seed_ent.get()))
            if self.seed is not None:
                if self.seed.dtype.char == 'S':
                    self.seed = None
        else:
            self.seed = None
            
        if self.outf_path_ent.get():       
            self.outf_path = self.outf_path_ent.get()
        else:
            self.outf_path = None
            
        self.grep_comm = ''
        
        self.comm_stat = self.comm_out_stat.get()
        
        if self.comm_stat == 'Output':
            self.demog_main.app_output_box_window.output_box.insert(INSERT,'\n\nERROR: Must select output statistic.\n\n')
            self.demog_main.app_output_box_window.output_box.see(tk.END)
            return        
 
        if self.Nref is None:
            self.demog_main.app_output_box_window.output_box.insert(INSERT,'\n\nERROR: Must specify reference population size.\n\n')
            self.demog_main.app_output_box_window.output_box.see(tk.END)
            return         

        if self.num_seqs is not None:
            nhap = np.sum(self.num_seqs)
        else:
            self.demog_main.app_output_box_window.output_box.insert(INSERT,'\n\nERROR: Must specify number of sequences.\n\n')
            self.demog_main.app_output_box_window.output_box.see(tk.END)
            return
            
        if self.num_loci is not None:
            nrep = self.num_loci * 1 #Copy by value
        else:
            self.demog_main.app_output_box_window.output_box.insert(INSERT,'\n\nERROR: Must specify number of replicate loci.\n\n')
            self.demog_main.app_output_box_window.output_box.see(tk.END)
            return
            
        self.command = 'scrm ' + str(nhap) + ' ' + str(nrep) + ' '
        
        if self.seed is not None:
            self.command = self.command + '-seed ' + str(self.seed) + ' '
        
        if self.digits is not None:
            self.command = self.command + '-p ' + str(self.digits) + ' '

        if self.comm_stat == 'Sequences':
            if self.mut_rate is None:
                self.demog_main.app_output_box_window.output_box.insert(INSERT,'For "Sequences", you must specify the mutation rate.\n\n')
                self.demog_main.app_output_box_window.output_box.see(tk.END)
                return
            else:
                theta = 4 * self.demog_main.Nref * self.mut_rate
                self.command = self.command + '-t ' + str(theta) + ' '
        elif self.comm_stat == 'Sequences (cleaned,csv)': #Trim off all non-sequence information and comma-separate the genotypes
            if self.mut_rate is None:
                self.demog_main.app_output_box_window.output_box.insert(INSERT,'For "Sequences", you must specify the mutation rate.\n\n')
                self.demog_main.app_output_box_window.output_box.see(tk.END)
                return
            else:
                theta = 4 * self.demog_main.Nref * self.mut_rate
                self.command = self.command + '-t ' + str(theta) + ' '
                self.grep_comm = self.grep_comm + ' | grep -v scrm | grep -v -e "[2-9]" | grep -v -e "^[[:space:]]*$" | grep -v // | grep -v segsites: | grep -v positions: | sed -e "s/0/0,/g" | sed -e "s/1/1,/g" | sed -e "s/,$//g" '                
        elif self.comm_stat == 'Trees (Newick format)':
            self.command = self.command + '-T ' + ' '
        elif self.comm_stat == 'Trees (Oriented Forest format)':
            self.command = self.command + '-O ' + ' '
        elif self.comm_stat == 'Local tree length (units of 4Nref generations)':
            self.command = self.command + '-L ' + ' '
        elif self.comm_stat == 'SFS':
            if self.mut_rate is None:
                self.demog_main.app_output_box_window.output_box.insert(INSERT,'\n\nERROR: For "SFS", you must specify the mutation rate.\n\n')
                self.demog_main.app_output_box_window.output_box.see(tk.END)
                return
            else:
                theta = 4 * self.demog_main.Nref * self.mut_rate
                self.command = self.command + '-t ' + str(theta) + ' ' + '-oSFS' + ' '
                self.grep_comm = self.grep_comm + '| grep -i SFS: '
        
        if self.rec_rate is not None:
            r = self.rec_rate * 4 * self.demog_main.Nref
            if self.num_bases is not None:
                L = self.num_bases * 1
                self.command = self.command + '-r ' + str(r) + ' ' + str(L) + ' '
            else:
                self.demog_main.app_output_box_window.output_box.insert(INSERT,'\n\nERROR: For recombination, you must specify the locus length in bases.\n\n')
                self.demog_main.app_output_box_window.output_box.see(tk.END)
                return
        
        npop = self.demog_main.npops * 1
        self.command = self.command + '-I ' + str(npop) + ' '
        for i in range(0,self.demog_main.npops):
            nhap = self.demog_main.ns[i] * 1
            self.command = self.command + str(nhap) + ' '
            
        
        for i in range(0,self.demog_main.hist.npops):
            ind = i * 1
            sz = self.demog_main.hist.nus[i][0] * 1
            self.command = self.command + '-n ' + str(ind+1) + ' ' + str(sz) + ' '
            #if self.demog_main.hist.expmat[i][0] is not None:
            if self.demog_main.hist.gammas[i][0] != 0:
                g = -2*self.demog_main.hist.gammas[i][0] #Demographer measures time in units of 2Nref generations. scrm measures it in units of 4Nref generations. So we scale g by 2 when passing it to scrm. Also, we scale by -1 because they define the rate to have the opposite sign.
                self.command = self.command + '-g ' + str(ind+1) + ' ' + str(g) + ' '

        #Set up vectors that store all events in sequential order
        event_type_vec = []
        event_time_vec = []
        event_index_vec = []
        for i in range(0,len(self.demog_main.hist.ts)):
            for j in range(0,len(self.demog_main.hist.ts[i])):
                event_type_vec = event_type_vec + [1]
                event_time_vec = event_time_vec + [np.array(self.demog_main.hist.ts[i][j]).tolist()]
                event_index_vec = event_index_vec + [[i,j]]
        
        for i in range(0,len(self.demog_main.hist.migs)):
            time = self.demog_main.hist.migs[i][0]
            ind = np.sum(np.array(event_time_vec) <= time) #index to insert at
            event_type_vec.insert(ind,2)
            event_time_vec.insert(ind,time)
            event_index_vec.insert(ind,i)            
            if self.demog_main.hist.migs[i][4] > 0: #If it's continuous migration
                time = self.demog_main.hist.migs[i][0] + self.demog_main.hist.migs[i][4]
                ind = np.sum(np.array(event_time_vec) <= time) #index to insert at
                event_type_vec.insert(ind,3)
                event_time_vec.insert(ind,time)
                event_index_vec.insert(ind,i)
        
        event_time_vec = (np.array(event_time_vec) / 2).tolist() #Time is in units of 2*Nref generations, so we convert to 4Nref gens.
                
        #Set up all size change and migration events
        for i in range(0,len(event_type_vec)):
            time = event_time_vec[i]
            if event_type_vec[i] == 1: #It's a size change
                if time > 0:
                    popind = event_index_vec[i][0]
                    epind = event_index_vec[i][1]
                    sz = self.demog_main.hist.nus[popind][epind] * 1
                    self.command = self.command + '-en ' + str(time) + ' ' + str(popind+1) + ' ' + str(sz) + ' '
                    #if self.demog_main.hist.expmat[popind][epind] is None:
                    gam = -2*self.demog_main.hist.gammas[popind][epind] #Demographer measures time in units of 2Nref generations. scrm measures it in units of 4Nref generations. So we scale g by 2 when passing it to ms. Also, we scale by -1 because ms defines the rate to have the opposite sign.
                    self.command = self.command + '-eg ' + ' ' + str(time) + ' ' + str(popind+1) + ' ' + str(gam) + ' '
            elif event_type_vec[i] == 2: #It's a migration start
                migind = event_index_vec[i]
                if self.demog_main.hist.migs[migind][3] >= 0:
                    startpop = self.demog_main.hist.migs[migind][1]
                    stoppop = self.demog_main.hist.migs[migind][2]
                    frac = self.demog_main.hist.migs[migind][3]
                else:
                    startpop = self.demog_main.hist.migs[migind][2]
                    stoppop = self.demog_main.hist.migs[migind][1]
                    frac = -self.demog_main.hist.migs[migind][3]
                dur = self.demog_main.hist.migs[migind][4]
                if dur == 0:
                    self.command = self.command + '-eps ' + str(time) + ' ' + str(startpop) + ' ' + str(stoppop) + ' ' + str(1-frac) + ' '
                else:
                    self.command = self.command + '-em ' + str(time) + ' ' + str(startpop) + ' ' + str(stoppop) + ' ' + str(4*frac*self.demog_main.Nref) + ' '
            elif event_type_vec[i] == 3: #It's a migration stop
                migind = event_index_vec[i]
                if self.demog_main.hist.migs[migind][3] >= 0:
                    startpop = self.demog_main.hist.migs[migind][1]
                    stoppop = self.demog_main.hist.migs[migind][2]
                else:
                    startpop = self.demog_main.hist.migs[migind][2]
                    stoppop = self.demog_main.hist.migs[migind][1]
                    frac = -self.demog_main.hist.migs[migind][3]
                self.command = self.command + '-em ' + str(time) + ' ' + str(startpop) + ' ' + str(stoppop) + ' ' + str(0) + ' '

                                                
        self.command = self.command + self.grep_comm
        if self.outf_path is not None:
            self.command = self.command + '> ' + self.outf_path
        

        self.demog_main.app_output_box_window.output_box.insert(INSERT,'\n\n>>> scrm command: \n' + self.command + '\n')
        self.demog_main.app_output_box_window.output_box.see(tk.END)


class statistic_visualization_window:
    def __init__(self, root, demog_main, hwxy):
        self.root = root
        self.frame = tk.Frame(self.root)
        self.demog_main = demog_main
        self.root.bind('<Button-1>',self.demog_main.reset_menubar)        

        self.root.geometry('%dx%d+%d+%d' % hwxy)
        self.root.wm_title("Statistics")
        
        #self.stat_list = ['FST','SFS','NLFT']
        self.stat_list = ['NLFT','SFS']
        self.stat_menu_item = tk.StringVar()
        self.stat_menu_item.set('Statistic')
        self.stat_drop_menu = tk.OptionMenu(root,self.stat_menu_item,*self.stat_list, command = self.on_stat_menu_selection)
        self.stat_drop_menu.grid(row = 1, column = 1, sticky = tk.EW)
        
        self.sfs_plotstyle_menu_exists = None
        self.sfs_plotstyle = None
        self.sfs_plotstyle_list = ['Line','Heatmap']        
        self.sfs_plotstyle_menu_item = tk.StringVar()
        self.sfs_plotstyle_menu_item.set('Plot style')
        self.sfs_plotstyle_drop_menu = tk.OptionMenu(root,self.sfs_plotstyle_menu_item,*self.sfs_plotstyle_list, command = self.on_sfs_plotstyle_menu_selection)
        #self.sfs_plotstyle_drop_menu.grid(row = 1, column = 1, sticky = tk.EW)
                        
        self.nentries_ent_exists = None
        self.nentries_label = tk.Label(self.root, text = "SFS Entries")
        self.nentries_ent = tk.Entry(self.root)
        self.nentries_ent.delete(0, tk.END)
        #ntstr = "[" + str(self.demog_main.ns[0])
        #for i in range(1,len(self.demog_main.ns)):
        #    ntstr = ntstr + "," + str(self.demog_main.ns[i])
        #ntstr = ntstr + "]"
        self.nentries_ent.insert(0, str([min(5,min(self.demog_main.ns))] * self.demog_main.npops))
        
        self.nlft_entries_ent_exists = None
        self.nlft_entries_label = tk.Label(self.root, text = "Number of samples")
        self.nlft_entries_ent = tk.Entry(self.root)
        self.nlft_entries_ent.delete(0, tk.END)
        #ntstr = "[" + str(self.demog_main.ns[0])
        #for i in range(1,len(self.demog_main.ns)):
        #    ntstr = ntstr + "," + str(self.demog_main.ns[i])
        #ntstr = ntstr + "]"
        self.nlft_entries_ent.insert(0, str(self.demog_main.ns))

        self.saved_sfs_path = None
        self.saved_sfs_path_button_exists = None
        self.browse_hist_button = tk.Button(master=self.root, text="Load SFS from file", command=self.askopenfilename)        
        
        self.compute_stat_button_exists = None
        self.compute_stat_button = tk.Button(master = self.root, text="Compute and save SFS", command = self.on_compute_stat_button_call)
        
        self.plot_stat_button_exists = None
        self.plot_stat_button = tk.Button(master = self.root, text="Plot NLFT", command = self.on_plot_stat_button_call)
        
        self.plot_sfs_button_exists = None
        self.plot_sfs_button = tk.Button(master = self.root, text="Plot SFS", command = self.on_plot_sfs_button_call)
        
        self.stat_to_compute = None
        self.sfs_method = 'Exact'
        self.stat_save_filepath = None
        self.file_opt = options = {}
        options["defaultextension"] = ".npy"
        options["title"] = "Statistic File Name"
        self.nodemat = None
        self.momi_branch_hists = None
        self.momi_mig_mat = None

                                
    def on_stat_menu_selection(self,val):
        self.stat_to_compute = self.stat_menu_item.get()
        if self.stat_to_compute == 'SFS':
            if self.nlft_entries_ent_exists is None:
                self.nlft_entries_label.grid(row = 2, column = 1, sticky = tk.E)
                self.nlft_entries_ent.grid(row = 2, column = 2, sticky = tk.W)
                self.nlft_entries_ent_exists = 1
            if self.nentries_ent_exists is None:
                self.nentries_label.grid(row = 3, column = 1, sticky = tk.E)
                self.nentries_ent.grid(row = 3, column = 2, sticky = tk.W)
                self.nentries_ent_exists = 1
            if self.saved_sfs_path_button_exists is None:
                self.browse_hist_button.grid(row = 4, column = 2, sticky = tk.W)
                self.saved_sfs_path_button_exists = 1            
            if self.plot_stat_button_exists is not None:
                self.plot_stat_button.grid_forget()
                self.plot_stat_button_exists = None
            if self.compute_stat_button_exists is None:
                self.compute_stat_button.grid(row = 1, column = 2, sticky = tk.W)
                self.compute_stat_button_exists = 1
            if self.plot_sfs_button_exists is None:
                self.plot_sfs_button.grid(row = 5, column = 2, sticky = tk.W)
                self.plot_sfs_button_exists = 1
            if self.sfs_plotstyle_menu_exists is None:
                self.sfs_plotstyle_drop_menu.grid(row = 5, column = 1, sticky = tk.E)
                self.sfs_plotstyle_menu_exists = 1
            #if self.sfs_method_list_exists is None:
                #self.sfs_method_drop_menu.grid(row = 1, column = 2, sticky = tk.EW)
                #self.sfs_method_list_exists = 1
        if self.stat_to_compute == 'FST':
            if self.nentries_ent_exists is not None:
                self.nentries_label.grid_forget()
                self.nentries_ent.grid_forget()
                self.nentries_ent_exists = None
            if self.plot_stat_button_exists is not None:
                self.plot_stat_button.grid_forget()
                self.plot_stat_button_exists = None
            if self.compute_stat_button_exists is None:
                self.compute_stat_button.grid(row = 1, column = 2, sticky = tk.W)
                self.compute_stat_button_exists = 1
            if self.nlft_entries_ent_exists is not None:
                self.nlft_entries_label.grid_forget()
                self.nlft_entries_ent.grid_forget()
                self.nlft_entries_ent_exists = None
            if self.plot_sfs_button_exists is not None:
                self.plot_sfs_button.grid_forget()
                self.plot_sfs_button_exists = None
            if self.saved_sfs_path_button_exists is not None:
                self.browse_hist_button.grid_forget()
                self.saved_sfs_path_button_exists = None
            if self.sfs_plotstyle_menu_exists is not None:
                self.sfs_plotstyle_drop_menu.grid_forget()
                self.sfs_plotstyle_menu_exists = None
            #if self.sfs_method_list_exists is not None:
                #self.sfs_method_drop_menu.grid_forget()
                #self.sfs_method_list_exists = None
        if self.stat_to_compute == 'NLFT':
            if self.compute_stat_button_exists is not None:
                self.compute_stat_button.grid_forget()
                self.compute_stat_button_exists = None
            if self.nentries_ent_exists is not None:
                self.nentries_label.grid_forget()
                self.nentries_ent.grid_forget()
                self.nentries_ent_exists = None
            if self.nlft_entries_ent_exists is None:
                self.nlft_entries_label.grid(row = 2, column = 1, sticky = tk.E)
                self.nlft_entries_ent.grid(row = 2, column = 2, sticky = tk.W)
                self.nlft_entries_ent_exists = 1
            if self.plot_stat_button_exists is None:
                self.plot_stat_button.grid(row = 1, column = 2, sticky = tk.W)
                self.plot_stat_button_exists = 1
            if self.plot_sfs_button_exists is not None:
                self.plot_sfs_button.grid_forget()
                self.plot_sfs_button_exists = None
            if self.saved_sfs_path_button_exists is not None:
                self.browse_hist_button.grid_forget()
                self.saved_sfs_path_button_exists = None
            if self.sfs_plotstyle_menu_exists is not None:
                self.sfs_plotstyle_drop_menu.grid_forget()
                self.sfs_plotstyle_menu_exists = None

    def on_sfs_plotstyle_menu_selection(self,val):
        self.sfs_plotstyle = self.sfs_plotstyle_menu_item.get()
                        
    def askopenfilename(self):
        self.saved_sfs_path = tkFileDialog.askopenfilename(**self.demog_main.file_opt)
        return

    def on_sfs_method_menu_selection(self,val):
        self.sfs_method = self.sfs_method_menu_item.get()

        
    def on_compute_stat_button_call(self):
        if self.stat_to_compute is None:
            self.demog_main.app_output_box_window.output_box.insert(INSERT,'\n\nERROR: Must select statistic to compute.\n\n')
            self.demog_main.app_output_box_window.output_box.see(tk.END)
        else:
            if self.stat_to_compute == 'FST':
                #if self.demog_main.momi_dir_path is None:
                #    momi_dir_opt = options = {}
                #    options["title"] = "Specify momi Directory"
                #    self.demog_main.momi_dir_path = tkFileDialog.askdirectory(**momi_dir_opt)
                #self.stat_save_filepath = self.demog_main.momi_dir_path + '/fst_sfs.npy'
                #self.demog_main.nentries = self.demog_main.ns
                #self.compute_momi_sfs()
                #norm_JSFS = np.load(self.stat_save_filepath)
                
                #self.demog_main.nentries = np.ceil(np.array(self.demog_main.ns)/2)
                self.demog_main.nentries = self.nentries                
                jsfs_obj = JUSFSprecise(self.demog_main.hist, self.demog_main.nentries, nuref=1, ns = self.demog_main.ns, tubd = 20, Ent_sum_nmax = 10, get_JSFS = False, precision = 400)
                #jsfs_obj = JUSFSprecise(self.demog_main.hist, self.demog_main.nentries, nuref=1, ns = self.demog_main.ns, tubd = 20)
                jsfs_obj.get_JSFS_point_migrations()
                JSFS = jsfs_obj.JSFS
                
                print ">>> well, this SFS works"                
                
                norm_JSFS = JSFS / np.sum(JSFS)                
                
                #Cycle over all elements to get FST
                HT = 0
                HS = 0
                FST = 0
                #temp = np.cumprod(np.array(self.demog_main.ns)+1) #Useful quantity for converting between a scalar index, and an entry of a multidimensional array
                #temp = np.concatenate(([1],temp[0:len(temp)-1]))
                #nelts = np.prod(np.array(self.demog_main.ns)+1) #Total number of elements in the SFS
                temp = np.cumprod(np.array(jsfs_obj.entvec)+1) #Useful quantity for converting between a scalar index, and an entry of a multidimensional array
                temp = np.concatenate(([1],temp[0:len(temp)-1]))
                nelts = np.prod(np.array(jsfs_obj.entvec)+1).astype(int) #Total number of elements in the SFS
                for i in range(1,nelts+1):
                    ents = np.array([0]*self.demog_main.hist.npops)
                    r = i;
                    for j in np.arange(self.demog_main.hist.npops,1,-1):
                        ents[j-1] = np.ceil(r/temp[j-1]);
                        r = r - (ents[j-1]-1) * temp[j-1];
                    ents[0] = r;
                    ents = ents-1; #Records which entry we're at (i1,i2,...,iP) for P populations
                    if (np.sum(ents) > 0) and (np.sum(np.abs(ents - self.demog_main.ns)) > 0): #Don't include base entry or top entry (non-polymorphic sites)
                        freqs = ents / self.demog_main.ns #Frequency of the allele in each sample
                        Xi_entry = norm_JSFS[tuple(ents)] #Entry of the JSFS       
                        #HS = (np.sum(freqs**2) + np.sum((1-freqs)**2)) / self.demog_main.hist.npops
                        #HT = (np.sum(freqs)/self.demog_main.hist.npops)**2 + (np.sum(1-freqs)/self.demog_main.hist.npops)**2
                        #F = (HT - HS) / HT
                        
                        #HS = HS + Xi_entry * (1 - np.sum(freqs**2) / self.demog_main.hist.npops)
                        #HT = HT + Xi_entry * (1 - (np.sum(freqs)/self.demog_main.hist.npops)**2)
                        #FSTthis = (HS - HT) / (1 - HT)
                        #FST = FST + Xi_entry * FSTthis                        
                        
                        #print ">>>>>> HS, HT, F, Xi_entry, freqs, npops"
                        #print HS, HT, F, Xi_entry, freqs, self.demog_main.npops                        
                        
                        #print ">>>>>> HS, HT, Xi_entry, freqs"
                        #print HS, HT, Xi_entry, freqs
                        
                        mean_freq = np.sum(freqs)/self.demog_main.hist.npops
                        DST = mean_freq * (1 - mean_freq)
                        HT = np.sum((np.array(freqs) - mean_freq)**2) / self.demog_main.npops
                        FSTthis = (DST/HT)
                        FST = FST + Xi_entry * FSTthis                        
                        
                        print ">>>>>>>>>>>>>> FST_this"
                        print FSTthis
                                                
                    #FST = (HS - HT) / (1 - HT)
                    print ">>>>>>>>>>>>>> FST"
                    print FST
                
                self.demog_main.app_output_box_window.output_box.insert(INSERT,"\n\nFST: " + str(FST) + "\n")
                self.demog_main.app_output_box_window.output_box.see(tk.END)
                self.demog_main.app_output_box_window.output_box.insert(INSERT,"Computed as Nei's GST: M. Nei (1973). Analysis of Gene Diversity in Subdivided Populations. PNAS (70):3321-3323.\n\n" )
                self.demog_main.app_output_box_window.output_box.see(tk.END)

            #elif self.stat_to_compute == 'FST2':
            #    ET0 = 0
            #    ET = 0
            #    for i in range(0,self.demog_main.npops):
            #        for j in range(0,self.demog_main.npops):
            #            T = self.getET(i,j)
            #            ET = ET + T
            #            if i == j:
            #                ET0 = ET0 + T
            #    ET0 = ET0 / self.demog_main.npops
            #    ET = ET / (self.demog_main.npops**2)
            #    
            #    FST = 1 - ET0/ET
            #    self.demog_main.app_output_box_window.output_box.insert(INSERT,"\n\nFST: " + str(FST) + "\n")
            #    self.demog_main.app_output_box_window.output_box.see(tk.END)
                
                
            #elif self.stat_to_compute == 'SFS2':
            #    self.demog_main.nentries = np.ceil(np.array(self.demog_main.ns)/2)
            #    which_pops = [0] * self.demog_main.hist.npops
            #    for pop in range(0,self.demog_main.hist.npops):
            #        which_pops[pop] = pop+1
            #    jsfs_obj = JUSFSprecise(self.demog_main.hist, self.demog_main.nentries, nuref=1, ns = self.demog_main.ns, tubd = 20, Ent_sum_nmax = 10, get_JSFS = False, precision = 400)
            #    #jsfs_obj = JUSFSprecise(self.demog_main.hist, self.demog_main.nentries, nuref=1, ns = self.demog_main.ns, tubd = 20)
            #    jsfs_obj.get_JSFS_point_migrations()
            #    JSFS = jsfs_obj.JSFS
            #    
            #    self.get_stat_save_path()
            #    
            #    np.save(self.stat_save_filepath,jsfs_obj.JSFS)
                
                
                        
            elif self.stat_to_compute == 'SFS':
                if self.demog_main.hist is None:
                    self.demog_main.app_output_box_window.output_box.insert(INSERT,'\n\nERROR: Must generate a history by clicking "Draw History" first.\n\n')
                    self.demog_main.app_output_box_window.output_box.see(tk.END)
                    return
                if self.nlft_entries_ent.get():
                    self.demog_main.ns = np.array(ast.literal_eval(self.nlft_entries_ent.get())).astype(int)
                    self.demog_main.hist.ns = self.demog_main.ns
                if self.nentries_ent.get():
                    temp = np.array(ast.literal_eval(self.nentries_ent.get()))
                    if np.min(self.demog_main.ns - temp) < 0:
                        self.demog_main.app_output_box_window.output_box.insert(INSERT,'\n\nERROR: Entries must be smaller than sample sizes.\n\n')
                        self.demog_main.app_output_box_window.output_box.see(tk.END)
                        return
                    else:
                        self.demog_main.nentries = ast.literal_eval(self.nentries_ent.get())
                        
                    if len(self.demog_main.nentries) != self.demog_main.npops:
                        self.demog_main.app_output_box_window.output_box.insert(INSERT,'\n\nERROR: Number of entries must equal number of populations.\n\n')
                        self.demog_main.app_output_box_window.output_box.see(tk.END)
                        return
                
                
                self.get_stat_save_path()
                max_duration = 0
                for mig_ind in range(0,len(self.demog_main.hist.migs)):
                    max_duration = max(max_duration,self.demog_main.hist.migs[mig_ind][4])
                
                if max_duration == 0:
                    if self.demog_main.momi_dir_path is not None:
                        self.sfs_method = 'Exact'
                    else:
                        self.sfs_method = 'Approximate'
                        self.demog_main.app_output_box_window.output_box.insert(INSERT,'\n\nWARNING: Momi directory not specified. Computing SFS approximately.\n\n')
                        self.demog_main.app_output_box_window.output_box.see(tk.END)
                else:
                    self.demog_main.app_output_box_window.output_box.insert(INSERT,'\n\nWARNING: Continuous migration events detected. Computing SFS approximately.\n\n')
                    self.demog_main.app_output_box_window.output_box.see(tk.END)
                    self.sfs_method = 'Approximate'
                
                #if self.demog_main.momi_dir_path is None:
                #    self.demog_main.app_output_box_window.output_box.insert(INSERT,'\n\nMomi directory not specified. Using asymptotic SFS approximation.\n\n')
                #    self.demog_main.app_output_box_window.output_box.see(tk.END)
                #    self.sfs_method = 'Approximate'
                if self.sfs_method == 'Approximate':                    
                    #self.demog_main.nentries = np.ceil(np.array(self.demog_main.ns)/2)
                    #which_pops = [0] * self.demog_main.hist.npops
                    #for pop in range(0,self.demog_main.hist.npops):
                    #    which_pops[pop] = pop+1
                    jsfs_obj = JUSFSprecise(self.demog_main.hist, self.demog_main.nentries, nuref=1, ns = self.demog_main.ns, tubd = 20, Ent_sum_nmax = 10, get_JSFS = False, precision = 400)
                    #jsfs_obj = JUSFSprecise(self.demog_main.hist, self.demog_main.nentries, nuref=1, ns = self.demog_main.ns, tubd = 20)
                    jsfs_obj.get_JSFS_point_migrations()
                    JSFS = jsfs_obj.JSFS
                    #JUSFS = jsfs_obj.JUSFS
                    
                    #temp = np.cumprod(np.array(self.demog_main.nentries)+1) #Useful quantity for converting between a scalar index, and an entry of a multidimensional array
                    #temp = np.concatenate(([1],temp[0:len(temp)-1]))
                    #nelts = np.prod(np.array(self.demog_main.nentries)+1).astype(int) #Total number of elements in the SFS
                    #for i in range(1,nelts+1):
                    #    ents = np.array(mtlb.repmat(0,1,self.demog_main.hist.npops)[0])
                    #    r = i;            
                    #    for j in np.arange(self.demog_main.hist.npops,1,-1):
                    #        ents[j-1] = np.ceil(r/temp[j-1]);
                    #        r = r - (ents[j-1]-1) * temp[j-1];
                    #    ents[0] = r;
                    #    ents = ents-1;
                    #    JUSFS[tuple(ents)] = round(JUSFS[tuple(ents)],4)
                    
                    np.save(self.stat_save_filepath,jsfs_obj.JSFS)
                    print ">>>>>>>>> SFS"
                    print JSFS
                    
                    #print ">>>>>>>>> JUSFS"
                    #print JUSFS
                    
                elif self.sfs_method == 'Exact':
                    self.compute_momi_sfs()



    def getET(self,i,j):
        x = np.zeros((self.demog_main.npops,1))
        x[i] = 1
        y = np.zeros((self.demog_main.npops,1))
        y[j] = 1
        S = 0
        E = 0
        #if self.demog_main.Nref is not None:
        #    Nref = self.demog_main.Nref
        #else:
        #    self.demog_main.Nref = 10
        #    Nref = self.demog_main.Nref
        dt = 0.01
        BigNum = np.floor(self.demog_main.hist.maxt / dt).astype(int)
        migsc = copy.deepcopy(self.demog_main.migs)
        for i in range(0,len(migsc)):
            migsc[i][0] = round(migsc[i][0] / dt) * dt
            migsc[i][4] = round(migsc[i][4] / dt) * dt
        for g in range(1,BigNum):
            M = self.get_M(migsc,g * dt)
            
            x = x + np.dot(M,x) * dt
            y = y + np.dot(M,y) * dt
            
            #print ">>>>>>>>>>>>>>> x"
            #print x
            
            nu = self.get_nu(self.demog_main.hist.ts,g * dt)            
            
            S = S + np.sum(x*y/nu) * dt
            E = E + g * np.exp(-S) * (dt**2)
            
        print ">>>>>>>>>>> E"
        print E
        return E
    
    def get_M(self,migsc,t):
        M = np.zeros((self.demog_main.npops,self.demog_main.npops))
        for i in range(0,len(migsc)):
            if migsc[i][0] <= t and t <= migsc[i][0] + migsc[i][4]:
                if migsc[i][3] > 0:
                    pop1ind = migsc[i][1].astype(int)-1
                    pop2ind = migsc[i][2].astype(int)-1
                else:
                    pop1ind = migsc[i][2].astype(int)-1
                    pop2ind = migsc[i][1].astype(int)-1
                M[pop2ind][pop1ind] = np.abs(migsc[i][3])
                M[pop1ind][pop1ind] = M[pop1ind][pop1ind] - np.abs(migsc[i][3])
        return M

    def get_nu(self,tsc,t):
        nu = np.zeros((self.demog_main.npops,1))
        for i in range(0,self.demog_main.npops):
            ep = np.sum(np.array(tsc[i]) <= t) - 1
            if self.demog_main.expmat[i][ep] is None:
                gam = np.log(self.demog_main.hist.nus[i][ep+1]/self.demog_main.hist.nus[i][ep]) / tsc[i][ep]
                nu[i] = self.demog_main.hist.nus[i][ep] * np.exp(gam * (t - tsc[i][ep]))
            else:
                nu[i] = copy.deepcopy(self.demog_main.hist.nus[i][ep])
        return nu
                                                                

    def get_stat_save_path(self):
        self.stat_save_filepath = tkFileDialog.asksaveasfilename(**self.file_opt)
        return

    def on_plot_stat_button_call(self):
        if self.stat_to_compute == 'NLFT':
            if self.nlft_entries_ent.get():
                self.demog_main.ns = np.array(ast.literal_eval(self.nlft_entries_ent.get())).astype(int)
                self.demog_main.hist.ns = self.demog_main.ns
            nlft_vis_obj = NLFTvisualization(self.demog_main, self.demog_main.hist, self.demog_main.nuref, self.demog_main.ns, self.demog_main.maxt, self.demog_main.hist.plotdt)
        return

    def on_plot_sfs_button_call(self):
        if self.nentries_ent.get():
            self.nentries = ast.literal_eval(self.nentries_ent.get())
            if np.array(self.nentries).dtype.char == 'S':
                self.demog_main.app_output_box_window.output_box.insert(INSERT,'ERROR: Specify numeric value for numbers of entries.\n')
                self.demog_main.app_output_box_window.output_box.see(tk.END)
                self.nentries = None
                return
        else:
            self.demog_main.app_output_box_window.output_box.insert(INSERT,'ERROR: Specify numeric value for numbers of entries.\n')
            self.demog_main.app_output_box_window.output_box.see(tk.END)
            return
        
        self.sfs_plotstyle = self.sfs_plotstyle_menu_item.get()
        if self.sfs_plotstyle == 'Plot style':
            self.demog_main.app_output_box_window.output_box.insert(INSERT,'ERROR: Specify plot style (Line or Heatmap).\n')
            self.demog_main.app_output_box_window.output_box.see(tk.END)
            return
            
        if self.nlft_entries_ent.get():
            self.nlft_entries = ast.literal_eval(self.nlft_entries_ent.get())
            if np.array(self.nlft_entries).dtype.char == 'S':
                self.demog_main.app_output_box_window.output_box.insert(INSERT,'ERROR: Specify numeric value for numbers of samples.\n')
                self.demog_main.app_output_box_window.output_box.see(tk.END)
                self.nlft_entries = None
                return
        else:
            self.demog_main.app_output_box_window.output_box.insert(INSERT,'ERROR: Specify numeric value for numbers of samples.\n')
            self.demog_main.app_output_box_window.output_box.see(tk.END)
            return
            
        if np.min(np.array(self.nlft_entries) - np.array(self.nentries)) < 0:
            self.demog_main.app_output_box_window.output_box.insert(INSERT,'\n\nERROR: Entries must be smaller than sample sizes.\n\n')
            self.demog_main.app_output_box_window.output_box.see(tk.END)
            return
        
        self.ref_jsfs_to_plot = None
        if self.saved_sfs_path is not None:
            self.ref_jsfs_to_plot = np.load(self.saved_sfs_path)
                
        tubd = 20 #Big number so that all lineages are expected to coalesce by this time (in coalescent units of 2Nref genrations)
        if self.sfs_plotstyle == 'Line':
            jsfs_vis = JUSFSvisualization(self.demog_main.hist, self.nentries, self.nlft_entries, tubd, self.ref_jsfs_to_plot)
        elif self.sfs_plotstyle == 'Heatmap':
            if self.demog_main.npops > 1:
                jsfs_vis = JUSFSvisualizationHeatmap(self.demog_main.hist, self.nentries, self.nlft_entries)
            else:
                #jsfs_vis = JUSFSvisualization(self.demog_main.hist, self.nentries, self.nlft_entries, tubd, self.ref_jsfs_to_plot)
                self.demog_main.app_output_box_window.output_box.insert(INSERT,'\n\nERROR: Heatmap only available for multiple populations. Select "Line" for plotstyle.\n\n')
                self.demog_main.app_output_box_window.output_box.see(tk.END)
                return
        

                
    def compute_momi_sfs(self):
        if self.demog_main.momi_dir_path is None:
            momi_dir_opt = options = {}
            options["title"] = "Specify momi Directory"
            self.demog_main.momi_dir_path = tkFileDialog.askdirectory(**momi_dir_opt)
        
        #Append momi file to system path and import momi demographies
        sys.path.append(self.demog_main.momi_dir_path)
        from size_history import PiecewiseHistory, ConstantTruncatedSizeHistory, ExponentialTruncatedSizeHistory
        from demography import Demography
        from sum_product import SumProduct
        
        
        if self.demog_main.npops > 1:
            self.nodemat = np.array([[None]*5]*(2*self.demog_main.npops-1)) #np.zeros((2*self.demog_main.npops-1,5)) #Each row is: corresponding population, child1, child2, time at base, time at top. All indices are one-indexed        
                    
            #Find all full migrations and store them in the form [time,from_pop,to_pop]
            #self.momi_mig_mat = np.zeros((self.demog_main.npops-1,3))
            self.momi_mig_mat = []
            for i in range(0,len(self.demog_main.migs)):
                if self.demog_main.migs[i][3] == 1:
                    mig_event = [None,None,None]
                    mig_event[0] = self.demog_main.migs[i][0]
                    if self.demog_main.migs[i][3] >= 0:
                        mig_event[1] = self.demog_main.migs[i][1]
                        mig_event[2] = self.demog_main.migs[i][2]
                    else:
                        mig_event[1] = self.demog_main.migs[i][2]
                        mig_event[2] = self.demog_main.migs[i][1]
                    self.momi_mig_mat = self.momi_mig_mat + [mig_event]
                    
            if len(self.momi_mig_mat) > 0:
                self.momi_mig_mat = np.array(self.momi_mig_mat)
                self.momi_mig_mat = self.momi_mig_mat[self.momi_mig_mat[:,0].argsort()[::1]]        
            
            if len(self.momi_mig_mat) != self.demog_main.npops-1:
                self.demog_main.app_output_box_window.output_box.insert(INSERT,'\n\nERROR: Improper migration history. Lineages may not converge\n')
                self.demog_main.app_output_box_window.output_box.insert(INSERT,'           or a migration may lead to a non-existent population.\n')
                self.demog_main.app_output_box_window.output_box.see(tk.END)
                return
            
            #Set up the nodemat object
            for i in range(0,self.demog_main.npops):
                self.nodemat[i][0] = i+1
                self.nodemat[i][3] = 0
            ct = self.demog_main.npops
            nodes = range(1,self.demog_main.npops+1)
            for i in range(0,len(self.momi_mig_mat)):
                self.nodemat[ct][0] = self.momi_mig_mat[i][2] #Corresponding population
                self.nodemat[ct][1] = nodes[self.momi_mig_mat[i][1].astype(int)-1] #Which node
                self.nodemat[ct][2] = nodes[self.momi_mig_mat[i][2].astype(int)-1] #Which node
                self.nodemat[ct][3] = self.momi_mig_mat[i][0] #Base time
                self.nodemat[self.nodemat[ct][1]-1][4] = self.momi_mig_mat[i][0] #Top time
                self.nodemat[self.nodemat[ct][2]-1][4] = self.momi_mig_mat[i][0] #Top time
                nodes[self.momi_mig_mat[i][2].astype(int)-1] = ct+1 #Update pop-node correspondence
                ct = ct+1
                        
            #Setup Newick tree
            self.momi_branch_hists = [None]*(2*self.demog_main.npops-1)
            for i in range(0,len(self.momi_branch_hists)):
                base = None
                if i >= self.demog_main.npops:
                    base = '(' + self.momi_branch_hists[self.nodemat[i][1]-1] + ',' + self.momi_branch_hists[self.nodemat[i][2]-1] + ')'
                else:
                    base = str(i+1)
                if i < len(self.momi_branch_hists)-1:
                    base = base + ':'
                if i < len(self.momi_branch_hists)-1:
                    base = base + str(self.nodemat[i][4] - self.nodemat[i][3]) #Time to parent node
    
                                                    
                #Form the population history
                if i == len(self.momi_branch_hists)-1:
                    popind = np.array(self.nodemat[i][0]).astype(int)-1
                    start_time = self.nodemat[i][3]
                    start_epind = np.sum(np.array(self.demog_main.ts[popind]) <= start_time) - 1                
                    
                    if (start_epind == len(self.demog_main.nus[popind])-1) and (self.demog_main.expmat[popind][start_epind] == 0):
                        hist = '[&&momi:N=' + str(self.demog_main.nus[popind][start_epind]) + ']'
                    else:
                        self.demog_main.app_output_box_window.output_box.insert(INSERT,'\n\nERROR: momi requires a single constant root epoch.\n')
                        self.demog_main.app_output_box_window.output_box.insert(INSERT,'           Delete ancestral size changes in the root first.\n')
                        self.demog_main.app_output_box_window.output_box.see(tk.END)
                        return
                else:
                    popind = np.array(self.nodemat[i][0]-1).astype(int)
                    start_time = self.nodemat[i][3]
                    stop_time = self.nodemat[i][4]
                    start_epind = np.array(np.sum(np.array(self.demog_main.ts[popind]) <= start_time) - 1).astype(int)
                    stop_epind = np.array(np.sum(np.array(self.demog_main.ts[popind]) < stop_time) - 1).astype(int)
                    
                    #Build the history
                    hist = '[&&momi:'
                    if i < self.demog_main.npops:
                        hist = hist + 'lineages=' + str(self.demog_main.ns[i]) + ':'
                    if start_epind == stop_epind:
                        if self.demog_main.expmat[popind][start_epind] == 0:
                            hist = hist + 'model=constant:N=' + str(self.demog_main.nus[popind][start_epind]) + ']'
                        else:
                            hist = hist + 'model=exponential:'
                            t1 = start_time - self.demog_main.ts[popind][start_epind]
                            g = self.demog_main.hist.gammas[popind][start_epind]
                            N0 = self.demog_main.nus[popind][start_epind]
                            N1 = N0 * np.exp(g * t1)
                            t2 = stop_time - self.demog_main.ts[popind][start_epind]
                            N2 = N0 * np.exp(g * t2)
                            hist = hist + 'N_top=' + str(N2) + ':N_bottom=' + str(N1) + ']'
                    else:
                        hist = hist + 'model=piecewise:'
                        if self.demog_main.expmat[popind][start_epind] == 0:
                            t = self.demog_main.ts[popind][start_epind+1] - start_time
                            hist = hist + 'model_0=constant:tau_0=' + str(t) + ':N_0=' + str(self.demog_main.nus[popind][start_epind]) + ':'
                        else:
                            t1 = start_time - self.demog_main.ts[popind][start_epind]
                            g = self.demog_main.hist.gammas[popind][start_epind]
                            N0 = self.demog_main.nus[popind][start_epind]
                            N1 = N0 * np.exp(g * t1)
                            t2 = self.demog_main.ts[popind][start_epind+1] - self.demog_main.ts[popind][start_epind]
                            N2 = N0 * np.exp(g * t2)
                            t = self.demog_main.ts[popind][start_epind+1] - start_time
                            hist = hist + 'model_0=exponential:tau_0=' + str(t) + ':N_top_0=' + str(N2) + ':N_bottom_0=' + str(N1) + ':'
                        ct = 1
                        for j in range(start_epind+1,stop_epind):
                            if self.demog_main.expmat[popind][j] == 0:
                                t = self.demog_main.ts[popind][j+1] - self.demog_main.ts[popind][j]
                                hist = hist + 'model_' + str(ct) + '=constant:tau_' + str(ct) + '=' + str(t) + ':N_' + str(ct) + '=' + str(self.demog_main.nus[popind][j]) + ':'
                            else:
                                t = self.demog_main.ts[popind][j+1] - self.demog_main.ts[popind][j]
                                g = self.demog_main.hist.gammas[popind][j]
                                N1 = self.demog_main.nus[popind][j]
                                N2 = N1 * np.exp(g * t)
                                hist = hist + 'model_' + str(ct) + '=exponential:tau_' + str(ct) + '=' + str(t) + ':N_top_' + str(ct) + '=' + str(N2) + ':N_bottom_' + str(ct) + '=' + str(N1) + ':'
                            ct = ct + 1
                        if self.demog_main.expmat[popind][stop_epind] == 0:
                            t = stop_time - self.demog_main.ts[popind][stop_epind]
                            hist = hist + 'model_' + str(ct) + '=constant:tau_' + str(ct) + '=' + str(t) + ':N_' + str(ct) + '=' + str(self.demog_main.nus[popind][stop_epind]) + ']'
                        else:
                            t = stop_time - self.demog_main.ts[popind][stop_epind]
                            g = self.demog_main.hist.gammas[popind][stop_epind]
                            N1 = self.demog_main.nus[popind][stop_epind]                    
                            N2 = N1 * np.exp(g * t)
                            hist = hist + 'model_' + str(ct) + '=exponential:tau_' + str(ct) + '=' + str(t) + ':N_top_' + str(ct) + '=' + str(N2) + ':N_bottom_' + str(ct) + '=' + str(N1) + ']'
                
                self.momi_branch_hists[i] = base + hist
                
            
            #self.demog_main.momi_dir_path
            #self.demog_main.app_output_box_window.output_box.insert(INSERT,'\n\nDIRPATH: ' + self.demog_main.momi_dir_path + '\n')
            #self.demog_main.app_output_box_window.output_box.insert(INSERT,'\n\nMOMINEWICKSTR:\n' + self.momi_branch_hists[-1] + '\n')
            #self.demog_main.app_output_box_window.output_box.see(tk.END)
            
            ## specify demography via a newick string
            ## to specify additional population parameters, follow branch length with [&&momi:...]
            ## where ... contains:
            ##    lineages= # alleles (if population is leaf)
            ##    model= population history (default=constant)
            ##    N, N_top, N_bottom= parameters for constant/exponential size history
            ##    model_i= model for i-th epoch of piecewise history (either constant or exponential)
            ##    N_i, N_top_i, N_bottom_i, tau_i= parameters for i-th epoch of piecewise history
            newick_str = self.momi_branch_hists[-1]
            
            demography = Demography.from_newick(newick_str)
            sfs = np.zeros(tuple(np.array(self.demog_main.nentries)+1));
            
            #Compute the SFS using momi
            #Loop over all entries 'ents' of the SFS where [i1,i2,i2,...,inpops], (ik=0,...,ns[k+1]) is the expected number of sites with ik copies in population k.
            temp = np.cumprod(np.array(self.demog_main.nentries)+1) #Useful quantity for converting between a scalar index, and an entry of a multidimensional array
            temp = np.concatenate(([1],temp[0:len(temp)-1]))
            nelts = np.prod(np.array(self.demog_main.nentries)+1) #Total number of elements in the SFS
            for i in range(1,nelts+1):
                ents = np.array([0]*self.demog_main.npops)
                r = i;
                for j in np.arange(self.demog_main.npops,1,-1):
                    ents[j-1] = np.ceil(r/temp[j-1]);
                    r = r - (ents[j-1]-1) * temp[j-1];
                ents[0] = r;
                ents = ents-1;
                momi_dict = []
                for j in range(0,self.demog_main.npops):
                    temp_dict = {'derived' : ents[j], 'ancestral': self.demog_main.ns[j] - ents[j]}
                    momi_dict = momi_dict + [(str(j+1),temp_dict)]
                demography.update_state(dict(momi_dict))
                sp = SumProduct(demography)
                sfs[tuple(ents)] = sp.p()
        else:
            print "Error: momi not setup for single population histories"
    
        np.save(self.stat_save_filepath,sfs)
        print ">>>>>>>>>>>>> sfs"
        print sfs
        
            

class DraggablePopHistory:
    def __init__(self, demog_main, fig, ax, ts, nus, expmat, migs, maxnes, maxt, plotdt, units, Nref, years_per_gen):
        #Figure parameters and units
        self.demog_main = demog_main
        self.units = units
        self.Nref = Nref
        self.years_per_gen = years_per_gen
        self.plotdt = plotdt
        self.fig = fig
        self.ax = ax

        
        #History parameters
        self.ts = ts
        self.nus = nus
        self.expmat = expmat
        self.migs = migs
        self.maxnes = maxnes
        self.maxnes_display = None
        if self.units == 'Coalescent units':
            self.maxnes_display = copy.deepcopy(self.maxnes)
        elif self.units == 'Ne/generations' or self.units == 'Ne/years':
            self.maxnes_display = np.array(copy.deepcopy(self.maxnes))*self.Nref
        self.maxt = maxt
        self.npops = len(maxnes)
        self.popctrs = np.zeros(self.npops)
        self.popctrs[0] = maxnes[0]
        for i in range(1,self.npops):
            self.popctrs[i] = self.popctrs[i-1] + maxnes[i-1] + maxnes[i]   
            
        #Set up axes with proper units
        self.ax.set_xlim([0,maxt])
        self.ax.set_ylim([0,self.popctrs[-1]+maxnes[-1]])                
        self.ytick_locs = np.union1d(self.popctrs,self.popctrs + self.maxnes)
        if self.units == 'Coalescent units':
            self.ax.set_ylabel('Relative Population Size (nu)')
            self.ax.set_xlabel('Time in the past (2N generations)')
        elif self.units == 'Ne/generations':
            self.ax.set_ylabel('Population Size (Ne)')
            self.ax.set_xlabel('Time in the past (generations)')
        elif self.units == 'Ne/years':
            self.ax.set_ylabel('Population Size (Ne)')
            self.ax.set_xlabel('Time in the past (years)')
        self.ax.yaxis.set_ticks(self.ytick_locs)
        self.ytick_labels = []
        for i in range(0,len(self.popctrs)):
            self.ytick_labels = self.ytick_labels + ['Pop ' + str(i+1)]
            self.ytick_labels = self.ytick_labels + [str(self.maxnes_display[i])]
        self.ax.yaxis.set_ticklabels(self.ytick_labels)

        self.xticks = self.ax.get_xticks()
        self.xtick_labels = []
        for i in range(0,len(self.xticks)):
            newxtick = None
            if self.units == 'Coalescent units':
                newxtick = self.xticks[i]
            elif self.units == 'Ne/generations':
                newxtick = self.xticks[i] * 2 * self.Nref
            elif self.units == 'Ne/years':
                newxtick = self.xticks[i] * 2 * self.Nref * self.years_per_gen
            self.xtick_labels = self.xtick_labels + [str(newxtick)]
        self.ax.xaxis.set_ticklabels(self.xtick_labels)
                
            
        #Set up rectangle tabs for dragging the history    
        self.rects = [None] * self.npops
        axes_xrange = self.ax.get_xlim()[1] - self.ax.get_xlim()[0]
        axes_yrange = self.ax.get_ylim()[1] - self.ax.get_ylim()[0]
        rect_xdim = axes_xrange/30
        rect_ydim = axes_yrange/30
        self.axes_xrange = axes_xrange
        self.axes_yrange = axes_yrange
        self.rect_xdim = rect_xdim
        self.rect_ydim = rect_ydim
        self.rect_xoffset = rect_xdim/2
        self.rect_yoffset = rect_ydim/2
        for i in range(0,self.npops):
            temp = [None] * len(self.ts[i]) #Array with number of entries equal to one plus the number of epochs in pop i+1
            for j in range(0,len(self.ts[i])):
                temp[j] = self.ax.add_patch(ptchs.Rectangle((self.ts[i][j] - self.rect_xoffset,self.popctrs[i]+self.nus[i][j] - self.rect_yoffset),rect_xdim,rect_ydim,alpha=0.5,facecolor='none',edgecolor='none'))
            self.rects[i] = temp
        temp = None
            
        #Set up circle tabs for dragging the history    
        self.circles = [None] * self.npops
        for i in range(0,self.npops):
            temp = [None] * len(self.ts[i]) #Array with number of entries equal to one plus the number of epochs in pop i+1
            for j in range(0,len(self.ts[i])):
                temp[j] = self.ax.add_patch(ptchs.Ellipse((self.ts[i][j],self.popctrs[i]+self.nus[i][j]),rect_xdim*2/3,rect_ydim*2/3,alpha=0.05,facecolor='black',edgecolor='none'))
            self.circles[i] = temp            
        temp = None
                
        #Set up history lines
        self.gammas = copy.deepcopy(self.expmat)
        self.histlines = [None] * self.npops
        for i in range(0,self.npops):
            temp = [None] * len(self.expmat[i])
            quantstemp = [None] * len(self.expmat[i])
            for j in range(0,len(temp)):
                if j < len(temp)-1:
                    plot_range = np.linspace(self.ts[i][j],self.ts[i][j+1],max(10,round((self.ts[i][j+1] - self.ts[i][j])/self.plotdt)))
                    if self.expmat[i][j] is None:
                        Nf = self.nus[i][j]
                        No = self.nus[i][j+1]
                        t = self.ts[i][j+1] - self.ts[i][j]
                        self.gammas[i][j] = np.log(No/Nf)/t
                else:
                    plot_range = np.linspace(self.ts[i][j],self.maxt,max(10,round((self.maxt - self.ts[i][j])/self.plotdt)))
                    
                tvals = plot_range-self.ts[i][j]
                upbd = self.popctrs[i] + self.nus[i][j]*np.exp(self.gammas[i][j]*tvals)
                lowbd = self.popctrs[i] - self.nus[i][j]*np.exp(self.gammas[i][j]*tvals)
                temp1 = np.transpose([plot_range,upbd])
                temp2 = np.transpose([plot_range,lowbd])
                temp3 = np.concatenate((temp1,np.flipud(temp2)),axis=0)
                temp[j] = ax.add_patch(ptchs.Polygon(temp3,facecolor='blue',alpha=0.15,edgecolor='none'))
                quantstemp[j] = [plot_range,tvals]
                
            self.histlines[i] = temp
        temp = None

        #Set up migrations
        self.mig_drag_rects = [None] * len(self.migs)
        self.mig_drag_circles = [None] * len(self.migs)
        self.mig_stren_rects = [None] * len(self.migs)
        self.mig_stren_circles = [None] * len(self.migs)      
        self.miggraphics = [None] * len(self.migs)
        self.mig_dur_graphics = [None] * len(self.migs)
        self.migmaskgraphics = [None] * len(self.migs)
        for i in range(0,len(self.migs)):
            time = self.migs[i][0]
            pop1ind = int(self.migs[i][1].astype(int)-1)
            pop2ind = int(self.migs[i][2].astype(int)-1)
            duration = self.migs[i][4]
            
            #If a migration involves 100% of lineages, it's a merger, so hide/mask the population previous to this event.
            mask = None
            if self.migs[i][3] == 1:
                mask = self.ax.add_patch(ptchs.Rectangle((self.migs[i][0],self.popctrs[self.migs[i][1].astype(int)-1] - self.maxnes[self.migs[i][1].astype(int)-1]),self.maxt-self.migs[i][0],2*self.maxnes[self.migs[i][1].astype(int)-1],alpha=self.migs[i][3],facecolor='white',edgecolor='none',zorder = len(self.ax.patches)))
            elif self.migs[i][3] == -1:
                mask = self.ax.add_patch(ptchs.Rectangle((self.migs[i][0],self.popctrs[self.migs[i][2].astype(int)-1] - self.maxnes[self.migs[i][2].astype(int)-1]),self.maxt-self.migs[i][0],2*self.maxnes[self.migs[i][2].astype(int)-1],alpha=-self.migs[i][3],facecolor='white',edgecolor='none',zorder = len(self.ax.patches)))            
            self.migmaskgraphics[i] = mask            
            
            epind1 = np.sum(np.array(self.ts[pop1ind]) <= time) - 1
            epind2 = np.sum(np.array(self.ts[pop2ind]) <= time) - 1
            arr_start_x = time
            arr_stop_x = time + duration            
            if pop1ind < pop2ind:
                if self.migs[i][3] > 0:
                    arr_start_y = self.popctrs[pop1ind] + self.nus[pop1ind][epind1] * np.exp(self.gammas[pop1ind][epind1] * (time - self.ts[pop1ind][epind1]))
                    arr_stop_y = self.popctrs[pop2ind] - self.nus[pop2ind][epind2] * np.exp(self.gammas[pop2ind][epind2] * (time - self.ts[pop2ind][epind2]))
                else:
                    arr_stop_y = self.popctrs[pop1ind] + self.nus[pop1ind][epind1] * np.exp(self.gammas[pop1ind][epind1] * (time - self.ts[pop1ind][epind1]))
                    arr_start_y = self.popctrs[pop2ind] - self.nus[pop2ind][epind2] * np.exp(self.gammas[pop2ind][epind2] * (time - self.ts[pop2ind][epind2]))
            elif pop1ind > pop2ind:
                if self.migs[i][3] > 0:
                    arr_stop_y = self.popctrs[pop2ind] + self.nus[pop2ind][epind2] * np.exp(self.gammas[pop2ind][epind2] * (time - self.ts[pop2ind][epind2]))
                    arr_start_y = self.popctrs[pop1ind] - self.nus[pop1ind][epind1] * np.exp(self.gammas[pop1ind][epind1] * (time - self.ts[pop1ind][epind1]))
                else:
                    arr_start_y = self.popctrs[pop2ind] + self.nus[pop2ind][epind2] * np.exp(self.gammas[pop2ind][epind2] * (time - self.ts[pop2ind][epind2]))
                    arr_stop_y = self.popctrs[pop1ind] - self.nus[pop1ind][epind1] * np.exp(self.gammas[pop1ind][epind1] * (time - self.ts[pop1ind][epind1]))

            self.arr_start_x = arr_start_x
            self.arr_start_y = arr_start_y
            self.arr_stop_x = arr_stop_x
            self.arr_stop_y = arr_stop_y
            arr_width_scale = 20 #max(40/self.migs[i][4],20)
            arr_head_width = max(self.migs[i][4]*rect_xdim/2,rect_xdim/2)
            arr_head_len = rect_ydim/2
            arr_posA = [arr_start_x, arr_start_y]
            arr_posB = [arr_start_x, arr_start_y + (arr_stop_y - arr_start_y)]
            if duration == 0:
                if np.abs(pop1ind - pop2ind) == 1:
                    arr_connect_style = 'arc3,rad=0'
                else:
                    if arr_start_y < arr_stop_y:
                        arr_connect_style = 'arc3,rad=0.1'
                    else:
                        arr_connect_style = 'arc3,rad=-0.1'
            elif duration > 0:
                arr_connect_style = 'arc3,rad=0'
            arr_color = [0.9290,0.6940,0.1250]
            transp = max(0.1,abs(self.migs[i][3]))
            linst = '-'
            if abs(self.migs[i][3]) == 0:
                linst = '--'
            arr = self.ax.add_patch(ptchs.FancyArrowPatch(posA = arr_posA, posB = arr_posB, connectionstyle = arr_connect_style, linestyle = linst, mutation_scale = arr_width_scale, color = arr_color, edgecolor = 'none', alpha = transp, zorder = len(self.ax.patches) + 1))             
            self.miggraphics[i] = arr
            
            self.mig_drag_rects[i] = self.ax.add_patch(ptchs.Rectangle((self.arr_start_x - self.rect_xoffset,self.arr_start_y - self.rect_yoffset),self.rect_xdim,self.rect_ydim,alpha=0.5,facecolor='none',edgecolor='none'))
            self.mig_drag_circles[i] = self.ax.add_patch(ptchs.Ellipse((self.arr_start_x,self.arr_start_y),rect_xdim*2/3,rect_ydim*2/3,alpha=0.05,facecolor='black',edgecolor='none'))
           
            self.mig_stren_rects[i] = self.ax.add_patch(ptchs.Rectangle((self.arr_stop_x - self.rect_xoffset,self.arr_stop_y - self.rect_yoffset),self.rect_xdim,self.rect_ydim,alpha=0.5,facecolor='none',edgecolor='none'))
            self.mig_stren_circles[i] = self.ax.add_patch(ptchs.Ellipse((self.arr_stop_x,self.arr_stop_y),rect_xdim*2/3,rect_ydim*2/3,alpha=0.05,facecolor='black',edgecolor='none'))
            
            
            if duration > 0:
                [temp,arr_stop_yf] = self.get_cts_mig_patch(self.migs[i])
                
                self.mig_dur_graphics[i] = self.ax.add_patch(ptchs.Polygon(temp,facecolor=arr_color, alpha=0.15, edgecolor='none'))
                
                self.mig_stren_rects[i].set_x(arr_start_x - self.rect_xoffset)
                self.mig_stren_rects[i].set_y(arr_stop_y - self.rect_yoffset)
                self.mig_stren_circles[i].center = (arr_start_x,arr_stop_y)
                    
            
        self.popup_window = None
        self.popup_textbox_change = False
        self.toggle_exp = None
        self.del_mig = None
        self.new_mig = None
        self.ghost_line_patch = None
        self.mig_drag_ind = None
        self.mig_stren_ind = None
        self.mig_stren_bds = [None,None]
        self.del_epoch = False
        self.new_epoch = False
        self.make_exp = False
        self._observers = []
        self._observer_counter = 0 #Stores a unique id for observers so we can delete them when we're done with them
        self._observer_dictionary = []
        self.selected_ind = None
        self.press = None
        self.background = None
        self.lock = None
        self.fig.canvas.draw()
               

    #Make a continuous migration patch
    def get_cts_mig_patch(self,mig):
        pop1ind = int(mig[1].astype(int)-1)
        pop2ind = int(mig[2].astype(int)-1)
        
        time = mig[0]
        duration = mig[4]
        
        epind1 = np.sum(np.array(self.ts[pop1ind]) <= time) - 1
        epind2 = np.sum(np.array(self.ts[pop2ind]) <= time) - 1
        arr_start_x = time
        arr_stop_x = time + duration            
        if pop1ind < pop2ind:
            if mig[3] > 0:
                arr_start_y = self.popctrs[pop1ind] + self.nus[pop1ind][epind1] * np.exp(self.gammas[pop1ind][epind1] * (time - self.ts[pop1ind][epind1]))
                arr_stop_y = self.popctrs[pop2ind] - self.nus[pop2ind][epind2] * np.exp(self.gammas[pop2ind][epind2] * (time - self.ts[pop2ind][epind2]))
            else:
                arr_stop_y = self.popctrs[pop1ind] + self.nus[pop1ind][epind1] * np.exp(self.gammas[pop1ind][epind1] * (time - self.ts[pop1ind][epind1]))
                arr_start_y = self.popctrs[pop2ind] - self.nus[pop2ind][epind2] * np.exp(self.gammas[pop2ind][epind2] * (time - self.ts[pop2ind][epind2]))
        elif pop1ind > pop2ind:
            if mig[3] > 0:
                arr_stop_y = self.popctrs[pop2ind] + self.nus[pop2ind][epind2] * np.exp(self.gammas[pop2ind][epind2] * (time - self.ts[pop2ind][epind2]))
                arr_start_y = self.popctrs[pop1ind] - self.nus[pop1ind][epind1] * np.exp(self.gammas[pop1ind][epind1] * (time - self.ts[pop1ind][epind1]))
            else:
                arr_start_y = self.popctrs[pop2ind] + self.nus[pop2ind][epind2] * np.exp(self.gammas[pop2ind][epind2] * (time - self.ts[pop2ind][epind2]))
                arr_stop_y = self.popctrs[pop1ind] - self.nus[pop1ind][epind1] * np.exp(self.gammas[pop1ind][epind1] * (time - self.ts[pop1ind][epind1]))
        
        arr_posA = [arr_start_x,arr_start_y]
        arr_posB = [arr_start_x,arr_stop_y]
        
        stop_epind1 = np.sum(np.array(self.ts[pop1ind]) <= arr_stop_x) - 1 #Epoch in pop1 when migration stops (going backwards in time)
        stop_epind2 = np.sum(np.array(self.ts[pop2ind]) <= arr_stop_x) - 1 #Epoch in pop2 when migration stops (going backwards in time)

        pop1range = []
        pop2range = []
        pop1profile = []
        pop2profile = []
        if epind2 == stop_epind2:
            temp_range = np.linspace(arr_start_x,arr_stop_x,max(10,round((arr_stop_x - arr_start_x)/self.plotdt)))
            pop2range = np.concatenate((pop2range,np.transpose(temp_range)),axis=0)
            temp_vals = self.nus[pop2ind][epind2]*np.exp(self.gammas[pop2ind][epind2]*(arr_start_x - self.ts[pop2ind][epind2])) * np.exp(self.gammas[pop2ind][epind2] * (temp_range - arr_start_x))
            pop2profile = np.concatenate((pop2profile,np.transpose(temp_vals)),axis=0)
        else:
            temp_range = np.linspace(arr_start_x,self.ts[pop2ind][epind2+1],max(10,round((self.ts[pop2ind][epind2+1] - arr_start_x)/self.plotdt)))
            pop2range = np.concatenate((pop2range,np.transpose(temp_range)),axis=0)
            temp_vals = self.nus[pop2ind][epind2]*np.exp(self.gammas[pop2ind][epind2]*(arr_start_x - self.ts[pop2ind][epind2])) * np.exp(self.gammas[pop2ind][epind2] * (temp_range - arr_start_x))
            pop2profile = np.concatenate((pop2profile,np.transpose(temp_vals)),axis=0)
            for j in range(epind2+1,stop_epind2):
                temp_range = np.linspace(self.ts[pop2ind][j],self.ts[pop2ind][j+1],max(10,round((self.ts[pop2ind][j+1] - self.ts[pop2ind][j])/self.plotdt)))
                pop2range = np.concatenate((pop2range,np.transpose(temp_range)),axis=0)
                temp_vals = self.nus[pop2ind][j] * np.exp(self.gammas[pop2ind][j] * (temp_range - self.ts[pop2ind][j]))
                pop2profile = np.concatenate((pop2profile,np.transpose(temp_vals)),axis=0)
            temp_range = np.linspace(self.ts[pop2ind][stop_epind2],arr_stop_x,max(10,round((arr_stop_x - self.ts[pop2ind][stop_epind2])/self.plotdt)))
            pop2range = np.concatenate((pop2range,np.transpose(temp_range)),axis=0)
            temp_vals = self.nus[pop2ind][stop_epind2] * np.exp(self.gammas[pop2ind][stop_epind2] * (temp_range - self.ts[pop2ind][stop_epind2]))
            pop2profile = np.concatenate((pop2profile,np.transpose(temp_vals)),axis=0)

        if epind1 == stop_epind1:
            temp_range = np.linspace(arr_start_x,arr_stop_x,max(10,round((arr_stop_x - arr_start_x)/self.plotdt)))
            pop1range = np.concatenate((pop1range,np.transpose(temp_range)),axis=0)
            temp_vals = self.nus[pop1ind][epind1]*np.exp(self.gammas[pop1ind][epind1]*(arr_start_x - self.ts[pop1ind][epind1])) * np.exp(self.gammas[pop1ind][epind1] * (temp_range - arr_start_x))
            pop1profile = np.concatenate((pop1profile,np.transpose(temp_vals)),axis=0)
        else:
            temp_range = np.linspace(arr_start_x,self.ts[pop1ind][epind1+1],max(10,round((self.ts[pop1ind][epind1+1] - arr_start_x)/self.plotdt)))
            pop1range = np.concatenate((pop1range,np.transpose(temp_range)),axis=0)
            temp_vals = self.nus[pop1ind][epind1]*np.exp(self.gammas[pop1ind][epind1]*(arr_start_x - self.ts[pop1ind][epind1])) * np.exp(self.gammas[pop1ind][epind1] * (temp_range - arr_start_x))
            pop1profile = np.concatenate((pop1profile,np.transpose(temp_vals)),axis=0)
            for j in range(epind1+1,stop_epind1):
                temp_range = np.linspace(self.ts[pop1ind][j],self.ts[pop1ind][j+1],max(10,round((self.ts[pop1ind][j+1] - self.ts[pop1ind][j])/self.plotdt)))
                pop1range = np.concatenate((pop1range,np.transpose(temp_range)),axis=0)
                temp_vals = self.nus[pop1ind][j] * np.exp(self.gammas[pop1ind][j] * (temp_range - self.ts[pop1ind][j]))
                pop1profile = np.concatenate((pop1profile,np.transpose(temp_vals)),axis=0)
            temp_range = np.linspace(self.ts[pop1ind][stop_epind1],arr_stop_x,max(10,round((arr_stop_x - self.ts[pop1ind][stop_epind1])/self.plotdt)))
            pop1range = np.concatenate((pop1range,np.transpose(temp_range)),axis=0)
            temp_vals = self.nus[pop1ind][stop_epind1] * np.exp(self.gammas[pop1ind][stop_epind1] * (temp_range - self.ts[pop1ind][stop_epind1]))
            pop1profile = np.concatenate((pop1profile,np.transpose(temp_vals)),axis=0)

        if pop1ind < pop2ind:
            lbd_range = copy.deepcopy(pop1range)
            lbd_profile = self.popctrs[pop1ind] + pop1profile
            
            ubd_range = copy.deepcopy(pop2range)
            ubd_profile = self.popctrs[pop2ind] - pop2profile
        else:
            lbd_range = copy.deepcopy(pop2range)
            lbd_profile = self.popctrs[pop2ind] + pop2profile
            
            ubd_range = copy.deepcopy(pop1range)
            ubd_profile = self.popctrs[pop1ind] - pop1profile
                                                        
        if pop1ind < pop2ind:
            if mig[3] > 0:
                arr_stop_yf = self.popctrs[pop1ind] + self.nus[pop1ind][stop_epind1] * np.exp(self.gammas[pop1ind][stop_epind1] * (arr_stop_x - self.ts[pop1ind][stop_epind1]))
                arr_stop_y0 = self.popctrs[pop2ind] - self.nus[pop2ind][stop_epind2] * np.exp(self.gammas[pop2ind][stop_epind2] * (arr_stop_x - self.ts[pop2ind][stop_epind2]))
            else:
                arr_stop_y0 = self.popctrs[pop1ind] + self.nus[pop1ind][stop_epind1] * np.exp(self.gammas[pop1ind][stop_epind1] * (arr_stop_x - self.ts[pop1ind][stop_epind1]))
                arr_stop_yf = self.popctrs[pop2ind] - self.nus[pop2ind][stop_epind2] * np.exp(self.gammas[pop2ind][stop_epind2] * (arr_stop_x - self.ts[pop2ind][stop_epind2]))
        else:
            if mig[3] > 0:
                arr_stop_y0 = self.popctrs[pop1ind] - self.nus[pop1ind][stop_epind1] * np.exp(self.gammas[pop1ind][stop_epind1] * (arr_stop_x - self.ts[pop1ind][stop_epind1]))
                arr_stop_yf = self.popctrs[pop2ind] + self.nus[pop2ind][stop_epind2] * np.exp(self.gammas[pop2ind][stop_epind2] * (arr_stop_x - self.ts[pop2ind][stop_epind2]))
            else:
                arr_stop_yf = self.popctrs[pop1ind] - self.nus[pop1ind][stop_epind1] * np.exp(self.gammas[pop1ind][stop_epind1] * (arr_stop_x - self.ts[pop1ind][stop_epind1]))
                arr_stop_y0 = self.popctrs[pop2ind] + self.nus[pop2ind][stop_epind2] * np.exp(self.gammas[pop2ind][stop_epind2] * (arr_stop_x - self.ts[pop2ind][stop_epind2]))

        arr_stop_posA = [arr_stop_x, arr_stop_y0]
        arr_stop_posB = [arr_stop_x, arr_stop_yf]


        start_arc_connection = ptchs.ConnectionStyle("Arc3, rad=0.1")
        stop_arc_connection = ptchs.ConnectionStyle("Arc3, rad=-0.1")
                
        if arr_posA[1] < arr_posB[1]:
            b1 = start_arc_connection(arr_posA,arr_posB)
        else:
            b1 = start_arc_connection(arr_posB,arr_posA)
        if arr_stop_posA[1] < arr_stop_posB[1]:
            b2 = stop_arc_connection(arr_stop_posB,arr_stop_posA)
        else:
            b2 = stop_arc_connection(arr_stop_posA,arr_stop_posB)

        nsamples = 20
        temp1 = np.transpose([ubd_range,ubd_profile])
        temp2 = self.get_Bezier_points(b2, nsamples) #np.array(b2.vertices)
        temp3 = np.transpose([lbd_range,lbd_profile])
        temp4 = self.get_Bezier_points(b1, nsamples) #np.array(b1.vertices)
        
        temp5 = copy.deepcopy(temp1)
        temp6 = copy.deepcopy(np.flipud(temp3))
        
        temp = np.concatenate((temp5,temp6),axis=0)
        return [temp,arr_stop_yf]


    #Get a bunch of points sampled from the Bezier curve of a migration arrow.
    #These serve as the edges of continuous migration patches so that they line
    #up with the migration arrows.
    def get_Bezier_points(self, path, nSamples):
        P0 = path.vertices[0,:]
        P1 = path.vertices[1,:]
        P2 = path.vertices[2,:]
        ans = np.zeros((nSamples,2))
        for i in xrange(nSamples):
            t = i/nSamples
            ans[i,0] = (1-t)**2 * P0[0] + 2*t*(1-t)*P1[0] + t**2 * P2[0]
            ans[i,1] = (1-t)**2 * P0[1] + 2*t*(1-t)*P1[1] + t**2 * P2[1]
        return ans

    #Connect dragging rectangles with mouse events
    def connect(self):
        'connect to all the events we need'
        for popind in range(0,self.npops):
            for epind in range(0,len(self.ts[popind])):
                rect = self.rects[popind][epind]
                self.cidpress = rect.figure.canvas.mpl_connect(
                    'button_press_event', self.on_press)
                #    '<ButtonPress-1>', self.on_press)
                self.cidrelease = rect.figure.canvas.mpl_connect(
                    'button_release_event', self.on_release)
                #    '<ButtonRelease-1>', self.on_release)
                self.cidmotion = rect.figure.canvas.mpl_connect(
                    'motion_notify_event', self.on_motion)
                #    '<Motion>', self.on_motion)


    def on_press(self, event):        
        'on button press we will see if the mouse is over us and store some data'
        if event.inaxes != self.ax: return
        if self.lock is not None: return
        
        
        x0 = None
        y0 = None
        popind = None
        epind = None
        contained = False
        for i in range(0,self.npops):
            for j in range(0,len(self.ts[i])):
                contains, attrd = self.rects[i][j].contains(event)
                if contains:
                    popind = i
                    epind = j
                    contained = True
                    if event.key == 'd':
                        self.del_epoch = True
                    if event.key == 'e':
                        self.expmat = list(self.expmat)
                        for i in range(0,len(self.expmat)):
                            self.expmat[i] = list(self.expmat[i])
                        if self.expmat[popind][epind] is None:
                            self.expmat[popind][epind] = 0
                            self.gammas[popind][epind] = 0
                        elif self.expmat[popind][epind] == 0:
                            self.expmat[popind][epind] = None
                        self.update_histline(popind,epind)
                        #self.toggle_exp = True
                    if event.key == 'v': #Make popup window for user to enter precise values
                        (x,y) = self.demog_main.root.winfo_pointerxy()
                        if self.popup_window is None:
                            self.popup_window = popup_epoch_textfield(self.demog_main,popind,epind,x+20,y+20)                        
                            self.popup_window.toplevel.deiconify()
                            self.popup_window.toplevel.wait_window()
                        self.popup_window = None
                        self.popup_textbox_change = True
                        self.selected_ind = [popind,epind]
                        self.press = event.x, event.y, event.xdata, event.ydata
                        #self.demog_main.root.wait_window(popup_window.toplevel)
                        return
                        
        if not contained: #Not contained in an epoch rectangle, but might be in a migration rectangle
            for i in range(0,len(self.mig_drag_rects)):
                contains, attrd = self.mig_drag_rects[i].contains(event)
                if contains:
                    if self.migs[i][3] >= 0:
                        popind = self.migs[i][1].astype(int)-1
                    else:
                        popind = self.migs[i][2].astype(int)-1
                    self.selected_ind = [popind,None]
                    x0 = event.xdata
                    y0 = event.ydata
                    self.mig_drag_ind = i
                    if event.key == 'v': #Make popup window for user to enter precise values
                        self.popup_textbox_change = True
                        self.selected_ind = [popind,epind]
                        (x,y) = self.demog_main.root.winfo_pointerxy()
                        self.press = x, y, event.xdata, event.ydata                        
                        popup_window = popup_migration_textfield(self.demog_main,self.mig_drag_ind,x,y)
                        return
                        
            for i in range(0,len(self.mig_stren_rects)):
                contains, attrd = self.mig_stren_rects[i].contains(event)
                if contains:
                    if self.migs[i][3] >= 0:
                        from_popind = self.migs[i][1].astype(int)-1
                        to_popind = self.migs[i][2].astype(int)-1
                    else:
                        from_popind = self.migs[i][2].astype(int)-1
                        to_popind = self.migs[i][1].astype(int)-1
                    self.selected_ind = [from_popind,to_popind]
                    x0 = event.xdata
                    y0 = event.ydata
                    self.mig_stren_ind = i
                    if event.key == 'v': #Make popup window for user to enter precise values
                        self.popup_textbox_change = True
                        self.selected_ind = [popind,epind]
                        (x,y) = self.demog_main.root.winfo_pointerxy()
                        self.press = x, y, event.xdata, event.ydata
                        popup_window = popup_migration_textfield(self.demog_main,self.mig_stren_ind,x,y)
                        return
            if (self.mig_drag_ind is not None) and event.key == 'd': #Delete the migration event
                self.del_mig = True
                self.mig_drag_rects[self.mig_drag_ind].remove()
                self.mig_drag_circles[self.mig_drag_ind].remove()
                self.mig_stren_rects[self.mig_drag_ind].remove()
                self.mig_stren_circles[self.mig_drag_ind].remove()
                if self.migmaskgraphics[self.mig_drag_ind] is not None:
                    self.migmaskgraphics[self.mig_drag_ind].remove()
                self.miggraphics[self.mig_drag_ind].remove()
                if self.mig_dur_graphics[self.mig_drag_ind] is not None:
                    self.mig_dur_graphics[self.mig_drag_ind].remove()
                
                del self.mig_drag_rects[self.mig_drag_ind]
                del self.mig_drag_circles[self.mig_drag_ind]
                del self.mig_stren_rects[self.mig_drag_ind]
                del self.mig_stren_circles[self.mig_drag_ind]
                del self.migmaskgraphics[self.mig_drag_ind]
                del self.miggraphics[self.mig_drag_ind]
                del self.mig_dur_graphics[self.mig_drag_ind]
                
                self.migs = list(self.migs)                
                for i in range(0,len(self.migs)):
                    self.migs[i] = list(self.migs[i])                
                del self.migs[self.mig_drag_ind]
                self.migs = np.array(self.migs)
            if (self.mig_drag_ind is None) and (self.mig_stren_ind is None):
                if event.key == 'm': #New migration event 
                    new_mig_start_popind = None
                    for i in range(0,self.npops):
                        if (event.ydata <= self.popctrs[i] + self.maxnes[i]) and (event.ydata > self.popctrs[i] - self.maxnes[i]):
                            new_mig_start_popind = i
                    new_mig_ind = None
                    if len(self.migs) == 0:
                        new_mig_ind = 0
                    else:
                        migts = [0] * len(self.migs) #zeros(len(self.migs)) #np.zeros((1,len(self.migs)))
                        for j in range(0,len(self.migs)):
                            migts[j] = self.migs[j][0]
                        new_mig_ind = np.sum(np.array(migts) <= event.xdata)

                    self.selected_ind = [new_mig_start_popind,new_mig_ind]
                    x0 = event.xdata
                    y0 = event.ydata
                    self.new_mig = True

                    arr_color = [0.9290,0.6940,0.1250]
                    #self.ghost_line_patch = self.ax.add_patch(ptchs.Arrow(x0,y0, 0,0, width = 1, color = arr_color, edgecolor = 'none', alpha = 1.0, zorder = len(self.ax.patches) + 1))
                    arr_connect_style = 'arc3,rad=0'
                    arr_width_scale = 20
                    self.ghost_line_patch = self.ax.add_patch(ptchs.FancyArrowPatch(posA = (x0,y0), posB = (x0,y0), connectionstyle = arr_connect_style, mutation_scale = arr_width_scale, color = arr_color, edgecolor = 'none', alpha = 1.0, zorder = len(self.ax.patches) + 1))
                    
                    #print "Patch should be added >>>>>>>>>>>>>>>>>>>>>>>>"
                    #print self.ghost_line_patch
                    
                    #Tell observers we're about to move
                    for callback in self._observers:
                        callback[0]()            
                    
                    self.ghost_line_patch.set_animated(True)            
                    
                    self.fig.canvas.draw()
                    self.background = self.fig.canvas.copy_from_bbox(self.ax.bbox)
                    
                    #Redraw just the part of the history that moves
                    self.ax.draw_artist(self.ghost_line_patch)

                    #Blit the redrawn area
                    self.fig.canvas.blit(self.ax.bbox)
                    

            
                elif event.key == 'n':
                    popind = None
                    for i in range(0,self.npops):
                        if (event.ydata <= self.popctrs[i] + self.maxnes[i]) and (event.ydata > self.popctrs[i] - self.maxnes[i]):
                            popind = i
                    for j in range(0,len(self.ts[popind])):
                        if j < len(self.ts[popind])-1:
                            if (self.ts[popind][j] <= event.xdata) and (event.xdata < self.ts[popind][j+1]):
                                epind = j+1
                        elif j == len(self.ts[popind])-1:
                            if (self.ts[popind][j] <= event.xdata) and (event.xdata < self.maxt):
                                epind = j+1
                    self.selected_ind = [popind,epind]
                    x0 = event.xdata
                    if event.ydata >= self.popctrs[popind]:
                        y0 = event.ydata
                    else:
                        y0 = self.popctrs[popind] + (self.popctrs[popind] - event.ydata)
                    self.new_epoch = True
                else:
                    return        
        
        elif contained:
            self.selected_ind = [popind,epind]
            x0, y0 = self.rects[popind][epind].xy
        
        self.press = x0, y0, event.xdata, event.ydata
        self.lock = self
        
           
        if self.del_epoch: #Remove the epoch and all the graphics associated with it
            if epind > 0:
                self.ts = list(self.ts)
                for i in range(0,len(self.ts)):
                    self.ts[i] = list(self.ts[i])
                del self.ts[popind][epind]
                self.ts = np.array(self.ts)
                
                self.nus = list(self.nus)                
                for i in range(0,len(self.nus)):
                    self.nus[i] = list(self.nus[i])
                del self.nus[popind][epind]
                self.nus = np.array(self.nus)
                
                self.expmat = list(self.expmat)                
                if self.expmat[popind][epind-1] is None:
                    self.expmat[popind][epind-1] = 0;
                for i in range(0,len(self.expmat)):
                    self.expmat[i] = list(self.expmat[i])
                del self.expmat[popind][epind]
                self.expmat = np.array(self.expmat)
                
                self.gammas = list(self.gammas)                
                for i in range(0,len(self.gammas)):
                    self.gammas[i] = list(self.gammas[i])                
                del self.gammas[popind][epind]
                self.gammas = np.array(self.gammas)
                
                self.rects[popind][epind].remove()
                del self.rects[popind][epind]
                
                self.circles[popind][epind].remove()
                del self.circles[popind][epind]
                
                self.histlines[popind][epind].remove()
                del self.histlines[popind][epind]
                
        elif self.new_epoch: #Make a new epoch. Update all data structures            
            self.ts = list(self.ts)
            for i in range(0,len(self.ts)):
                self.ts[i] = list(self.ts[i])
            self.ts[popind].insert(epind,self.press[0])
            self.ts = np.array(self.ts)

            self.nus = list(self.nus)                
            for i in range(0,len(self.nus)):
                self.nus[i] = list(self.nus[i])
            self.nus[popind].insert(epind,self.press[1] - self.popctrs[popind])
            self.nus = np.array(self.nus)

            self.expmat = list(self.expmat)
            #if self.expmat[popind][epind-1] is None:
            #    self.expmat[popind][epind-1] = 0;
            for i in range(0,len(self.expmat)):
                self.expmat[i] = list(self.expmat[i])
            self.expmat[popind].insert(epind,0)
            self.expmat = np.array(self.expmat)

            self.gammas = [None] * len(self.expmat)
            for pop in range(0,len(self.expmat)):
                self.gammas[pop] = [None] * len(self.expmat[pop])
            
            for pop in range(0,len(self.gammas)):
                for ep in range(0,len(self.gammas[pop])):
                    if self.expmat[pop][ep] is None:
                        if ep < len(self.expmat[pop])-1:
                            Nf = self.nus[pop][ep]
                            No = self.nus[pop][ep+1]
                            t = self.ts[pop][ep]
                            self.gammas[pop][ep] = np.log(No/Nf)/t
                        else:
                            self.gammas[pop][ep] = 0
                    else:
                        self.gammas[pop][ep] = 0
            
            temp = self.ax.add_patch(ptchs.Rectangle((self.ts[popind][epind] - self.rect_xoffset,self.popctrs[popind]+self.nus[popind][epind] - self.rect_yoffset),self.rect_xdim,self.rect_ydim,alpha=0.5,facecolor='none',edgecolor='none'))
            self.rects[popind].insert(epind,temp)
            
            temp = self.ax.add_patch(ptchs.Ellipse((self.ts[popind][epind],self.popctrs[popind]+self.nus[popind][epind]),self.rect_xdim*2/3,self.rect_ydim*2/3,alpha=0.05,facecolor='black',edgecolor='none'))            
            self.circles[popind].insert(epind,temp)
            
            if epind < len(self.ts[popind])-1:
                plot_range = np.linspace(self.ts[popind][epind],self.ts[popind][epind+1],max(10,round((self.ts[popind][epind+1] - self.ts[popind][epind])/self.plotdt)))
            else:
                plot_range = np.linspace(self.ts[popind][epind],self.maxt,max(10,round((self.maxt - self.ts[popind][epind])/self.plotdt)))
                    
            tvals = plot_range-self.ts[popind][epind]
            upbd = self.popctrs[popind] + self.nus[popind][epind] * np.exp(self.gammas[popind][epind]*tvals)
            lowbd = self.popctrs[popind] - self.nus[popind][epind]*np.exp(self.gammas[popind][epind]*tvals)
            temp1 = np.transpose([plot_range,upbd])
            temp2 = np.transpose([plot_range,lowbd])
            temp3 = np.concatenate((temp1,np.flipud(temp2)),axis=0)
            temp = self.ax.add_patch(ptchs.Polygon(temp3,facecolor='blue',alpha=0.15,edgecolor='none'))
            self.histlines[popind].insert(epind,temp)
            
            #self.animate_canvas()
            #self.redraw_canvas()
            #self.fig.canvas.blit(self.ax.bbox)
            #self.unanimate_canvas()
            
            if epind > 0:
                self.update_histline(popind, epind-1)
            
            
            
            
        if (self.new_mig is None):
            #Tell observers we're about to move
            for callback in self._observers:
                callback[0]()            
                                        
            #Draw everything but the data for the epochs adjacent to the selected node
            #if not (self.mig_drag_ind is None):
            for i in range(0,len(self.mig_drag_rects)):
                self.mig_drag_rects[i].set_animated(True)            
                self.mig_drag_circles[i].set_animated(True)
                self.mig_stren_rects[i].set_animated(True)
                self.mig_stren_circles[i].set_animated(True)                
                
            if (self.mig_drag_ind is None) and (self.mig_stren_ind is None):
                if not self.del_epoch:
                    self.rects[popind][epind].set_animated(True)
                    self.circles[popind][epind].set_animated(True)
                    self.histlines[popind][epind].set_animated(True)
                    if epind > 0:
                        self.rects[popind][epind-1].set_animated(True)
                        self.circles[popind][epind-1].set_animated(True)            
                        self.histlines[popind][epind-1].set_animated(True)
                else:
                    self.rects[popind][epind-1].set_animated(True)
                    self.circles[popind][epind-1].set_animated(True)            
                    self.histlines[popind][epind-1].set_animated(True)
            
            for i in range(0,len(self.miggraphics)):
                self.miggraphics[i].set_animated(True)
            
            for i in range(0,len(self.mig_dur_graphics)):
                if self.mig_dur_graphics[i] is not None:
                    self.mig_dur_graphics[i].set_animated(True)
            
            for i in range(0,len(self.migmaskgraphics)):
                if not (self.migmaskgraphics[i] is None):
                    self.migmaskgraphics[i].set_animated(True)
    
            self.fig.canvas.draw()
            self.background = self.fig.canvas.copy_from_bbox(self.ax.bbox)
            
            #Redraw just the part of the history that moves
            #if not (self.mig_drag_ind is None):
            for i in range(0,len(self.mig_drag_rects)):
                self.ax.draw_artist(self.mig_drag_rects[i])
                self.ax.draw_artist(self.mig_drag_circles[i])
                self.ax.draw_artist(self.mig_stren_circles[i])
                self.ax.draw_artist(self.mig_stren_circles[i])
            if (self.mig_drag_ind is None) and (self.mig_stren_ind is None):
                if not self.del_epoch:
                    self.ax.draw_artist(self.rects[popind][epind])
                    self.ax.draw_artist(self.circles[popind][epind])
                    self.ax.draw_artist(self.histlines[popind][epind])
                    if epind > 0:
                        self.ax.draw_artist(self.rects[popind][epind-1])
                        self.ax.draw_artist(self.circles[popind][epind-1])
                        self.ax.draw_artist(self.histlines[popind][epind-1])
                else:
                    self.ax.draw_artist(self.rects[popind][epind-1])
                    self.ax.draw_artist(self.circles[popind][epind-1])
                    self.ax.draw_artist(self.histlines[popind][epind-1])
    
            for i in range(0,len(self.migmaskgraphics)):
                if not (self.migmaskgraphics[i] is None):
                    self.ax.draw_artist(self.migmaskgraphics[i])
                    
            for i in range(0,len(self.miggraphics)):
                self.ax.draw_artist(self.miggraphics[i])
            
            for i in range(0,len(self.mig_dur_graphics)):
                if self.mig_dur_graphics[i] is not None:
                    self.ax.draw_artist(self.mig_dur_graphics[i])
    
            self.new_epoch = False
                            
            #Blit the redrawn area
            self.fig.canvas.blit(self.ax.bbox)
            #print "DONE on_press >>>>>>>>>>>> LINE 1843"

            

    def on_motion(self, event):
        'on motion we will move the rect if the mouse is over us'
        if self.popup_textbox_change is not False: return
        if self.lock is not self: return
        if self.selected_ind is None: return
        if event.inaxes != self.ax: return

        x0, y0, xpress, ypress = self.press
        dx = event.xdata - xpress
        dy = event.ydata - ypress

        if self.new_mig is None:
            popind = self.selected_ind[0]
            epind = self.selected_ind[1]
    
            if (self.mig_drag_ind is not None) and (self.del_mig == False):
                newy = min(max(self.popctrs[popind],y0+self.rect_yoffset+dy),self.popctrs[popind]+self.maxnes[popind])
                newrecty = min(max(self.popctrs[popind],y0+dy),self.popctrs[popind]+self.maxnes[popind])
                newx = min(max(0,x0+self.rect_xoffset+dx),self.maxt)
                newrectx = min(max(0,x0+dx),self.maxt)
                
                duration = self.migs[self.mig_drag_ind][4]
                
                patch_coords = None
                arr_stop_yf = None
                
                
                if duration > 0:
                    [patch_coords,arr_stop_yf] = self.get_cts_mig_patch(self.migs[self.mig_drag_ind])
                    if self.mig_dur_graphics[self.mig_drag_ind] is not None:
                        self.mig_dur_graphics[self.mig_drag_ind].remove()
                    arr_color = [0.9290,0.6940,0.1250]
                    self.mig_dur_graphics[self.mig_drag_ind] = self.ax.add_patch(ptchs.Polygon(patch_coords,facecolor=arr_color, alpha=0.15, edgecolor='none'))
                
                self.migs[self.mig_drag_ind][0] = newx
                self.mig_drag_rects[self.mig_drag_ind].set_x(newrectx)
                self.mig_drag_circles[self.mig_drag_ind].center = (newrectx+self.rect_xoffset,y0+self.rect_yoffset)
                self.mig_stren_rects[self.mig_drag_ind].set_x(newrectx)
                y_tmp = self.mig_stren_circles[self.mig_drag_ind].center[1]
                self.mig_stren_circles[self.mig_drag_ind].center = (newrectx,y_tmp)
                
                arr_posA = [newx, y0]
                arr_posB = None            
                self.miggraphics[self.mig_drag_ind].set_positions(arr_posA, arr_posB)
                
                if self.migmaskgraphics[self.mig_drag_ind] is not None:
                    self.migmaskgraphics[self.mig_drag_ind].set_x(newx)
                    self.migmaskgraphics[self.mig_drag_ind].set_width(self.maxt - newx)
            elif self.mig_stren_ind is not None:
                temp = np.array(self.miggraphics[self.mig_stren_ind].get_path().vertices)                
     
                xs = temp[:,0]
                ys = temp[:,1]
                
                y_lbd = min(ys)
                y_ubd = max(ys)
                x_lbd = min(xs)
                x_ubd = max(xs)
                
                #temp = self.miggraphics[self.mig_stren_ind].get_extents().get_points()
                #x_lbd = temp[0][0]
                #y_lbd = temp[0][1]
                #x_ubd = temp[1][0]
                #y_ubd = temp[1][1]
                
                duration = max(0,x0+dx-self.migs[self.mig_stren_ind][0])
                x_loc = self.migs[self.mig_stren_ind][0]
                
                if duration > 0:
                    self.miggraphics[self.mig_stren_ind].set_connectionstyle('Arc3,rad=0')
                else:
                    if self.migs[self.mig_stren_ind][3] > 0:
                        if self.migs[self.mig_stren_ind][2] - self.migs[self.mig_stren_ind][1] > 1:
                            self.miggraphics[self.mig_stren_ind].set_connectionstyle('Arc3,rad=0.1')
                        elif self.migs[self.mig_stren_ind][1] - self.migs[self.mig_stren_ind][2] > 1:
                            self.miggraphics[self.mig_stren_ind].set_connectionstyle('Arc3,rad=-0.1')

                y_start = None
                y_stop = None
                if self.migs[self.mig_stren_ind][1] < self.migs[self.mig_stren_ind][2]:
                    if self.migs[self.mig_stren_ind][3] >= 0:
                        y_start = y_lbd
                        y_stop = y_ubd
                    else:
                        y_start = y_ubd
                        y_stop = y_lbd
                else:
                    if self.migs[self.mig_stren_ind][3] >= 0:
                        y_start = y_ubd
                        y_stop = y_lbd
                    else:
                        y_start = y_lbd
                        y_stop = y_ubd


                patch_coords = None
                arr_stop_yf = None
                if duration > 0:
                    [patch_coords,arr_stop_yf] = self.get_cts_mig_patch(self.migs[self.mig_stren_ind])
                    if self.mig_dur_graphics[self.mig_stren_ind] is not None:
                        self.mig_dur_graphics[self.mig_stren_ind].remove()
                        self.mig_dur_graphics[self.mig_stren_ind] = None
                    arr_color = [0.9290,0.6940,0.1250]
                    self.mig_dur_graphics[self.mig_stren_ind] = self.ax.add_patch(ptchs.Polygon(patch_coords,facecolor=arr_color, alpha=0.15, edgecolor='none'))                                
                else:
                    if self.mig_dur_graphics[self.mig_stren_ind] is not None:
                        self.mig_dur_graphics[self.mig_stren_ind].remove()
                        self.mig_dur_graphics[self.mig_stren_ind] = None

                newy = min(max(y0 + dy,y_lbd),y_ubd)
                newrecty = newy + self.rect_yoffset
                newx = x_loc
                newrectx = x_loc + self.rect_xoffset
                
                self.mig_stren_rects[self.mig_stren_ind].set_y(newrecty)
                y_tmp = self.mig_stren_circles[self.mig_stren_ind].center[1]
                self.mig_stren_circles[self.mig_stren_ind].center = (newx,newy)
                
                #arr_posA = [newx, y0]
                #arr_posB = None            
                #self.miggraphics[self.mig_drag_ind].set_positions(arr_posA, arr_posB)
                
                mig_stren = abs(newy - y_start)/(y_ubd - y_lbd)
                
                transp = max(0.1,abs(self.migs[self.mig_stren_ind][3]))
                linst = '-'
                arr_width_scale = 20
                if abs(self.migs[self.mig_stren_ind][3]) == 0:
                    linst = '--'
                    arr_width_scale = 1
                
                self.miggraphics[self.mig_stren_ind].set_alpha(transp)
                self.miggraphics[self.mig_stren_ind].set_linestyle(linst)
                self.miggraphics[self.mig_stren_ind].set_mutation_scale(arr_width_scale)
                
                if self.migs[self.mig_stren_ind][3] >= 0:
                    self.migs[self.mig_stren_ind][3] = mig_stren
                else:
                    self.migs[self.mig_stren_ind][3] = -mig_stren
                
                self.migs[self.mig_stren_ind][4] = duration
                    
                #[patch_coords,arr_stop_yf] = self.get_cts_mig_patch(self.migs[self.mig_stren_ind]) 
                
            elif (self.mig_drag_ind is None) and (self.mig_stren_ind is None):
                if not self.del_epoch:
                    newy = min(max(self.popctrs[popind],y0+self.rect_yoffset+dy),self.popctrs[popind]+self.maxnes[popind])
                    newrecty = min(max(self.popctrs[popind],y0+dy),self.popctrs[popind]+self.maxnes[popind])
                    #newy = min(max(self.popctrs[popind],y0+dy),self.popctrs[popind]+self.maxnes[popind])
                    self.nus[popind][epind] = newy - self.popctrs[popind]
                    if ((epind > 0) and (epind < (len(self.ts[popind])-1))):
                        newx = min(max(self.ts[popind][epind-1],x0+self.rect_xoffset+dx),self.ts[popind][epind+1])
                        newrectx = min(max(self.ts[popind][epind-1],x0+dx),self.ts[popind][epind+1])
                        #newx = min(max(self.ts[popind][epind-1],x0+dx),self.ts[popind][epind+1])
                    elif epind == 0:
                        newx = 0
                        newrectx = 0-self.rect_xoffset
                        #newx = 0
                    elif epind == len(self.ts[popind])-1:
                        newx = max(min(x0+self.rect_xoffset+dx,self.maxt),self.ts[popind][epind-1])
                        newrectx = max(min(x0+dx,self.maxt),self.ts[popind][epind-1])
                        #newx = max(min(x0+dx,self.maxt),self.ts[popind][epind-1])
                        
                    self.ts[popind][epind] = newx
                
                    self.update_histline(popind, epind)
                    if epind > 0:
                        self.update_histline(popind, epind-1)
                
                    self.rects[self.selected_ind[0]][self.selected_ind[1]].set_x(newrectx)
                    self.rects[self.selected_ind[0]][self.selected_ind[1]].set_y(newrecty)
                
                    self.circles[self.selected_ind[0]][self.selected_ind[1]].center = (newrectx+self.rect_xoffset,newrecty+self.rect_yoffset)
                else:
                    self.update_histline(popind, epind-1)
    
                self.update_cts_mig_graphics()
            
            self.update_mig_graphics()
            
            #Update each observer by passing the history to the observer
            for callback in self._observers:
                callback[1]()
            
            #Restore the background region
            self.fig.canvas.restore_region(self.background)
    
            #Redraw the current shapes only
            if (self.mig_drag_ind is not None) and (self.del_mig == False):
                self.ax.draw_artist(self.mig_drag_rects[self.mig_drag_ind])
                self.ax.draw_artist(self.mig_drag_circles[self.mig_drag_ind])
                self.ax.draw_artist(self.mig_stren_rects[self.mig_drag_ind])
                self.ax.draw_artist(self.mig_stren_circles[self.mig_drag_ind])
            elif (self.mig_drag_ind is None) and (self.mig_stren_ind is None):           
                if not self.del_epoch:
                    self.ax.draw_artist(self.rects[popind][epind])
                    self.ax.draw_artist(self.circles[popind][epind])
                    self.ax.draw_artist(self.histlines[popind][epind])
                    if epind > 0:
                        self.ax.draw_artist(self.rects[popind][epind-1])
                        self.ax.draw_artist(self.circles[popind][epind-1])
                        self.ax.draw_artist(self.histlines[popind][epind-1])
                else:
                    self.ax.draw_artist(self.rects[popind][epind-1])
                    self.ax.draw_artist(self.circles[popind][epind-1])
                    self.ax.draw_artist(self.histlines[popind][epind-1])
    
    
            for i in range(0,len(self.migmaskgraphics)):
                if not (self.migmaskgraphics[i] is None):
                    self.ax.draw_artist(self.migmaskgraphics[i])
                                                                    
            for i in range(0,len(self.miggraphics)):
                self.ax.draw_artist(self.miggraphics[i])
            
            for i in range(0,len(self.mig_dur_graphics)):
                if self.mig_dur_graphics[i] is not None:
                    self.ax.draw_artist(self.mig_dur_graphics[i])
                                
            #Blit only the redrawn area
            self.fig.canvas.blit(self.ax.bbox)
            #print "on_press done >>>>>>>>>>>> LINE 1982"
        else: #We're just drawing a new migration arrow
            
            #Update each observer by passing the history to the observer
            for callback in self._observers:
                callback[1]()
            
            #Restore the background region
            self.fig.canvas.restore_region(self.background)
    
            #Redraw the current shapes only
            self.ghost_line_patch.set_positions(None, (x0,y0+dy))
            self.ax.draw_artist(self.ghost_line_patch)
            
            #print "Patch move >>>>>>>>>>>>>>>>>>>>>>>>"
            #print self.ghost_line_patch
                                            
            #Blit only the redrawn area
            self.fig.canvas.blit(self.ax.bbox)
            
            


    def on_release(self, event):
        'on release we reset the press data'
        if self.popup_textbox_change == True:
            self.selected_ind = None
            self.press = None
            self.popup_textbox_change = False
            return
        if self.lock is not self: return
        
        if self.new_mig is None:
            #print "on_release new mig false >>>>>>>>>>>> LINE 1990"
            popind = self.selected_ind[0]
            epind = self.selected_ind[1]
            
            if self.mig_stren_ind is not None:
                if abs(self.migs[self.mig_stren_ind][3]) < 1:
                    if self.migmaskgraphics[self.mig_stren_ind] is not None:
                        self.migmaskgraphics[self.mig_stren_ind].set_animated(False)
                        self.migmaskgraphics[self.mig_stren_ind].remove()
                        self.migmaskgraphics[self.mig_stren_ind] = None
                elif abs(self.migs[self.mig_stren_ind][3]) == 1:
                    if self.migmaskgraphics[self.mig_stren_ind] is None:
                        mask = None
                        if self.migs[self.mig_stren_ind][3] == 1:
                            mask = self.ax.add_patch(ptchs.Rectangle((self.migs[self.mig_stren_ind][0],self.popctrs[self.migs[self.mig_stren_ind][1].astype(int)-1] - self.maxnes[self.migs[self.mig_stren_ind][1].astype(int)-1]),self.maxt-self.migs[self.mig_stren_ind][0],2*self.maxnes[self.migs[self.mig_stren_ind][1].astype(int)-1],alpha=self.migs[self.mig_stren_ind][3],facecolor='white',edgecolor='none',zorder = len(self.ax.patches)))
                        elif self.migs[self.mig_stren_ind][3] == -1:
                            mask = self.ax.add_patch(ptchs.Rectangle((self.migs[self.mig_stren_ind][0],self.popctrs[self.migs[self.mig_stren_ind][2].astype(int)-1] - self.maxnes[self.migs[self.mig_stren_ind][2].astype(int)-1]),self.maxt-self.migs[self.mig_stren_ind][0],2*self.maxnes[self.migs[self.mig_stren_ind][2].astype(int)-1],alpha=-self.migs[self.mig_stren_ind][3],facecolor='white',edgecolor='none',zorder = len(self.ax.patches)))            
                        self.migmaskgraphics[self.mig_stren_ind] = mask
                for i in range(0,len(self.miggraphics)):
                    self.miggraphics[i].set_zorder(len(self.ax.patches)+1)                    
    
            #Redraw the current shapes only
            #if not (self.mig_drag_ind is None):
            for i in range(0,len(self.mig_drag_rects)):
                self.ax.draw_artist(self.mig_drag_rects[i])
                self.ax.draw_artist(self.mig_drag_circles[i])
                self.ax.draw_artist(self.mig_stren_rects[i])
                self.ax.draw_artist(self.mig_stren_circles[i])            
                
            if (self.mig_drag_ind is None) and (self.mig_stren_ind is None):
                if not self.del_epoch:
                    self.ax.draw_artist(self.histlines[popind][epind])
                    if epind > 0:
                        self.ax.draw_artist(self.histlines[popind][epind-1])
                else:
                    self.ax.draw_artist(self.histlines[popind][epind-1])
    
            for i in range(0,len(self.migmaskgraphics)):
                if not (self.migmaskgraphics[i] is None):
                    self.ax.draw_artist(self.migmaskgraphics[i])
                
            #Redraw the current shapes only
            if (self.mig_drag_ind is None) and (self.mig_stren_ind is None):
                if (not self.del_epoch):
                    self.ax.draw_artist(self.rects[popind][epind])
                    self.ax.draw_artist(self.circles[popind][epind])
                    if epind > 0:
                        self.ax.draw_artist(self.rects[popind][epind-1])
                        self.ax.draw_artist(self.circles[popind][epind-1])
                else:
                    self.ax.draw_artist(self.rects[popind][epind-1])
                    self.ax.draw_artist(self.circles[popind][epind-1])   
                    
            for i in range(0,len(self.miggraphics)):
                self.ax.draw_artist(self.miggraphics[i])
            
            for i in range(0,len(self.mig_dur_graphics)):
                if self.mig_dur_graphics[i] is not None:
                    self.ax.draw_artist(self.mig_dur_graphics[i])
                            
            #Turn off animation and reset background
            #if not (self.mig_drag_ind is None):
            for i in range(0,len(self.mig_drag_rects)):
                self.mig_drag_rects[i].set_animated(False)
                self.mig_drag_circles[i].set_animated(False)
                self.mig_stren_rects[i].set_animated(False)
                self.mig_stren_circles[i].set_animated(False)
            if (self.mig_drag_ind is None) and (self.mig_stren_ind is None):
                if not self.del_epoch:
                    self.rects[popind][epind].set_animated(False)
                    self.circles[popind][epind].set_animated(False)
                    self.histlines[popind][epind].set_animated(False)
                    if epind > 0:
                        self.rects[popind][epind-1].set_animated(False)
                        self.circles[popind][epind-1].set_animated(False)
                        self.histlines[popind][epind-1].set_animated(False)
                else:
                    self.rects[popind][epind-1].set_animated(False)
                    self.circles[popind][epind-1].set_animated(False)
                    self.histlines[popind][epind-1].set_animated(False)
    
            for i in range(0,len(self.migmaskgraphics)):
                if not (self.migmaskgraphics[i] is None):
                    self.migmaskgraphics[i].set_animated(False)            
                                        
            for i in range(0,len(self.miggraphics)):
                self.miggraphics[i].set_animated(False)
                
            for i in range(0,len(self.mig_dur_graphics)):
                if self.mig_dur_graphics[i] is not None:
                    self.mig_dur_graphics[i].set_animated(False)
                                    
            self.background = None           
            
            self.mig_drag_ind = None
            self.mig_stren_ind = None
            self.lock = None        
            self.selected_ind = None
            self.press = None
            
            #Tell observers we're done moving
            for callback in self._observers:
                callback[2]()        
            
            self.del_epoch = False
            self.del_mig = False
                    
            #Redraw the full figure
            self.fig.canvas.draw()
        elif self.new_mig is not None:            
            #Delete the ghost line
            self.ghost_line_patch.set_animated(False)
            self.ghost_line_patch.remove()
            self.ghost_line_patch = None            
            
            new_mig_stop_popind = None
            for i in range(0,self.npops):
                if (event.ydata <= self.popctrs[i] + self.maxnes[i]) and (event.ydata > self.popctrs[i] - self.maxnes[i]):
                    new_mig_stop_popind = i
            if new_mig_stop_popind == None:
                return
                
            new_mig_start_popind = self.selected_ind[0]
            if new_mig_start_popind == new_mig_stop_popind:
                return
            else:
                pop1ind = new_mig_start_popind
                pop2ind = new_mig_stop_popind            
                
                t0, y0, xpress, ypress = self.press
                new_mig_ind = self.selected_ind[1]
                
                self.migs = list(self.migs)
                for i in range(0,len(self.migs)):
                    self.migs[i] = list(self.migs[i])
                #print "NEW MIG START POPIND >>>>>>>>>>>>>>>>>"
                #print new_mig_start_popind
                #print "NEW MIG STOP POPIND >>>>>>>>>>>>>>>>>"
                #print new_mig_stop_popind                
                mig_obj = [t0,new_mig_start_popind+1,new_mig_stop_popind+1,1,0]
                #print "NEW MIG IND>>>>>>"
                #print new_mig_ind
                #print "del mig status>>>>>>"
                #print self.del_mig
                self.migs.insert(new_mig_ind,mig_obj)
                self.migs = np.array(self.migs)
                
                #print "MIGs >>>>>>>>>>>>>>>>>"
                #print self.migs
            
                                
                mask = self.ax.add_patch(ptchs.Rectangle((self.migs[new_mig_ind][0],self.popctrs[self.migs[new_mig_ind][1].astype(int)-1] - self.maxnes[self.migs[new_mig_ind][1].astype(int)-1]),self.maxt-self.migs[new_mig_ind][0],2*self.maxnes[self.migs[new_mig_ind][1].astype(int)-1],alpha=self.migs[new_mig_ind][3],facecolor='white',edgecolor='none', zorder = len(self.ax.patches)))
                
                
                self.migmaskgraphics.insert(new_mig_ind,mask)
                
                time = t0
                epind1 = np.sum(np.array(self.ts[pop1ind]) <= time) - 1
                epind2 = np.sum(np.array(self.ts[pop2ind]) <= time) - 1
                arr_start_x = time
                #arr_stop_x = time + duration           
                if pop1ind < pop2ind:
                    if self.migs[new_mig_ind][3] > 0:
                        arr_start_y = self.popctrs[pop1ind] + self.nus[pop1ind][epind1] * np.exp(self.gammas[pop1ind][epind1] * (time - self.ts[pop1ind][epind1]))
                        arr_stop_y = self.popctrs[pop2ind] - self.nus[pop2ind][epind2] * np.exp(self.gammas[pop2ind][epind2] * (time - self.ts[pop2ind][epind2]))
                    else:
                        arr_stop_y = self.popctrs[pop1ind] + self.nus[pop1ind][epind1] * np.exp(self.gammas[pop1ind][epind1] * (time - self.ts[pop1ind][epind1]))
                        arr_start_y = self.popctrs[pop2ind] - self.nus[pop2ind][epind2] * np.exp(self.gammas[pop2ind][epind2] * (time - self.ts[pop2ind][epind2]))
                elif pop1ind > pop2ind:
                    if self.migs[new_mig_ind][3] > 0:
                        arr_stop_y = self.popctrs[pop2ind] + self.nus[pop2ind][epind2] * np.exp(self.gammas[pop2ind][epind2] * (time - self.ts[pop2ind][epind2]))
                        arr_start_y = self.popctrs[pop1ind] - self.nus[pop1ind][epind1] * np.exp(self.gammas[pop1ind][epind1] * (time - self.ts[pop1ind][epind1]))
                    else:
                        arr_start_y = self.popctrs[pop2ind] + self.nus[pop2ind][epind2] * np.exp(self.gammas[pop2ind][epind2] * (time - self.ts[pop2ind][epind2]))
                        arr_stop_y = self.popctrs[pop1ind] - self.nus[pop1ind][epind1] * np.exp(self.gammas[pop1ind][epind1] * (time - self.ts[pop1ind][epind1]))
                arr_width_scale = 20 
                arr_head_width = max(self.migs[new_mig_ind][4]*self.rect_xdim/2,self.rect_xdim/2)
                arr_head_len = self.rect_ydim/2
                arr_posA = [arr_start_x, arr_start_y]
                arr_posB = [arr_start_x, arr_start_y + (arr_stop_y - arr_start_y)]
                if np.abs(pop1ind - pop2ind) == 1:
                    arr_connect_style = 'arc3,rad=0'
                else:
                    if arr_start_y < arr_stop_y:
                        arr_connect_style = 'arc3,rad=0.1'
                    else:
                        arr_connect_style = 'arc3,rad=-0.1'
                arr_color = [0.9290,0.6940,0.1250]
                arr = self.ax.add_patch(ptchs.FancyArrowPatch(posA = arr_posA, posB = arr_posB, connectionstyle = arr_connect_style, mutation_scale = arr_width_scale, color = arr_color, edgecolor = 'none', alpha = 1.0, zorder = len(self.ax.patches) + 1))
                
                self.miggraphics.insert(new_mig_ind,arr)
                
                drag_rect_pos = [arr_start_x - self.rect_xdim/2,arr_start_y - self.rect_ydim/2]
                drag_rect = self.ax.add_patch(ptchs.Rectangle(tuple(drag_rect_pos),self.rect_xdim,self.rect_ydim,alpha=0.5,facecolor='none',edgecolor='none'))
                drag_circle = self.ax.add_patch(ptchs.Ellipse((arr_posA[0],arr_posA[1]),self.rect_xdim*2/3,self.rect_ydim*2/3,alpha=0.05,facecolor='black',edgecolor='none'))
                self.mig_drag_rects.insert(new_mig_ind,drag_rect)
                self.mig_drag_circles.insert(new_mig_ind,drag_circle)
                
                stren_rect_pos = [arr_start_x - self.rect_xdim/2,arr_stop_y - self.rect_ydim/2]
                stren_rect = self.ax.add_patch(ptchs.Rectangle(tuple(stren_rect_pos),self.rect_xdim,self.rect_ydim,alpha=0.5,facecolor='none',edgecolor='none'))
                stren_circle = self.ax.add_patch(ptchs.Ellipse((arr_posB[0],arr_posB[1]),self.rect_xdim*2/3,self.rect_ydim*2/3,alpha=0.05,facecolor='black',edgecolor='none'))
                self.mig_stren_rects.insert(new_mig_ind,stren_rect)
                self.mig_stren_circles.insert(new_mig_ind,stren_circle)
                
                self.mig_dur_graphics.insert(new_mig_ind,None)
                
                #print "drag_rects >>>>>>>>>>>>>>>>>> LINE 2161"
                #print self.mig_drag_rects
                #print self.mig_drag_circles
                
                max_zorder = len(self.ax.patches)
                for i in range(0,len(self.miggraphics)):
                    self.miggraphics[i].zorder = max_zorder + 1
                    self.mig_drag_rects[i].zorder = max_zorder + 2
                    self.mig_drag_circles[i].zorder = max_zorder + 2
                    self.mig_stren_rects[i].zorder = max_zorder + 2
                    self.mig_stren_circles[i].zorder = max_zorder + 2
                
                self.background = None
                self.new_mig = None
                self.lock = None        
                self.selected_ind = None
                self.press = None
                
                
                #Redraw the full figure
                self.fig.canvas.draw()  
                
                #Tell observers we're done moving
                for callback in self._observers:
                    callback[2]()              
                

    def animate_canvas(self):
        #Draw everything but the data for the epochs adjacent to the selected node
        for i in range(0,len(self.mig_drag_rects)):
            self.mig_drag_rects[i].set_animated(True)            
            self.mig_drag_circles[i].set_animated(True)
            self.mig_stren_rects[i].set_animated(True)
            self.mig_stren_circles[i].set_animated(True)                
        
        for popind in range(0,len(self.nus)):
            for epind in range(0,len(self.nus[popind])):   
                self.rects[popind][epind].set_animated(True)
                self.circles[popind][epind].set_animated(True)
                self.histlines[popind][epind].set_animated(True)
                if epind > 0:
                    self.rects[popind][epind-1].set_animated(True)
                    self.circles[popind][epind-1].set_animated(True)            
                    self.histlines[popind][epind-1].set_animated(True)
        
        for i in range(0,len(self.miggraphics)):
            self.miggraphics[i].set_animated(True)
        
        for i in range(0,len(self.mig_dur_graphics)):
            if self.mig_dur_graphics[i] is not None:
                self.mig_dur_graphics[i].set_animated(True)
        
        for i in range(0,len(self.migmaskgraphics)):
            if not (self.migmaskgraphics[i] is None):
                self.migmaskgraphics[i].set_animated(True)

        #self.fig.canvas.draw()
        #self.background = self.fig.canvas.copy_from_bbox(self.ax.bbox)
        

    def redraw_canvas(self):
        for i in range(0,len(self.mig_drag_rects)):
            self.ax.draw_artist(self.mig_drag_rects[i])
            self.ax.draw_artist(self.mig_drag_circles[i])
            self.ax.draw_artist(self.mig_stren_rects[i])
            self.ax.draw_artist(self.mig_stren_circles[i])
            
        for popind in range(0,len(self.nus)):
            for epind in range(0,len(self.nus[popind])):
                self.ax.draw_artist(self.rects[popind][epind])
                self.ax.draw_artist(self.circles[popind][epind])
                self.ax.draw_artist(self.histlines[popind][epind])
                if epind > 0:
                    self.ax.draw_artist(self.rects[popind][epind-1])
                    self.ax.draw_artist(self.circles[popind][epind-1])
                    self.ax.draw_artist(self.histlines[popind][epind-1])

        for i in range(0,len(self.migmaskgraphics)):
            if not (self.migmaskgraphics[i] is None):
                self.ax.draw_artist(self.migmaskgraphics[i])
                                                                
        for i in range(0,len(self.miggraphics)):
            self.ax.draw_artist(self.miggraphics[i])
        
        for i in range(0,len(self.mig_dur_graphics)):
            if self.mig_dur_graphics[i] is not None:
                self.ax.draw_artist(self.mig_dur_graphics[i])
                                
    def unanimate_canvas(self):
        #Draw everything but the data for the epochs adjacent to the selected node
        for i in range(0,len(self.mig_drag_rects)):
            self.mig_drag_rects[i].set_animated(False)            
            self.mig_drag_circles[i].set_animated(False)
            self.mig_stren_rects[i].set_animated(False)
            self.mig_stren_circles[i].set_animated(False)                
        
        for popind in range(0,len(self.nus)):
            for epind in range(0,len(self.nus[popind])):   
                self.rects[popind][epind].set_animated(False)
                self.circles[popind][epind].set_animated(False)
                self.histlines[popind][epind].set_animated(False)
                if epind > 0:
                    self.rects[popind][epind-1].set_animated(False)
                    self.circles[popind][epind-1].set_animated(False)            
                    self.histlines[popind][epind-1].set_animated(False)
        
        for i in range(0,len(self.miggraphics)):
            self.miggraphics[i].set_animated(False)
        
        for i in range(0,len(self.mig_dur_graphics)):
            if self.mig_dur_graphics[i] is not None:
                self.mig_dur_graphics[i].set_animated(False)
        
        for i in range(0,len(self.migmaskgraphics)):
            if not (self.migmaskgraphics[i] is None):
                self.migmaskgraphics[i].set_animated(False)
                

    def disconnect(self):
        'disconnect all the stored connection ids'        
        for popind in range(0,self.npops):
            for epind in range(0,len(self.ts[popind])):
                rect = self.rects[popind][epind]
                rect.figure.canvas.mpl_disconnect(self.cidpress)
                rect.figure.canvas.mpl_disconnect(self.cidrelease)
                rect.figure.canvas.mpl_disconnect(self.cidmotion)


    #Bind an observer and retrun a unique index we can use to reference it             
    def bind_observer(self, callback):
        newcounter = self._observer_counter+1
        self._observers.append(callback)
        self._observer_dictionary.append(newcounter)
        return newcounter
    
    #Remove an observer when the observer tells us our services are no longer required
    def remove_observer(self, observer_index):
        ind = self._observer_dictionary.index(observer_index) #Find the position in the list of the observer with the given index
        self._observers.pop(ind)
        self._observer_dictionary.pop(ind)

    #Update continuous migration graphics
    def update_cts_mig_graphics(self):
        #Update the continuous migration events near this change
        for i in range(0,len(self.migs)): #Scan over migration events
                if self.migs[i][4] > 0: #Then update the continuous migration event                            
                    if self.mig_dur_graphics[i] is not None:
                        [patch_coords,arr_stop_yf] = self.get_cts_mig_patch(self.migs[i])
                        self.mig_dur_graphics[i].remove()
                        self.mig_dur_graphics[i] = None
                        arr_color = [0.9290,0.6940,0.1250]
                        self.mig_dur_graphics[i] = self.ax.add_patch(ptchs.Polygon(patch_coords,facecolor=arr_color, alpha=0.15, edgecolor='none'))
                    else:
                        [patch_coords,arr_stop_yf] = self.get_cts_mig_patch(self.migs[i])
                        arr_color = [0.9290,0.6940,0.1250]
                        self.mig_dur_graphics[i] = self.ax.add_patch(ptchs.Polygon(patch_coords,facecolor=arr_color, alpha=0.15, edgecolor='none'))
                elif self.migs[i][4] == 0:
                    if self.mig_dur_graphics[i] is not None:
                        self.mig_dur_graphics[i].remove()
                        self.mig_dur_graphics[i] = None

        #Rearrange patches so that they're in the right order on top of each other
        max_zorder = len(self.ax.patches)
        for i in range(0,len(self.miggraphics)):
            self.miggraphics[i].zorder = max_zorder + 1
            self.mig_drag_rects[i].zorder = max_zorder + 2
            self.mig_drag_circles[i].zorder = max_zorder + 2
            self.mig_stren_rects[i].zorder = max_zorder + 2
            self.mig_stren_circles[i].zorder = max_zorder + 2


    #Update migration graphics
    def update_mig_graphics(self):                                
        for i in range(0,len(self.miggraphics)):
            time = self.migs[i][0]
            pop1ind = self.migs[i][1].astype(int)-1
            pop2ind = self.migs[i][2].astype(int)-1           
            epind1 = np.sum(np.array(self.ts[pop1ind]) <= time) - 1
            epind2 = np.sum(np.array(self.ts[pop2ind]) <= time) - 1
            arr_start_x = time
            if pop1ind < pop2ind:
                if self.migs[i][3] > 0:
                    arr_start_y = self.popctrs[pop1ind] + self.nus[pop1ind][epind1] * np.exp(self.gammas[pop1ind][epind1] * (time - self.ts[pop1ind][epind1]))
                    arr_stop_y = self.popctrs[pop2ind] - self.nus[pop2ind][epind2] * np.exp(self.gammas[pop2ind][epind2] * (time - self.ts[pop2ind][epind2]))
                else:
                    arr_stop_y = self.popctrs[pop1ind] + self.nus[pop1ind][epind1] * np.exp(self.gammas[pop1ind][epind1] * (time - self.ts[pop1ind][epind1]))
                    arr_start_y = self.popctrs[pop2ind] - self.nus[pop2ind][epind2] * np.exp(self.gammas[pop2ind][epind2] * (time - self.ts[pop2ind][epind2]))
            elif pop1ind > pop2ind:
                if self.migs[i][3] > 0:
                    arr_stop_y = self.popctrs[pop2ind] + self.nus[pop2ind][epind2] * np.exp(self.gammas[pop2ind][epind2] * (time - self.ts[pop2ind][epind2]))
                    arr_start_y = self.popctrs[pop1ind] - self.nus[pop1ind][epind1] * np.exp(self.gammas[pop1ind][epind1] * (time - self.ts[pop1ind][epind1]))
                else:
                    arr_start_y = self.popctrs[pop2ind] + self.nus[pop2ind][epind2] * np.exp(self.gammas[pop2ind][epind2] * (time - self.ts[pop2ind][epind2]))
                    arr_stop_y = self.popctrs[pop1ind] - self.nus[pop1ind][epind1] * np.exp(self.gammas[pop1ind][epind1] * (time - self.ts[pop1ind][epind1]))
            arr_posA = [arr_start_x, arr_start_y]
            arr_posB = [arr_start_x, arr_start_y + (arr_stop_y - arr_start_y)]
            self.miggraphics[i].set_positions(arr_posA, arr_posB)
            transp = max(0.1,abs(self.migs[i][3]))
            self.miggraphics[i].set_alpha(transp)
            self.mig_drag_rects[i].set_x(arr_start_x-self.rect_xoffset)
            self.mig_drag_rects[i].set_y(arr_start_y-self.rect_yoffset)
            self.mig_drag_circles[i].center = (arr_start_x,arr_start_y)
            self.mig_stren_rects[i].set_x(arr_start_x-self.rect_xoffset)
            self.mig_stren_rects[i].set_y(arr_stop_y-self.rect_yoffset)
            self.mig_stren_circles[i].center = (arr_start_x,arr_stop_y)
            if abs(self.migs[i][3]) == 0:
                linst = '--'
                arr_width_scale = 1
            else:
                linst = '-'
                arr_width_scale = 20
            self.miggraphics[i].set_linestyle(linst)
            self.miggraphics[i].set_mutation_scale(arr_width_scale)
            
            #Update mig mask graphics
            if abs(self.migs[i][3]) < 1:
                if self.migmaskgraphics[i] is not None:
                    self.migmaskgraphics[i].set_animated(False)
                    self.migmaskgraphics[i].remove()
                    self.migmaskgraphics[i] = None
            elif abs(self.migs[i][3]) == 1:
                if self.migmaskgraphics[i] is None:
                    if self.migs[i][3] == 1:
                        mask = self.ax.add_patch(ptchs.Rectangle((self.migs[i][0],self.popctrs[self.migs[i][1].astype(int)-1] - self.maxnes[self.migs[i][1].astype(int)-1]),self.maxt-self.migs[i][0],2*self.maxnes[self.migs[i][1].astype(int)-1],alpha=self.migs[i][3],facecolor='white',edgecolor='none',zorder = len(self.ax.patches)))
                    elif self.migs[i][3] == -1:
                        mask = self.ax.add_patch(ptchs.Rectangle((self.migs[i][0],self.popctrs[self.migs[i][2].astype(int)-1] - self.maxnes[self.migs[i][2].astype(int)-1]),self.maxt-self.migs[i][0],2*self.maxnes[self.migs[i][2].astype(int)-1],alpha=-self.migs[i][3],facecolor='white',edgecolor='none',zorder = len(self.ax.patches)))            
                    self.migmaskgraphics[i] = mask
            
            if self.migmaskgraphics[i] is not None:
                self.migmaskgraphics[i].set_x(arr_start_x)
                self.migmaskgraphics[i].set_width(self.maxt - arr_start_x)

        #Rearrange patches so that they're in the right order on top of each other                    
        max_zorder = len(self.ax.patches)
        for i in range(0,len(self.miggraphics)):
            self.miggraphics[i].zorder = max_zorder + 1
            self.mig_drag_rects[i].zorder = max_zorder + 2
            self.mig_drag_circles[i].zorder = max_zorder + 2
            self.mig_stren_rects[i].zorder = max_zorder + 2
            self.mig_stren_circles[i].zorder = max_zorder + 2


    def update_rects_circles(self,popind,epind):
        newnu = self.demog_main.hist.nus[popind][epind]
        newt = self.demog_main.hist.ts[popind][epind]
        newx = newt
        newy = self.popctrs[popind] + newnu
        self.rects[popind][epind].set_x(newx - self.rect_xoffset)
        self.rects[popind][epind].set_y(newy - self.rect_yoffset)
        self.circles[popind][epind].center = (newx,newy)


    #Update the history object to reflect the new rectangle positions
    def update_histline(self, popind, epind):
        if epind < len(self.histlines[popind])-1:
            plot_range = np.linspace(self.ts[popind][epind],self.ts[popind][epind+1],max(10,round((self.ts[popind][epind+1] - self.ts[popind][epind])/self.plotdt)))
            if self.expmat[popind][epind] is None:             
                Nf = self.nus[popind][epind]
                No = self.nus[popind][epind+1]
                t = self.ts[popind][epind+1] - self.ts[popind][epind]
                self.gammas[popind][epind] = np.log(No/Nf)/t
        else:
            plot_range = np.linspace(self.ts[popind][epind],self.maxt,max(10,round((self.maxt - self.ts[popind][epind])/self.plotdt)))
    
        tvals = plot_range-self.ts[popind][epind]            
        upbd = self.popctrs[popind] + self.nus[popind][epind]*np.exp(self.gammas[popind][epind]*tvals)
        lowbd = self.popctrs[popind] - self.nus[popind][epind]*np.exp(self.gammas[popind][epind]*tvals)
        temp1 = np.transpose([plot_range,upbd])
        temp2 = np.transpose([plot_range,lowbd])
        temp3 = np.concatenate((temp1,np.flipud(temp2)),axis=0)
        self.histlines[popind][epind].set_xy(temp3)



class JUSFSvisualizationHeatmap: #Assumes npops > 1 (otherwise you should plot a line plot using JUSFSvisualization)
    def __init__(self, hist, nentries, ns, tubd = 20, jsfstoplot = None, Ent_sum_nmax = 10, get_JSFS = True, jsfs_to_plot = None): #Try to implement this without including the statistic to compute... you can include it later
        self.fig = plt.figure(facecolor = 'white')
        self.ax = self.fig.add_subplot(111)
        self.ax.cla()
        
        self.hist = hist
        self.nentries = nentries
        self.nuref = 1
        self.ns = ns
        self.tubd = tubd
        self.Ent_sum_nmax = Ent_sum_nmax
        self.get_JSFS = get_JSFS
        self.which_pops = np.where(np.array(ns) > 0)[0]
        if len(self.which_pops) > 2:
            self.which_pops = self.which_pops[0:1]
        self.approx_jsfs_to_plot = None
        self.approx_jsfs_plot_object = None
                        
        self.jsfs = JUSFSprecise(self.hist, self.nentries, self.nuref, self.ns, self.tubd, self.Ent_sum_nmax, self.get_JSFS)

        #Assume npops is bigger than 1 (otherwise we plot a line plot using JUSFSvisualization)
        self.slice_obj = [None] * self.hist.npops
        self.slice_obj[self.which_pops[0]] = slice(0,self.nentries[self.which_pops[0]]+1)
        self.slice_obj[self.which_pops[1]] = slice(0,self.nentries[self.which_pops[1]]+1)
        for i in range(0,len(self.slice_obj)):
            if self.slice_obj[i] is None:
                self.slice_obj[i] = 0
        #self.approx_jsfs_to_plot = np.array(self.jsfs.JSFS.tolist(),dtype=np.float64)[self.slice_obj]
        #print self.slice_obj
        self.approx_jsfs_to_plot = self.jsfs.JSFS[self.slice_obj]
        self.approx_jsfs_to_plot[0][0] = None

        self.ny = self.nentries[self.which_pops[0]]+1
        self.nx = self.nentries[self.which_pops[1]]+1
        #self.rects = [None] * self.nx
        #self.rects = [self.rects] * self.ny
        
        #self.cmap = matplotlib.cm.get_cmap('Spectral')
        #for i in range(0,self.ny):
        #    for j in range(0,self.nx):
        #        color = self.cmap(self.approx_jsfs_to_plot[i][j])[0:3]
        #        self.rects[i][j] = self.ax.add_patch(ptchs.Rectangle((i,j),1,1,alpha=1,facecolor=color,edgecolor=color))
        
        #self.xlims = [0, self.nx]
        #self.ylims = [0, self.ny]        
        #self.ax.set_xlim(self.xlims)
        #self.ax.set_ylim(self.ylims)
                
        #Bind movement in this plot to movement of the history plot, and store the index of the observer in DraggablePopHistory
        #self.observer_ind = self.hist.bind_observer([self.prepare_to_update_plot,self.update_plot,self.end_update_plot])

        #Needed for the animation
        #self.background = None
        #self.lock = None
                
        #self.fig.canvas.draw()
        
        #Bind movement in this plot to movement of the history plot, and store the index of the observer in DraggablePopHistory
        self.observer_ind = self.hist.bind_observer([self.prepare_to_update_plot,self.update_plot,self.end_update_plot])
                
        imobj = np.zeros((self.ny,self.nx))
        for i in range(0,self.ny):
            for j in range(0,self.nx):
                imobj[i][j] = copy.deepcopy(self.approx_jsfs_to_plot[i][j])
        
        self.ax.set_ylabel('Population 1 derived allele count')
        self.ax.set_xlabel('Population 2 derived allele count')
        self.ax.set_title('Allele frequency spectrum')
                
        self.im = self.ax.imshow(imobj,interpolation='none')
                
        #Needed for the animation
        self.background = None
        self.lock = None
        
        self.fig.canvas.show(block=False)
        


                
    def prepare_to_update_plot(self):
        if self.lock is not None: return
        
        #Unlock
        self.lock = self
        
        #if self.lock is not None: return

        #Draw everything but the data that changes (which is the )
        #for i in range(0,self.ny):
        #    for j in range(0,self.nx):
        #        self.rects[i][j].set_animated(True)
                        
        #self.fig.canvas.draw()
        #self.background = self.fig.canvas.copy_from_bbox(self.ax.bbox)
        
        #Redraw just the part of the history that moves (which is all of it)
        #for i in range(0,self.ny):
        #    for j in range(0,self.nx):
        #        self.rects[i][j].remove()
        #        color = self.cmap(self.approx_jsfs_to_plot[i][j])[0:3]
        #        self.rects[i][j] = self.ax.add_patch(ptchs.Rectangle((i,j),1,1,alpha=1,facecolor=color,edgecolor=color)) 
        #        self.ax.draw_artist(self.rects[i][j])
 
        #Unlock
        #self.lock = self
        
        #Blit the redrawn area d
        #self.fig.canvas.blit(self.ax.bbox)
        
        
        
    def update_plot(self):
        if self.lock is not self: return
        
        self.jsfs.get_JSFS_point_migrations()
        self.approx_jsfs_to_plot = self.jsfs.JSFS[self.slice_obj]
        self.approx_jsfs_to_plot[0][0] = None
        
        imobj = np.zeros((self.ny,self.nx))
        for i in range(0,self.ny):
            for j in range(0,self.nx):
                imobj[i][j] = copy.deepcopy(self.approx_jsfs_to_plot[i][j])
                #imobj[i][j] = self.approx_jsfs_to_plot[i][j]+0 #Copy by value
        
        self.im.set_array(imobj)
        
        self.fig.canvas.draw()
        
        #if self.lock is not self: return
        
        #self.jsfs.get_JSFS_point_migrations()

        #for i in range(0,self.ny):
        #    for j in range(0,self.nx):
        #        self.rects[i][j].color = self.cmap(self.approx_jsfs_to_plot[i][j])[0:3]
                                
        #Restore the background region
        #self.fig.canvas.restore_region(self.background)
        
        #Redraw the current shapes only      
        #for i in range(0,self.ny):
        #    for j in range(0,self.nx):
        #        self.ax.draw_artist(self.rects[i][j])
        
        #Blit only the redrawn area
        #self.fig.canvas.blit(self.ax.bbox)
        
        
        
        
    def end_update_plot(self):
        if self.lock is not self: return
        self.background = None        
        self.lock = None        
        self.press = None
        
        #if self.lock is not self: return

        #Turn of animation and reset background
        #for i in range(0,self.ny):
        #    for j in range(0,self.nx):
        #        self.rects[i][j].set_animated(False)

        #self.background = None           
        
        #self.lock = None        
        #self.press = None            
        
        #Redraw the full figure
        #self.fig.canvas.draw()
        
        #self.fig.canvas.draw()



class JUSFSvisualization:
    def __init__(self, hist, nentries, ns, tubd, jsfstoplot, Ent_sum_nmax = 10, get_JSFS = True, jsfs_to_plot = None): #Try to implement this without including the statistic to compute... you can include it later
        self.fig = plt.figure(facecolor = 'white')
        self.ax = self.fig.add_subplot(111)
        self.ax.cla()
        
        self.hist = hist
        self.nentries = nentries
        self.nuref = 1
        self.ns = ns
        self.tubd = tubd
        self.Ent_sum_nmax = Ent_sum_nmax
        self.get_JSFS = get_JSFS
        self.which_pops = np.where(np.array(ns) > 0)[0]
        if len(self.which_pops) > 2:
            self.which_pops = self.which_pops[0:1]
        self.ref_jsfs_to_plot = jsfstoplot
        self.ref_jsfs_plot_object = None
        self.approx_jsfs_to_plot = None
        self.approx_jsfs_plot_object = None
                        
        self.jsfs = JUSFSprecise(self.hist, self.nentries, self.nuref, self.ns, self.tubd, self.Ent_sum_nmax, self.get_JSFS)

        print ">>>>>>>>>>>>>>>>> JSFS shape"
        print self.jsfs.JSFS.shape

        if self.hist.npops > 1:
            self.slice_obj = [None] * self.hist.npops
            self.slice_obj[self.which_pops[0]] = slice(0,self.nentries[self.which_pops[0]]+1)
            self.slice_obj[self.which_pops[1]] = slice(0,self.nentries[self.which_pops[1]]+1)
            for i in range(0,len(self.slice_obj)):
                if self.slice_obj[i] is None:
                    self.slice_obj[i] = 0
            #self.approx_jsfs_to_plot = np.array(self.jsfs.JSFS.tolist(),dtype=np.float64)[self.slice_obj]
            print self.slice_obj
            self.approx_jsfs_to_plot = self.jsfs.JSFS[self.slice_obj]
            self.approx_jsfs_to_plot[0][0] = None
        else:
            self.approx_jsfs_to_plot = self.jsfs.JSFS
            self.approx_jsfs_to_plot[0] = None
        
        
        #If there's a reference SFS (loaded from a file) to plot, plot it
        if self.ref_jsfs_to_plot is not None:
            if self.hist.npops > 1:
                self.ref_jsfs_to_plot = self.ref_jsfs_to_plot[self.slice_obj]
                self.ref_jsfs_to_plot[0][0] = None
                self.ref_jsfs_plot_object = mtlb.repmat(None,1,self.ref_jsfs_to_plot.shape[1])[0]
                for ind in range(0,self.ref_jsfs_to_plot.shape[1]):
                    xgrid = np.arange(0,self.ref_jsfs_to_plot.shape[0])
                    vals = self.ref_jsfs_to_plot[:,ind]
                    self.ref_jsfs_plot_object[ind] = Line2D(xgrid,vals, linestyle='dashed' , marker = "o", mec = [0,0,0], mfc = [0,0,0])
                    self.ax.add_line(self.ref_jsfs_plot_object[ind])
            else:
                self.ref_jsfs_to_plot[0] = None
                self.ref_jsfs_plot_object = [None]
                xgrid = np.arange(0,len(self.ref_jsfs_to_plot))
                vals = self.ref_jsfs_to_plot
                self.ref_jsfs_plot_object[0] = Line2D(xgrid,vals, linestyle='dashed' , marker = "o", mec = [0,0,0], mfc = [0,0,0])
                self.ax.add_line(self.ref_jsfs_plot_object[0])
        
        self.line_colors = [[0,0.4470,0.7410],[0.8500,0.3250,0.0980],[0.9290,0.6940,0.1250],[0.4940,0.1840,0.5560],[0.4660,0.6740,0.1880],[0.3010,0.7450,0.9330],[0.6350,0.0780,0.1840]] #MATLAB ColorOrder, replicated max(self.nentries) times                
        #Plot the computed approximate SFS
        if self.hist.npops > 1:
            self.approx_jsfs_plot_object = mtlb.repmat(None,1,self.approx_jsfs_to_plot.shape[1])[0]
            xgrid_approx_sfs = np.arange(0,self.approx_jsfs_to_plot.shape[0])
            for ind in range(0,self.approx_jsfs_to_plot.shape[1]):            
                vals = self.approx_jsfs_to_plot[:,ind]
                self.approx_jsfs_plot_object[ind] = Line2D(xgrid_approx_sfs,vals, color = self.line_colors[np.mod(ind,7)] , marker = "o",mec = self.line_colors[np.mod(ind,7)], mfc = self.line_colors[np.mod(ind,7)])
                self.ax.add_line(self.approx_jsfs_plot_object[ind])
        else:
            self.approx_jsfs_plot_object = [None]
            xgrid_approx_sfs = np.arange(0,len(self.approx_jsfs_to_plot))
            vals = self.approx_jsfs_to_plot
            self.approx_jsfs_plot_object[0] = Line2D(xgrid_approx_sfs,vals, color = self.line_colors[np.mod(0,7)] , marker = "o",mec = self.line_colors[np.mod(0,7)], mfc = self.line_colors[np.mod(0,7)])
            self.ax.add_line(self.approx_jsfs_plot_object[0])
                            
                
        self.xlims = [0, max(xgrid_approx_sfs)+1]
        self.ylims = [0, 2 * np.max(self.approx_jsfs_to_plot)]        
        self.ax.set_xlim(self.xlims)
        self.ax.set_ylim(self.ylims)
        
        self.ax.set_xlabel('Population 1 derived allele count')
        self.ax.set_ylabel('Expected sites/(2*Nref*mu)')
        self.ax.set_title('Allele frequency spectrum')
        
        self.fig.canvas.mpl_connect('pick_event', self.show_line_index)
                
        #Bind movement in this plot to movement of the history plot, and store the index of the observer in DraggablePopHistory
        self.observer_ind = self.hist.bind_observer([self.prepare_to_update_plot,self.update_plot,self.end_update_plot])

        #Needed for the animation
        self.background = None
        self.lock = None
                
        #self.ax.set_yscale('log')
        self.fig.canvas.draw()

                
    def show_line_index(self):
        ind = event.ind
        print 'onpick3 scatter:', ind, np.take(x, ind), np.take(y, ind)
        
        
    def prepare_to_update_plot(self):
        if self.lock is not None: return

        #Draw everything but the data that changes (which is the )
        for i in range(0,len(self.approx_jsfs_plot_object)):
            self.approx_jsfs_plot_object[i].set_animated(True)
                
        self.fig.canvas.draw()
        self.background = self.fig.canvas.copy_from_bbox(self.ax.bbox)
        
        #Redraw just the part of the history that moves (which is all of it)
        for i in range(0,len(self.approx_jsfs_plot_object)):
            self.ax.draw_artist(self.approx_jsfs_plot_object[i])
 
        #Unlock
        self.lock = self
        
        #Blit the redrawn area d
        self.fig.canvas.blit(self.ax.bbox)     
           
    
    def update_plot(self):
        if self.lock is not self: return
        
        self.jsfs.get_JSFS_point_migrations()
        #self.approx_jsfs_to_plot = np.array(self.jsfs.JSFS.tolist(),dtype=np.float64)[self.slice_obj]
        if self.hist.npops > 1:
            self.approx_jsfs_to_plot = self.jsfs.JSFS[self.slice_obj]
            self.approx_jsfs_to_plot[0][0] = None
        else:
            self.approx_jsfs_to_plot = self.jsfs.JSFS
            self.approx_jsfs_to_plot[0] = None
        
        
        #Plot the computed approximate SFS
        if self.hist.npops > 1:
            for ind in range(0,self.approx_jsfs_to_plot.shape[1]):
                xgrid = np.arange(0,self.approx_jsfs_to_plot.shape[0])
                vals = self.approx_jsfs_to_plot[:,ind]
                self.approx_jsfs_plot_object[ind].set_data(xgrid,vals)
        else:
            xgrid = np.arange(0,len(self.approx_jsfs_to_plot))
            vals = self.approx_jsfs_to_plot
            self.approx_jsfs_plot_object[0].set_data(xgrid,vals)
        
        #Restore the background region
        self.fig.canvas.restore_region(self.background)
        
        #Redraw the current shapes only      
        for i in range(0,len(self.approx_jsfs_plot_object)):
            self.ax.draw_artist(self.approx_jsfs_plot_object[i])
        
        #Blit only the redrawn area
        self.fig.canvas.blit(self.ax.bbox)         

        
    def end_update_plot(self):
        if self.lock is not self: return

        #Turn of animation and reset background
        for i in range(0,len(self.approx_jsfs_plot_object)):
            self.approx_jsfs_plot_object[i].set_animated(False)

        self.background = None           
        
        self.lock = None        
        self.press = None            
        
        #Redraw the full figure
        self.fig.canvas.draw()
    
    
    
    
class NLFTvisualization2:
    def __init__(self, fig, ax, hist, nuref, ns, tubd, plotdt):
        self.fig = fig
        self.ax = ax
        #self.xlims = xlims
        #self.ylims = ylims
        self.hist = hist
        self.nuref = nuref
        self.ns = ns
        self.tubd = tubd
        self.plotdt = plotdt
                
        self.nlft = NLFTprecise(self.hist, self.nuref, self.ns, self.tubd, self.plotdt)
        self.nlft.get_NLFT_point_migrations()

        self.scale_factors = np.array(self.hist.maxnes) / max(np.array(self.ns))
        #self.JUSFS_plot_objects = [[None] * self.hist.npops] * self.hist.npops
        self.JUSFS_plot_objects = [None] * (self.hist.npops**2)
        self.line_colors = [[0,0.4470,0.7410],[0.8500,0.3250,0.0980],[0.9290,0.6940,0.1250],[0.4940,0.1840,0.5560],[0.4660,0.6740,0.1880],[0.3010,0.7450,0.9330],[0.6350,0.0780,0.1840]] #MATLAB ColorOrder, replicated max(self.nentries) times        
        obj_ct = 0
        for i in range(0,self.hist.npops):
            for j in range(0,self.hist.npops):
                self.JUSFS_plot_objects[obj_ct] = Line2D(self.nlft.all_ts,self.hist.popctrs[j] + self.scale_factors[j] * self.nlft.NLFT[i,:,j], linestyle='solid' , color = self.line_colors[np.mod(i,7)])
                self.ax.add_line(self.JUSFS_plot_objects[obj_ct])
                obj_ct = obj_ct + 1
            maxy = max(self.hist.popctrs) + max(self.hist.maxnes)
            miny = min(self.hist.popctrs) - max(self.hist.maxnes)
            maxx = self.tubd

        #for pop in range(0,self.hist.npops):
        #    obj = Line2D(self.nlft.all_ts,self.hist.popctrs[pop] * np.array([1] * len(self.nlft.all_ts)), linestyle = '--', color = 'black')
        #    self.ax.add_line(obj)
                
        self.xlims = [0, maxx]
        self.ylims = [miny, maxy]        
        self.ax.set_xlim(self.xlims)
        self.ax.set_ylim(self.ylims)
                
        #Bind movement in this plot to movement of the history plot, and store the index of the observer in DraggablePopHistory
        self.observer_ind = self.hist.bind_observer([self.prepare_to_update_plot,self.update_plot,self.end_update_plot])

        #Needed for the animation
        self.background = None
        self.lock = None
        
        #print("Okay so far!")
        
        self.fig.canvas.draw()
    
    def prepare_to_update_plot(self):
        if self.lock is not None: return

        #Draw everything but the data that changes
        obj_ct = 0
        for i in range(0,self.hist.npops):
            for j in range(0,self.hist.npops):
                self.JUSFS_plot_objects[obj_ct].set_animated(True)
                obj_ct = obj_ct+1
                
        self.fig.canvas.draw()
        self.background = self.fig.canvas.copy_from_bbox(self.ax.bbox)
        
        #Redraw just the part of the history that moves
        obj_ct = 0
        for i in range(0,self.hist.npops):
            for j in range(0,self.hist.npops):
                self.ax.draw_artist(self.JUSFS_plot_objects[obj_ct])
                obj_ct = obj_ct + 1
 
        #Unlock
        self.lock = self
        
        #Blit the redrawn area d
        self.fig.canvas.blit(self.ax.bbox)     
           
    
    def update_plot(self):
        if self.lock is not self: return

        self.nlft.get_NLFT_point_migrations()
        #print self.nlft.NLFT[:,:,0]
        obj_ct = 0
        for i in range(0,self.hist.npops):
            for j in range(0,self.hist.npops):
                #print [i,j]
                self.JUSFS_plot_objects[obj_ct].set_data(self.nlft.all_ts.tolist(),(self.hist.popctrs[j] + self.scale_factors[j] * self.nlft.NLFT[i,:,j]).tolist())
                #self.JUSFS_plot_objects[i][j].set_data(self.nlft.all_ts,self.scale_factors[j] * self.nlft.NLFT[i,:,j])
                obj_ct = obj_ct + 1
        
        #Restore the background region
        self.fig.canvas.restore_region(self.background)
        
        #Redraw the current shapes only     
        obj_ct = 0 
        for i in range(0,self.hist.npops):
            for j in range(0,self.hist.npops):
                self.ax.draw_artist(self.JUSFS_plot_objects[obj_ct])
                obj_ct = obj_ct + 1
        
        #Blit only the redrawn area
        self.fig.canvas.blit(self.ax.bbox)         

        
    def end_update_plot(self):
        if self.lock is not self: return

        #Turn of animation and reset background
        obj_ct = 0
        for i in range(0,self.hist.npops):
            for j in range(0,self.hist.npops):
                self.JUSFS_plot_objects[obj_ct].set_animated(False)
                obj_ct = obj_ct + 1

        self.background = None           
        
        self.lock = None        
        self.press = None            
        
        #Redraw the full figure
        self.fig.canvas.draw()



class NLFTvisualization:
    def __init__(self, demog_main, hist, nuref, ns, tubd, plotdt):
        self.fig = plt.figure(facecolor = 'white')
        self.ax = self.fig.add_subplot(111)
        self.ax.cla()
        self.hist = hist
        self.nuref = nuref
        self.ns = ns
        self.tubd = tubd
        self.plotdt = plotdt
        self.demog_main = demog_main
        self.maxnes = self.demog_main.maxnes
        self.Nref = self.demog_main.Nref
        self.years_per_gen = self.demog_main.years_per_gen
                
        self.nlft = NLFTprecise(hist, ns, tubd) #compute NLFT for each population. nlft.NLFT[i][j] is the number of lineages from polulation i in population j at time t, where times are in self.nlft.tgrid
        self.nlft.get_nlft_cts_migration()

        #Set up NLFT plot
        self.scale_factors = np.array(self.hist.maxnes) / max(np.array(self.ns))

        self.NLFT_plot_objects = mtlb.repmat(None,self.hist.npops,self.hist.npops)
        self.line_colors = [[0,0.4470,0.7410],[0.8500,0.3250,0.0980],[0.9290,0.6940,0.1250],[0.4940,0.1840,0.5560],[0.4660,0.6740,0.1880],[0.3010,0.7450,0.9330],[0.6350,0.0780,0.1840]] #MATLAB ColorOrder, replicated max(self.nentries) times
        for i in range(0,self.hist.npops):
            for j in range(0,self.hist.npops):                                
                self.NLFT_plot_objects[i][j] = Line2D(self.nlft.tgrid[j],self.hist.popctrs[j] + self.scale_factors[j] * self.nlft.NLFT[i][j], linewidth = 2, linestyle='solid' , color = self.line_colors[np.mod(i,7)])
                self.ax.add_line(self.NLFT_plot_objects[i][j])
            miny = min(self.hist.popctrs) - max(self.hist.maxnes)
            maxy = max(self.hist.popctrs) + max(self.hist.maxnes)
            maxx = self.tubd
                
        self.xlims = [0, maxx]
        self.ylims = [miny, maxy]        
        self.ax.set_xlim(self.xlims)
        self.ax.set_ylim(self.ylims)
        
        self.ytick_locs = np.union1d(self.hist.popctrs,self.hist.popctrs + self.maxnes)
        if self.hist.units == 'Coalescent units':
            self.ax.set_ylabel('Number of lineages')
            self.ax.set_xlabel('Time in the past (2N generations)')
        elif self.hist.units == 'Ne/generations':
            self.ax.set_ylabel('Number of lineages')
            self.ax.set_xlabel('Time in the past (generations)')
        elif self.hist.units == 'Ne/years':
            self.ax.set_ylabel('Number of lineages')
            self.ax.set_xlabel('Time in the past (years)')
        self.ax.yaxis.set_ticks(self.ytick_locs)
        self.ytick_labels = []
        for i in range(0,len(self.hist.popctrs)):
            self.ytick_labels = self.ytick_labels + ['Pop ' + str(i+1)]
            maxn = max(self.ns)
            self.ytick_labels = self.ytick_labels + [str(maxn)]
        self.ax.yaxis.set_ticklabels(self.ytick_labels)

        self.xticks = self.ax.get_xticks()
        self.xtick_labels = []
        for i in range(0,len(self.xticks)):
            newxtick = None
            if self.hist.units == 'Coalescent units':
                newxtick = self.xticks[i]
            elif self.hist.units == 'Ne/generations':
                newxtick = self.xticks[i] * 2 * self.Nref
            elif self.hist.units == 'Ne/years':
                newxtick = self.xticks[i] * 2 * self.Nref * self.years_per_gen
            self.xtick_labels = self.xtick_labels + [str(newxtick)]
        self.ax.xaxis.set_ticklabels(self.xtick_labels)
                
        #Bind movement in this plot to movement of the history plot, and store the index of the observer in DraggablePopHistory
        self.observer_ind = self.hist.bind_observer([self.prepare_to_update_plot,self.update_plot,self.end_update_plot])

        #Needed for the animation
        self.background = None
        self.lock = None        
        
        self.fig.canvas.show()
        
    
    def prepare_to_update_plot(self):
        if self.lock is not None: return

        #Draw everything but the data that changes (actually the whole things moves, so animate everything)
        for i in range(0,len(self.NLFT_plot_objects)):
            for j in range(0,len(self.NLFT_plot_objects[i])):
                self.NLFT_plot_objects[i][j].set_animated(True)
                
        self.fig.canvas.draw()
        self.background = self.fig.canvas.copy_from_bbox(self.ax.bbox)
        
        #Redraw just the part of the history that moves (actually, the whole things moves, so draw everything)
        for i in range(0,len(self.NLFT_plot_objects)):
            for j in range(0,len(self.NLFT_plot_objects[i])):
                self.ax.draw_artist(self.NLFT_plot_objects[i][j])
 
        #Unlock
        self.lock = self
        
        #Blit the redrawn area d
        self.fig.canvas.blit(self.ax.bbox)
        
           
    
    def update_plot(self):
        if self.lock is not self: return
         
        self.nlft.get_nlft_cts_migration()  
                
        for i in range(0,len(self.NLFT_plot_objects)):
            for j in range(0,len(self.NLFT_plot_objects[i])):
                self.NLFT_plot_objects[i][j].set_data(self.nlft.tgrid[j],self.hist.popctrs[j] + self.scale_factors[j] * self.nlft.NLFT[i][j])
        
        #Restore the background region
        self.fig.canvas.restore_region(self.background)
        
        #Redraw the current shapes only      
        for i in range(0,len(self.NLFT_plot_objects)):
            for j in range(0,len(self.NLFT_plot_objects[i])):
                self.ax.draw_artist(self.NLFT_plot_objects[i][j])

        
        #Blit only the redrawn area
        self.fig.canvas.blit(self.ax.bbox)         

        
    def end_update_plot(self):
        if self.lock is not self: return

        #Turn of animation and reset background
        for i in range(0,len(self.NLFT_plot_objects)):
            for j in range(0,len(self.NLFT_plot_objects[i])):
                self.NLFT_plot_objects[i][j].set_animated(False)

        self.background = None           
        
        self.lock = None        
        self.press = None            
        
        #Redraw the full figure
        self.fig.canvas.draw()



class NLFTvisualization_point_migrations:
    def __init__(self, fig, ax, hist, nuref, ns, tubd, plotdt):
        self.fig = fig
        self.ax = ax
        #self.xlims = xlims
        #self.ylims = ylims
        self.hist = hist
        self.nuref = nuref
        self.ns = ns
        self.tubd = tubd
        self.plotdt = plotdt
        #self.Ent_sum_nmax = Ent_sum_nmax
        
        self.nlft = NLFTprecise(hist, nuref, ns, tubd, plotdt) #compute NLFT for each population. nlft.NLFT[i][j] is the number of lineages from polulation i in population j at time t, where times are in self.nlft.tgrid
        self.nlft.get_NLFT_point_migrations()

        #Set up NLFT plot
        self.scale_factors = np.array(self.hist.maxnes) / max(np.array(self.ns))
        #self.NLFT = np.array(self.nlft.NLFT.tolist(),dtype=np.float64)
        #print 'JUSFS post listing -->'
        #print self.npJUSFS
        self.NLFT_plot_objects = [[None] * self.hist.npops] * self.hist.npops 
        self.line_colors = [[0,0.4470,0.7410],[0.8500,0.3250,0.0980],[0.9290,0.6940,0.1250],[0.4940,0.1840,0.5560],[0.4660,0.6740,0.1880],[0.3010,0.7450,0.9330],[0.6350,0.0780,0.1840]] #MATLAB ColorOrder, replicated max(self.nentries) times
        for i in range(0,self.hist.npops):
            for j in range(0,self.hist.npops):
                self.NLFT_plot_objects[i][j] = Line2D(self.nlft.all_ts,self.hist.popctrs[j] + self.scale_factors[j] * self.nlft.NLFT[i,:,j], linestyle='solid' , mec = self.line_colors[np.mod(i,7)], mfc = self.line_colors[np.mod(i,7)])
                self.ax.add_line(self.NLFT_plot_objects[i][j])
            miny = min(self.hist.popctrs) - max(self.hist.maxnes)
            maxy = max(self.hist.popctrs) + max(self.hist.maxnes)
            maxx = self.tubd
                
        self.xlims = [0, maxx]
        self.ylims = [miny, maxy]        
        self.ax.set_xlim(self.xlims)
        self.ax.set_ylim(self.ylims)
                
        #Bind movement in this plot to movement of the history plot, and store the index of the observer in DraggablePopHistory
        self.observer_ind = self.hist.bind_observer([self.prepare_to_update_plot,self.update_plot,self.end_update_plot])

        #Needed for the animation
        self.background = None
        self.lock = None
        
        #print("Okay so far!")
        
        self.fig.canvas.draw()
    
    def prepare_to_update_plot(self):
        if self.lock is not None: return

        #Draw everything but the data that changes
        for i in range(0,len(self.NLFT_plot_objects[i])):
            for j in range(0,len(self.NLFT_plot_objects[i])):
                self.NLFT_plot_objects[i][j].set_animated(True)
                
        self.fig.canvas.draw()
        self.background = self.fig.canvas.copy_from_bbox(self.ax.bbox)
        
        #Redraw just the part of the history that moves
        for i in range(0,len(self.NLFT_plot_objects)):
            for j in range(0,len(self.NLFT_plot_objects[i])):
                self.ax.draw_artist(self.NLFT_plot_objects[i][j])
 
        #Unlock
        self.lock = self
        
        #Blit the redrawn area d
        self.fig.canvas.blit(self.ax.bbox)     
           
    
    def update_plot(self):
        if self.lock is not self: return
                
        self.nlft.get_NLFT_point_migrations()
        #self.NLFT = np.array(self.nlft.NLFT.tolist(),dtype=np.float64)
        for i in range(0,len(self.NLFT_plot_objects)):
            for j in range(0,len(self.NLFT_plot_objects[i])):
                self.NLFT_plot_objects[i][j].set_data(self.all_ts,self.nlft.NLFT[i,:,j])
        
        #Restore the background region
        self.fig.canvas.restore_region(self.background)
        
        #Redraw the current shapes only      
        for i in range(0,len(self.NLFT_plot_objects)):
            for j in range(0,len(self.NLFT_plot_objects[i])):
                self.ax.draw_artist(self.NLFT_plot_objects[i][j])
        
        #Blit only the redrawn area
        self.fig.canvas.blit(self.ax.bbox)         

        
    def end_update_plot(self):
        if self.lock is not self: return

        #Turn of animation and reset background
        for i in range(0,len(self.NLFT_plot_objects)):
            for j in range(0,len(self.NLFT_plot_objects[i])):
                self.NLFT_plot_objects[i][j].set_animated(False)

        self.background = None           
        
        self.lock = None        
        self.press = None            
        
        #Redraw the full figure
        self.fig.canvas.draw()





class JUSFSprecise:
    def __init__(self, hist, nentries, nuref, ns, tubd = 10, Ent_sum_nmax = 10, get_JSFS = False, precision = 400):
        
        mp.dps = precision
        if len(ns) == 1: #For one populatoin, can't compute nth entry
            nentries = [min(ns[0]-1,nentries[0])]
        self.mig_indicator = None        
        self.all_ts = None
        self.all_nus = None
        self.all_gammas = None
        self.all_migs = None        
        self.nuref = nuref #Reference population scaling
        self.tubd = tubd #Upper bound for integrating the ENLFT... In other words, we consider sites in the SFS arising since time tubd
        self.nentries = np.array(nentries).astype(int)
        self.max_nents = self.nentries + 1
        self.Ent_sum_nmax = Ent_sum_nmax #The max value of n we sum to in Tavare's formula for Ent
        self.hist = hist        
        
        self.ns = ns        
        self.npops = np.array(self.hist.npops).astype(int)
        self.entvec = copy.deepcopy(self.nentries)
        self.nus = self.hist.nus
        self.ts = self.hist.ts
        self.expmat = self.hist.expmat
        self.gammas = self.hist.gammas
        self.migs = self.hist.migs
        
        
        self.migs_sorted = deepcopy(self.migs)
        self.migs_sorted = sorted(self.migs_sorted,key=lambda x: x[0])
        

        mat = 0
        for i in range(0,self.npops):
            mat = [mat] * (self.entvec[self.npops-1-i] + 1)
        mat = np.array(mat) * mpf(0)
                        
        self.JUSFS = np.array(mat) #Makes an nd array such that element self.JUSFS[i1,i2,...,inpops] is the element of the JUSFS with i1 copies in population 1, i2 copies in population 2, ... etc.
        self.get_JUSFS_point_migrations()

        #Set up inverse matrices
        self.Minvs = []
        for pop in range(0,self.npops):
            self.Minvs = self.Minvs + [None]
        for i in range(0,self.npops):
            self.Minvs[i] = self.get_Minv(self.ns[i],self.entvec[i]+1)
        mat = mpf('0')
        for i in range(0,self.npops):
            mat = [mat] * (self.entvec[self.npops-1-i] + 1)
        self.JSFS = np.array(mat) #Makes an nd array such that element self.JSFS[i1,i2,...,inpops] is the element of the JSFS with i1 copies in population 1, i2 copies in population 2, ... etc.
            
        
        if get_JSFS:
            self.get_JSFS_point_migrations()
            
                    


    def get_JSFS_point_migrations(self):
        self.get_JUSFS_point_migrations()      

        self.JSFS = self.tensor_prod(self.JUSFS,self.Minvs)
        temp = np.cumprod(np.array(self.entvec)+1) #Useful quantity for converting between a scalar index, and an entry of a multidimensional array
        temp = np.concatenate(([1],temp[0:len(temp)-1]))
        nelts = np.prod(np.array(self.entvec)+1).astype(int) #Total number of elements in the SFS
        for i in range(1,nelts+1):
            ents = np.array(mtlb.repmat(0,1,self.npops)[0])
            r = i;            
            for j in np.arange(self.npops,1,-1):
                ents[j-1] = np.ceil(r/temp[j-1]);
                r = r - (ents[j-1]-1) * temp[j-1];
            ents[0] = r;
            ents = ents-1;
            self.JSFS[tuple(ents)] = round(self.JSFS[tuple(ents)],4)
            

    def tensor_prod(self,SFS,Minvs):     
        from_tensor = copy.deepcopy(SFS)
        dims = np.array(SFS).shape
        ndims = len(dims)
        for dim1 in range(0,ndims):        
            mat = mpf("0")
            for i in range(0,ndims):
                mat = [mat] * (dims[ndims-1-i])
                                    
            to_tensor = np.array(mat)
            for iind in range(0,dims[dim1]):
                slice_object_i = []
                for d in range(0,ndims):
                    slice_object_i = slice_object_i + [slice(0,dims[d])]
                slice_object_i[dim1] = iind
                for jind in range(0,dims[dim1]):
                    slice_object_j = []
                    for d in range(0,ndims):
                        slice_object_j = slice_object_j + [slice(0,dims[d])]
                    slice_object_j[dim1] = jind
                    to_tensor[slice_object_i] = to_tensor[slice_object_i] + from_tensor[slice_object_j] * Minvs[dim1][iind,jind]
                    #to_tensor[slice_object_i] = to_tensor[slice_object_i] + from_tensor[slice_object_j] * Minvs[iind,jind]
            from_tensor = to_tensor-0
        return from_tensor
                    

    def get_JUSFS_point_migrations(self):
                
        self.get_whole_history()
                
        ns = matrix(np.array(self.ns).astype(str))
        Ltot = self.integrate_total_branch_len(ns-0)
        
        #Loop over all entries 'ents' of the SFS where [i1,i2,i2,...,inpops], (ik=0,...,ns[k+1]) is the expected number of sites with ik copies in population k.
        temp = np.cumprod(np.array(self.entvec)+1) #Useful quantity for converting between a scalar index, and an entry of a multidimensional array
        temp = np.concatenate(([1],temp[0:len(temp)-1]))
        nelts = np.prod(np.array(self.entvec)+1).astype(int) #Total number of elements in the SFS
        for i in range(1,nelts+1):
            ents = np.array(mtlb.repmat(0,1,self.npops)[0])
            r = i;            
            for j in np.arange(self.npops,1,-1):
                ents[j-1] = np.ceil(r/temp[j-1]);
                r = r - (ents[j-1]-1) * temp[j-1];
            ents[0] = r;
            ents = ents-1;
            
            self.JUSFS[tuple(ents)] = (Ltot - self.integrate_total_branch_len(ns-matrix(ents))).real




    def integrate_total_branch_len(self, ns):
        totalL = mpf(0) #Initialize the sum total of branch lengths for the history
        nupto = copy.deepcopy(ns)

        if len(self.ns) > 1:
            mig_ct = 0
            for i in range(0,len(self.all_ts)-1):
                if np.amax(np.abs(self.all_gammas[:,i])) == 0 and (self.all_cts_migmats[i] is None):
                    Lphi = self.integrate_ENLFT_1epoch_asym(i, nupto)                
                elif self.all_cts_migmats[i] is None:
                    #Lphi = self.integrate_ENLFT_1epoch2(i, nupto)
                    Lphi = self.integrate_ENLFT_1epoch_asym_finite_diff(i, nupto)                    
                else:
                    Lphi = self.integrate_ENLFT_1epoch_asym_finite_diff_cts_mig(i, nupto)
                totalL = totalL + sum(Lphi[0])
                nupto = Lphi[1]*1

                if self.mig_indicator[i+1]:
                    mig_ct = self.mig_inds[i+1]
                    mig = self.all_migs[mig_ct,:]
                    if mig[3] >= 0:
                        nupto[int(mig[2])-1] = nupto[int(mig[2])-1] + nupto[int(mig[1])-1] * mig[3]
                        nupto[int(mig[1])-1] = nupto[int(mig[1])-1] * (1 - mig[3])
                    else:
                        nupto[int(mig[1])-1] = nupto[int(mig[1])-1] - nupto[int(mig[2])-1] * mig[3]
                        nupto[int(mig[2])-1] = nupto[int(mig[2])-1] * (1 + mig[3])
        else:
            for i in range(0,len(self.all_ts)-1):
                if np.amax(np.abs(self.all_gammas[:,i])) == 0:
                    Lphi = self.integrate_ENLFT_1epoch_asym(i, nupto)
                else:
                    #Lphi = self.integrate_ENLFT_1epoch2(i, nupto)
                    Lphi = self.integrate_ENLFT_1epoch_asym_finite_diff(i, nupto)
                totalL = totalL + sum(Lphi[0])
                nupto = Lphi[1]*1

        return totalL
        

    #Approximate nu(t) in each population by a piecewise constant population with K epochs
    def integrate_ENLFT_1epoch_asym_finite_diff(self, epind, ns):
        nuref_mp = mpf(np.array([self.nuref]).astype(str)[0]) #Mess around to get self.nuref as an mpf object
        nus_start = self.all_nus[:,epind]
        T = self.all_ts[epind+1] - self.all_ts[epind]
        xend = copy.deepcopy(ns)
        
        gams = self.all_gammas[:,epind]
        L = mtlb.repmat(mpf(0),self.npops,1)
                
        K = 20 #Number of epochs in approximate piecewise constant history                
        for pop in range(0,self.npops):
            nu = nus_start[pop]+0
            x = ns[pop]+0
            if gams[pop] != 0:
                if x > 1:
                    for k in range(0,K):
                        #dt1, dt1+dt2, dt1+dt2+dt3, etc. are the points bounding 1/K, 2/K, 3/K, etc. of the mass of the population history
                        dt = log((k+1) * (exp(gams[pop] * T) - 1) / K + 1) / gams[pop] - log(k * (exp(gams[pop] * T) - 1) / K + 1) / gams[pop]
                        L[pop] = L[pop] + 2 * (nu / nuref_mp) * log(1 + (exp(dt * nuref_mp / (2*nu)) - 1) * x)
                        x = x / (x - (x-1) * exp(- dt / (2*nu)))
                        #print round(dt,4)
                        #print round(x,4)
                        #print round(L[pop],4)
                        #print round(nu,4)
                        nu = nu * exp(gams[pop] * dt)
                    xend[pop] = x+0 #copy by value
                else:
                    L[pop] = x * T
                    xend[pop] = x+0
            else:
                L[pop] = 2 * (nu / nuref_mp) * log(1 + (exp(T * nuref_mp / (2*nu)) - 1) * x)
                xend[pop] = x / (x - (x-1) * exp(- T / (2*nu)))

        return [L,xend]
    

    def integrate_ENLFT_1epoch2(self, epind, ns): 
        nuref_mp = mpf(np.array([self.nuref]).astype(str)[0]) #Mess around to get self.nuref as an mpf object
        nus = self.all_nus[:,epind]
        npops = len(nus)          
        npns = np.array(ns)  
        zero_inds = (npns == 0)
        nonzero_inds = (npns > 0)        
        chg_inds = (npns > 1)
        no_chg_inds = (npns <= 1) * nonzero_inds
        gammas = self.all_gammas[:,epind]
        growth_inds = (np.array(gammas) != 0) 
        
        t = self.all_ts[epind+1] - self.all_ts[epind]
        
        temp = np.arange(0,self.npops)
        no_chg_inds = temp[no_chg_inds]
        chg_inds = temp[chg_inds]
        zero_inds = temp[zero_inds]
         
        L = mtlb.repmat(0,1,self.npops)[0]
        for i in no_chg_inds:
            L[i] = t * ns[i]
        newn = ns+0#copy by value

        for i in chg_inds:
            L[i] = 2 * (nus[i] / nuref_mp) * log(1 + (exp(t * nuref_mp / (2*nus[i])) - 1) * ns[i])
            newn[i] = ns[i] / (ns[i] - (ns[i]-1) * exp(- t * nuref_mp / (2*nus[i])))
        for i in zero_inds:
            L[i] = 0

        #Growth
        for i in range(0,npops):
            if growth_inds[i]:
                newL = t
                #newn_temp = 0
                #for k in range(2,self.Ent_sum_nmax):
                g_mp = mpf(np.array([gammas[i]]).astype(str)[0])
                n_mp = mpf(np.array([ns[i]]).astype(str)[0])
                nu_mp = mpf(np.array([nus[i]]).astype(str)[0])
                t_mp = mpf(np.array([t]).astype(str)[0])                
                #for k in range(2,floor(ns[i])): 
                nmax = 20                   
                for k in range(2,nmax):
                    temp1 = (2*k - 1) * rf(n_mp-k+1,k) / rf(n_mp,k)
                    Rterm1 = exp((k * (k-1) / 2) * nuref_mp / (g_mp * nu_mp)) * (1/g_mp)
                    Rterm2 = ei(-(k*(k-1)/2) * (nuref_mp / (nu_mp * g_mp)) * exp(g_mp * t_mp))
                    Rterm3 = ei(-(k*(k-1)/2) * (nuref_mp / (nu_mp * g_mp)))
                    newL = newL + temp1 * Rterm1 * (Rterm2 - Rterm3)
                L[i] = newL
                newn[i] = n_mp / (n_mp - (n_mp-1) * exp(- (exp(g_mp * t_mp) - 1) * nuref_mp / (2 * g_mp * nu_mp)))

        return [L,newn]  


   
    def integrate_ENLFT_1epoch_asym(self, epind, ns): #Only works if all population sizes are constant!
        nuref_mp = mpf(np.array([self.nuref]).astype(str)[0]) #Mess around to get self.nuref as an mpf object
        nus = self.all_nus[:,epind]   
        npns = np.array(ns)  
        zero_inds = (npns == 0)
        nonzero_inds = (npns > 0)        
        chg_inds = (npns > 1)
        no_chg_inds = (npns <= 1) * nonzero_inds
        t = self.all_ts[epind+1] - self.all_ts[epind]
        
        temp = np.arange(0,self.npops)
        no_chg_inds = temp[no_chg_inds]
        chg_inds = temp[chg_inds]
        zero_inds = temp[zero_inds]
        
        L = mtlb.repmat(mpf(0),self.npops,1)
        
        for i in no_chg_inds:
            L[i] = t * ns[i]
        newn = ns+0#copy by value
        for i in chg_inds:            
            L[i] = 2 * (nus[i] / nuref_mp) * log(1 + (exp(t * nuref_mp / (2*nus[i])) - 1) * ns[i])
            newn[i] = ns[i] / (ns[i] - (ns[i]-1) * exp(- t * nuref_mp / (2*nus[i])))
        for i in zero_inds:
            L[i] = 0        
            
        return [L,newn]   

      
    def integrate_ENLFT_1epoch_asym_finite_diff_cts_mig(self, epind, ns):
        nuref_mp = mpf(np.array([self.nuref]).astype(str)[0]) #Mess around to get self.nuref as an mpf object
        nus_start = self.all_nus[:,epind]  
        x = ns+0#copy by value     
        T = self.all_ts[epind+1] - self.all_ts[epind]
        
        M = self.all_cts_migmats[epind]
        Mevals, Mevecs = np.linalg.eig(np.eye(self.hist.npops) + M)
        Miginv = np.linalg.inv(Mevecs)
        #print np.dot(np.dot(Mevecs, np.diag(Mevals)),Miginv)
        
        gams = self.all_gammas[:,epind]
        L = mtlb.repmat(mpf(0),self.npops,1)

        nus = copy.deepcopy(nus_start)
        for pop in range(0,self.npops):
            nus[pop] = mpf(str(nus[pop]))

        #Set up a grid of points to capture population size changes by piecewise constant populations
        #Grid points are clustered in regions of greatest size change                
        #K = 100
        K = ceil(T * 2 * self.hist.Nref / 40)
        dtgrid = [0]
        for pop in range(0,self.npops):
            ttot = 0
            for k in range(0,K):
                if gams[pop] != 0:
                    #dt1, dt1+dt2, dt1+dt2+dt3, etc. are the points bounding 1/K, 2/K, 3/K, etc. of the mass of the population history
                    dt = log((k+1) * (exp(gams[pop] * T) - 1) / K + 1) / gams[pop] - log(k * (exp(gams[pop] * T) - 1) / K + 1) / gams[pop]
                    ttot = ttot + dt
                    dtgrid = dtgrid + [ttot]
                else:
                    dt = T/K
                    dtgrid = dtgrid + [((k+1)/K) * T]
                
        dtgrid = np.unique(dtgrid)
                        
        for k in range(1,len(dtgrid)):
            t = dtgrid[k-1]
            dt = dtgrid[k] - dtgrid[k-1]
            #Integrate total branch length and propagate lineages in each branch
            for pop in range(0,self.npops):
                nu = nus[pop] * exp(gams[pop] * t) #Size at start of time interval
                L[pop] = L[pop] + 2 * (nu / nuref_mp) * log(1 + (exp(dt * nuref_mp / (2*nu)) - 1) * x[pop])
                x[pop] = x[pop] / (x[pop] - (x[pop]-1) * exp(- dt / (2*nu)))

            #Do migration
            ngens = 2 * self.hist.Nref * dt
            Mprod = np.dot(np.dot(Mevecs, np.diag(Mevals**ngens)),Miginv) #Effective migration matrix after dt coalescent time units... I.e., M^ngens
            for pop in range(0,self.npops):
                temp = 0
                for pop2 in range(0,self.npops):
                    temp = temp + Mprod[pop][pop2] * x[pop2]
                x[pop] = temp+0#Copy by value                

        return [L,x]



    #Make a data object where every population has an equal number of epochs that
    #all begin and end at the same times. Do this by finding a list of times of
    #all events (size changes, migrations, migration stops) and build epoch boundaries
    #at these times. Find nus, gammas, ts that are the same as hist.nus, hist.gammas, hist.ts
    #except for the fact that every population now has the same number of pieces.
    #Also get a vector of all times and some other stuff.
    def get_whole_history(self):        
        #Get gammas from expmat and ns
        for i in range(0,len(self.expmat)):
            for j in range(0,len(self.expmat[i])):
                if not (self.expmat[i][j] is None):
                    self.gammas[i][j] = self.expmat[i][j]
                elif j < len(self.expmat[i])-1:                    
                    Nf = self.nus[i][j]
                    No = self.nus[i][j+1]
                    t = self.ts[i][j+1] - self.ts[i][j]
                    self.gammas[i][j] = np.log(No/Nf)/t
                else:
                    self.gammas[i][j] = 0
        
        self.migs_sorted = copy.deepcopy(self.migs)
        self.migs_sorted = sorted(self.migs_sorted,key=lambda x: x[0])
        all_ts = np.unique(self.ts[0])
        if self.npops > 1:
            for i in range(1,self.npops):
                all_ts = np.union1d(all_ts,self.ts[i])
        mig_ts = []
        mig_inds = []
        for i in range(0,len(self.migs)):
            all_ts = np.union1d(all_ts,[self.migs_sorted[i][0]])
            if self.migs_sorted[i][4] == 0:
                mig_ts = np.concatenate((mig_ts,[self.migs_sorted[i][0]]))
                mig_inds = np.concatenate((mig_inds,[i]))
        mig_stop_ts = np.zeros(len(self.migs_sorted))
        for i in range(0,len(self.migs)):
            all_ts = np.union1d(all_ts,[self.migs_sorted[i][0] + self.migs_sorted[i][4]])
            mig_stop_ts[i] = self.migs_sorted[i][0] + self.migs_sorted[i][4]
        all_ts = np.union1d(all_ts,[self.tubd])
        self.all_ts = matrix(all_ts.astype(str))
        self.mig_indicator = np.in1d(all_ts,mig_ts)
        self.mig_inds = mtlb.repmat(None,1,len(self.all_ts))[0]
        ct = 0
        for i in range(0,len(self.all_ts)):
            if self.mig_indicator[i]:
                self.mig_inds[i] = mig_inds[ct]
                ct = ct+1
        self.mig_stop_indicator = np.in1d(all_ts,mig_stop_ts)
        if len(self.migs_sorted) > 0:
            self.all_migs = matrix(np.array(self.migs_sorted).astype(str))
        else:
            self.all_migs = []

        neps = len(all_ts)
        self.all_nus = np.zeros((self.npops,len(all_ts)))
        self.all_gammas = np.zeros((self.npops,len(all_ts)))
        for i in range(0,self.npops):
            for j in range(0,neps):
                epind = np.sum(np.array(self.ts[i]) <= all_ts[j]) - 1#index of the epoch all_ts[j] is in
                self.all_gammas[i][j] = self.gammas[i][epind]
                if self.gammas[i][epind] == 0:
                    self.all_nus[i][j] = self.nus[i][epind]
                else:
                    self.all_nus[i][j] = self.nus[i][epind] * np.exp(self.gammas[i][epind] * (all_ts[j] - self.ts[i][epind]))
        
        self.all_cts_migmats = mtlb.repmat(None,1,neps)[0]
        for ep in range(0,neps):
            t = all_ts[ep]            
            #M = np.eye(self.npops)
            M = np.zeros((self.npops,self.npops))
            cts_mig_happens = None
            for m in range(0,len(self.migs)):
                if self.migs[m][4] > 0 and self.migs[m][0] <= t and t < self.migs[m][0] + self.migs[m][4]:
                    cts_mig_happens = 1
                    if self.migs[m][3] >= 0:
                        pop1ind = self.migs[m][1].astype(int) - 1
                        pop2ind = self.migs[m][2].astype(int) - 1
                    else:
                        pop1ind = self.migs[m][2].astype(int) - 1
                        pop2ind = self.migs[m][1].astype(int) - 1                        
                    M[pop2ind][pop1ind] = np.abs(self.migs[m][3])
                    M[pop1ind][pop1ind] = M[pop1ind][pop1ind] - np.abs(self.migs[m][3])
                if cts_mig_happens is not None:
                    self.all_cts_migmats[ep] = M
                else:
                    self.all_cts_migmats[ep] = None
                    
        
        self.all_nus = matrix(self.all_nus.astype(str))
        self.all_gammas = matrix(self.all_gammas.astype(str))
        

    def get_M(self,n,nelts):
        nelts = np.array(nelts).astype(int)
        M = mtlb.repmat(mpf(0),nelts,nelts)
        for i in range(1,nelts+1):
            for j in range(1,nelts+1):
                M[i-1,j-1] = binomial(i-1,j-1) / binomial(n,j-1)
        return M

    def get_Minv(self,n,nelts):
        nelts = np.array(nelts).astype(int)
        Minv = mtlb.repmat(mpf(0),nelts,nelts)
        for i in range(1,nelts+1):
            for j in range(1,nelts+1):
                Minv[i-1,j-1] = (mpf(-1) ** mpf(i-j)) * binomial(n,i-1) * binomial(i-1,j-1)
        return Minv    
        
    
    def get_elts(self, arr, inds):
        arrout = []
        for i in range(0,len(inds)):
            arrout.append(arr[inds[i]])
        return arrout
        
    def rf_vec(self, arr, k):
        arrout = mtlb.repmat(mpf(0),len(arr),1) 
        for i in range(0,len(arrout)):
            arrout[i] = rf(arr[i],k)
        return arrout
    
    def div_vec(self, arr1, arr2):
        len1 = len(arr1)
        len2 = len(arr2)
        if len1 == len2:
            arrout = mtlb.repmat(mpf(0),len1,1) 
            for i in range(0,len1):
                arrout[i] = arr1[i] / arr2[i]
        elif len1 == 1:
            arrout = mtlb.repmat(mpf(0),len2,1) 
            for i in range(0,len2):
                arrout[i] = arr1[0] / arr2[i]
        else:
            print "Len(arr1) must equal len(arr2)."
                
        return arrout

    def mult_vec(self, arr1, arr2):
        len1 = len(arr1)
        len2 = len(arr2)
        assert(len1 == len2)
        arrout = mtlb.repmat(mpf(0),len1,1) 
        for i in range(0,len1):
            arrout[i] = arr1[i] * arr2[i]
        return arrout
        
    def exp_vec(self, arr):
        len1 = len(arr)
        arrout = mtlb.repmat(mpf(0),len1,1) 
        for i in range(0,len1):
            arrout[i] = exp(arr[i])
        return arrout
        
    def ei_vec(self, arr):
        len1 = len(arr)
        arrout = mtlb.repmat(mpf(0),len1,1) 
        for i in range(0,len1):
            arrout[i] = ei(arr[i])
        return arrout


class NLFTprecise:
    def __init__(self, hist, ns, tubd = 10):
        self.mig_indicator = None        
        self.all_ts = None
        self.all_nus = None
        self.all_gammas = None
        self.all_migs = None        
        self.nuref = 1 #Reference population scaling
        self.tubd = tubd #Upper bound for integrating the ENLFT... In other words, we consider sites in the SFS arising since time tubd
        self.hist = hist 
        self.dt = self.hist.plotdt       
        self.ns = ns        
        self.npops = np.array(self.hist.npops).astype(int)
        
        self.nus = self.hist.nus
        self.ts = self.hist.ts
        self.expmat = self.hist.expmat
        self.gammas = self.hist.gammas
        self.migs = self.hist.migs
        
        
        self.migs_sorted = copy.deepcopy(self.migs)
        self.migs_sorted = sorted(self.migs_sorted,key=lambda x: x[0])
        
        self.tgrid = None
        self.NLFT = mtlb.repmat(None,self.npops,self.npops)

                    

    def get_nlft_cts_migration(self):
        self.get_whole_history()
        ns = matrix(np.array(self.ns).astype(str))

        for pop in range(0,self.npops):
            nupto = np.zeros((self.npops,1))
            nupto[pop] = ns[pop]*1 #Copy by value
            
            NLFT = []
            tgrid = []
            for i in range(0,self.npops):
                NLFT = NLFT + [[]]
                tgrid = tgrid + [[]]
                
            for i in range(0,len(self.all_ts)-1):
                #if np.trace(self.all_cts_migmats[i]) == 0: #If this epoch contains no continuous migration between any pair of populations          
                if self.all_cts_migmats[i] is None: #If this epoch contains no continuous migration between any pair of populations          
                    nlft_nupto_tgrid = self.get_nlft_point_migration_1epoch(i, nupto)                
                else:
                    nlft_nupto_tgrid = self.get_nlft_cts_migration_1epoch(i, nupto)
                    
                for j in range(0,self.npops):
                    NLFT[j] = np.concatenate((NLFT[j],nlft_nupto_tgrid[0][j,:]),axis=0)
                    nupto[j] = nlft_nupto_tgrid[1][j] #Pass by value
                    tgrid[j] = np.concatenate((tgrid[j],nlft_nupto_tgrid[2]),axis=0)
                    

                #if self.mig_indicator[i+1] and self.all_migs[mig_ct,4] == 0: #a point migration happens
                if self.mig_indicator[i+1]:
                    mig_ct = self.mig_inds[i+1]
                    mig = self.all_migs[mig_ct,:]
                    if mig[3] >= 0:
                        nupto[int(mig[2])-1] = nupto[int(mig[2])-1] + nupto[int(mig[1])-1] * mig[3]
                        nupto[int(mig[1])-1] = nupto[int(mig[1])-1] * (1 - mig[3])
                    else:
                        nupto[int(mig[1])-1] = nupto[int(mig[1])-1] - nupto[int(mig[2])-1] * mig[3]
                        nupto[int(mig[2])-1] = nupto[int(mig[2])-1] * (1 + mig[3])

            
            for i in range(0,self.npops):
                self.NLFT[pop][i] = NLFT[i]

        self.tgrid = tgrid
    

    def get_nlft_point_migration_1epoch(self, epind, ns):
        T = self.all_ts[epind+1] - self.all_ts[epind]

        ts = []
        for i in range(0,50):
            ts = np.concatenate((ts,[i*T/50]),axis=0)
        
        nlft = np.zeros((self.npops,len(ts)))
        
        for i in range(0,self.npops):
            if ns[i] > 1:
                if self.all_gammas[i,epind] == 0:
                    for j in range(0,len(ts)):
                        temp = ns[i] / (ns[i] - (ns[i]-1) * exp(- ts[j] / (2*self.all_nus[i,epind])))
                        nlft[i,j] = round(temp,4)
                    ns[i] = round(ns[i] / (ns[i] - (ns[i]-1) * exp(- ts[-1] / (2*self.all_nus[i,epind]))),4)
                else:
                    for j in range(0,len(ts)):
                        temp = ns[i] / (ns[i] - (ns[i]-1) * exp((exp(- self.all_gammas[i,epind]*ts[j]) - 1) / (2*self.all_nus[i,epind]*self.all_gammas[i,epind])))
                        nlft[i,j] = round(temp,4)
                    ns[i] = round(ns[i] / (ns[i] - (ns[i]-1) * exp((exp(- self.all_gammas[i,epind]*ts[-1]) - 1) / (2*self.all_nus[i,epind]*self.all_gammas[i,epind]))),4)
            else:
                for j in range(0,len(ts)):                        
                    nlft[i,j] = round(ns[i],4)
                ns[i] = round(ns[i],4)

        tgrid = self.all_ts[epind] + ts
        
        
        return [nlft,ns,tgrid]  

      
    def get_nlft_cts_migration_1epoch(self, epind, ns):
        nus_start = self.all_nus[:,epind]      
        t = self.all_ts[epind+1] - self.all_ts[epind]
        M = self.all_cts_migmats[epind]
        gams = self.all_gammas[:,epind]
                
        
        dt = 0.001
        J = np.array(round(t/dt)).astype(int)
        tgrid = []
        for i in range(0,J):
            tgrid = np.concatenate((tgrid,[self.all_ts[epind] + i*dt]),axis=0)
        
        nlft = np.zeros((self.npops,len(tgrid)))

        for j in range(0,J):            
            nus = mtlb.repmat(mpf(0),1,self.npops)[0]
            for pop in range(0,self.npops):
                nus[pop] = nus_start[pop] * exp(gams[pop] * j * dt)

            for pop in range(0,self.npops):
                Mdot = 0
                for pop1 in range(0,self.npops):
                    Mdot = Mdot + M[pop][pop1] * ns[pop1]
                
                ns[pop] = ns[pop] + dt * (-1/nus[pop]) * max(0,ns[pop] * (ns[pop] - 1)/2) + dt * Mdot #Note: np.maximum is elementwise, for future reference
                nlft[pop][j] = ns[pop]
        

        return [nlft,ns,tgrid]


    def get_whole_history(self):        
        #Get gammas from expmat and ns
        for i in range(0,len(self.expmat)):
            for j in range(0,len(self.expmat[i])):
                if not (self.expmat[i][j] is None):
                    self.gammas[i][j] = self.expmat[i][j]
                elif j <= len(self.expmat[i])-1:                    
                    Nf = self.nus[i][j]
                    No = self.nus[i][j+1]
                    t = self.ts[i][j+1] - self.ts[i][j]
                    #print "NP>>>>>>>>>>>>>>>>>>>>"
                    #print np
                    self.gammas[i][j] = np.log(No/Nf)/t
                else:
                    self.gammas[i][j] = 0
        
        self.migs_sorted = copy.deepcopy(self.migs)
        self.migs_sorted = sorted(self.migs_sorted,key=lambda x: x[0])
        all_ts = np.unique(self.ts[0])
        if self.npops > 1:
            for i in range(1,self.npops):
                all_ts = np.union1d(all_ts,self.ts[i])
        mig_ts = []
        mig_inds = []
        for i in range(0,len(self.migs)):
            all_ts = np.union1d(all_ts,[self.migs_sorted[i][0]])
            if self.migs_sorted[i][4] == 0:
                mig_ts = np.concatenate((mig_ts,[self.migs_sorted[i][0]]))
                mig_inds = np.concatenate((mig_inds,[i]))
        mig_stop_ts = np.zeros(len(self.migs_sorted))
        for i in range(0,len(self.migs)):
            all_ts = np.union1d(all_ts,[self.migs_sorted[i][0] + self.migs_sorted[i][4]])
            mig_stop_ts[i] = self.migs_sorted[i][0] + self.migs_sorted[i][4]
        all_ts = np.union1d(all_ts,[self.tubd])
        self.all_ts = matrix(all_ts.astype(str))
        self.mig_indicator = np.in1d(all_ts,mig_ts)
        self.mig_inds = mtlb.repmat(None,1,len(self.all_ts))[0]
        ct = 0
        for i in range(0,len(self.all_ts)):
            if self.mig_indicator[i]:
                self.mig_inds[i] = mig_inds[ct]
                ct = ct+1
        self.mig_stop_indicator = np.in1d(all_ts,mig_stop_ts)
        if len(self.migs_sorted) > 0:
            self.all_migs = matrix(np.array(self.migs_sorted).astype(str))
        else:
            self.all_migs = []

        neps = len(all_ts)
        self.all_nus = np.zeros((self.npops,len(all_ts)))
        self.all_gammas = np.zeros((self.npops,len(all_ts)))
        for i in range(0,self.npops):
            for j in range(0,neps):
                epind = np.sum(np.array(self.ts[i]) <= all_ts[j]) - 1#index of the epoch all_ts[j] is in
                self.all_gammas[i][j] = self.gammas[i][epind]
                if self.gammas[i][epind] == 0:
                    self.all_nus[i][j] = self.nus[i][epind]
                else:
                    self.all_nus[i][j] = self.nus[i][epind] * np.exp(self.gammas[i][epind] * (all_ts[j] - self.ts[i][epind]))
        
        self.all_cts_migmats = mtlb.repmat(None,1,neps)[0]
        for ep in range(0,neps):
            t = all_ts[ep]            
            #M = np.eye(self.npops)
            M = np.zeros((self.npops,self.npops))
            cts_mig_happens = None
            for m in range(0,len(self.migs)):
                if self.migs[m][4] > 0 and self.migs[m][0] <= t and t < self.migs[m][0] + self.migs[m][4]:
                    cts_mig_happens = 1
                    if self.migs[m][3] >= 0:
                        pop1ind = self.migs[m][1].astype(int) - 1
                        pop2ind = self.migs[m][2].astype(int) - 1
                    else:
                        pop1ind = self.migs[m][2].astype(int) - 1
                        pop2ind = self.migs[m][1].astype(int) - 1                        
                    M[pop2ind][pop1ind] = np.abs(self.migs[m][3])
                    M[pop1ind][pop1ind] = M[pop1ind][pop1ind] - np.abs(self.migs[m][3])
                if cts_mig_happens is not None:
                    self.all_cts_migmats[ep] = M
                else:
                    self.all_cts_migmats[ep] = None
                    
        
        self.all_nus = matrix(self.all_nus.astype(str))
        self.all_gammas = matrix(self.all_gammas.astype(str))
        







class NLFTprecise_point_migrations:
    def __init__(self, hist, nuref, ns, tubd, plotdt = 0.005):
        self.hist = hist
    	self.ns = ns
    	self.plotdt = plotdt
        self.mig_indicator = None        
        self.all_ts = None
        self.all_nus = None
        self.all_gammas = None 
        self.nuref = nuref #Reference population scaling
        self.tubd = tubd #Upper bound on time
        self.hist = hist                
           
        self.npops = self.hist.npops        
        self.nus = self.hist.nus
        self.ts = self.hist.ts
        self.expmat = self.hist.expmat
        self.gammas = self.hist.gammas
        #print 'GAMMAS:   ------------------------'
        #print self.gammas
        self.migs = self.hist.migs
        
        self.migs_sorted = deepcopy(self.migs)
        self.migs_sorted = sorted(self.migs_sorted,key=lambda x: x[0])

        self.temp_tgrid = np.arange(0,tubd + plotdt, plotdt)
        self.NLFT = None
                    
                    
    def get_NLFT_point_migrations(self):
        self.get_whole_history()
                
        #print 'ALL ts: >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
        #print self.all_ts
        #print 'ALL gammas: >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
        #print self.all_gammas        
        ns = np.array(deepcopy(self.ns))
        self.NLFT = np.zeros((self.npops,len(self.all_ts),self.npops))
        for pop in range(0,self.hist.npops):
            self.NLFT[pop,0,pop] = ns[pop]
        
        mig_ct = 0
        for i in range(1,len(self.all_ts)):
            dt = self.all_ts[i] - self.all_ts[i-1]
            for pop in range(0,self.npops):                
                nown = self.NLFT[:,i-1,pop]
                newn = np.array([0]*self.npops)
                tau = 0
                g = self.all_gammas[pop][i-1]
                nu = self.all_nus[pop][i-1]
                if g == 0:
                    tau = dt * self.nuref / nu
                else:
                    tau = (np.exp(g * dt) - 1) * self.nuref / (nu * g)
        		
                chg_inds = (nown >= 1) 
                no_chg_inds = (nown < 1)
                #print 'chg inds: >>>>>>>>>>>>>>>>>>>>>>>>>'
                #print chg_inds
                #print 'nown: >>>>>>>>>>>>>>>>>>>>>>>'
                #print nown
                #print 'newn: >>>>>>>>>>>>>>>>>>>>>>>>>'
                #print newn
                #print 'NOWN CHANGE INDS: >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
                #print nown[chg_inds]
                #print 'NEWN change inds: >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
                #print newn[chg_inds]
                newn[chg_inds] = nown[chg_inds] / (nown[chg_inds] - (nown[chg_inds] - 1) * np.exp(-tau/2))
                newn[no_chg_inds] = nown[no_chg_inds]
                self.NLFT[:,i,pop] = newn
        	
            if self.mig_indicator[i]:
                pop_from = self.migs_sorted[mig_ct][1]-1 #Minus 1 because we want zero-indexing
                pop_to = self.migs_sorted[mig_ct][2]-1
                #print 'migs_sorted: >>>>>>>>>>>>>>>>>>>>>>>'
                #print self.migs_sorted[mig_ct][3]
                moven = self.NLFT[:,i,pop_from] * self.migs_sorted[mig_ct][3]
                self.NLFT[:,i,pop_from] = self.NLFT[:,i,pop_from] - moven
                self.NLFT[:,i,pop_to] = self.NLFT[:,i,pop_to] + moven
                mig_ct = mig_ct + 1
        	

    def get_whole_history(self):
        #print 'GOT TO get_whole_history():>>>>>>>>>>>'

        #print 'self.temp_grid: >>>>>>>>>>>>>>>>>>>>>'
        #print self.temp_tgrid
        
        #Get gammas from expmat and ns
        for i in range(0,len(self.expmat)):
            for j in range(0,len(self.expmat[i])):
                if not (self.expmat[i][j] is None):
                    self.gammas[i][j] = self.expmat[i][j]
                elif j <= len(self.expmat[i])-1:                    
                    Nf = self.nus[i][j]
                    No = self.nus[i][j+1]
                    t = self.ts[i][j+1] - self.ts[i][j]
                    self.gammas[i][j] = np.log(No/Nf)/t
                else:
                    self.gammas[i][j] = 0
        
        self.migs_sorted = deepcopy(self.migs)
        self.migs_sorted = sorted(self.migs_sorted,key=lambda x: x[0])
        self.all_ts = np.unique(self.ts[0])
        if self.npops > 1:
            for i in range(1,self.npops):
                self.all_ts = np.union1d(self.all_ts,self.ts[i])
        self.all_ts = np.union1d(self.all_ts, self.temp_tgrid)
        mig_ts = np.zeros(len(self.migs_sorted))
        for i in range(0,len(self.migs)):
            self.all_ts = np.union1d(self.all_ts,[self.migs_sorted[i][0]])
            mig_ts[i] = self.migs_sorted[i][0]
        self.all_ts = np.union1d(self.all_ts,[self.tubd])
        #self.all_ts = matrix(all_ts.astype(str))
        self.mig_indicator = np.in1d(self.all_ts,mig_ts)
        #self.all_migs = matrix(np.array(self.migs_sorted).astype(str))

        neps = len(self.all_ts)
        self.all_nus = np.zeros((self.npops,len(self.all_ts)))
        self.all_gammas = np.zeros((self.npops,len(self.all_ts)))
        for i in range(0,self.npops):
            for j in range(0,neps):
                epind = np.sum(np.array(self.ts[i]) <= self.all_ts[j]) - 1#index of the epoch all_ts[j] is in
                self.all_gammas[i][j] = self.gammas[i][epind]
                if self.gammas[i][epind] == 0:
                    self.all_nus[i][j] = self.nus[i][epind]
                else:
                    self.all_nus[i][j] = self.nus[i][epind] * np.exp(self.gammas[i][epind] * (self.all_ts[j] - self.ts[i][epind]))




#nu_2infer: ndarray [obj1,obj2,...] where obj = [popind,epind].... optional: use obj = [popind,epind,grow_indic,cons1,cons2,...], consi is the epoch indicator of an epoch in population 'popind' whose size is constrained in some way to the size in epoch 'epind'. Set 'grow_indic' to None to constrain the sizes in epochs cons1,cons2,... to change exponentially starting with size nus[popind][epind] at time ts[popind][epind] and ending with size nus[popind][nextind] at time ts[popind][nextind], where nextind is the index of the epoch following the last 'cons' epoch. Set 'grow_ind' to something that is not None to constrain the sizes in cons1,cons2,... to equal the size nus[popind][epind].
#t_2infer: ndarray [obj1,obj2,...] where obj = [popind,epind]... optional: use obj = [popind,epind,cons1,cons2,cons3,...], where consi is the index of a migration event to which the time should be constrained
#mig_mag_2infer: ndarray [obj1,obj2,...] where obj = [mig_event_index]
#mig_t_2infer: ndarray [obj1,obj2,...] where obj = [mig_event_index,lbd,ubd]
#If you want to infer the history using the JUSFS, set use_jsfs = False and set observed_jusfs to the observed JUSFS
#If you want to infer the history using the JSFS, set use_jsfs = True and set observed_jusfs to the observed *JSFS*
class JUSFS_optimizer:
    def __init__(self, jusfs_object, observed_jusfs, nu_2infer, t_2infer, mig_mag_2infer, mig_t_2infer, max_nu, max_t, num_start_posits = 5, use_jsfs = False):                
        self.use_jsfs = use_jsfs
        self.xmins = np.array([None]*num_start_posits)
        self.fvals = np.array([None]*num_start_posits)

        #print 'MIGS OPTIMIZER (START): -----------------------'
        #print jusfs_object.migs                
                        
        self.jusfs_obj = jusfs_object
        self.obs_jusfs = np.array(observed_jusfs.tolist(),dtype=np.float64)
        self.tstart = deepcopy(np.array(self.jusfs_obj.hist.ts)) #Copy by value        

        #print 'MIGS OPTIMIZER (START2): -----------------------'
        #print self.jusfs_obj.migs        
                        
        self.num_start_posits = num_start_posits
        self.max_nu = max_nu
        self.max_t = max_t #This should be changed to self.jusfs_obj.tubd
        
        self.buffer = 0.00000000001 #prevents pop sizes and epoch durations from being zero
        
        self.nu_2infer = nu_2infer
        self.t_2infer = t_2infer
        self.mig_t_2infer = mig_t_2infer
        self.mig_mag_2infer = mig_mag_2infer
        
        self.t_inf_eps = [None] * self.jusfs_obj.npops #Store info about which epochs time is inferred for in a handy way
        for i in range(0,self.jusfs_obj.npops): #Initialize an array
            self.t_inf_eps[i] = np.array([[False,None]] * len(self.jusfs_obj.hist.nus[i]))
        for i in range(0,len(self.t_2infer)):
            popind = self.t_2infer[i][0]
            epind = self.t_2infer[i][1]
            self.t_inf_eps[popind][epind][0] = True #Indicate that we infer in this epoch/population.
            self.t_inf_eps[popind][epind][1] = i #Record the index of the object in self.ep2infer        
        
        self.t_sim_inds = None #Initialize an object that's useful for getting random starting conditions x0
        self.nparams = len(self.t_2infer) + len(self.nu_2infer) + len(self.mig_mag_2infer) + len(self.mig_t_2infer) #number of parameters to infer
        self.x0 = np.zeros(self.nparams) #Initialize x0

        #print 'MIGS OPTIMIZER (BEFORE CONSTRAINTS): -----------------------'
        #print self.jusfs_obj.migs
                
        #Set up constraints on optimization
        self.cons = []
        i = 0
        xdim = 0
        for i in range(0,len(t_2infer)):
            popind = copy.deepcopy(self.t_2infer[i][0])
            epind = copy.deepcopy(self.t_2infer[i][1])
            ind = copy.deepcopy(xdim)+0
            if epind > 0:
                if not self.t_inf_eps[popind][epind-1][0]: #If we don't infer t for the previous epoch
                    #print 'JUSFS obj history ts: >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
                    prev_ep_time = copy.deepcopy(self.jusfs_obj.hist.ts[popind][epind-1])
                    #self.cons = self.cons + [{'type' : 'ineq' , 'fun' : lambda x: x[ind] - max(self.buffer,prev_ep_time+self.buffer)}]
                    #self.cons = self.cons + [{'type' : 'ineq' , 'fun' : lambda x: x[ind] - prev_ep_time+self.buffer}]
                    self.cons = self.cons + [{'type' : 'ineq' , 'fun' : self.lbd_const(ind,prev_ep_time+self.buffer)}]
                else:
                    x_ind = self.t_inf_eps[popind][epind-1][1]
                    #self.cons = self.cons + [{'type' : 'ineq' , 'fun' : lambda x: x[ind] - max(self.buffer,x[x_ind]+self.buffer)}]
                    self.cons = self.cons + [{'type' : 'ineq' , 'fun' : lambda x: x[ind] - x[x_ind]+self.buffer}]
                    #self.cons = self.cons + [{'type' : 'ineq' , 'fun' : self.lbd_const(ind,x[x_ind]+self.buffer)}]
            else: #In principle, we should never execute this. Inference on present time is no allowed.
                #self.cons = self.cons + [{'type' : 'ineq' , 'fun' : lambda x: x[ind] - max(self.buffer,self.buffer)}]
                #self.cons = self.cons + [{'type' : 'ineq' , 'fun' : lambda x: x[ind] - self.buffer}]
                self.cons = self.cons + [{'type' : 'ineq' , 'fun' : self.lbd_const(ind,self.buffer)}]
            if epind < len(self.jusfs_obj.hist.nus[popind]) - 1:
                if not self.t_inf_eps[popind][epind+1][0]: #If we don't infer t for the next epoch
                    next_ep_time = copy.deepcopy(self.jusfs_obj.hist.ts[popind][epind+1])+0
                    #self.cons = self.cons + [{'type' : 'ineq' , 'fun' : lambda x: next_ep_time - max(self.buffer,x[ind]+self.buffer)}]
                    #self.cons = self.cons + [{'type' : 'ineq' , 'fun' : lambda x: next_ep_time - x[ind]+self.buffer}]
                    self.cons = self.cons + [{'type' : 'ineq' , 'fun' : self.ubd_const(ind,next_ep_time - self.buffer)}]
                else:
                    x_ind = copy.deepcopy(self.t_inf_eps[popind][epind+1][1])+0
                    #self.cons = self.cons + [{'type' : 'ineq' , 'fun' : lambda x: x[x_ind] - max(self.buffer,x[ind]+self.buffer)}]
                    self.cons = self.cons + [{'type' : 'ineq' , 'fun' : lambda x: x[x_ind] - x[ind]+self.buffer}]
                    #self.cons = self.cons + [{'type' : 'ineq' , 'fun' : self.ubd_const(ind,x[x_ind] - self.buffer)}]
            else:
                #self.cons = self.cons + [{'type' : 'ineq' , 'fun' : lambda x: self.max_t - max(self.buffer,x[ind]+self.buffer)}]
                #self.cons = self.cons + [{'type' : 'ineq' , 'fun' : lambda x: self.max_t - x[ind]+self.buffer}]
                self.cons = self.cons + [{'type' : 'ineq' , 'fun' : self.ubd_const(ind,self.max_t)}]
            xdim = xdim + 1

        #print 'MIGS OPTIMIZER (DURING CONSTRAINTS 1): -----------------------'
        #print self.jusfs_obj.migs                
        
        for i in range(0,len(self.nu_2infer)):
            popind = self.nu_2infer[i][0]
            epind = self.nu_2infer[i][1]
            ind = copy.deepcopy(xdim)+0
            #self.cons = self.cons + [{'type' : 'ineq' , 'fun' : lambda x: x[ind] - self.buffer}]
            #self.cons = self.cons + [{'type' : 'ineq' , 'fun' : lambda x: self.max_nu - x[ind]}]
            self.cons = self.cons + [{'type' : 'ineq' , 'fun' : self.lbd_const(ind,self.buffer)}]
            self.cons = self.cons + [{'type' : 'ineq' , 'fun' : self.ubd_const(ind,self.max_nu[popind] - self.buffer)}]
            xdim = xdim + 1

        #print 'MIGS OPTIMIZER (DURING CONSTRAINTS 2): -----------------------'
        #print self.jusfs_obj.migs
                
        for j in range(0,len(self.mig_mag_2infer)):
            ind = copy.deepcopy(xdim)+0
            self.cons = self.cons + [{'type' : 'ineq' , 'fun' : self.lbd_const(ind,-1)}]
            self.cons = self.cons + [{'type' : 'ineq' , 'fun' : self.ubd_const(ind,1)}]
            xdim = xdim + 1
            
        #print 'MIGS OPTIMIZER (DURING CONSTRAINTS 3): -----------------------'
        #print self.jusfs_obj.migs            
        
        for i in range(0,len(self.mig_t_2infer)):
            ind = copy.deepcopy(xdim)+0
            if hasattr(self.mig_t_2infer[i], "__len__"):
                if self.mig_t_2infer[i][1] is None:
                    self.cons = self.cons + [{'type' : 'ineq' , 'fun' : self.lbd_const(ind,self.buffer)}]
                else:
                    self.cons = self.cons + [{'type' : 'ineq' , 'fun' : self.lbd_const(ind,max(self.buffer,self.mig_t_2infer[i][1]+self.buffer))}]
                if self.mig_t_2infer[i][2] is None:
                    self.cons = self.cons + [{'type' : 'ineq' , 'fun' : self.ubd_const(ind,self.max_t-self.buffer)}]
                else:
                    self.cons = self.cons + [{'type' : 'ineq' , 'fun' : self.ubd_const(ind,min(self.max_t-self.buffer,self.mig_t_2infer[i][2]-self.buffer))}]
            else:
                self.cons = self.cons + [{'type' : 'ineq' , 'fun' : self.lbd_const(ind,self.buffer)}]
                self.cons = self.cons + [{'type' : 'ineq' , 'fun' : self.ubd_const(ind,self.max_t - self.buffer)}]
            xdim = xdim + 1

        #print 'MIGS OPTIMIZER (AFTER CONSTRAINTS): -----------------------'
        #print self.jusfs_obj.migs


    def lbd_const(self, ind, bd):
        return lambda x: x[ind] - max(self.buffer,bd)

        
    def ubd_const(self, ind, bd):
        return lambda x: bd - x[ind]

    
    def optimize_jusfs(self):
        
        #print 'MIGS OPTIMIZE (START): -----------------------'
        #print self.jusfs_obj.migs
        
        i = 0
        while (i < self.num_start_posits):
            self.get_random_x0()
            temp = minimize(self.eval_obj_fun, self.x0, method='SLSQP', constraints = self.cons, tol = 1e-12, options={'disp': True, 'maxiter': 500})
            #temp = minimize(self.eval_obj_fun, self.x0, method='Nelder-Mead', constraints = self.cons, tol = 1e-10, options={'disp': True, 'maxiter': 200})
            if temp.success:
                self.xmins[i] = temp.x
                self.fvals[i] = temp.fun
                i = i+1
        
        #print 'MIGS OPTIMIZE (END): -----------------------'
        #print self.jusfs_obj.migs


    def get_random_x0(self):
        
        #print 'MIGS GET RANDOM (START): -----------------------'
        #print self.jusfs_obj.migs
        
        self.t_sim_inds = [None] * self.jusfs_obj.npops
        for popind in range(0,self.jusfs_obj.npops):
            self.t_sim_inds[popind] = [None] * len(self.jusfs_obj.hist.nus[popind]) #WARNING: THIS MAY BE INCORRECT! MAYBE USE NEXT LINE. I'M PRETTY SURE THIS SHOULD BE .NUS[POPIND] THOUGH.
            #self.t_sim_inds[popind] = [None] * len(self.jusfs_obj.hist.nus)                
        for popind in range(0,self.jusfs_obj.npops):
            for epind in range(0,len(self.t_inf_eps[popind])):
                if self.t_inf_eps[popind][epind][0] == False:
                    self.t_sim_inds[popind][epind] = self.jusfs_obj.hist.ts[popind][epind]
        
        self.x0 = np.zeros(self.nparams)
        i = 0
        xdim = 0
        #Simulate t values
        for i in range(0,len(self.t_2infer)):
            popind = self.t_2infer[i][0]
            epind = self.t_2infer[i][1]
            lbd = 0
            ubd = 0
            lbd_ep_ind = epind
            ubd_ep_ind = epind
            while lbd_ep_ind > 0 and self.t_sim_inds[popind][lbd_ep_ind-1] is None: #Scan until we find the first non-None time
                lbd_ep_ind = lbd_ep_ind - 1
            while ubd_ep_ind < len(self.t_sim_inds[popind])-1 and self.t_sim_inds[popind][ubd_ep_ind+1] is None:
                ubd_ep_ind = ubd_ep_ind + 1
            if lbd_ep_ind > 0:
                lbd = max(0,self.tstart[popind][lbd_ep_ind])
                #lbd = self.jusfs_obj.hist.ts[popind][lbd_ep_ind]
            else: #Shortest time should be zero
                lbd = 0
            if ubd_ep_ind < len(self.t_sim_inds[popind])-1:
                ubd = self.tstart[popind][ubd_ep_ind]
                #ubd = self.jusfs_obj.hist.ts[popind][ubd_ep_ind]
            else:
                ubd = deepcopy(self.jusfs_obj.tubd)
            #print "jusfs_obj.hist.ts: "
            #print self.jusfs_obj.hist.ts
            #print "popind, lbd_ep_ind: "
            #print popind, lbd_ep_ind     
            #print "lbd, ubd: "           
            #print lbd, ubd
            tsim = np.random.uniform(low=lbd+self.buffer, high=ubd-self.buffer, size=None)
            self.x0[xdim] = tsim
            self.t_sim_inds[popind][epind] = tsim
            xdim = xdim + 1
        
        for i in range(0,len(self.nu_2infer)):
            popind = self.nu_2infer[i][0]
            nusim = np.random.uniform(low=self.buffer, high=self.max_nu[popind]-self.buffer, size=None)
            self.x0[xdim] = nusim
            xdim = xdim + 1
        
        for i in range(0,len(self.mig_mag_2infer)):
            self.x0[xdim] = np.random.uniform(low=-1.0, high=1.0, size=None)
            xdim = xdim + 1
        
        for i in range(0,len(self.mig_t_2infer)):
            if hasattr(self.mig_t_2infer[i], "__len__"):
                if (self.mig_t_2infer[i][1] is None) and (self.mig_t_2infer[i][2] is None):
                    self.x0[xdim] = np.random.uniform(low=0.0+self.buffer, high=self.max_t-self.buffer, size=None)
                elif (self.mig_t_2infer[i][1] is not None) and (self.mig_t_2infer[i][2] is None):
                    self.x0[xdim] = np.random.uniform(low= max(0.0+self.buffer,self.mig_t_2infer[i][1]+self.buffer), high=self.max_t-self.buffer, size=None)
                elif (self.mig_t_2infer[i][1] is None) and (self.mig_t_2infer[i][2] is not None):
                    self.x0[xdim] = np.random.uniform(low= 0.0+self.buffer, high= min(self.max_t,self.mig_t_2infer[i][2]) - self.buffer, size=None)
                elif (self.mig_t_2infer[i][1] is not None) and (self.mig_t_2infer[i][2] is not None):
                    self.x0[xdim] = np.random.uniform(low= max(0.0,self.mig_t_2infer[i][1]) + self.buffer, high= min(self.max_t,self.mig_t_2infer[i][2]) - self.buffer, size=None)
            else:
                self.x0[xdim] = np.random.uniform(low=self.buffer, high=self.max_t-self.buffer, size=None)
            xdim = xdim + 1
        
        #print 'MIGS GET RANDOM (END): -----------------------'
        #print self.jusfs_obj.migs

    def eval_obj_fun(self, x):    
        i = 0
        xdim = 0
        
        if min(x) < 0:
            print "Optimizer out of bounds (negative value).>>>>>>>>>>>>"
            return 1
        
        #print 'MIGS 1: -----------------------'
        #print self.jusfs_obj.migs
        
        #print "x >>>>>>>>>>>>>>>>>>"
        #print x
        
        for i in range(0,len(self.t_2infer)):
            popind = self.t_2infer[i][0]
            epind = self.t_2infer[i][1]
            self.jusfs_obj.ts[popind][epind] = x[i]
            for j in range(2,len(self.t_2infer[i])):
                self.jusfs_obj.migs[self.t_2infer[i][j]][0] = max(self.buffer,x[i]) #FORCE THIS TO BE POSITIVE. SOMETIMES THE OPTIMIZER TRIES TO EVALUATE NEGATIVE NUMBERS
            xdim = xdim + 1

        for i in range(0,len(self.nu_2infer)):
            popind = self.nu_2infer[i][0]
            epind = self.nu_2infer[i][1]        
            self.jusfs_obj.nus[popind][epind] = max(self.buffer,x[xdim]) #FORCE THIS TO BE POSITIVE. SOMETIMES THE OPTIMIZER TRIES TO EVALUATE NEGATIVE NUMBERS
            if len(self.nu_2infer[i]) > 2:
                if self.nu_2infer[i][2] is not None: #Then sizes are constrained to be equal
                    for j in range(3,len(self.nu_2infer[i])):
                        ep_epind = self.nu_2infer[i][j]
                        self.jusfs_obj.nus[popind][ep_epind] = self.jusfs_obj.nus[popind][epind]
                else: #Then sizes are constrained to change exponentially
                    #print "nu_2infer[i]>>>>>>>>>>>>>>"
                    #print self.nu_2infer[i]
                    next_epind = self.nu_2infer[i][-1]+1 #Index of the epoch following the last constrained epoch
                    nu_inf_ind = None
                    for j in range(0,len(self.nu_2infer)):
                        if popind == self.nu_2infer[j][0] and next_epind == self.nu_2infer[j][1]: #Then we infer its size
                            nu_inf_ind = j
                    t_inf_ind = None
                    for j in range(0,len(self.t_2infer)):
                        if popind == self.t_2infer[j][0] and next_epind == self.t_2infer[j][1]: #Then we infer its time
                            t_inf_ind = j
                    nuval = None #nu in the following epoch
                    if nu_inf_ind is None:
                        nuval = max(self.buffer,self.jusfs_obj.nus[popind][next_epind]) #FORCE THIS TO BE POSITIVE. SOMETIMES THE OPTIMIZER TRIES TO EVALUATE NEGATIVE NUMBERS
                    else:
                        nuval = max(self.buffer,x[len(self.t_2infer) + nu_inf_ind]) #FORCE THIS TO BE POSITIVE. SOMETIMES THE OPTIMIZER TRIES TO EVALUATE NEGATIVE NUMBERS
                    tval = None #Time at which the following epoch begins
                    if t_inf_ind is None:
                        tval = max(self.buffer,self.jusfs_obj.ts[popind][next_epind]) #FORCE THIS TO BE POSITIVE. SOMETIMES THE OPTIMIZER TRIES TO EVALUATE NEGATIVE NUMBERS
                    else:
                        tval = max(self.buffer,x[t_inf_ind]) #FORCE THIS TO BE POSITIVE. SOMETIMES THE OPTIMIZER TRIES TO EVALUATE NEGATIVE NUMBERS
                    tstart = self.jusfs_obj.ts[popind][epind]
                    nustart = self.jusfs_obj.nus[popind][epind]
                    gam = (1 / (tval - tstart)) * log(nuval/nustart)
                    for j in range(3,len(self.nu_2infer[i])):
                        ep_epind = self.nu_2infer[i][j]
                        tep = self.jusfs_obj.ts[popind][ep_epind]
                        ep_nu = nustart * exp(gam * (tep - tstart))
                        self.jusfs_obj.nus[popind][ep_epind] = max(self.buffer,ep_nu)
            xdim = xdim + 1
        
        ##print 'MIG MAG 2 infer: -----------------------'
        ##print self.mig_mag_2infer
        for i in range(0,len(self.mig_mag_2infer)):
            miginds = self.mig_mag_2infer[i]
            if not (hasattr(miginds, "__len__")):
                self.jusfs_obj.migs[miginds][3] = min(1,max(-1,x[xdim])) #FORCE THIS TO BE BIGGER THAN -1. SOMETIMES THE OPTIMIZER TRIES TO EVALUATE stuff outside of the bounds
            else:
                for j in range(0,len(miginds)):
                    self.jusfs_obj.migs[miginds[j]][3] = min(1,max(-1,x[xdim])) #FORCE THIS TO BE BIGGER THAN -1. SOMETIMES THE OPTIMIZER TRIES TO EVALUATE stuff outside of the bounds
            xdim = xdim + 1
        
        ##print 'MIGS 1: -----------------------'
        ##print self.jusfs_obj.migs    
                    
        for i in range(0,len(self.mig_t_2infer)):
            migind = self.mig_t_2infer[i][0]
            self.jusfs_obj.migs[migind][0] = max(self.buffer,x[xdim]) #FORCE THIS TO BE POSITIVE. SOMETIMES THE OPTIMIZER TRIES TO EVALUATE NEGATIVE NUMBERS
            xdim = xdim + 1
        
        #print 'MIGS 2: -----------------------'
        #print self.jusfs_obj.migs
                    
        #for i in range(0,self.jusfs_obj.npops):
        #    for j in range(0,len(self.jusfs_obj.expmat[i])):
        #        if np.isnan(self.jusfs_obj.expmat[i][j]):
        #            Nf = self.jusfs_obj.nus[i][j]
        #            No = self.jusfs_obj.nus[i][j+1]
        #            t = self.jusfs_obj.ts[i][j+1] - self.jusfs_obj.ts[i][j]
        #            self.jusfs_obj.gammas[i][j] = np.log(No/Nf)/t
                
        if not self.use_jsfs:
            self.jusfs_obj.get_JUSFS_point_migrations()
            JUSFS = np.array(self.jusfs_obj.JUSFS.tolist(),dtype=np.float64)
            temp = np.sum(np.log((JUSFS - self.obs_jusfs)**2+1))
            #temp = np.sum(((JUSFS - self.obs_jusfs)**2+1))
        elif self.use_jsfs:
            if self.jusfs_obj.npops == 2: #If there are two populations
                self.jusfs_obj.get_JSFS_point_migrations_2pop()
            else:
                self.jusfs_obj.get_JSFS_point_migrations()
            JSFS = np.array(self.jusfs_obj.JSFS.tolist(),dtype=np.float64)
            temp = np.sum(np.log((JSFS - self.obs_jusfs)**2+1))
            #temp = np.sum(((JSFS - self.obs_jusfs)**2+1))
                
        return temp



def main():   
	np.seterr(all='ignore')
	DGwindow = DemoGrapher()
	tk.mainloop()

