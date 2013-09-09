# -*- coding: utf-8 -*-
#!/usr/bin/python2.7

#description     :This file creates a map: Calculates a 1*1 km grid over the map. For each grid the amount of distinct contributers is calculated. Grids <15 contributers are rendered red, grids >=15 are rendered green
#author          :Christopher Barron @ http://giscience.uni-hd.de/
#date            :19.01.2013
#version         :0.1
#usage           :python pyscript.py
#==============================================================================

import psycopg2
import mapnik2
from optparse import OptionParser
import sys, os, subprocess
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
### database-query for overlay-data
db_query = '''(
SELECT geom FROM grid WHERE cnt < 15
) AS foo
'''

db_query2 = '''(
SELECT geom FROM grid WHERE cnt >= 15
) AS foo
'''

###
###

###
### Path to OSM-XML file (should be provided in the "osm-mapnik-style"-folder providedby Mapnik
path_to_osm_xml = "/opt/osm-mapnik-style/osm.xml"
###
###

###
### Path to Point-Symbolizer for point objects that are overlaid
point_marker = 'pin.png'

###
### Width (in px), Height (in px), Name and Format of the output-picture
pic_output_width = 1200
pic_output_height = 800
pic_output_name = 'pics/c3_map_roads_pos_acc'
pic_output_format = 'jpeg'
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
    -- START function: (Source: http://gis.stackexchange.com/questions/16374/how-to-create-a-regular-polygon-grid-in-postgis)
    --
    CREATE OR REPLACE FUNCTION public.makegrid_2d (
  bound_polygon public.geometry,
  grid_step integer,
  metric_srid integer = 900913 
)
RETURNS public.geometry AS
$body$
DECLARE
  BoundM public.geometry; --Bound polygon transformed to metric projection (with metric_srid SRID)
  Xmin DOUBLE PRECISION;
  Xmax DOUBLE PRECISION;
  Ymax DOUBLE PRECISION;
  X DOUBLE PRECISION;
  Y DOUBLE PRECISION;
  sectors public.geometry[];
  i INTEGER;
BEGIN
  BoundM := ST_Transform($1, $3); --From WGS84 (SRID 4326) to metric projection, to operate with step in meters
  Xmin := ST_XMin(BoundM);
  Xmax := ST_XMax(BoundM);
  Ymax := ST_YMax(BoundM);

  Y := ST_YMin(BoundM); --current sector's corner coordinate
  i := -1;
  <<yloop>>
  LOOP
    IF (Y > Ymax) THEN  --Better if generating polygons exceeds bound for one step. You always can crop the result. But if not you may get not quite correct data for outbound polygons (if you calculate frequency per a sector  e.g.)
        EXIT;
    END IF;

    X := Xmin;
    <<xloop>>
    LOOP
      IF (X > Xmax) THEN
          EXIT;
      END IF;

      i := i + 1;
      sectors[i] := ST_GeomFromText('POLYGON(('||X||' '||Y||', '||(X+$2)||' '||Y||', '||(X+$2)||' '||(Y+$2)||', '||X||' '||(Y+$2)||', '||X||' '||Y||'))', $3);

      X := X + $2;
    END LOOP xloop;
    Y := Y + $2;
  END LOOP yloop;

  RETURN ST_Transform(ST_Collect(sectors), ST_SRID($1));
END;
$body$
LANGUAGE 'plpgsql';

--
-- END function
--

--
-- Create 1000m x 1000m cells from a specified polygon (area)
--
DROP TABLE IF EXISTS cell;
CREATE TABLE cell AS 
SELECT 
	cell AS geom 
FROM 
	(SELECT 
		(ST_Dump
			(makegrid_2d
				(ST_GeomFromText
					('Polygon((8.632900 49.382500,8.733098 49.382500,8.733098 49.440999,8.632900 49.440999,8.632900 49.382500))',
					4326), -- WGS84 SRID
				1000) -- cell step in meters
			)
		).geom AS cell
	) AS q_grid;

ALTER TABLE cell ADD COLUMN pky serial NOT NULL PRIMARY KEY;
CREATE INDEX idx_cell_geom ON cell USING gist (geom);


-- Select grids with less than 15 distinct contributers
DROP TABLE IF EXISTS grid;
CREATE TABLE grid AS
SELECT 
	ST_Transform(geom, 900913) AS geom,
	cnt
FROM
	(SELECT 
		COUNT(DISTINCT a.user_name) AS cnt, 
		b.pky,
		b.geom
	FROM 
		-- hist_plp table is the reference for distinct names
		(SELECT 
			user_name,
			ST_Transform (geom, 4326) AS geom 
		FROM
			hist_plp
		) a, 
		cell b
	WHERE
		ST_Intersects (a.geom, b.geom) = 'true'
	GROUP BY 
		b.pky
	) AS foo
;

-- Add geom rows to geometry_columns to prevent the mapnik "srid = -1" error
DELETE FROM geometry_columns WHERE f_table_name = 'grid';
INSERT INTO geometry_columns (f_table_catalog, f_table_schema, f_table_name, f_geometry_column, coord_dimension, srid, type) 
VALUES ('', 'public', 'grid', 'geom', 2, 900913, 'POLYGON');

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
s2 = mapnik2.Style() 

# rule object to hold symbolizers
r = mapnik2.Rule() 
r2 = mapnik2.Rule() 

# Lines (outlines of polygons and/or simple lines. Line-Color (RGB) line-thickness
polygon_symbolizer = mapnik2.PolygonSymbolizer(mapnik2.Color('#ec0000'))
polygon_symbolizer.fill_opacity = 0.5

polygon_symbolizer2 = mapnik2.PolygonSymbolizer(mapnik2.Color('#00d200')) 
polygon_symbolizer2.fill_opacity = 0.5

# add the polygon_symbolizer to the rule object
r.symbols.append(polygon_symbolizer)
r2.symbols.append(polygon_symbolizer2) 

# now add the rule(s) to the style
s.rules.append(r)
s2.rules.append(r2) 

# Styles are added to the map
m.append_style('My Style',s) 
m.append_style('My Style2',s2) 

# Projection from PostGIS-Layer-Data
lyr = mapnik2.Layer('Geometry from PostGIS', '+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs +over')
lyr2 = mapnik2.Layer('Geometry from PostGIS', '+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs +over')


# PostGIS-Connection + DB-Query
lyr.datasource = mapnik2.PostGIS(host=hostname, user=db_user, password=db_pw, dbname=db_name,table=db_query) 
lyr2.datasource = mapnik2.PostGIS(host=hostname, user=db_user, password=db_pw, dbname=db_name,table=db_query2) 

# Append Style to layer
lyr.styles.append('My Style')
lyr2.styles.append('My Style2')

###
### END Layer 1
###

# Append overlay-layers to the map
m.layers.append(lyr)
m.layers.append(lyr2)


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
