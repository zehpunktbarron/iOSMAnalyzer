# -*- coding: utf-8 -*-
#!/usr/bin/python2.7

#description     :This file creates a plot: Calculates the total amount and percentage of node-contributions by each contributer. Results are grouped by three mappertypes: ""Senior-Mappers", "Junior-Mappers" and "Nonrecurring-Mappers"
#author          :Christopher Barron  @ http://giscience.uni-hd.de/
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
      
# Verbindung mit der DB mittels psycopg2 herstellen
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
	-- Senior Mapper
	(SELECT 
		COUNT(user_name) 
	FROM 
		(SELECT 
			user_name, 
			COUNT(user_name) AS edits_absolut
		FROM 
			hist_point 
		WHERE
			visible = 'true'
		GROUP BY 
			user_name
		) as foo1
	WHERE 
		edits_absolut >=1000) AS senior_mappers,

	-- Junior Mapper
	(SELECT 
		COUNT(user_name) 
	FROM 
		(SELECT 
			user_name, 
			COUNT(user_name) AS edits_absolut
		FROM 
			hist_point
		WHERE
			visible = 'true'
		GROUP BY 
			user_name
		) AS foo2 
	WHERE 
		edits_absolut <1000 AND edits_absolut >=10) AS junior_mappers,

	-- Nonrecurring Mapper
	(SELECT 
		COUNT(user_name) 
	FROM 
		(SELECT 
			user_name, 
			COUNT(user_name) AS edits_absolut
		FROM 
			hist_point
		WHERE
			visible = 'true'
		GROUP BY 
			user_name) AS foo3 
	WHERE 
		edits_absolut <10) as Nonrecurring_mappers
;

  """)

# Return the results of the query. Fetchall() =  all rows, fetchone() = first row
  records = cur.fetchone()
  cur.close()

except:
  print "Query could not be executed"

  
# Get data from query
senior_m = records[0]
junior_m = records[1]
nonrecurring_m = records[2]


# make a square figure and axes
figure(1, figsize=(6,6))
ax = axes([0.2, 0.2, 0.6, 0.6])

# pie-labelling
labels = 'Senior Mappers', 'Junior Mappers', 'Nonrecurring Mappers'

# get db-values as fracs
fracs = [senior_m, junior_m, nonrecurring_m]

# explode values
explode=(0.05, 0.05, 0.05)

# Color in RGB. not shure about the values (counts). Source: http://stackoverflow.com/questions/5133871/how-to-plot-a-pie-of-color-list
data = {(0, 210, 0): 110, (236, 0, 0): 4, (234, 234, 0): 11} # values in hexa: #2DD700 ,#00A287, #FF6700

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
title('Mappertypes based on their Node-Contribution')

# Save plot to *.jpeg-file
savefig('pics/c7_mappertyp.jpeg')

plt.clf()
