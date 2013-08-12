# -*- coding: utf-8 -*-
#!/usr/bin/python2.7

#description     :This file creates a plot: Calculates the number of osm-features with full address information according to the "Karlsruhe-Schema"
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
      
  conn = psycopg2.connect(conn_string)
  print "Connection to database was established succesfully"
except:
  print "Connection to database failed"

###
### Execute SQL query
###  
  
# New cursor method for sql
cur = conn.cursor()

# Execute SQL query. For more than one row use three '"'
try:
  cur.execute(""" 
  
SELECT
	(SELECT 
		COUNT(DISTINCT id)::int
	FROM 
		hist_plp 
	WHERE
		(valid_from <= generate_series) 
		AND
		(
		tags ? 'addr:housenumber' AND
		tags ? 'addr:street' AND
		tags ? 'addr:city' AND
		tags ? 'addr:postcode' AND
		tags ? 'addr:country' 		
		)
		
	) AS full_addr, date_trunc('month', generate_series)::date

FROM generate_series(
	(SELECT date_trunc ('month',(
		SELECT MIN(valid_from) FROM hist_plp)) as foo),  -- Select minimum date (month)
	(SELECT MAX(valid_from) FROM hist_plp)::date,	-- Select maximum date
	interval '1 month')
;

  """)

# Getting a list of tuples from the database-cursor (cur)
  data_tuples = []
  for row in cur:
    data_tuples.append(row)


except:
  print "Query could not be executed"

###
### Plot (Barchart)
###

# Datatypes of the returning data: column 1(col1) --> integer, column 2(date) --> string
datatypes = [('col1', 'i4'), ('date', 'S20')]

# Data-tuple and datatype
data = np.array(data_tuples, dtype=datatypes)

#
col1 = data['col1']

# Converts date to a manageable date-format for matplotlib
dates = mdates.num2date(mdates.datestr2num(data['date']))
fig, ax1 = plt.subplots()

# Create barchart (x-axis=dates, y-axis=col1, 
ax1.plot(dates, col1, linewidth = '2', color = '#2dd700')

# Place a gray dashed grid behind the thicks (only for y-axis)
ax1.yaxis.grid(color='gray', linestyle='dashed')

# Set this grid behind the thicks
ax1.set_axisbelow(True) 

# Rotate x-labels on the x-axis
fig.autofmt_xdate()

# Label x- and y-axis
plt.xlabel('Date')
plt.ylabel('Number of OSM-Features')

# Plot-title
plt.title("Development of OSM-Features with a complete Address-Information")

# Save plot to *.jpeg-file
plt.savefig('pics/c4_full_addr.jpeg')

plt.clf()