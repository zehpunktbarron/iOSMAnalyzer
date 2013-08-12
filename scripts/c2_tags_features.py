# -*- coding: utf-8 -*-
#!/usr/bin/python2.7

#description     :This file creates a plot: How many currently valid OSM objects have how many tags?
#author          :Christopher Barron
#date            :19.01.2013
#version         :0.1
#usage           :python pyscript.py
#==============================================================================

import psycopg2
from pylab import *
import matplotlib

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
  
SELECT count_today::int AS tags_total, count(id)::int AS count FROM (
		SELECT 
			T1.id, 
			T1.count AS count_today, -- Tags of currently valid objects
			T2.count AS count_total, -- Tags the objects ever had
			(T2.count-T1.count) AS differenz -- Amount of tags the object had but are no longer part of a currently valid object
		FROM    -- Tags from an object that is currently valid
			(SELECT id, count(kvp) FROM 
				(SELECT id, (each(tags)) AS kvp FROM hist_plp 
				WHERE visible = 'true' AND
					version = (SELECT max(version) FROM hist_plp AS h WHERE h.id = hist_plp.id AND
						(valid_from <= CURRENT_TIMESTAMP AND (valid_to >= CURRENT_TIMESTAMP OR valid_to is null))) 
					AND minor = (SELECT max(minor) FROM hist_plp AS h WHERE h.id = hist_plp.id AND h.version = hist_plp.version AND
						(valid_from <= CURRENT_TIMESTAMP AND (valid_to >= CURRENT_TIMESTAMP OR valid_to is null)))
			GROUP BY kvp, id) AS foo GROUP BY id ORDER BY count DESC
			) T1 
		
		JOIN    -- Total tags from an object 
			(SELECT id, count(kvp) FROM 
				(SELECT id, (each(tags)) AS kvp FROM hist_plp 
			GROUP BY kvp, id) AS foo2 GROUP BY id
			) T2 
		ON T1.id = T2.id ) AS foo 
	GROUP BY count_today ORDER BY count_today ASC; 
; 

  """)
  
# Getting a list of tuples from the database-cursor (cur)
  data_tuples = []
  for row in cur:
    data_tuples.append(row)
  
except:
  print "Query could not be executed"

# Datatypes of the returning data: column 1(col1) --> integer, column 2(date) --> string
datatypes = [('col1', 'int'),('col2', 'int')]

# Data-tuple and datatype
data = np.array(data_tuples, dtype=datatypes)

# Date comes from 'col1'
col1 = data['col1']
col2 = data['col2']

###
### Plot (Barchart)
###

fig, ax = plt.subplots()

# Plot Scatterplot
plt.bar(col1,col2, color = '#2dd700')

# Title of the pie chart
plt.title('Distribution of the Number of Tags from all OSM-Objects')

# Label x and y axis
ax.set_xlabel('Number of Tags [currently valid Version]')
ax.set_ylabel('Number of OSM-Objects')

# Place a gray dashed grid behind the thicks (only for y-axis)
ax.yaxis.grid(color='gray', linestyle='dashed')

# Set this grid behind the thicks
ax.set_axisbelow(True) 

# Save plot to *.jpeg-file
savefig('pics/c2_tags_features.jpeg')

plt.clf()