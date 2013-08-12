# -*- coding: utf-8 -*-
#!/usr/bin/python2.7

#description     :This file creates a plot: Calculate the actuality of all lines
#author          :Christopher Barron
#date            :19.01.2013
#version         :0.1
#usage           :python pyscript.py
#==============================================================================

import psycopg2
from pylab import *

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
		count(id) 
	FROM
		(SELECT 
			id, 
			-- select latest edit in the whole database as timestamp of the dataset
			extract(days FROM(SELECT max(valid_from) FROM hist_plp) - valid_from) AS age
		FROM 
			hist_line 
		WHERE 
			visible = 'true' AND
			(version = (SELECT max(version) FROM hist_line AS h WHERE h.id = hist_line.id AND
				(valid_from <= CURRENT_TIMESTAMP AND (valid_to >= CURRENT_TIMESTAMP OR valid_to is null))) 
			AND minor = (SELECT max(minor) FROM hist_line AS h WHERE h.id = hist_line.id AND h.version = hist_line.version AND
				(valid_from <= CURRENT_TIMESTAMP AND (valid_to >= CURRENT_TIMESTAMP OR valid_to is null))))
		) AS foo
	WHERE
		age <= 183 -- less than 6 months
	),

	
	(SELECT 
		count(id) 
	FROM
		(SELECT 
			id, 
			-- select latest edit in the whole database as timestamp of the dataset
			extract(days FROM(SELECT max(valid_from) FROM hist_plp) - valid_from) AS age
		FROM 
			hist_line 
		WHERE 
			visible = 'true' AND
			(version = (SELECT max(version) FROM hist_line AS h WHERE h.id = hist_line.id AND
				(valid_from <= CURRENT_TIMESTAMP AND (valid_to >= CURRENT_TIMESTAMP OR valid_to is null))) 
			AND minor = (SELECT max(minor) FROM hist_line AS h WHERE h.id = hist_line.id AND h.version = hist_line.version AND
				(valid_from <= CURRENT_TIMESTAMP AND (valid_to >= CURRENT_TIMESTAMP OR valid_to is null))))
		) AS foo
	WHERE
		age > 183 AND age <= 365 -- older than 6 months and les than 1 year
	),


	(SELECT 
		count(id) 
	FROM
		(SELECT 
			id, 
			-- select latest edit in the whole database as timestamp of the dataset
			extract(days FROM(SELECT max(valid_from) FROM hist_plp) - valid_from) AS age
		FROM 
			hist_line 
		WHERE 
			visible = 'true' AND
			(version = (SELECT max(version) FROM hist_line AS h WHERE h.id = hist_line.id AND
				(valid_from <= CURRENT_TIMESTAMP AND (valid_to >= CURRENT_TIMESTAMP OR valid_to is null))) 
			AND minor = (SELECT max(minor) FROM hist_line AS h WHERE h.id = hist_line.id AND h.version = hist_line.version AND
				(valid_from <= CURRENT_TIMESTAMP AND (valid_to >= CURRENT_TIMESTAMP OR valid_to is null))))
		) AS foo
	WHERE
		age > 365 AND age <= 730 -- older than 1 year and less than 2 years
	),


	(SELECT 
		count(id) 
	FROM
		(SELECT 
			id, 
			-- select latest edit in the whole database as timestamp of the dataset
			extract(days FROM(SELECT max(valid_from) FROM hist_plp) - valid_from) AS age
		FROM 
			hist_line 
		WHERE 
			visible = 'true' AND
			(version = (SELECT max(version) FROM hist_line AS h WHERE h.id = hist_line.id AND
				(valid_from <= CURRENT_TIMESTAMP AND (valid_to >= CURRENT_TIMESTAMP OR valid_to is null))) 
			AND minor = (SELECT max(minor) FROM hist_line AS h WHERE h.id = hist_line.id AND h.version = hist_line.version AND
				(valid_from <= CURRENT_TIMESTAMP AND (valid_to >= CURRENT_TIMESTAMP OR valid_to is null))))
		) AS foo
	WHERE
		age > 730 -- older than 2 years
	)

  """)

# Return the results of the query. Fetchall() =  all rows, fetchone() = first row
  records = cur.fetchone()
  cur.close()

except:
  print "Query could not be executed"

  
# Get data from query
one = records[0]
two = records[1]
three = records[2]
four = records[3]


# make a square figure and axes
figure(1, figsize=(9,9))
ax = axes([0.2, 0.2, 0.6, 0.6])

# pie-labelling
labels = '< 6 months', '> 6 and <= 12 months', '> 1 year and <= 2 years', '> 2 years'

# get db-values as fracs
fracs = [one, two, three, four]

# explode values
explode=(0.05, 0.05, 0.05, 0.05)

# Color in RGB. not shure about the values (counts). Source: http://stackoverflow.com/questions/5133871/how-to-plot-a-pie-of-color-list
# Matplotlib for some reasons changes colors. Therefore color 2 and 4 have to be changed...
data = {(0, 210, 0): 11, (236, 0, 0): 11, (255, 127, 36): 11, (234, 234, 0): 11, } # values in hexa: #2DD700 ,#00A287, #FF6700

colors = []
counts = []

for color, count in data.items():
    # matplotlib wants colors as 0.0-1.0 floats, not 0-255 ints
    colors.append([float(x)/255 for x in color])
    counts.append(count)
    
# Percentage (and total values)
def my_autopct(pct):
    total=sum(fracs)
    val=int(pct*total/100.0)
    return '{p:.1f}%  ({v:d})'.format(p=pct,v=val)
    

# The pie chart (DB-values, explode pies, Labels, decimal places, add shadows to pies
pie(fracs, explode=explode, colors=colors, autopct=my_autopct, labels=labels, shadow=True)

# Title of the pie chart
title('Actuality of all OSM-Line-Features')

# Save plot to *.png-file
plt.savefig('pics/c2_actuality_line.jpeg')

plt.clf()
 