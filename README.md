iOSMAnalyzer
============

A tool for intrinsic OpenStreetMap data quality analyses.
Developed by Christopher Barron & Pascal Neis @ http://giscience.uni-hd.de/

This command line tool generates a PDF document containing statistics, maps and diagrams which can be used for assessing the quality of a selected OSM area. As an input only an OSM-Full-History-Dump is needed. It is written in python mainly performing SQL queries on a local database on Linux (Ubuntu) operating system. The tool is published under GNU GENERAL PUBLIC LICENSE V3. Feel free to use and contribute to the tool on GitHub.

To run the tool the following prerequisites are necessary:

- Osmium: http://wiki.openstreetmap.org/wiki/Osmium/Quick_Start
- OSM-History-Splitter (Splits *.osh files into smaller extracts): https://github.com/MaZderMind/osm-history-splitter
- OSM-History-Renderer/Importer (Imports an *.osh file to a PostGIS database): https://github.com/MaZderMind/osm-history-renderer. The importer has some bugs which have to be considered. Deleted ways and polygons are imported as if they have not been deleted! Furthermore I extended the importer to also consider user names and user ids. Add the lines added in the attached files "handler.hpp" and "00-before.sql" to your version. When using the OSM-History-Importer I figured out some problems if the user name of the database and the linux user differed. To avoid any problems use the same name.
- PostgreSQL/PostGIS database. The tool was developed under PostgreSQL 9.1.9 and PostGIS 1.5.3. I did not test it on PostGIS 2.x
- You need “psycopg2” (http://www.initd.org/psycopg/) to connect the database with the python tool: 

<pre><code>sudo apt-get build-dep python-psycopg2 python-pip
sudo apt-get install python-pip
sudo pip install psycopg2</code></pre>

The “ReportLab-Toolkit” (http://www.reportlab.com/software/opensource/rl-toolkit/) is needed to generate and style the pdf-document:

<pre><code>sudo python setup.py install 
sudo apt-get install libfreetype6-dev
sudo apt-get install python-dev 
sudo apt-get install python-imaging 
sudo apt-get install python-reportlab python-reportlab-accel python-renderpm</code></pre>

MatplotLib (http://matplotlib.org/) is used for generating the diagrams: 
    
<pre><code>sudo apt-get install python-matplotlib</code></pre>

If all these prerequisites are installed you can clone the iOSMAnalyzer (https://github.com/zehpunktbarron/iOSMAnalyzer) to a directory of your choice:

<pre><code>git clone https://github.com/zehpunktbarron/iOSMAnalyzer</code></pre>

Some general hints for installation and usage:

- During the installation process some dependencies had to be installed manually. Carefully read the command line output after each and every installation as some of them have been developed further.
- Database tuning for a better performance: A good reference is this guide provided by OpenGeo (http://workshops.opengeo.org/postgis-intro/tuning.html).
- Some queries of the iOSMAnalyzer also write new (temporary) tables or views to the database. Therefore problems can occur if not all tables or views are assigned to the correct user/owner.
- Get the data: You can download the latest worldwide OSM-Full-History-Dump (http://planet.openstreetmap.org/planet/full-history/) or use previously created extracts (http://osm.personalwerk.de/full-history-extracts/).
- I created a simple tool that works. Focus was not on a high performance piece of software. On my machine the entire tool took around 10-15 minutes to run on an area with around 2.000.000 nodes in the hist_point table.
- You can also create single diagrams by calling the appropriate script instead of “main.py”. 

Run the tool using the terminal (command line) after navigating to the directory:

<pre><code>python main.py -D yourDatabaseName -U yourDatabaseUsername -P yourDatabasePassword -h localhost</code></pre>

If you have any questions feel free to drop me a line on GitHub or write me an email (first name dot last name at gmx dot de). 
