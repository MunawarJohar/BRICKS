# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 17:22:42 2024

@author: aprosperi, JFuertes
"""

#%% Import Modules
from diana import *
import os

#%% Export folder

path_exp=r'C:\Lavori\TEST' # path to export images

analysis_name="Analysis1" # "Analysis1" is the name of the analysis

fitAll(  )
steps=resultCases(analysis_name) # steps where 
setViewSettingValue( "view setting", "RESULT/DEFORM/MODE", "OFF" ) # no deformation
for i in range(0,len(steps)): 
 current_step=steps[i]
 # step step
 setResultCase( [ analysis_name, "OutputMain", current_step ] )
 # Vertical Displacements
 selectResult( { "component": "TDtY", "result": "Displacements", "type": "Node" } )
 # set the legend
 setViewSettingValue( "view setting", "RESULT/CONTOU/LEVELS", "SPECIF" )
 setViewSettingValue( "view setting", "RESULT/CONTOU/SPECIF/VALUES", [ -50, -40, -30, -20, -10, -9, -8, -7, -6, -5, -4, -3, -2, -1, 0 ] )
 setViewSettingValue( "view setting", "RESULT/CONTOU/AUTRNG", "LIMITS" )
 setViewSettingValue( "view setting", "RESULT/CONTOU/LIMITS/MINVAL", -50 )
 setViewSettingValue( "view setting", "RESULT/CONTOU/LIMITS/MAXVAL", 0 )
 # boundary colors
 setViewSettingValue( "view setting", "RESULT/CONTOU/BNDCLR/MAXCLR", [ 76, 17, 48, 255 ] )
 setViewSettingValue( "view setting", "RESULT/CONTOU/BNDCLR/MINCLR", [ 217, 234, 211, 255 ] )
 saveImage( path_exp + "\\" + current_step + ".png", 4000, 3000, 1 )