######################
Luftdatenpumpe backlog
######################


******
Prio 1
******
- [x] Download cache for data feed (5 minutes)
- [x] Write metadata directly to Postgres
- [o] Refactor for handling multiple data sources and targets
- [o] Redesign commandline interface
- [o] Write measurement data directly to InfluxDB
- [o] Create CHANGES.rst, update documentation and repository (tags)
- [o] Add tooling for packaging
- [o] Publish to PyPI


******
Prio 2
******
- [o] Run some metric about total count of measuremnts per feed action
- [o] Export to tabular format: http://docs.python-tablib.org/
- [o] Output data in tabular, markdown or rst formats
- [o] Publish to MQTT with separate topics
- [o] Store stations / data **while** processing


******
Prio 3
******
- [o] Write metadata directly to PostGIS
  https://dataset.readthedocs.io/en/latest/
- [o] Add support for JSON and GIS data to "dataset" module


****
Misc
****
::

    #result = self.db.query(self.stationtable.join(self.osmtable))

    #statement = table.select(table.c.name.like('%John%'))
    #result = self.db.query(statement)

    #q = session.query(User).join(User.addresses)


    # https://docs.sqlalchemy.org/en/latest/core/selectable.html#sqlalchemy.sql.expression.CompoundSelect.join
    from sqlalchemy import select, join
    from sqlalchemy.orm import aliased
    table_stations = self.stationtable.table
    table_osmdata = self.osmtable.table
    rel = table_stations.join(table_osmdata, table_stations.c.location_id == table_osmdata.c.location_id)
    stmt = select([table_stations]).select_from(rel)
    result = self.db.query(stmt)
    #result = self.db.query(select([rel]))
    #result = self.db.query(table_stations.select(), table_osmdata).filter(table_stations.c.location_id == table_osmdata.location_id).all()
    #result = self.db.query(self.stationtable, self.osmtable) #.filter(table_stations.c.location_id == table_osmdata.location_id).all()

    fa = aliased(table_osmdata)
    #j = join(table_stations, fa, table_stations.c.location_id == fa.c.location_id, isouter=True, full=True)
    j = join(table_stations, table_osmdata, table_stations.c.location_id == table_osmdata.c.location_id)
    stmt = select([table_stations, table_osmdata.c.display_name]).select_from(j)
    stmt = table_stations.join(fa, table_stations.c.location_id == fa.c.location_id)
    print(dir(stmt))
    #result = self.db.query(stmt.select())
    #result = self.db.query(table_stations).join(table_osmdata)
