#######
PostGIS
#######

Luftdatenpumpe uses a PostGIS ``POINT`` to store the geoposition of LDI stations.

In the query expression examples displayed below, we use the geocoordinates
``POINT(9.1800132 48.7784485)`` for Stuttgart, Germany.

This coordinate has been returned by asking Nominatim_ for
`querying Nominatim for city==stuttgart <https://nominatim.hiveeyes.org/search.php?format=jsonv2&addressdetails=1&polygon_text=1&city=stuttgart>`_.


************
Introduction
************
- http://postgis.net/workshops/postgis-intro/geography.html
- http://postgis.net/workshops/postgis-intro/knn.html

In order to enable GIS extensions on your PostgreSQL database, invoke::

    CREATE EXTENSION postgis;


Excerpts from the documentation
===============================
4.2.2. When to use Geography Data type over Geometry data type
If your data is global or covers a continental region, you may find that
GEOGRAPHY allows you to build a system without having to worry about
projection details. You store your data in longitude/latitude, and use
the functions that have been defined on GEOGRAPHY.
-- https://postgis.net/docs/using_postgis_dbmanagement.html#PostGIS_GeographyVSGeometry

4.2.3.1. Do you calculate on the sphere or the spheroid?
By default, all distance and area calculations are done on the spheroid.
-- https://postgis.net/docs/using_postgis_dbmanagement.html#idm1387


.. highlight:: sql

*************************
PostGIS query expressions
*************************

Sort by distance
================
::

    -- Find specified number of nearest stations through sorting by distance,
    -- display name and textual representation of coordinates.
    SELECT name, ST_AsText(geopoint) AS geopoint
    FROM ldi_stations
    ORDER BY geopoint <-> 'POINT(9.18001 48.77844)'
    LIMIT 5;

::

    -- Same as above, but display name and GeoJson representation of coordinates.
    SELECT name, ST_AsGeoJson(geopoint) AS geojson
    FROM ldi_stations
    ORDER BY geopoint <-> 'POINT(9.18001 48.77844)'
    LIMIT 5;


Match within range
==================
::

    -- Find all stations within specified range in meters while sorting by distance.
    -- The computation uses a bounding box expanded from the specified geographic point,
    -- by specifying a single distance with which the box will be expanded in all directions.
    -- https://postgis.net/docs/ST_DWithin.html
    -- https://postgis.net/docs/ST_Expand.html
    SELECT name, ST_AsText(geopoint) AS geopoint
    FROM ldi_stations
    WHERE ST_DWithin(geopoint, 'POINT(9.18001 48.77844)', 3000)
    ORDER BY geopoint <-> 'POINT(9.18001 48.77844)';

In order to save on repeating this ``POINT`` coordinates here, we can alias it into a virtual ``position`` field::

    -- List all stations within 3000 meters around specified coordinates.
    -- This is what OpenStreetMap/Nominatim thinks the center of Stuttgart is.
    WITH stuttgart AS (
        SELECT ST_GeographyFromText('POINT(9.18001 48.77844)') AS position
    )
    SELECT name, ST_AsText(geopoint) AS geopoint
    FROM ldi_stations, stuttgart
    WHERE ST_DWithin(geopoint, stuttgart.position, 3000)
    ORDER BY geopoint <-> stuttgart.position;


Mixing in OSM/Nominatim
=======================
As these expressions use the constraint ``osm_city = 'Stuttgart'``, OSM data is involved.
Centroid of OSM input coordinates

::

    -- Compute center of city as the arithmetic mean of the input coordinates.
    -- http://postgis.net/workshops/postgis-intro/geometry_returning.html
    -- http://postgis.net/workshops/postgis-intro/advanced_geometry_construction.html
    -- https://postgis.net/docs/ST_Collect.html
    -- https://postgis.net/docs/ST_Centroid.html
    SELECT ST_AsText(ST_Centroid(ST_Collect(geopoint::geometry))::geography) AS geopoint
    FROM ldi_network
    WHERE osm_city = 'Stuttgart';

::

    -- Using the formula above, find specified number of nearest stations by city name.
    -- https://stackoverflow.com/a/19859047
    -- https://postgis.net/docs/ST_X.html
    -- https://postgis.net/docs/ST_Y.html
    WITH center_of AS (
        SELECT ST_Centroid(ST_Collect(geopoint::geometry))::geography AS position FROM ldi_network WHERE osm_city = 'Stuttgart'
    )
    SELECT name, ST_AsText(geopoint) AS geopoint
    FROM ldi_stations, center_of
    ORDER BY geopoint <-> center_of.position
    LIMIT 5;

::

    -- List all stations within 3000 meters around what LDI thinks the center of Stuttgart is.
    WITH stuttgart AS (
        SELECT ST_Centroid(ST_Collect(geopoint::geometry))::geography AS position FROM ldi_network WHERE osm_city = 'Stuttgart'
    )
    SELECT name, ST_AsText(geopoint) AS geopoint
    FROM ldi_stations, stuttgart
    WHERE ST_DWithin(geopoint, stuttgart.position, 3000)
    ORDER BY geopoint <-> stuttgart.position;



*******************************
Accessing the OSM/Nominatim API
*******************************
By using the PostgreSQL extension `pgsql-http`_, which is effectively a
»HTTP client for PostgreSQL«, you can directly access the Nominatim HTTP API
for asking for a ``geotext`` field from a specified city or other location
by using the ``polygon_text=1`` query parameter.

The ``geotext`` field yielded by the response of the API is in
PostGIS-compatible ``POINT(lon lat)`` format already.

.. _pgsql-http: https://github.com/pramsey/pgsql-http

Print coordinate by asking for ``city=stuttgart``, effectively roundtripping through HTTP and PostGIS::

    -- https://github.com/pramsey/pgsql-http
    -- https://wiki.openstreetmap.org/wiki/Nominatim
    -- https://www.postgresql.org/docs/9.3/functions-json.html
    -- TODO: Provide this as a native Grafana datasource and/or variable somehow?
    CREATE EXTENSION http;

    -- Nominatim request subselect.
    WITH stuttgart AS (
        SELECT
            ST_GeographyFromText(content::json->0->>'geotext') AS position
        FROM
            http_get('https://nominatim.hiveeyes.org/search.php?format=jsonv2&addressdetails=1&polygon_text=1&city=stuttgart')
    )

    -- Print position as text.
    -- You should do more sophisticated things here, see below.
    SELECT ST_AsText(position) FROM stuttgart;


Match within range
==================
::

    -- List all stations within 3000 meters around specified city.
    -- The coordinates of the city is coming from OpenStreetMap/Nominatim.
    WITH stuttgart AS (
        SELECT ST_GeographyFromText(content::json->0->>'geotext') AS position
        FROM http_get('https://nominatim.hiveeyes.org/search.php?format=jsonv2&addressdetails=1&polygon_text=1&city=stuttgart')
    )
    SELECT name, ST_AsText(geopoint) AS geopoint
    FROM ldi_stations, stuttgart
    WHERE ST_DWithin(geopoint, stuttgart.position, 3000)
    ORDER BY geopoint <-> stuttgart.position;
