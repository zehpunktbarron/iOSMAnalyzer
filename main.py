# -*- coding: utf-8 -*-
#!/usr/bin/python2.7

#description :This file executes all the files from the script-folder
#author :Christopher Barron @ http://giscience.uni-hd.de/
#date :18.04.2013
#version :0.1
#usage :python main.py -D database -U username -H host -P password
#==============================================================================

# import modules
import argparse
import logging
import os
from time import *
import psycopg2
import sys
import pprint
import matplotlib.pyplot as plt
from reportlab.platypus import *
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.platypus.doctemplate import NextPageTemplate
from reportlab.platypus.flowables import PageBreak 
from reportlab.pdfbase.pdfdoc import PDFPageLabels
from reportlab.lib.units import inch
from time import strftime

import subprocess
import db_conn_para


# current date
current_date = strftime("%Y-%m-%d %H:%M:%S")

# create the logfile. Set parameters for logging
logging.basicConfig(filename='iOSMAnalyzer_' + current_date + '.log',level=logging.DEBUG,format = "%(asctime)s [%(levelname)-8s] %(message)s")

# create folder for pictures
if not os.path.exists('pics'):
    os.makedirs('pics')

# execute all files from the "script" directory and print a message to the logfile
for x in sorted(os.listdir("scripts")):
  if x.endswith(".py"):
    print str(x)
    
    logging.debug('###')
    logging.debug('###')
    try:
      print 'Executing script ' + str(x) + ' ...'
      logging.debug('Executing script ' + str(x) + ' ...')
      execfile('scripts/'+ x)
      logging.debug('File: ' + str(x) + ' was executed succesfully')
      print ' ... was executed succesfully'
      print ''
    except:
      print ' ... ERROR!' + str(x) + ' was NOT created succesfully'
      logging.debug('An ERROR occured in script ' + str(x))
      print ''
      pass
    


#####################################
# Start creating PDF with Reportlab #
#####################################

# Create PDF-file
c = canvas.Canvas("OSM-History-Stats_" + str(current_date) + ".pdf")


###
### First Page
###

c.setFont("Helvetica", 28)
c.drawString(100,700,"Statistics and Maps")
c.drawString(100,650,"based on an OSM-Full-History-File")
 
c.setFont("Helvetica", 10)
c.drawString(100,220,"Source code available at: https://github.com/zehpunktbarron/iosmanalyzer")
c.drawString(100,200,"Author: Christopher Barron")
c.drawString(100,180,"Version: 0.2")
c.drawString(100,160,"Last Update: 06.08.2013")
c.drawString(100,140,"PDF created: " + str(strftime("%Y-%m-%d %H:%M:%S")))

# page break
c.showPage()
 
###
### All other pages: Get images and plot them each on a single page
###

print  str(os.getcwd())
os.chdir("pics")
for images in os.listdir("."):
  print images
  
  # draw image (file.jpeg, x(bottom -> top), y (bottom -> top), image size (x), image size (y)
  c.drawImage(images, 150, 550, 350, 250)
  
  # page break
  c.showPage()

# change directory to save pdf
os.chdir("../")

# save to pdf file
c.save()
