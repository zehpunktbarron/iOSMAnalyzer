# -*- coding: utf-8 -*-
#!/usr/bin/python2.7

#description     :This file creates a plot: Calculates the actuality of the total OSM highway. Additionally plots the first version for comparison purposes
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

-- Currently valid version of the road
SELECT 
	coalesce(SUM -- Lenght of these highway-objects
		(ST_Length
			(ST_GeographyFromText
				(ST_AsText 
					(ST_Transform(geom, 4326))
				)
			)
		/1000)
	, 0) AS length_spheroid,
	date_trunc('month', valid_from)::date, 
	count(valid_from)::int -- Amount of highway-objects 
FROM 
	hist_line 
WHERE 
	visible = 'true' AND
	((version = (SELECT max(version) from hist_line as h where h.id = hist_line.id AND
		valid_from <= CURRENT_TIMESTAMP AND (valid_to >= CURRENT_TIMESTAMP OR valid_to is null))) 
	AND minor = (SELECT max(minor) from hist_line as h where h.id = hist_line.id AND h.version = hist_line.version AND
		(valid_from <= CURRENT_TIMESTAMP AND (valid_to >= CURRENT_TIMESTAMP OR valid_to is null)))
	AND 
	( -- Total OSM-road-network
	((tags->'highway') = 'motorway') OR
	((tags->'highway') = 'motorway_link') OR
	((tags->'highway') = 'trunk') OR
	((tags->'highway') = 'trunk_link') OR
	((tags->'highway') = 'primary') OR
	((tags->'highway') = 'primary_link') OR
	((tags->'highway') = 'secondary') OR
	((tags->'highway') = 'secondary_link') OR
	((tags->'highway') = 'tertiary') OR
	((tags->'highway') = 'tertiary_link') OR
	((tags->'highway') = 'unclassified') OR
	((tags->'highway') = 'residential') OR
	((tags->'highway') = 'road') OR
	((tags->'highway') = 'living_street') OR
	((tags->'highway') = 'service') OR
	((tags->'highway') = 'track') OR
	((tags->'highway') = 'path') OR
	((tags->'highway') = 'pedestrian') OR
	((tags->'highway') = 'footway') OR
	((tags->'highway') = 'cycleway') OR
	((tags->'highway') = 'steps') OR
	((tags->'highway') = 'platform') OR
	((tags->'highway') = 'bridleway'))
	)
GROUP BY date_trunc
ORDER BY date_trunc ASC;
        
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
datatypes = [('col1', 'double'), ('date', 'S20'), ('count', 'int')]

# Data-tuple and datatype
data = np.array(data_tuples, dtype=datatypes)

# Date comes from 'col1'
col1 = data['col1']


  
###      
### Execute SQL query2
###

# Mit dieser neuen "cursor Methode" koennen SQL-Abfragen abgefeuert werden
cur2 = conn.cursor()

# Execute SQL query. For more than one row use three '"'
try:
  cur2.execute("""

-- First created version of the road
SELECT 
	coalesce(SUM -- Lenght of these highway-objects
		(ST_Length
			(ST_GeographyFromText
				(ST_AsText 
					(ST_Transform(geom, 4326))
				)
			)
		/1000)
	, 0) AS length_spheroid,
	date_trunc('month', valid_from)::date, 
	count(valid_from)::int -- Amount of highway-objects 
FROM  
	hist_line 
WHERE 
	visible = 'true' AND
	version = 1 AND minor = 0
	AND 
	( -- Total OSM-road-network
	((tags->'highway') = 'motorway') OR
	((tags->'highway') = 'motorway_link') OR
	((tags->'highway') = 'trunk') OR
	((tags->'highway') = 'trunk_link') OR
	((tags->'highway') = 'primary') OR
	((tags->'highway') = 'primary_link') OR
	((tags->'highway') = 'secondary') OR
	((tags->'highway') = 'secondary_link') OR
	((tags->'highway') = 'tertiary') OR
	((tags->'highway') = 'tertiary_link') OR
	((tags->'highway') = 'unclassified') OR
	((tags->'highway') = 'residential') OR
	((tags->'highway') = 'road') OR
	((tags->'highway') = 'living_street') OR
	((tags->'highway') = 'service') OR
	((tags->'highway') = 'track') OR
	((tags->'highway') = 'path') OR
	((tags->'highway') = 'pedestrian') OR
	((tags->'highway') = 'footway') OR
	((tags->'highway') = 'cycleway') OR
	((tags->'highway') = 'steps') OR
	((tags->'highway') = 'platform') OR
	((tags->'highway') = 'bridleway'))
	
GROUP BY date_trunc
ORDER BY date_trunc ASC;

""")

# Getting a list of tuples from the database-cursor (cur)
  data_tuples2 = []
  for row2 in cur2:
    data_tuples2.append(row2)
  
except:
  print "Query could not be executed"
  
###
### Plot (Multiline-Chart)
###

# Datatypes of the returning data: column 1(col1) --> integer, column 2(date) --> string
datatypes2 = [('col1_2', 'double'), ('date_2', 'S20'), ('count_2', 'int')]

# Data-tuple and datatype
data2 = np.array(data_tuples2, dtype=datatypes2)

# Date comes from 'col1'
col1_2 = data2['col1_2']


# Converts date to a manageable date-format for matplotlib
dates = mdates.num2date(mdates.datestr2num(data['date']))
dates2 = mdates.num2date(mdates.datestr2num(data2['date_2']))
fig, ax = plt.subplots()

# Create linechart
plt.plot(dates, col1, color = '#2dd700', linewidth=2, label='currently valid version') # date of currently valid roads
plt.plot(dates2, col1_2,  color = '#ff6700', linewidth=2, label='first version') # date of the first created roads

# Place a gray dashed grid behind the thicks (only for y-axis)
ax.yaxis.grid(color='gray', linestyle='dashed')

# Set this grid behind the thicks
ax.set_axisbelow(True) 

# Rotate x-labels on the x-axis
fig.autofmt_xdate()

# Label x and y axis
plt.xlabel('Date')
plt.ylabel('Length [km]')

# place legend
ax.legend(loc='upper right',  prop={'size':12})

# Plot-title
plt.title("Actuality of the total Highway Length")

# Save plot to *.jpeg-file
plt.savefig('pics/c3_highway_actuality.jpeg')

plt.clf()