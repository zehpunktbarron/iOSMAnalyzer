# -*- coding: utf-8 -*-
#!/usr/bin/python2.7

#description     :This file creates a plot: Calculates the development of active distinct contributers per month
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

-- How many distinct Users have been activ in the area per month/year
SELECT count(DISTINCT t.user_id)::int AS count
      ,date_trunc('month', s.day)::date AS month --http://ben.goodacre.name/tech/Group_by_day,_week_or_month_%28PostgreSQL%29
      
FROM  (
   SELECT generate_series(min(valid_from)::date
                         ,max(valid_from)::date
                         ,interval '1 day'
          )::date AS day
   FROM   hist_point t
   ) s
LEFT   JOIN hist_point t ON t.valid_from::date = s.day
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
### Plot (Line-Chart)
###

# Create Subplot
fig = plt.figure()
ax = fig.add_subplot(111)

# Data-tuple and datatype
data1 = np.array(data_tuples, dtype=datatypes)

# Converts date to a manageable date-format for matplotlib
dates = mdates.num2date(mdates.datestr2num(data1['date']))

# Create barchart (x-axis=dates, y-axis=col1, 
plt.plot(dates, col1_1,  color = '#2dd700', linewidth=2, label='created nodes')

# Place a gray dashed grid behind the thicks (only for y-axis)
ax.yaxis.grid(color='gray', linestyle='dashed')

# Set this grid behind the thicks
ax.set_axisbelow(True) 

# Rotate x-labels on the x-axis
fig.autofmt_xdate()

# Label x and y axis
plt.xlabel('Date')
plt.ylabel('Number of distinct Contributors')

# Plot-title
plt.title("Development of distinct Contributors per Month")

# Save plot to *.jpeg-file
plt.savefig('pics/c7_distinct_users.jpeg')

plt.clf()