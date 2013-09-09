# -*- coding: utf-8 -*-
#!/usr/bin/python2.7

#description     :This file creates a map: Actuality of all lines
#author          :Christopher Barron @ http://giscience.uni-hd.de/
#date            :19.01.2013
#version         :0.1
#usage           :python pyscript.py
#==============================================================================

import mapnik2

# import db connection parameters
import db_conn_para as db

###
###
db_name = db.g_my_dbname
db_user = db.g_my_username
hostname = db.g_my_hostname
db_pw = db.g_my_dbpassword
###
### 

###
### Width (in px), Height (in px), Name and Format of the output-picture
pic_output_width = 1200
pic_output_height = 800
pic_output_name = 'pics/c2_map_actuality_lines'
pic_output_format = 'jpeg'
###
###

# create a map with a given width and height in pixels
# note: m.srs will default to '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'
# the 'map.srs' is the target projection of the map and can be whatever you wish
m = mapnik2.Map(pic_output_width,pic_output_height) 

# Background color of the data
m.background = mapnik2.Color('White') # set background colour to. List of RGB-Colors: http://gucky.uni-muenster.de/cgi-bin/rgbtab

# style object to hold rules
s = mapnik2.Style() 
s2 = mapnik2.Style() 
s3 = mapnik2.Style() 
s4 = mapnik2.Style() 

# rule object to hold symbolizers
r = mapnik2.Rule() 
r2 = mapnik2.Rule() 
r3 = mapnik2.Rule() 
r4 = mapnik2.Rule() 

###
### Color of the lines
###
line_symbolizer = mapnik2.LineSymbolizer(mapnik2.Color('#00d200'),3)	# green
line_symbolizer2 = mapnik2.LineSymbolizer(mapnik2.Color('#eaea00'),3)	# yellow
line_symbolizer3 = mapnik2.LineSymbolizer(mapnik2.Color('#ff7f24'),3)	# orange
line_symbolizer4 = mapnik2.LineSymbolizer(mapnik2.Color('#ec0000'),3)# red

# add the line_symbolizer to the rule object
r.symbols.append(line_symbolizer)
r2.symbols.append(line_symbolizer2)
r3.symbols.append(line_symbolizer3) 
r4.symbols.append(line_symbolizer4) 

# now add the rule(s) to the style and we're done
s.rules.append(r)
s2.rules.append(r2)
s3.rules.append(r3)
s4.rules.append(r4)

# Styles are added to the map
m.append_style('My Style',s) 
m.append_style('My Style2',s2)
m.append_style('My Style3',s3)
m.append_style('My Style4',s4)

###
### START Layer 1
###
lyr = mapnik2.Layer('Geometry from PostGIS')
# note: layer.srs will default to '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'

# database-query for overlay-data
db_query = '''(

SELECT geom FROM
	(SELECT 
		geom, 
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
	--age > 183 AND age <= 365 -- older than 6 months and les than 1 year
	--age > 365 AND age <= 730 -- older than 1 year and less than 2 years
	--age > 730 -- older than 2 years
) AS foo'''

lyr.datasource = mapnik2.PostGIS(host=hostname,user=db_user,password=db_pw,dbname=db_name,table=db_query)

# Append Style to layer
lyr.styles.append('My Style')
###
### END Layer 1
###


###
### START Layer 2
###

lyr_2 = mapnik2.Layer('Geometry from PostGIS')
# note: layer.srs will default to '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'

# database-query for overlay-data
db_query2 = '''(

SELECT geom FROM
	(SELECT 
		geom, 
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
	--age <= 183 -- less than 6 months
	age > 183 AND age <= 365 -- older than 6 months and les than 1 year
	--age > 365 AND age <= 730 -- older than 1 year and less than 2 years
	--age > 730 -- older than 2 years
) AS foo'''


lyr_2.datasource = mapnik2.PostGIS(host=hostname,user=db_user,password=db_pw,dbname=db_name,table=db_query2)

# Append Style to layer
lyr_2.styles.append('My Style2')
###
### END Layer 2
###


###
### START Layer 3
###

lyr_3 = mapnik2.Layer('Geometry from PostGIS')
# note: layer.srs will default to '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'

# database-query for overlay-data
db_query3 = '''(

SELECT geom FROM
	(SELECT 
		geom, 
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
	--age <= 183 -- less than 6 months
	--age > 183 AND age <= 365 -- older than 6 months and les than 1 year
	age > 365 AND age <= 730 -- older than 1 year and less than 2 years
	--age > 730 -- older than 2 years
) AS foo'''


lyr_3.datasource = mapnik2.PostGIS(host=hostname,user=db_user,password=db_pw,dbname=db_name,table=db_query3)

# Append Style to layer
lyr_3.styles.append('My Style3')


###
### END Layer 3
###


###
### START Layer 4
###

lyr_4 = mapnik2.Layer('Geometry from PostGIS')
# note: layer.srs will default to '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'

# database-query for overlay-data
db_query4 = '''(

SELECT geom FROM
	(SELECT 
		geom, 
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
	--age <= 183 -- less than 6 months
	--age > 183 AND age <= 365 -- older than 6 months and les than 1 year
	--age > 365 AND age <= 730 -- older than 1 year and less than 2 years
	age > 730 -- older than 2 years
) AS foo'''


lyr_4.datasource = mapnik2.PostGIS(host=hostname,user=db_user,password=db_pw,dbname=db_name,table=db_query4)

# Append Style to layer
lyr_4.styles.append('My Style4')
###
### END Layer 4
###


###
### Append overlay-layers to the map
###
m.layers.append(lyr)
m.layers.append(lyr_2)
m.layers.append(lyr_3)
m.layers.append(lyr_4)

# Zoom to all
m.zoom_all()


# Write the map with its overlays to a png image 
mapnik2.render_to_file(m,pic_output_name, pic_output_format)

del m
