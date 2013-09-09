# -*- coding: utf-8 -*-
#!/usr/bin/python2.7

#description     :This file creates a map: Calculates all points where two roads intersect each other without a common node. Segments with a bridge or a tunnel are excluded
#author          :Christopher Barron @ http://giscience.uni-hd.de/
#date            :19.01.2013
#version         :0.1
#usage           :python pyscript.py
#==============================================================================

import psycopg2
import mapnik2
from optparse import OptionParser
import sys, os, subprocess
import os.path
import cStringIO
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
### Path to OSM-XML file (should be provided in the "osm-mapnik-style"-folder providedby Mapnik
path_to_osm_xml = "/opt/osm-mapnik-style/osm.xml"
###
###

###
### Path to Point-Symbolizer for point objects that are overlai
point_marker = '../iOSMAnalyzer/pin.png'

###
### Width (in px), Height (in px), Name and Format of the output-picture
pic_output_width = 1200
pic_output_height = 800
pic_output_name = 'pics/c3_map_topology_junctions'
pic_output_format = 'jpeg'
###
###

###
### database-query for overlay-data
db_query = '''(

SELECT geom FROM kreuzungen_falsch_fertig

) AS foo'''

###
###


###
### Create views
dsn = ""
dbprefix = "hist"
viewprefix = "hist_view"
hstore = ""
date = 'CURRENT_TIMESTAMP'
viewcolumns = "access,addr:housename,addr:housenumber,addr:interpolation,admin_level,aerialway,aeroway,amenity,area,barrier,bicycle,brand,bridge,boundary,building,construction,covered,culvert,cutting,denomination,disused,embankment,foot,generator:source,harbour,highway,tracktype,capital,ele,historic,horse,intermittent,junction,landuse,layer,leisure,lock,man_made,military,motorcar,name,natural,oneway,operator,population,power,power_source,place,railway,ref,religion,route,service,shop,sport,surface,toll,tourism,tower:type,tunnel,water,waterway,wetland,width,wood"
extracolumns = ""
###
###

# Split columns into the osm2pgsql-database-schema for rendering with Mapnik
# This part of the code is taken from Peter Koerner's "OSM-History-Renderer" (https://github.com/MaZderMind/osm-history-renderer/blob/master/renderer/render.py)
columns = viewcolumns.split(',')
if(extracolumns):
    columns += options.extracolumns.split(',')

def create_views(dsn, dbprefix, viewprefix, hstore, columns, date):
    try:
      conn_string="dbname=%s user=%s host=%s password=%s" % (db_name, db_user, hostname, db_pw)
      print "Connecting to database\n->%s" % (conn_string)
      con = psycopg2.connect(conn_string)
      print "Connection to database was established succesfully"
    except:
      print "Connection to database failed"
    cur = con.cursor()
    
    columselect = ""
    for column in columns:
        columselect += "tags->'%s' AS \"%s\", " % (column, column)
    
    cur.execute("DELETE FROM geometry_columns WHERE f_table_catalog = '' AND f_table_schema = 'public' AND f_table_name IN ('%s_point', '%s_line', '%s_roads', '%s_polygon');" % (viewprefix, viewprefix, viewprefix, viewprefix))
    
    cur.execute("DROP VIEW IF EXISTS %s_point" % (viewprefix))
    cur.execute("CREATE OR REPLACE VIEW %s_point AS SELECT id AS osm_id, %s geom AS way FROM %s_point WHERE %s BETWEEN valid_from AND COALESCE(valid_to, '9999-12-31');" % (viewprefix, columselect, dbprefix, date))
    cur.execute("INSERT INTO geometry_columns (f_table_catalog, f_table_schema, f_table_name, f_geometry_column, coord_dimension, srid, type) VALUES ('', 'public', '%s_point', 'way', 2, 900913, 'POINT');" % (viewprefix))
    
    cur.execute("DROP VIEW IF EXISTS %s_line" % (viewprefix))
    cur.execute("CREATE OR REPLACE VIEW %s_line AS SELECT id AS osm_id, %s z_order, geom AS way FROM %s_line WHERE %s BETWEEN valid_from AND COALESCE(valid_to, '9999-12-31');" % (viewprefix, columselect, dbprefix, date))
    cur.execute("INSERT INTO geometry_columns (f_table_catalog, f_table_schema, f_table_name, f_geometry_column, coord_dimension, srid, type) VALUES ('', 'public', '%s_line', 'way', 2, 900913, 'LINESTRING');" % (viewprefix))
    
    cur.execute("DROP VIEW IF EXISTS %s_roads" % (viewprefix))
    cur.execute("CREATE OR REPLACE VIEW %s_roads AS SELECT id AS osm_id, %s z_order, geom AS way FROM %s_line WHERE %s BETWEEN valid_from AND COALESCE(valid_to, '9999-12-31');" % (viewprefix, columselect, dbprefix, date))
    cur.execute("INSERT INTO geometry_columns (f_table_catalog, f_table_schema, f_table_name, f_geometry_column, coord_dimension, srid, type) VALUES ('', 'public', '%s_roads', 'way', 2, 900913, 'LINESTRING');" % (viewprefix))
    
    cur.execute("DROP VIEW IF EXISTS %s_polygon" % (viewprefix))
    cur.execute("CREATE OR REPLACE VIEW %s_polygon AS SELECT id AS osm_id, %s z_order, area AS way_area, geom AS way FROM %s_polygon WHERE %s BETWEEN valid_from AND COALESCE(valid_to, '9999-12-31');" % (viewprefix, columselect, dbprefix, date))
    cur.execute("INSERT INTO geometry_columns (f_table_catalog, f_table_schema, f_table_name, f_geometry_column, coord_dimension, srid, type) VALUES ('', 'public', '%s_polygon', 'way', 2, 900913, 'POLYGON');" % (viewprefix))
    
    # bbox-extent of database. Global variable for bbox extent
    cur.execute("SELECT ST_XMin(ST_Extent(ST_Transform(geom, 4326))) FROM %s_point;" % (dbprefix))
    global xmin
    xmin = cur.fetchone()[0]
        
    cur.execute("SELECT ST_YMin(ST_Extent(ST_Transform(geom, 4326))) FROM %s_point;" % (dbprefix))
    global ymin
    ymin = cur.fetchone()[0]
    
    cur.execute("SELECT ST_XMax(ST_Extent(ST_Transform(geom, 4326))) FROM %s_point;" % (dbprefix))
    global xmax
    xmax = cur.fetchone()[0]
    
    cur.execute("SELECT ST_YMax(ST_Extent(ST_Transform(geom, 4326))) FROM %s_point;" % (dbprefix))
    global ymax
    ymax = cur.fetchone()[0]
    
    cur.execute("""
    
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
    
    """)
   
    cur.execute("""
    
    -- Extract currently valid roads
    DROP TABLE IF EXISTS hist_line_today;
    CREATE TABLE hist_line_today AS SELECT * FROM hist_line WHERE tags ? 'highway' AND visible = 'true' AND 
		    (version = (SELECT max(version) FROM hist_line AS h WHERE h.id = hist_line.id AND
			    (valid_from <= CURRENT_TIMESTAMP AND (valid_to >= CURRENT_TIMESTAMP OR valid_to is null))) 
		    AND minor = (SELECT max(minor) FROM hist_line AS h WHERE h.id = hist_line.id AND h.version = hist_line.version AND
			    (valid_from <= CURRENT_TIMESTAMP AND (valid_to >= CURRENT_TIMESTAMP OR valid_to is null))));

    ALTER TABLE hist_line_today ADD COLUMN pky serial NOT NULL PRIMARY KEY;
    CREATE INDEX idx_hist_line_today_geom ON hist_line_today USING gist (geom);


    -- Find roads that cross each other without being a bridge or a tunnel
    -- Furthermore no "intersections" are allowed to be taken where two roads touch each other at their start- or/and endpoint

    DROP TABLE IF EXISTS kreuzungen_ohne_ende_start;
    CREATE TABLE kreuzungen_ohne_ende_start AS SELECT DISTINCT (ST_Dump(intersection(b.geom, a.geom))).geom AS the_intersection 
    FROM
	    hist_line_today AS a,
	    hist_line_today AS b
    WHERE
	    (ST_Crosses(a.geom,b.geom) AND NOT (a.tags ? 'bridge' OR b.tags ? 'bridge' OR a.tags ? 'layer' OR b.tags ? 'layer'))
	    AND NOT (
	    ST_StartPoint(a.geom) = ST_StartPoint(b.geom) OR
	    ST_EndPoint(a.geom) = ST_EndPoint(b.geom) OR
	    ST_StartPoint(a.geom) = ST_EndPoint(b.geom) OR
	    ST_EndPoint(a.geom) = ST_StartPoint(b.geom)
	    )
    ;

    ALTER TABLE kreuzungen_ohne_ende_start ADD COLUMN pky serial NOT NULL PRIMARY KEY;
    CREATE INDEX idx_kreuzungen_ohne_ende_start_geom ON kreuzungen_ohne_ende_start USING gist (the_intersection);

    -- Every node of all roads
    DROP TABLE IF EXISTS hist_line_today_points;
    CREATE TABLE hist_line_today_points AS SELECT (ST_DumpPoints(geom)).geom AS geom FROM hist_line_today;

    ALTER TABLE hist_line_today_points ADD COLUMN pky serial NOT NULL PRIMARY KEY;
    CREATE INDEX idx_hist_line_today_points_geom ON hist_line_today_points USING gist (geom);


    -- Join all nodes to a potential false intersection. Everytime a value is within into the "geom" column the value has to be deleted in the following stept.
    DROP TABLE IF EXISTS kreuzungen_falsch;
    CREATE TABLE kreuzungen_falsch AS SELECT T1.geom, T2.the_intersection 
    FROM 
	    hist_line_today_points T1 
	    RIGHT JOIN 
	    kreuzungen_ohne_ende_start T2
    ON T1.geom = T2.the_intersection;

    ALTER TABLE kreuzungen_falsch ADD COLUMN pky serial NOT NULL PRIMARY KEY;
    CREATE INDEX idx_kreuzungen_falsch_geom ON kreuzungen_falsch USING gist (geom);

    -- Löschen der doppelten Einträge (Das bedeutet, dass an einem Straßennode auch eine Linienkreuzung vorliegt. Und die muss weg)
    -- Delete duplicate nodes. (If there are two nodes on the same position (one from a possible intersecation and one from the highway-line) there is a intersection with a 
    -- common node in the database
    DELETE FROM kreuzungen_falsch WHERE (the_intersection <> '' AND geom <> '');

    -- Remove all start- and endpoints (all start- and endpoints which are also an intersection of two lines
    DROP TABLE IF EXISTS hist_line_today_start_end;
    CREATE TABLE hist_line_today_start_end AS
    SELECT ST_StartPoint(geom) AS geom 
    FROM 
	    hist_line_today 
	    UNION
	    SELECT ST_EndPoint(geom) AS geom FROM hist_line_today; 

    ALTER TABLE hist_line_today_start_end ADD COLUMN pky serial NOT NULL PRIMARY KEY;
    CREATE INDEX idx_hist_line_today_start_end_geom ON hist_line_today_start_end USING gist (geom);


    -- Start- and endpoint = wrong intersection?
    DROP TABLE IF EXISTS loeschen;
    CREATE TABLE loeschen AS
    SELECT the_intersection FROM kreuzungen_falsch AS a, hist_line_today_start_end AS b 
    WHERE 
	    ST_Intersects(a.the_intersection, b.geom);


    -- Delete all entries where a value is within both geom columns
    DROP TABLE IF EXISTS kreuzungen_falsch_fertig;
    CREATE TABLE kreuzungen_falsch_fertig AS
    SELECT T1.the_intersection AS geom, T2.the_intersection AS loeschen 
    FROM 
	    kreuzungen_falsch T1 
	    LEFT JOIN 
	    loeschen T2
    ON T1.geom = T2.the_intersection;

    -- Delete
    DELETE FROM kreuzungen_falsch_fertig WHERE geom <>'' AND loeschen <>'';
   
   
    --
    -- Mapnik gets the SRID from the geometry_columns table, so this is necessary
    --
    DELETE FROM geometry_columns WHERE f_table_name = 'kreuzungen_falsch_fertig';
    INSERT INTO geometry_columns (f_table_catalog, f_table_schema, f_table_name, f_geometry_column, coord_dimension, srid, type) 
    VALUES ('', 'public', 'kreuzungen_falsch_fertig', 'geom', 2, 900913, 'POINT');

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
	      
	      
    DROP TABLE IF EXISTS hist_line_today;
    DROP TABLE IF EXISTS kreuzungen_ohne_ende_start;
    DROP TABLE IF EXISTS hist_line_today_points;
    DROP TABLE IF EXISTS kreuzungen_falsch;
    DROP TABLE IF EXISTS hist_line_today_start_end;   
    DROP TABLE IF EXISTS loeschen;	      
	      
""")
 
    con.commit()
    cur.close()
    con.close()


# Call function to create the views
create_views(dsn, dbprefix, viewprefix, hstore, columns, date)

# Create map with width height
m = mapnik2.Map(pic_output_width, pic_output_height)

# Load osm-xml-stylesheet for rendering the views
mapnik2.load_map(m, path_to_osm_xml)

# Define projection
prj = mapnik2.Projection("+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs +over")

# Map bounds. Bound values come from SQL-query
if hasattr(mapnik2, 'Box2d'):
    bbox = mapnik2.Box2d(xmin,ymin,xmax,ymax)
else:
    bbox = mapnik2.Envelope(xmin,ymin,xmax,ymax)

# Project bounds to map projection
e = mapnik2.forward_(bbox, prj)

# Zoom map to bounding box
m.zoom_to_box(e)

###
### START Layer 1
###

# style object to hold rules
s = mapnik2.Style() 

# rule object to hold symbolizers
r = mapnik2.Rule() 

# Lines (outlines of polygons and/or simple lines. Line-Color (RGB) line-thickness
#polygon_symbolizer = mapnik2.PolygonSymbolizer(mapnik2.Color('red')) #rgb(5%,5%,5%)
# add the polygon_symbolizer to the rule object
#r.symbols.append(polygon_symbolizer) 

# Point Style. Path to marker.png
point_symbolizer = mapnik2.PointSymbolizer(mapnik2.PathExpression(point_marker) )

# Allow Overlaps and set opacity of marker
point_symbolizer.allow_overlap = True
point_symbolizer.opacity = 0.7

# add the point_symbolizer to the rule object
r.symbols.append(point_symbolizer) 

# now add the rule(s) to the style
s.rules.append(r) 

# Styles are added to the map
m.append_style('My Style',s) 

# Projection from PostGIS-Layer-Data
lyr = mapnik2.Layer('Geometry from PostGIS', '+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs +over')

# PostGIS-Connection + DB-Query
lyr.datasource = mapnik2.PostGIS(host=hostname, user=db_user, password=db_pw, dbname=db_name,table=db_query) 

# Append Style to layer
lyr.styles.append('My Style')

###
### END Layer 1
###

# Append overlay-layers to the map
m.layers.append(lyr)

###
### START scale
###

# center of the image
label_x = xmin + ((xmax - xmin) / 2)

# bottom of the image
label_y = ymin + ((ymax - ymin) / 30)

# create PointDatasource
pds = mapnik2.PointDatasource()

# place scale at the bottom-center of the map
pds.add_point(label_x, label_y, 'Name', "Scale: 1:" + str(m.scale_denominator()))

# create label symbolizers
if mapnik2.mapnik_version() >= 800:
    text = mapnik2.TextSymbolizer(mapnik2.Expression('[Name]'),'DejaVu Sans Bold',12,mapnik2.Color('black'))
else:
    text = mapnik2.TextSymbolizer('Name','DejaVu Sans Bold',12,mapnik2.Color('black'))

s3 = mapnik2.Style()
r3 = mapnik2.Rule()
r3.symbols.append(text)
s3.rules.append(r3)

lyr3 = mapnik2.Layer('Memory Datasource')
lyr3.datasource = pds
lyr3.styles.append('Style')
m.layers.append(lyr3)
m.append_style('Style',s3)

###
### END scale
###

# Render Mapnik-map to png-file
mapnik2.render_to_file(m, pic_output_name, pic_output_format)

del m
