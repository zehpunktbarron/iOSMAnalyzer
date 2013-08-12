# -*- coding: utf-8 -*-
#!/usr/bin/python2.7

#description     :This file creates a database view containing all points, lines and polygons
#		  This is necessary for querying the whole database
#author          :Christopher Barron
#date            :18.04.2013
#version         :0.1
#usage           :python pyscript.py
#==============================================================================

# import psycopg2 module
import psycopg2

# import db connection parameters from the commande line
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

statement = """ 

  -- Remove columns incase they already exist
  ALTER TABLE hist_point DROP COLUMN IF EXISTS typ CASCADE;
  ALTER TABLE hist_point DROP COLUMN IF EXISTS minor CASCADE;
  ALTER TABLE hist_line DROP COLUMN IF EXISTS typ CASCADE;
  ALTER TABLE hist_polygon DROP COLUMN IF EXISTS typ CASCADE;
  
  -- Add the columns for their feature type (point, line, polygon)
  ALTER TABLE hist_point ADD COLUMN typ text;
  ALTER TABLE hist_point ADD COLUMN minor int;
  ALTER TABLE hist_line ADD COLUMN typ text;
  ALTER TABLE hist_polygon ADD COLUMN typ text;

  -- Insert feature type into the columns so the UNION in the next step will work
  UPDATE hist_point SET typ = 'point' WHERE typ isnull;
  UPDATE hist_point SET minor = 0 WHERE minor isnull;
  UPDATE hist_line SET typ = 'line' WHERE typ isnull;
  UPDATE hist_polygon SET typ = 'polygon' WHERE typ isnull;

  -- Create a view out of all three tables (points, lines, polygons)
  CREATE VIEW hist_plp AS SELECT * FROM
	  (
	  SELECT id, version, minor, visible, valid_from, valid_to, user_id, user_name, tags, geom, typ FROM hist_point
	  UNION ALL
	  SELECT id, version, minor, visible, valid_from, valid_to, user_id, user_name, tags, geom, typ FROM hist_line
	  UNION ALL
	  SELECT id, version, minor, visible, valid_from, valid_to, user_id, user_name, tags, geom, typ FROM hist_polygon
	  ) AS foo;

    --
    -- Create or replace function for altering all tables to the same user defined in the input
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
      
  """
  
cur.execute(statement)

cur.close()
conn.commit()
conn.close()