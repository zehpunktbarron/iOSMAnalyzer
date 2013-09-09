# -*- coding: utf-8 -*-
#!/usr/bin/python2.7

#description     :This file creates a plot: Calculates the development of untouched points, lines and polygons of all OSM-features
#author          :Christopher Barron  @ http://giscience.uni-hd.de/
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

SELECT 
	generate_series,
	--
	-- Points
	--
	-- To prevent a "division by zero" error this CASE WHEN ... THEN is needed
	CASE WHEN 
		(SELECT 
			count (id) 
		FROM 
			hist_point 
		WHERE 	visible = 'true' AND
			(version = (SELECT max(version) FROM hist_point AS h WHERE h.id = hist_point.id AND
				(valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))) 
			AND minor = (SELECT max(minor) FROM hist_point AS h WHERE h.id = hist_point.id AND h.version = hist_point.version AND
				(valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))))
		) <> 0 THEN

	ROUND(
		(SELECT 
			count (id) 
		FROM 
			hist_point 
		WHERE 
			version = 1 AND 
			minor = 0 AND
			(version = (SELECT max(version) FROM hist_point AS h WHERE h.id = hist_point.id AND
				(valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))) 
			AND minor = (SELECT max(minor) FROM hist_point AS h WHERE h.id = hist_point.id AND h.version = hist_point.version AND
				(valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))))
		) *100.00/

		(SELECT 
			count (id) 
		FROM 
			hist_point 
		WHERE 	visible = 'true' AND
			(version = (SELECT max(version) FROM hist_point AS h WHERE h.id = hist_point.id AND
				(valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))) 
			AND minor = (SELECT max(minor) FROM hist_point AS h WHERE h.id = hist_point.id AND h.version = hist_point.version AND
				(valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))))
		)
	, 2)  ELSE 100 END::float AS count_point,


	--
	-- Lines
	--
	-- To prevent a "division by zero" error this CASE WHEN ... THEN is needed
	CASE WHEN 
		(SELECT 
			count (id) 
		FROM 
			hist_line 
		WHERE 	visible = 'true' AND
			(version = (SELECT max(version) FROM hist_line AS h WHERE h.id = hist_line.id AND
				(valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))) 
			AND minor = (SELECT max(minor) FROM hist_line AS h WHERE h.id = hist_line.id AND h.version = hist_line.version AND
				(valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))))
		) <> 0 THEN

	ROUND(
		(SELECT 
			count (id) 
		FROM 
			hist_line 
		WHERE 
			version = 1 AND 
			minor = 0 AND
			(version = (SELECT max(version) FROM hist_line AS h WHERE h.id = hist_line.id AND
				(valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))) 
			AND minor = (SELECT max(minor) FROM hist_line AS h WHERE h.id = hist_line.id AND h.version = hist_line.version AND
				(valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))))
		) *100.00/

		(SELECT 
			count (id) 
		FROM 
			hist_line 
		WHERE 	visible = 'true' AND
			(version = (SELECT max(version) FROM hist_line AS h WHERE h.id = hist_line.id AND
				(valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))) 
			AND minor = (SELECT max(minor) FROM hist_line AS h WHERE h.id = hist_line.id AND h.version = hist_line.version AND
				(valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))))
		)
	, 2)  ELSE 100 END::float AS count_line,


	--
	-- Polygons
	--
	-- To prevent a "division by zero" error this CASE WHEN ... THEN is needed
	CASE WHEN 
		(SELECT 
			count (id) 
		FROM 
			hist_polygon 
		WHERE 	visible = 'true' AND
			(version = (SELECT max(version) FROM hist_polygon AS h WHERE h.id = hist_polygon.id AND
				(valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))) 
			AND minor = (SELECT max(minor) FROM hist_polygon AS h WHERE h.id = hist_polygon.id AND h.version = hist_polygon.version AND
				(valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))))
		) <> 0 THEN

	ROUND(
		(SELECT 
			count (id) 
		FROM 
			hist_polygon 
		WHERE 
			version = 1 AND 
			minor = 0 AND
			(version = (SELECT max(version) FROM hist_polygon AS h WHERE h.id = hist_polygon.id AND
				(valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))) 
			AND minor = (SELECT max(minor) FROM hist_polygon AS h WHERE h.id = hist_polygon.id AND h.version = hist_polygon.version AND
				(valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))))
		) *100.00/

		(SELECT 
			count (id) 
		FROM 
			hist_polygon 
		WHERE 	visible = 'true' AND
			(version = (SELECT max(version) FROM hist_polygon AS h WHERE h.id = hist_polygon.id AND
				(valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))) 
			AND minor = (SELECT max(minor) FROM hist_polygon AS h WHERE h.id = hist_polygon.id AND h.version = hist_polygon.version AND
				(valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))))
		)
	, 2)  ELSE 100 END::float AS count_polygon


	

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
### Plot (Multiline-Chart)
###

# Datatypes of the returning data
datatypes = [('date', 'S20'),('col2', 'double'), ('col3', 'double'), ('col4', 'double')]

# Data-tuple and datatype
data = np.array(data_tuples, dtype=datatypes)

# Date comes from 'col1'
col2 = data['col2']
col3 = data['col3']
col4 = data['col4']


# Converts date to a manageable date-format for matplotlib
dates = mdates.num2date(mdates.datestr2num(data['date']))
fig, ax = plt.subplots()

# Create linechart
plt.plot(dates, col2, color = '#2dd700', linewidth=2, label='Points')
plt.plot(dates, col3, color = '#00a287', linewidth=2, label='Lines')
plt.plot(dates, col4, color = '#f5001d', linewidth=2, label='Polygons')

# Forces the plot to start from 0 and end at 100
pylab.ylim([0,100])

# Place a gray dashed grid behind the thicks (only for y-axis)
ax.yaxis.grid(color='gray', linestyle='dashed')

# Set this grid behind the thicks
ax.set_axisbelow(True) 

# Rotate x-labels on the x-axis
fig.autofmt_xdate()

# Label x and y axis
plt.xlabel('Date')
plt.ylabel('Untouched Points, Lines and Polygons [%]')

# place legend
ax.legend(loc='upper right',  prop={'size':12})

# Plot-title
plt.title('Development of untouched Points, Lines and Polygons')

# Save plot to *.jpeg-file
plt.savefig('pics/c6_untouched.jpeg')

plt.clf()
