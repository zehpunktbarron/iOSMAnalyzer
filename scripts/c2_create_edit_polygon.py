# -*- coding: utf-8 -*-
#!/usr/bin/python2.7

#title           :All created and edited polygons
#description     :This file creates a plot: How many polygons have been created or edited per month?
#author          :Christopher Barron
#date            :19.01.2013
#version         :0.1
#usage           :python pyscript.py
#==============================================================================

import psycopg2
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pylab

# import db connection parameters
import db_conn_para as db

###
### Connect to database with psycopg2. Add arguments from parser to the connection-string
###

try:
  conn_string="dbname= %s user= %s host= %s password= %s" %(db.g_my_dbname, db.g_my_username, db.g_my_hostname, db.g_my_dbpassword)
  print "Connecting to database\n->%s" % (conn_string)
      
# Verbindung mit der DB mittels psycopg2 herstellen
  conn = psycopg2.connect(conn_string)
  print "Connection to database was established succesfully"
except:
  print "Connection to database failed"

      
###      
### Execute SQL query (1)
###

# New cursor method for sql. We need two cur-cursors, one for each query!
cur = conn.cursor()

# Execute SQL query. For more than one row use three '"'
try:
  cur.execute(""" 

-- Created Polygons over time
SELECT count(t.id)::int AS count
      ,date_trunc('month', s.day)::date AS month
FROM  (
   SELECT generate_series(min(valid_from)::date
                         ,max(valid_from)::date
                         ,interval '1 day'
          )::date AS day
   FROM   hist_polygon t
   ) s
LEFT   JOIN hist_polygon t ON t.valid_from::date = s.day AND t.version = 1 AND t.minor = 0
GROUP  BY month
ORDER  BY month;

  """)

# Getting a list of tuples from the database-cursor (cur)
  data_tuples = []
  for row in cur:
    data_tuples.append(row)

except:
  print "Query could not be executed"

datatypes = [('col1', 'i4'), ('date', 'S20')]
data1 = np.array(data_tuples, dtype=datatypes)
col1_1 = data1['col1']

###      
### Execute SQL query (2)    
###

# Mit dieser neuen "cursor Methode" koennen SQL-Abfragen abgefeuert werden
cur2 = conn.cursor()

# Execute SQL query. For more than one row use three '"'
try:
  cur2.execute("""

-- Edited Polygons over time
SELECT count(t.id)::int AS count
      ,date_trunc('month', s.day)::date AS month
FROM  (
   SELECT generate_series(min(valid_from)::date
                         ,max(valid_from)::date
                         ,interval '1 day'
          )::date AS day
   FROM   hist_polygon t
   ) s
LEFT   JOIN hist_polygon t ON t.valid_from::date = s.day AND NOT (t.version = 1 AND t.minor = 0) AND visible = 'true'
GROUP  BY month
ORDER  BY month;


  """)

# Getting a list of tuples from the database-cursor (cur)
  data_tuples2 = []
  for row2 in cur2:
    data_tuples2.append(row2)

except:
  print "Query could not be executed"

datatypes2 = [('col1', 'i4'), ('date', 'S20')]
data2 = np.array(data_tuples2, dtype=datatypes2)
col1_2 = data2['col1']  

###
### Plot (Multiline-Chart)
###

# Create Subplot
fig = plt.figure()
ax = fig.add_subplot(111)

# set figure size
fig.set_size_inches(10,6)

# Data-tuple and datatype
data1 = np.array(data_tuples, dtype=datatypes)

# Converts date to a manageable date-format for matplotlib
dates = mdates.num2date(mdates.datestr2num(data1['date']))

# Create barchart (x-axis=dates, y-axis=col1, 
plt.plot(dates, col1_1, color = '#2dd700', linewidth=2, label='Created Polygons')
plt.plot(dates, col1_2, color = '#ff6700', linewidth=2, label='Polygon-Edits')

# Place a gray dashed grid behind the thicks (only for y-axis)
ax.yaxis.grid(color='gray', linestyle='dashed')

# Set this grid behind the thicks
ax.set_axisbelow(True) 

# Rotate x-labels on the x-axis
fig.autofmt_xdate()

# Label x and y axis
plt.xlabel('Date')
plt.ylabel('Number of created Polygons and Polygon-Edits')

# Locate legend on the plot (http://matplotlib.org/users/legend_guide.html#legend-location)
# Shink current axis by 20%
box = ax.get_position()
ax.set_position([box.x0, box.y0, box.width * 0.9, box.height * 0.9])

# Put a legend to the right of the current axis and reduce the font size
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), prop={'size':9})

# Plot-title
plt.title("Development of created Polygons and Polygon-Edits")

# Save plot to *.png-file
plt.savefig('pics/c2_create_edit_polygon.jpeg')

plt.clf()
