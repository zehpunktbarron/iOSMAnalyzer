# -*- coding: utf-8 -*-
#!/usr/bin/python2.7

#description     :This file creates a plot: Calculates the development of the total OSM highway length [km]
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
### Execute SQL query
###

# Mit dieser neuen "cursor Methode" koennen SQL-Abfragen abgefeuert werden
cur = conn.cursor()

# Execute SQL query. For more than one row use three '"'
try:
  cur.execute("""

  -- Total highway length over time
SELECT
	(SELECT 
		coalesce(SUM
			(ST_Length
				(ST_GeographyFromText
					(ST_AsText 
						(ST_Transform(geom, 4326))
					)
				)
			/1000)
		, 0) AS length_spheroid 
	FROM 
		hist_line 
	WHERE
		((version = (SELECT max(version) from hist_line as h where h.id = hist_line.id AND
		valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))) 
		AND minor = (SELECT max(minor) from hist_line as h where h.id = hist_line.id AND h.version = hist_line.version AND
		(valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null)))
		AND visible = 'true' AND tags ? 'highway')
	) AS length, date_trunc('month', generate_series)::date

FROM generate_series(
	(SELECT date_trunc ('month',(
		SELECT MIN(valid_from) FROM hist_line)) as foo),  -- Select minimum date (month)
	(SELECT MAX(valid_from) FROM hist_line)::date,	-- Select maximum date
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
### Plot (Multiline-Chart)
###

# Datatypes of the returning data: column 1(col1) --> integer, column 2(date) --> string
datatypes = [('col1', 'double'), ('date', 'S20')]

# Data-tuple and datatype
data = np.array(data_tuples, dtype=datatypes)

# Date comes from 'col1'
col1 = data['col1']

# Converts date to a manageable date-format for matplotlib
dates = mdates.num2date(mdates.datestr2num(data['date']))
fig, ax = plt.subplots()

# Create barchart (x-axis=dates, y-axis=col1, 
ax.bar(dates, col1, width=15, align='center', color = '#2dd700', label='Total highway length')

# Place a gray dashed grid behind the thicks (only for y-axis)
ax.yaxis.grid(color='gray', linestyle='dashed')

# Set this grid behind the thicks
ax.set_axisbelow(True) 

# Rotate x-labels on the x-axis
fig.autofmt_xdate()

# Label x and y axis
plt.xlabel('Date')
plt.ylabel('Length [km]')

# Plot-title
plt.title("Development of the total Highway Length")

# Save plot to *.jpeg-file
plt.savefig('pics/c3_highway.jpeg')

plt.clf()