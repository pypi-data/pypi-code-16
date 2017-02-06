#!/usr/bin/python3
# coding=utf8
#
# Copyright (c) 2017 - Luís Moreira de Sousa
#
# Creates a spectral choropleth for QGIS. The output is a .sld file. 
#
# Author: Luís Moreira de Sousa (luis.de.sousa[@]protonmail.ch)
# Date: 13-01-2017 

from choropleth_gen.choropleth import Choropleth

class Spectral(Choropleth):

    def run(self):
        
        args = self.setArguments()
        
        colours = [[43, 131, 186], [171, 221, 164], [254, 238, 171], [253, 174, 97], [215, 25, 28]]
        col_increments = []
        
        increment = (args.top - args.bottom) / args.classes
        col_levels = int(args.classes / (len(colours) - 1)) 
        
        for i in range(len(colours) - 1):
            
            inc = []
            inc.append((colours[i + 1][0] - colours[i][0]) / col_levels)
            inc.append((colours[i + 1][1] - colours[i][1]) / col_levels)
            inc.append((colours[i + 1][2] - colours[i][2]) / col_levels)
            col_increments.append(inc)
            
        # Colour increments for last class    
        col_increments.append([0,0,0])    
        i_col = 0
        
        for i in range(args.classes):
            
            num_inc = i % col_levels
            
            r = hex(int(colours[i_col][0] + num_inc * col_increments[i_col][0])).split('x')[1]    
            g = hex(int(colours[i_col][1] + num_inc * col_increments[i_col][1])).split('x')[1]
            b = hex(int(colours[i_col][2] + num_inc * col_increments[i_col][2])).split('x')[1]
            
            val_bot = args.bottom + i * increment 
            val_top = val_bot + increment
            self.rules = self.rules + self.create_level(val_bot, val_top, r + g + b)
            
            i_col = int((i + 1) / col_levels)
            
        self.dump_sld_file(args.outputFile)
        
        print ("Spectral choropleth generated successfully.")
        
    
def main():  
    s = Spectral()
    s.run()
                