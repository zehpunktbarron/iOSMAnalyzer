# -*- coding: utf-8 -*-
#!/usr/bin/python2.7

#description     :This file creates a plot: Calculates the development of the OSM road network length [km] by street-category
#author          :Christopher Barron @ http://giscience.uni-hd.de/
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

-- Road-network length by Street Category over time
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
			AND visible = 'true' AND
			(
			((tags->'highway') = 'motorway') OR 
			((tags->'highway') = 'motorway_link') OR
			((tags->'highway') = 'trunk') OR
			((tags->'highway') = 'trunk_link') OR
			((tags->'highway') = 'primary') OR
			((tags->'highway') = 'primary_link'))
			)

		) AS motorway_highway, 

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
			AND visible = 'true' AND
			(
			((tags->'highway') = 'secondary') OR
			((tags->'highway') = 'secodary_link') OR
			((tags->'highway') = 'tertiary') OR
			((tags->'highway') = 'tertiary_link'))
			) 
		) AS secondary_tertiary,

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
			AND visible = 'true' AND
			(
			((tags->'highway') = 'residential') OR
			((tags->'highway') = 'living_street'))
			) 
		) AS residential, 


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
			AND visible = 'true' AND
			(
			((tags->'highway') = 'unclassified') OR
			((tags->'highway') = 'road') OR
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
		) AS other_roads, date_trunc('month', generate_series)::date

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
datatypes = [('col1', 'double'), ('col2', 'double'), ('col3', 'double'), ('col4', 'double'), ('date', 'S20')]

# Data-tuple and datatype
data = np.array(data_tuples, dtype=datatypes)

# Date comes from 'col1'
y1 = data['col1'] # motorways/highways
y2 = data['col2'] # secondary/tertiary roads
y3 = data['col3'] # residential roads
y4 = data['col4'] # other roads

###
### Plot (stacked chart)
###

# Create Subplot
fig = plt.figure()
ax = fig.add_subplot(111)

# Data-tuple and datatype
data1 = np.array(data_tuples, dtype=datatypes)

# Converts date to a manageable date-format for matplotlib
x = mdates.num2date(mdates.datestr2num(data1['date']))

# Add values for stacking
y2s = y1+y2
y3s = y1+y2+y3
y4s = y1+y2+y3+y4

# Hackish way of placing the legend but "fill_between" doesn't support legends
plt.plot(x,y4s,color = '#2dd700',label='Other Roads')
plt.plot(x,y3s,color = '#00a287', label='Residential Roads')
plt.plot(x,y2s,color = '#ff6700', label='Secondary/Tertiary Roads')
plt.plot(x,y1,color = '#f5001d',label='Motorway/Highway')

# Fill-color between stacks
plt.fill_between(x,y1,0,color='#f5001d')
plt.fill_between(x,y1,y2s,color='#ff6700')
plt.fill_between(x,y2s,y3s,color='#00a287')
plt.fill_between(x,y3s,y4s,color='#2dd700')

# Place a gray dashed grid behind the thicks (only for y-axis)
ax.yaxis.grid(color='gray', linestyle='dashed')

# Set this grid behind the thicks
ax.set_axisbelow(True) 

# Rotate x-labels on the x-axis
fig.autofmt_xdate()

# Label x and y axis
plt.xlabel('Date')
plt.ylabel('Length [km]')

# Locate legend on the plot (http://matplotlib.org/users/legend_guide.html#legend-location)
# Shink current axis by 20%
box = ax.get_position()
ax.set_position([box.x0, box.y0, box.width * 0.8, box.height * 0.8])

# Put a legend to the right of the current axis and reduce the font size
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), prop={'size':8})

# Plot-title
plt.title("Development of the OSM Road Network Length by Street Category")

# show plot
#pylab.show()

# Save plot to *.jpeg-file
plt.savefig('pics/c3_car_routing_high_net.jpeg')

plt.clf()
