#!/usr/bin/python3
# coding=utf8
#
# Copyright (c) 2017 - Luís Moreira de Sousa
#
# Abstract class for QGis choropleths. 
#
# Author: Luís Moreira de Sousa (luis.de.sousa[@]protonmail.ch)
# Date: 27-01-2017 

import argparse

class Choropleth:
    
    header = """<?xml version="1.0" encoding="UTF-8"?>
    <StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1.1.0" xmlns:xlink="http://www.w3.org/1999/xlink" units="mm" xsi:schemaLocation="http://www.opengis.net/sld http://schemas.opengis.net/sld/1.1.0/StyledLayerDescriptor.xsd" xmlns:se="http://www.opengis.net/se">
      <NamedLayer>
        <se:Name>test8DEMFinal.hasc output Polygon</se:Name>
        <UserStyle>
          <se:Name>test8DEMFinal.hasc output Polygon</se:Name>
          <se:FeatureTypeStyle>"""
    
    rules = ""
    
    footer = """
          </se:FeatureTypeStyle>
        </UserStyle>
      </NamedLayer>
    </StyledLayerDescriptor>"""
    
    def create_level(self, bot, top, colour):
        
        return """
            <se:Rule>
              <se:Name> """ + str(bot) + " - " + str(top) + """ </se:Name>
              <se:Description>
                <se:Title> """ + str(bot) + " - " + str(top) + """ </se:Title>
              </se:Description>
              <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
                <ogc:And>
                  <ogc:PropertyIsGreaterThanOrEqualTo>
                    <ogc:PropertyName>value</ogc:PropertyName>
                    <ogc:Literal>""" + str(bot) + """</ogc:Literal>
                  </ogc:PropertyIsGreaterThanOrEqualTo>
                  <ogc:PropertyIsLessThanOrEqualTo>
                    <ogc:PropertyName>value</ogc:PropertyName>
                    <ogc:Literal>""" + str(top) + """</ogc:Literal>
                  </ogc:PropertyIsLessThanOrEqualTo>
                </ogc:And>
              </ogc:Filter>
              <se:PolygonSymbolizer>
                <se:Fill>
                  <se:SvgParameter name="fill">#""" + colour + """</se:SvgParameter>
                </se:Fill>
                <se:Stroke>
                  <se:SvgParameter name="stroke">#""" + colour + """</se:SvgParameter>
                  <se:SvgParameter name="stroke-width">0</se:SvgParameter>
                  <se:SvgParameter name="stroke-linejoin">bevel</se:SvgParameter>
                </se:Stroke>
              </se:PolygonSymbolizer>
            </se:Rule>"""   
            
    
    def setArguments(self):
        
        parser = argparse.ArgumentParser(description='Creates a spectral choropleth for QGis.')
        parser.add_argument("-b", "--bottom", dest="bottom", default = 0,
                          type=float, help="bottom scale value" )
        parser.add_argument("-t", "--top", dest="top", default = 100,
                          type=float, help="top scale value" )
        parser.add_argument("-c", "--classes", dest="classes", default = 20,
                          type=int, help="number of classes in the choropleth" )
        parser.add_argument("-o", "--output", dest="outputFile", default = "out.sld",
                          help="output .sld file" )
        
        return parser.parse_args()
    
    
    def dump_sld_file(self, file_path):
        
        text_file = open(file_path, "w")
        text_file.write(self.header)
        text_file.write(self.rules)
        text_file.write(self.footer)
        text_file.close()