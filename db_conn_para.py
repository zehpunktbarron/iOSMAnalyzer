# -*- coding: utf-8 -*-
import argparse


# Set flags for DB-connection
parser = argparse.ArgumentParser()

parser.add_argument('-D', '--database', action="store", type=str, dest="my_dbname", required=True, help="DB name")

parser.add_argument('-U', '--username', action="store", type=str, dest="my_username", required=True, help="DB username")

parser.add_argument('-P', '--password', action="store", type=str, dest="my_dbpassword", required=True, help="Password for DB connection")

parser.add_argument('-H', '--hostname', action="store", type=str, dest="my_hostname",  required=True, help="Hostname of the DB")

args = parser.parse_args()

# Set variables global for usage in other scripts
global g_my_dbname
g_my_dbname = args.my_dbname

global g_my_username
g_my_username = args.my_username

global g_my_dbpassword
g_my_dbpassword = args.my_dbpassword

global g_my_hostname
g_my_hostname = args.my_hostname
  


