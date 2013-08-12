# -*- coding: utf-8 -*-
#!/usr/bin/python2.7

#description     :This file creates a plot: Calculates the development of the tag-completeness [%] of all "art & culture" POIs
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

--
-- Kunst und Kultur
--
SELECT
	generate_series,

	-- START Key "name"
	(CASE WHEN 
		cnt_total <> 0
	THEN 
		ROUND((cnt_name * 100.00 / cnt_total), 2)
	ELSE 0
	END)::float AS perc_name,
	-- END Key "name"

	-- START Key "operator"
	(CASE WHEN 
		cnt_total <> 0
	THEN 
		ROUND((cnt_operator * 100.00 / cnt_total), 2)
	ELSE 0
	END)::float AS perc_operator,
	-- END Key "operator"

	-- START Key "website"
	(CASE WHEN 
		cnt_total <> 0
	THEN 
		ROUND((cnt_website * 100.00 / cnt_total), 2)
	ELSE 0
	END)::float AS perc_website,
	-- END Key "website"

	-- START Key "housenumber"
	(CASE WHEN 
		cnt_total <> 0
	THEN 
		ROUND((cnt_housenumber * 100.00 / cnt_total), 2)
	ELSE 0
	END)::float AS perc_housenumber,
	-- END Key "housenumber"

	-- START Key "phone"
	(CASE WHEN 
		cnt_total <> 0
	THEN 
		ROUND((cnt_phone * 100.00 / cnt_total), 2)
	ELSE 0
	END)::float AS perc_phone,
	-- END Key "phone"

	-- START Key "wheelchair"
	(CASE WHEN 
		cnt_total <> 0
	THEN 
		ROUND((cnt_wheelchair * 100.00 / cnt_total), 2)
	ELSE 0
	END)::float AS perc_wheelchair
	-- END Key "wheelchair"




FROM
	(SELECT generate_series,
		(SELECT 
			count(distinct id)
		FROM
			(SELECT 
				id, 
				skeys(tags)
			FROM 
				hist_plp h 
			WHERE 
				-- Kunst und Kultur
				(
				((tags->'amenity') = 'arts_centre') OR
				((tags->'amenity') = 'cinema') OR
				((tags->'amenity') = 'community_centre') OR
				((tags->'amenity') = 'fountain') OR
				((tags->'amenity') = 'nightclub') OR
				((tags->'amenity') = 'social_centre') OR
				((tags->'amenity') = 'stripclub') OR
				((tags->'amenity') = 'studio') OR
				((tags->'amenity') = 'swingerclub') OR
				((tags->'amenity') = 'theatre')
				) 
				AND visible = 'true'
				AND
				(version = (SELECT max(version) FROM hist_plp WHERE typ = h.typ AND h.id = hist_plp.id) AND
					( valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))
				AND minor = (SELECT max(minor) from hist_plp where typ = h.typ AND h.id = hist_plp.id AND h.version = hist_plp.version AND
					( valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))))
			) AS foo
		WHERE
			skeys = 'name'
		) AS cnt_name, 

		-- START operator
		(SELECT 
			count(distinct id)
		FROM
			(SELECT 
				id, 
				skeys(tags)
			FROM 
				hist_plp h 
			WHERE 
				-- Kunst und Kultur
				(
				((tags->'amenity') = 'arts_centre') OR
				((tags->'amenity') = 'cinema') OR
				((tags->'amenity') = 'community_centre') OR
				((tags->'amenity') = 'fountain') OR
				((tags->'amenity') = 'nightclub') OR
				((tags->'amenity') = 'social_centre') OR
				((tags->'amenity') = 'stripclub') OR
				((tags->'amenity') = 'studio') OR
				((tags->'amenity') = 'swingerclub') OR
				((tags->'amenity') = 'theatre')
				) 
				AND visible = 'true'
				AND
				(version = (SELECT max(version) FROM hist_plp WHERE typ = h.typ AND h.id = hist_plp.id) AND
					( valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))
				AND minor = (SELECT max(minor) from hist_plp where typ = h.typ AND h.id = hist_plp.id AND h.version = hist_plp.version AND
					( valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))))
			) AS foo
		WHERE
			skeys = 'operator'
		) AS cnt_operator, 
		-- END operator

		-- START website
		(SELECT 
			count(distinct id)
		FROM
			(SELECT 
				id, 
				skeys(tags)
			FROM 
				hist_plp h 
			WHERE 
				-- Kunst und Kultur
				(
				((tags->'amenity') = 'arts_centre') OR
				((tags->'amenity') = 'cinema') OR
				((tags->'amenity') = 'community_centre') OR
				((tags->'amenity') = 'fountain') OR
				((tags->'amenity') = 'nightclub') OR
				((tags->'amenity') = 'social_centre') OR
				((tags->'amenity') = 'stripclub') OR
				((tags->'amenity') = 'studio') OR
				((tags->'amenity') = 'swingerclub') OR
				((tags->'amenity') = 'theatre')
				) 
				AND visible = 'true'
				AND
				(version = (SELECT max(version) FROM hist_plp WHERE typ = h.typ AND h.id = hist_plp.id) AND
					( valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))
				AND minor = (SELECT max(minor) from hist_plp where typ = h.typ AND h.id = hist_plp.id AND h.version = hist_plp.version AND
					( valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))))
			) AS foo
		WHERE
			skeys = 'website'
		) AS cnt_website, 
		-- END website

		-- START housenumber
		(SELECT 
			count(distinct id)
		FROM
			(SELECT 
				id, 
				skeys(tags)
			FROM 
				hist_plp h 
			WHERE 
				-- Kunst und Kultur
				(
				((tags->'amenity') = 'arts_centre') OR
				((tags->'amenity') = 'cinema') OR
				((tags->'amenity') = 'community_centre') OR
				((tags->'amenity') = 'fountain') OR
				((tags->'amenity') = 'nightclub') OR
				((tags->'amenity') = 'social_centre') OR
				((tags->'amenity') = 'stripclub') OR
				((tags->'amenity') = 'studio') OR
				((tags->'amenity') = 'swingerclub') OR
				((tags->'amenity') = 'theatre')
				) 
				AND visible = 'true'
				AND
				(version = (SELECT max(version) FROM hist_plp WHERE typ = h.typ AND h.id = hist_plp.id) AND
					( valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))
				AND minor = (SELECT max(minor) from hist_plp where typ = h.typ AND h.id = hist_plp.id AND h.version = hist_plp.version AND
					( valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))))
			) AS foo
		WHERE
			skeys = 'addr:housenumber'
		) AS cnt_housenumber, 
		-- END housenumber

		-- START phone
		(SELECT 
			count(distinct id)
		FROM
			(SELECT 
				id, 
				skeys(tags)
			FROM 
				hist_plp h 
			WHERE 
				-- Kunst und Kultur
				(
				((tags->'amenity') = 'arts_centre') OR
				((tags->'amenity') = 'cinema') OR
				((tags->'amenity') = 'community_centre') OR
				((tags->'amenity') = 'fountain') OR
				((tags->'amenity') = 'nightclub') OR
				((tags->'amenity') = 'social_centre') OR
				((tags->'amenity') = 'stripclub') OR
				((tags->'amenity') = 'studio') OR
				((tags->'amenity') = 'swingerclub') OR
				((tags->'amenity') = 'theatre')
				) 
				AND visible = 'true'
				AND
				(version = (SELECT max(version) FROM hist_plp WHERE typ = h.typ AND h.id = hist_plp.id) AND
					( valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))
				AND minor = (SELECT max(minor) from hist_plp where typ = h.typ AND h.id = hist_plp.id AND h.version = hist_plp.version AND
					( valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))))
			) AS foo
		WHERE
			skeys = 'phone'
		) AS cnt_phone, 
		-- END phone

		-- START wheelchair
		(SELECT 
			count(distinct id)
		FROM
			(SELECT 
				id, 
				skeys(tags)
			FROM 
				hist_plp h 
			WHERE 
				-- Kunst und Kultur
				(
				((tags->'amenity') = 'arts_centre') OR
				((tags->'amenity') = 'cinema') OR
				((tags->'amenity') = 'community_centre') OR
				((tags->'amenity') = 'fountain') OR
				((tags->'amenity') = 'nightclub') OR
				((tags->'amenity') = 'social_centre') OR
				((tags->'amenity') = 'stripclub') OR
				((tags->'amenity') = 'studio') OR
				((tags->'amenity') = 'swingerclub') OR
				((tags->'amenity') = 'theatre')
				) 
				AND visible = 'true'
				AND
				(version = (SELECT max(version) FROM hist_plp WHERE typ = h.typ AND h.id = hist_plp.id) AND
					( valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))
				AND minor = (SELECT max(minor) from hist_plp where typ = h.typ AND h.id = hist_plp.id AND h.version = hist_plp.version AND
					( valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))))
			) AS foo
		WHERE
			skeys = 'wheelchair'
		) AS cnt_wheelchair, 
		-- END wheelchair

		-- START total
		(SELECT 
			count(distinct id)
		FROM
			(SELECT 
				id, 
				skeys(tags)
			FROM 
				hist_plp h 
			WHERE 
				-- Kunst und Kultur
				(
				((tags->'amenity') = 'arts_centre') OR
				((tags->'amenity') = 'cinema') OR
				((tags->'amenity') = 'community_centre') OR
				((tags->'amenity') = 'fountain') OR
				((tags->'amenity') = 'nightclub') OR
				((tags->'amenity') = 'social_centre') OR
				((tags->'amenity') = 'stripclub') OR
				((tags->'amenity') = 'studio') OR
				((tags->'amenity') = 'swingerclub') OR
				((tags->'amenity') = 'theatre')
				) 
				AND visible = 'true'
				AND
				(version = (SELECT max(version) FROM hist_plp WHERE typ = h.typ AND h.id = hist_plp.id) AND
					( valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))
				AND minor = (SELECT max(minor) from hist_plp where typ = h.typ AND h.id = hist_plp.id AND h.version = hist_plp.version AND
					( valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))))
			) AS foo
		) AS cnt_total
		-- END total

		
	FROM generate_series(
		(SELECT date_trunc ('month',(
			SELECT MIN(valid_from) FROM hist_plp)) as foo),  -- Select minimum date (month)
		(SELECT MAX(valid_from) FROM hist_plp)::date,	-- Select maximum date
		interval '1 month')
	) AS foo2
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
datatypes = [('date', 'S20'),('col2', 'double'), ('col3', 'double'), ('col4', 'double'), ('col5', 'double'), ('col6', 'double'), ('col7', 'double')]

# Data-tuple and datatype
data = np.array(data_tuples, dtype=datatypes)

# Date comes from 'col1'
col2 = data['col2']
col3 = data['col3']
col4 = data['col4']
col5 = data['col5']
col6 = data['col6']
col7 = data['col7']


# Converts date to a manageable date-format for matplotlib
dates = mdates.num2date(mdates.datestr2num(data['date']))
fig, ax = plt.subplots()

# set figure size
fig.set_size_inches(12,8)


# Create linechart
plt.plot(dates, col2, color = '#2dd700', linewidth=2, label='name = *')
#plt.plot(dates, col3, color = '#00a287', linewidth=2, label='opening_hours = *')
plt.plot(dates, col3, color = '#ff6700', linewidth=2, linestyle='dashed', label='operator = *')
plt.plot(dates, col4, color = '#ff6700', linewidth=2, label='website = *')
plt.plot(dates, col5, color = '#f5001d', linewidth=2, label='addr:housenumber = *')
plt.plot(dates, col6, color = '#2dd700', linewidth=2, linestyle='dashed', label='phone = *')
plt.plot(dates, col7, color = '#00a287', linewidth=2, linestyle='dashed', label='wheelchair = *')

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
plt.ylabel('Tag-Completeness [%]')

# Locate legend on the plot (http://matplotlib.org/users/legend_guide.html#legend-location)
# Shink current axis by 20%
box = ax.get_position()
ax.set_position([box.x0, box.y0, box.width * 0.9, box.height * 0.9])

# Put a legend to the right of the current axis and reduce the font size
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), prop={'size':9})


# Plot-title
plt.title('Development of the Tag-Completeness of all Art & Culture POIs')

# Save plot to *.jpeg-file
plt.savefig('pics/c5_tag_completeness_art_culture.jpeg')

plt.clf()