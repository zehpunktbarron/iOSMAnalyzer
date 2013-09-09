# -*- coding: utf-8 -*-
#!/usr/bin/python2.7

#description     :This file creates a Plot: Calculates number of buildings and all buildings with an housenumber (as a node, tag or interpolation-line)
#author          :Christopher Barron @ http://giscience.uni-hd.de/
#date            :06.06.2013
#version         :0.2
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
  

-- Buildings with an address-tag overlaid from the point-table
SELECT 
	(SELECT 
		count(b.id)
		--b.geom
	FROM
		-- all polygons with a building-tag
		(SELECT 
			geom, id 
		FROM 
			hist_polygon 
		WHERE 
			tags ? 'building' AND  
			visible = 'true' AND
			((version = (SELECT max(version) from hist_polygon as h where h.id = hist_polygon.id AND
				valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))) 
			AND minor = (SELECT max(minor) from hist_polygon as h where h.id = hist_polygon.id AND h.version = hist_polygon.version AND
				(valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))))) AS b,
				 
		-- all points with a housenumber or housename-tag (in some countries housenames are used instead (or in addition to) a housenumber
		(SELECT 
			geom
		FROM 
			hist_point 
		WHERE 
			(tags ? 'addr:housenumber' OR tags ? 'addr:housename') AND
			visible = 'true' AND
			((version = (SELECT max(version) from hist_point as h where h.id = hist_point.id AND
				valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))) 
			)) AS n
	WHERE
		ST_intersects(b.geom, n.geom) = 'true'
	) AS node, 

	-- buildings with an address-tag from the polygon itself
	(SELECT 
		count(id) 
	FROM 
		hist_polygon 
	WHERE 
		tags ? 'building' AND 
		(tags ? 'addr:housenumber' OR tags ? 'addr:housename') AND 
		visible = 'true' AND
		((version = (SELECT max(version) from hist_polygon as h where h.id = hist_polygon.id AND
			valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))) 
		AND minor = (SELECT max(minor) from hist_polygon as h where h.id = hist_polygon.id AND h.version = hist_polygon.version AND
			(valid_from <= generate_series AND (valid_to >= CURRENT_TIMESTAMP OR valid_to is null))))
	) AS tag,
	
	-- buildings intersectiong with an addr:interpolation-line
	(SELECT 
		count(b.id)
		--b.geom
	FROM
		-- all polygons with a building-tag
		(SELECT 
			geom, id 
		FROM 
			hist_polygon 
		WHERE 
			tags ? 'building' AND  
			visible = 'true' AND
			((version = (SELECT max(version) from hist_polygon as h where h.id = hist_polygon.id AND
				valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))) 
			AND minor = (SELECT max(minor) from hist_polygon as h where h.id = hist_polygon.id AND h.version = hist_polygon.version AND
				(valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))))) AS b,
				 
		-- all points with a housenumber or housename-tag (in some countries housenames are used instead (or in addition to) a housenumber
		(SELECT 
			geom
		FROM 
			hist_line 
		WHERE 
			tags ? 'addr:interpolation' AND
			visible = 'true' AND
			((version = (SELECT max(version) from hist_line as h where h.id = hist_line.id AND
				valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))) 
			AND minor = (SELECT max(minor) from hist_line as h where h.id = hist_line.id AND h.version = hist_line.version AND
				(valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))))) AS n
	WHERE
		ST_intersects(b.geom, n.geom) = 'true'
	) AS interpolation, date_trunc('month', generate_series)::date

FROM generate_series(
	(SELECT date_trunc ('month',(
		SELECT MIN(valid_from) FROM hist_point)) as foo),  -- Select minimum date (month)
	(SELECT MAX(valid_from) FROM hist_point)::date,	-- Select maximum date
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
datatypes = [('col1', 'i4'), ('col2', 'i4'), ('col3', 'i4'), ('date', 'S20')]

# Data-tuple and datatype
data = np.array(data_tuples, dtype=datatypes)

#
col1 = data['col1']
col2 = data['col2']
col3 = data['col3']

# Converts date to a manageable date-format for matplotlib
x = mdates.num2date(mdates.datestr2num(data['date']))



# START Execute SQL query2.
cur2 = conn.cursor()

try:
  cur2.execute("""

-- Amount of currently valid buildings which potentially have a house number or house name
SELECT	
	(SELECT count(id) 
	FROM 
		hist_polygon 
	WHERE 
		visible = 'true' AND 
		tags ? 'building' AND

		-- exclude buildings which shouldn't have a house number
		NOT (
			((tags->'building') = 'stable') OR
			((tags->'building') = 'shed') OR
			((tags->'building') = 'roof') OR
			((tags->'building') = 'greenhouse') OR
			((tags->'building') = 'garage') OR
			((tags->'building') = 'garages') OR
			((tags->'building') = 'bridge') OR
			((tags->'building') = 'barn')
		) AND

		-- exclude buildings with a very small footprint
		St_Area(geom) > 10 AND
		(version = (SELECT max(version) FROM hist_polygon AS h WHERE h.id = hist_polygon.id AND
			(valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))) 
		AND minor = (SELECT max(minor) FROM hist_polygon AS h WHERE h.id = hist_polygon.id AND h.version = hist_polygon.version AND
			(valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))))
	) AS buildings, generate_series

FROM generate_series(
	(SELECT date_trunc ('month',(
		SELECT MIN(valid_from) FROM hist_point)) as foo),  -- Select minimum date (month)
	(SELECT MAX(valid_from) FROM hist_point)::date,	-- Select maximum date
	interval '1 month')
  """)

# Getting a list of tuples from the database-cursor (cur)
  data_tuples2 = []
  for row2 in cur2:
    data_tuples2.append(row2)
  
except:
  print "Query2 could not be executed"

# END Execute SQL query2.

# Datatypes of the returning data (total amount of Polygons)
datatypes2 = [('col4', 'i4'), ('date', 'S20')]

# Data-tuple and datatype
data2 = np.array(data_tuples2, dtype=datatypes2)

# Date comes from 'col1'
col4 = data2['col4']


fig, ax1 = plt.subplots()


# Date comes from 'col1'
y1 = data['col1'] # motorways/highways
y2 = data['col2'] # secondary/tertiary roads
y3 = data['col3'] # residential roads

# Add values for stacking
y2s = y1+y2
y3s = y1+y2+y3

# Hackish way of placing the legend but "fill_between" doesn't support legends
ax1.plot(x, col4,  linewidth=2, color = '#00a287', label = 'Total Number')
ax1.plot(x, y1, linewidth=2, color = '#2dd700', label = 'House Number/-name [Node]')
ax1.plot(x, y2s, linewidth=2, color = '#ff6700', label = 'House Number/-name [Polygon]')
ax1.plot(x, y3s, linewidth=2, color = '#f5001d', label = 'House Number/-name [Interpolation]')

# Fill-color between stacks
ax1.fill_between(x,y1,0,color='#2dd700')
ax1.fill_between(x,y1,y2s,color='#ff6700')
ax1.fill_between(x,y2s,y3s,color='#f5001d')

# Place a gray dashed grid behind the thicks (only for y-axis)
ax1.yaxis.grid(color='gray', linestyle='dashed')

# Set this grid behind the thicks
ax1.set_axisbelow(True) 

# Rotate x-labels on the x-axis
fig.autofmt_xdate()
    
# place legend
ax1.legend(loc='upper left',  prop={'size':12})

# Plot-title
plt.title('Development of Buildings [with a House Number/-name]')

# Label x- and y-axis
plt.xlabel('Date')
plt.ylabel('Number of Buildings')

# Save plot to *.jpeg-file
plt.savefig('c4_building_hnr.jpeg')

plt.clf()
