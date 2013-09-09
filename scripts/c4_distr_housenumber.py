# -*- coding: utf-8 -*-
#!/usr/bin/python2.7

#description     :This file creates a plot: Calculates the distribution (node, additional tag or interpolation-line) of all housenumbers
#author          :Christopher Barron @ http://giscience.uni-hd.de/
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
cur1 = conn.cursor()

# Execute SQL query. For more than one row use three '"'
try:
  cur1.execute(""" 

-- Calculate number of interpolated housenumbers
DROP TABLE IF EXISTS hausnummern;
CREATE TABLE hausnummern AS SELECT 
	T1.road_id,
	T1.start_interpol -> 'addr:interpolation' AS interpolation_type,
	(T1.start_hnr -> 'addr:housenumber') AS start_hnr,
	(T2.end_hnr -> 'addr:housenumber') AS end_hnr
FROM 
	(SELECT 
		a.id AS road_id,
		a.tags AS start_interpol,
		b.tags AS start_hnr
	FROM
		(SELECT 
			id,
			ST_StartPoint(geom) AS startpoint,
			ST_EndPoint(geom)  AS endpoint,
			tags,
			geom
		FROM
			hist_line 
		WHERE 
			tags ? 'addr:interpolation' AND
			visible = 'true' AND
			((version = (SELECT max(version) from hist_line as h where h.id = hist_line.id AND
				valid_from <= CURRENT_TIMESTAMP AND (valid_to >= CURRENT_TIMESTAMP OR valid_to is null))) 
			AND minor = (SELECT max(minor) from hist_line as h where h.id = hist_line.id AND h.version = hist_line.version AND
				(valid_from <= CURRENT_TIMESTAMP AND (valid_to >= CURRENT_TIMESTAMP OR valid_to is null))))
		) AS a,
		
		(SELECT
			id,
			geom,
			tags
		FROM
			hist_point
		WHERE 
			tags ? 'addr:housenumber' AND
			visible = 'true' AND
			((version = (SELECT max(version) from hist_point as h where h.id = hist_point.id AND
				valid_from <= CURRENT_TIMESTAMP AND (valid_to >= CURRENT_TIMESTAMP OR valid_to is null))) 
			AND minor = (SELECT max(minor) from hist_point as h where h.id = hist_point.id AND h.version = hist_point.version AND
				(valid_from <= CURRENT_TIMESTAMP AND (valid_to >= CURRENT_TIMESTAMP OR valid_to is null))))
		) AS b
	WHERE 
		a.startpoint = b.geom
	) AS T1

JOIN 
	(SELECT 
		a.id AS road_id,
		a.tags AS end_interpol,
		b.tags AS end_hnr
	FROM
		(SELECT 
			id,
			ST_EndPoint(geom) AS endpoint,
			tags
		FROM
			hist_line 
		WHERE 
			tags ? 'addr:interpolation' AND
			visible = 'true' AND
			((version = (SELECT max(version) from hist_line as h where h.id = hist_line.id AND
				valid_from <= CURRENT_TIMESTAMP AND (valid_to >= CURRENT_TIMESTAMP OR valid_to is null))) 
			AND minor = (SELECT max(minor) from hist_line as h where h.id = hist_line.id AND h.version = hist_line.version AND
				(valid_from <= CURRENT_TIMESTAMP AND (valid_to >= CURRENT_TIMESTAMP OR valid_to is null))))
		) AS a,
		
		(SELECT
			id,
			geom,
			tags
		FROM
			hist_point
		WHERE 
			tags ? 'addr:housenumber' AND
			visible = 'true' AND
			((version = (SELECT max(version) from hist_point as h where h.id = hist_point.id AND
				valid_from <= CURRENT_TIMESTAMP AND (valid_to >= CURRENT_TIMESTAMP OR valid_to is null))) 
			AND minor = (SELECT max(minor) from hist_point as h where h.id = hist_point.id AND h.version = hist_point.version AND
				(valid_from <= CURRENT_TIMESTAMP AND (valid_to >= CURRENT_TIMESTAMP OR valid_to is null))))
		) AS b
	WHERE 
		a.endpoint = b.geom
	) AS T2
ON 
	T1.road_id = T2.road_id;
	


-- delete last letter from start-housenumber if exists (e.g. 11b or 27a)
UPDATE 
	hausnummern 
SET 
	start_hnr = RTRIM(
		LEFT(start_hnr, char_length(start_hnr)-1)
	) WHERE ASCII
		(RIGHT(RTRIM(start_hnr),1)) NOT BETWEEN 48 AND 57 -- asci for numbers 0-9
;

-- delete last letter from end-housenumber if exists (e.g. 11b or 27a)
UPDATE 
	hausnummern 
SET 
	end_hnr = RTRIM(
		LEFT(end_hnr, char_length(start_hnr)-1)
	) WHERE ASCII
		(RIGHT(RTRIM(end_hnr),1)) NOT BETWEEN 48 AND 57 -- asci for numbers 0-9
;	
--
-- Create or replace function for altering all tables to the same user
--
CREATE OR REPLACE FUNCTION exec(text) returns text language plpgsql volatile
AS $f$ 
BEGIN
  EXECUTE $1;
  RETURN $1;
END;
$f$;
ALTER FUNCTION exec(text) OWNER TO """ +  db.g_my_username + """;

-- Run function
SELECT exec('ALTER TABLE ' || quote_ident(s.nspname) || '.' ||
	quote_ident(s.relname) || ' OWNER TO """ +  db.g_my_username + """')
FROM (SELECT nspname, relname
      FROM pg_class c JOIN pg_namespace n ON (c.relnamespace = n.oid) 
    WHERE nspname NOT LIKE E'pg\\_%' AND 
	  nspname <> 'information_schema' AND 
	  relkind IN ('r','S','v') ORDER BY relkind = 'S') s;


-- Calculate the number of housenumbers along each road tagged with "addr:interpolation"
SELECT COALESCE(sum(number_of_hnr), 0)::int FROM
	(SELECT 
		road_id, interpolation_type, start_hnr, end_hnr,
		CASE 
			-- If start-housenumber < end-housenumber
			WHEN (end_hnr - start_hnr) > 0 THEN
			(((end_hnr - start_hnr)/2)+1)
			
			-- If start-housenumber > end-housenumber
			ELSE
			(((start_hnr - end_hnr)/2)+1)
		END AS number_of_hnr
	FROM 
		-- Deletes cases like 99/1 and casts the result to int
		(SELECT 
			road_id, interpolation_type, start_hnr::int, end_hnr::int
		FROM 
			hausnummern 
		WHERE 
			NOT ((start_hnr !~ '^[0-9]+$') OR (end_hnr !~ '^[0-9]+$'))
		) AS foo
	) AS foo2
;

  """)

# Return the results of the query. Fetchall() =  all rows, fetchone() = first row
  records1 = cur1.fetchone()
  cur1.close()
except:
  print "Query could not be executed"



# START Execute SQL query2.
cur2 = conn.cursor()

try:
  cur2.execute("""

SELECT 
-- Housenumbers as or at a node
	(SELECT count(id)
	FROM 
		hist_polygon t 
	WHERE 
		tags ? 'addr:housenumber' AND 
		visible = 'true' AND
		version = (SELECT max(version) FROM hist_polygon WHERE typ = t.typ AND t.id = hist_polygon.id) AND
			( valid_from <= CURRENT_TIMESTAMP AND (valid_to >= CURRENT_TIMESTAMP OR valid_to is null))
		AND minor = (SELECT max(minor) from hist_polygon where typ = t.typ AND t.id = hist_polygon.id AND t.version = hist_polygon.version AND
			( valid_from <= CURRENT_TIMESTAMP AND (valid_to >= CURRENT_TIMESTAMP OR valid_to is null)))
	)::int AS hnr_polygon,


	-- Housenumbers at a polygon
	(SELECT count(id)
	FROM 
		hist_point t 
	WHERE 
		tags ? 'addr:housenumber' AND 
		visible = 'true' AND
		version = (SELECT max(version) FROM hist_point WHERE typ = t.typ AND t.id = hist_point.id) AND
			( valid_from <= CURRENT_TIMESTAMP AND (valid_to >= CURRENT_TIMESTAMP OR valid_to is null))
		AND minor = (SELECT max(minor) from hist_point where typ = t.typ AND t.id = hist_point.id AND t.version = hist_point.version AND
			( valid_from <= CURRENT_TIMESTAMP AND (valid_to >= CURRENT_TIMESTAMP OR valid_to is null)))
	)::int AS hnr_point
;

  """)

# Return the results of the query. Fetchall() =  all rows, fetchone() = first row
  records2 = cur2.fetchone()
  cur2.close()
  conn.close()
  
except:
  print "Query2 could not be executed"

# END Execute SQL query2.

# Get data from query
col1 = records1[0]
col2 = records2[0]
col3 = records2[1]


# make a square figure and axes
figure(1, figsize=(6,6))
ax = axes([0.2, 0.2, 0.6, 0.6])

# pie-labelling
labels = 'Interpolation', 'Tag of a Polygon', 'Single Node'

# get db-values as fracs
fracs = [col1,col2, col3]

# explode values
explode=(0.05, 0.05, 0.05)

# Color in RGB. not shure about the values (counts). Source: http://stackoverflow.com/questions/5133871/how-to-plot-a-pie-of-color-list
data = {(45, 215, 0): 110, (0, 162, 135): 11, (255, 103, 0): 4} # values in hexa: #2DD700 ,#00A287, #FF6700

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
#pie(fracs, explode=explode, colors=colors, autopct=lambda(p): '%.0f' % (p * sum(fracs) / 100), labels=labels, shadow=True)

# Title of the pie chart
title('Distribution of House Numbers')

# Save plot to *.jpeg-file
savefig('pics/c4_distr_housenumber.jpeg')

plt.clf()
