#!/usr/bin/python3
# coding=utf8
#
# Copyright (c) 2017 - Luís Moreira de Sousa
#
# Creates a greyscale choropleth for QGIS. The output is a .sld file. 
#
# Author: Luís Moreira de Sousa (luis.de.sousa[@]protonmail.ch)
# Date: 27-01-2017

from choropleth_gen.choropleth import Choropleth

class Greyscale(Choropleth):
    
    def run(self):
        
        args = self.setArguments()
        
        colour_bottom = [0, 0, 0]
        colour_top = [255, 255, 255]
        
        increment = (args.top - args.bottom) / args.classes
        col_increments = []
        col_increments.append((colour_top[0] - colour_bottom[0]) / args.classes)
        col_increments.append((colour_top[1] - colour_bottom[1]) / args.classes)
        col_increments.append((colour_top[2] - colour_bottom[2]) / args.classes)
        
        for i in range(args.classes):
            
            r =  hex(int(colour_bottom[0] + i * col_increments[0])).split('x')[1]
            g =  hex(int(colour_bottom[1] + i * col_increments[1])).split('x')[1]
            b =  hex(int(colour_bottom[2] + i * col_increments[2])).split('x')[1]
        
            val_bot = args.bottom + i * increment 
            val_top = val_bot + increment
            self.rules = self.rules + self.create_level(val_bot, val_top, r + g + b)
            
        self.dump_sld_file(args.outputFile)
        
        print ("Greyscale choropleth generated successfully.")
        

def main():  
    g = Greyscale()
    g.run()