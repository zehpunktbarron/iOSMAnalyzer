# -*- coding: utf-8 -*-
#!/usr/bin/python2.7

#description     :This file creates a plot: Calculates the number of POIs grouped by category
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

-- How many POIs exists since when?
SELECT 
	date_trunc('month', generate_series)::date AS mydate,
	(SELECT 
		count(id) 
	FROM 
		hist_plp h 
	WHERE
		-- POI-Tags & Keys
		(
		-- accomodation & gastronomy
		((tags->'amenity') = 'bar') OR
		((tags->'amenity') = 'bbq') OR
		((tags->'amenity') = 'biergarten') OR
		((tags->'amenity') = 'cafe') OR
		((tags->'amenity') = 'drinking_water') OR
		((tags->'amenity') = 'fast_food') OR
		((tags->'amenity') = 'food_court') OR
		((tags->'amenity') = 'ice_cream') OR
		((tags->'amenity') = 'pub') OR
		((tags->'amenity') = 'restaurant') 
		)
		AND visible = 'true'
		AND valid_from <= generate_series AND 
		(version = (SELECT max(version) FROM hist_plp WHERE typ = h.typ AND h.id = hist_plp.id) AND
			( valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))
		AND minor = (SELECT max(minor) from hist_plp where typ = h.typ AND h.id = hist_plp.id AND h.version = hist_plp.version AND
			( valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))))

	)::int AS count_accomodation ,

	(SELECT 
		count(id) 
	FROM 
		hist_plp h 
	WHERE
		-- POI-Tags & Keys
		(
		-- education
		((tags->'amenity') = 'college') OR
		((tags->'amenity') = 'kindergarten') OR
		((tags->'amenity') = 'library') OR
		((tags->'amenity') = 'school') OR
		((tags->'amenity') = 'university')
		)
		AND visible = 'true'
		AND valid_from <= generate_series AND 
		(version = (SELECT max(version) FROM hist_plp WHERE typ = h.typ AND h.id = hist_plp.id) AND
			( valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))
		AND minor = (SELECT max(minor) from hist_plp where typ = h.typ AND h.id = hist_plp.id AND h.version = hist_plp.version AND
			( valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))))

	)::int AS count_education,

	(SELECT 
		count(id) 
	FROM 
		hist_plp h 
	WHERE
		-- POI-Tags & Keys
		(
		-- transport
		((tags->'amenity') = 'bicycle_parking') OR
		((tags->'amenity') = 'bicycle_rental') OR
		((tags->'amenity') = 'bus_station') OR
		((tags->'amenity') = 'car_rental') OR
		((tags->'amenity') = 'car_sharing') OR
		((tags->'amenity') = 'car_wash') OR
		((tags->'amenity') = 'ev_charging') OR
		((tags->'amenity') = 'ferry_terminal') OR
		((tags->'amenity') = 'fuel') OR
		((tags->'amenity') = 'grit_bin') OR
		((tags->'amenity') = 'parking') OR
		((tags->'amenity') = 'parking_entrance') OR
		((tags->'amenity') = 'parking_space') OR
		((tags->'amenity') = 'taxi')
		)
		AND visible = 'true'
		AND valid_from <= generate_series AND 
		(version = (SELECT max(version) FROM hist_plp WHERE typ = h.typ AND h.id = hist_plp.id) AND
			( valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))
		AND minor = (SELECT max(minor) from hist_plp where typ = h.typ AND h.id = hist_plp.id AND h.version = hist_plp.version AND
			( valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))))

	)::int AS count_transport,

	(SELECT 
		count(id) 
	FROM 
		hist_plp h 
	WHERE
		-- POI-Tags & Keys
		(
		-- finances
		((tags->'amenity') = 'atm') OR
		((tags->'amenity') = 'bank') OR
		((tags->'amenity') = 'bureau_de_change')
		)
		AND visible = 'true'
		AND valid_from <= generate_series AND 
		(version = (SELECT max(version) FROM hist_plp WHERE typ = h.typ AND h.id = hist_plp.id) AND
			( valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))
		AND minor = (SELECT max(minor) from hist_plp where typ = h.typ AND h.id = hist_plp.id AND h.version = hist_plp.version AND
			( valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))))

	)::int AS count_finances,

	(SELECT 
		count(id) 
	FROM 
		hist_plp h 
	WHERE
		-- POI-Tags & Keys
		(
		-- health care
		((tags->'amenity') = 'baby_hatch') OR
		((tags->'amenity') = 'clinic') OR
		((tags->'amenity') = 'dentist') OR
		((tags->'amenity') = 'doctors') OR
		((tags->'amenity') = 'hospital') OR
		((tags->'amenity') = 'nursing_home') OR
		((tags->'amenity') = 'pharmacy') OR
		((tags->'amenity') = 'social_facility') OR
		((tags->'amenity') = 'veterinary')
		)
		AND visible = 'true'
		AND valid_from <= generate_series AND 
		(version = (SELECT max(version) FROM hist_plp WHERE typ = h.typ AND h.id = hist_plp.id) AND
			( valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))
		AND minor = (SELECT max(minor) from hist_plp where typ = h.typ AND h.id = hist_plp.id AND h.version = hist_plp.version AND
			( valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))))

	)::int AS count_health,

	(SELECT 
		count(id) 
	FROM 
		hist_plp h 
	WHERE
		-- POI-Tags & Keys
		(
		-- art & culture
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
		AND valid_from <= generate_series AND 
		(version = (SELECT max(version) FROM hist_plp WHERE typ = h.typ AND h.id = hist_plp.id) AND
			( valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))
		AND minor = (SELECT max(minor) from hist_plp where typ = h.typ AND h.id = hist_plp.id AND h.version = hist_plp.version AND
			( valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))))

	)::int AS count_art,

	(SELECT 
		count(id) 
	FROM 
		hist_plp h 
	WHERE
		-- POI-Tags & Keys
		-- shops
		tags ? 'shop'
		AND visible = 'true'
		
		AND valid_from <= generate_series AND 
		(version = (SELECT max(version) FROM hist_plp WHERE typ = h.typ AND h.id = hist_plp.id) AND
			( valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))
		AND minor = (SELECT max(minor) from hist_plp where typ = h.typ AND h.id = hist_plp.id AND h.version = hist_plp.version AND
			( valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))))

	)::int AS count_shop,

	(SELECT 
		count(id) 
	FROM 
		hist_plp h 
	WHERE
		-- POI-Tags & Keys
		-- shops
		tags ? 'tourism'
		AND visible = 'true'
		
		AND valid_from <= generate_series AND 
		(version = (SELECT max(version) FROM hist_plp WHERE typ = h.typ AND h.id = hist_plp.id) AND
			( valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))
		AND minor = (SELECT max(minor) from hist_plp where typ = h.typ AND h.id = hist_plp.id AND h.version = hist_plp.version AND
			( valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))))

	)::int AS count_tourism,

	(SELECT 
		count(id) 
	FROM 
		hist_plp h 
	WHERE
		-- POI-Tags & Keys
		(
		-- other
		((tags->'amenity') = 'animal_boarding') OR
		((tags->'amenity') = 'animal_shelter') OR
		((tags->'amenity') = 'bench') OR
		((tags->'amenity') = 'brothel') OR
		((tags->'amenity') = 'clock') OR
		((tags->'amenity') = 'courthouse') OR
		((tags->'amenity') = 'crematorium') OR
		((tags->'amenity') = 'crypt') OR
		((tags->'amenity') = 'embassy') OR
		((tags->'amenity') = 'fire_station') OR
		((tags->'amenity') = 'grave_yard') OR
		((tags->'amenity') = 'hunting_stand') OR
		((tags->'amenity') = 'marketplace') OR
		((tags->'amenity') = 'place_of_worship') OR
		((tags->'amenity') = 'police') OR
		((tags->'amenity') = 'post_box') OR
		((tags->'amenity') = 'post_office') OR
		((tags->'amenity') = 'prison') OR
		((tags->'amenity') = 'public_building') OR
		((tags->'amenity') = 'recycling') OR
		((tags->'amenity') = 'sauna') OR
		((tags->'amenity') = 'shelter') OR
		((tags->'amenity') = 'shower') OR
		((tags->'amenity') = 'telephone') OR
		((tags->'amenity') = 'toilets') OR
		((tags->'amenity') = 'townhall') OR
		((tags->'amenity') = 'vending_machine') OR
		((tags->'amenity') = 'waste_basket') OR
		((tags->'amenity') = 'waste_disposal') OR
		((tags->'amenity') = 'watering_place')
		)
		AND visible = 'true'		
		AND valid_from <= generate_series AND 
		(version = (SELECT max(version) FROM hist_plp WHERE typ = h.typ AND h.id = hist_plp.id) AND
			( valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))
		AND minor = (SELECT max(minor) from hist_plp where typ = h.typ AND h.id = hist_plp.id AND h.version = hist_plp.version AND
			( valid_from <= generate_series AND (valid_to >= generate_series OR valid_to is null))))

	)::int AS count_other


	

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
datatypes = [('date', 'S20'),('col2', 'i4'), ('col3', 'i4'), ('col4', 'i4'), ('col5', 'i4'), ('col6', 'i4'), ('col7', 'i4'), ('col8', 'i4'), ('col9', 'i4'), ('col10', 'i4')]

# Data-tuple and datatype
data = np.array(data_tuples, dtype=datatypes)

# Date comes from 'col1'
col2 = data['col2']
col3 = data['col3']
col4 = data['col4']
col5 = data['col5']
col6 = data['col6']
col7 = data['col7']
col8 = data['col8']
col9 = data['col9']
col10 = data['col10']

# Converts date to a manageable date-format for matplotlib
dates = mdates.num2date(mdates.datestr2num(data['date']))
fig, ax = plt.subplots()

# set figure size
fig.set_size_inches(14,8)

# Create linechart
plt.plot(dates, col2, color = '#2dd700', linewidth=2, label='Accomodation & Gastronomy')
plt.plot(dates, col3, color = '#00a287', linewidth=2, label='Education')
plt.plot(dates, col4, color = '#ff6700', linewidth=2, label='Transportation')
plt.plot(dates, col5, color = '#f5001d', linewidth=2, label='Finance')
plt.plot(dates, col6, color = '#2dd700', linewidth=2, linestyle='dashed', label='Health Care')
plt.plot(dates, col7, color = '#00a287', linewidth=2, linestyle='dashed', label='Art & Culture')
plt.plot(dates, col8, color = '#ff6700', linewidth=2, linestyle='dashed', label='Shop')
plt.plot(dates, col9, color = '#f5001d', linewidth=2, linestyle='dashed', label='Tourism')
plt.plot(dates, col10, color = 'b', linewidth=2, linestyle='dashed', label='Others')


# Place a gray dashed grid behind the thicks (only for y-axis)
ax.yaxis.grid(color='gray', linestyle='dashed')

# Set this grid behind the thicks
ax.set_axisbelow(True) 

# Rotate x-labels on the x-axis
fig.autofmt_xdate()

# Label x and y axis
plt.xlabel('Date')
plt.ylabel('Number of POIs')

# Locate legend on the plot (http://matplotlib.org/users/legend_guide.html#legend-location)
# Shink current axis by 20%
box = ax.get_position()
ax.set_position([box.x0, box.y0, box.width * 0.9, box.height * 0.9])

# Put a legend to the right of the current axis and reduce the font size
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), prop={'size':9})


# Plot-title
plt.title('Development of different POI-Groupes')

# Save plot to *.jpeg-file
plt.savefig('pics/c5_poi_grouped.jpeg')

plt.clf()
