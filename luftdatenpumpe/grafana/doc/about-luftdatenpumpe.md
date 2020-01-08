## About Luftdatenpumpe

#### Features
- **Data sources**: [luftdaten.info] (LDI), [IRCELINE], [OpenAQ]
- **Production**: [Luftdatenpumpe]
- **Development**: [Erneuerung der Luftdatenpumpe], [LDI data plane v2]. All contributions welcome. 
- **Composition**: [The Hiveeyes Project]. Developing a flexible beehive monitoring infrastructure.

#### Production process
1. [Luftdatenpumpe] acquires the current window of measurement readings from the upstream data source.
2. While iterating the readings, it collects information about all stations and sensors they are originating from.
3. Then, each stations location information gets enhanced by 
   - attaching its geospatial position as a [Geohash].
   - attaching a synthetic real-world address resolved using the reverse geocoding service [Nominatim] by [OpenStreetMap].
4. Finally, station information is stored into a PostGIS database using the fine  
   [dataset] package while observation/measurement data is stored into InfluxDB.
5. Luftdatenpumpe also includes templates for the Grafana panels you are seeing here.

Enjoy exploring and stay curious.

[luftdaten.info]: http://luftdaten.info/
[IRCELINE]: http://www.irceline.be/en/documentation/open-data
[OpenAQ]: https://openaq.org/

[Luftdatenpumpe]: https://github.com/hiveeyes/luftdatenpumpe
[Erneuerung der Luftdatenpumpe]: https://community.hiveeyes.org/t/erneuerung-der-luftdatenpumpe/1199
[LDI data plane v2]: https://community.hiveeyes.org/t/ldi-data-plane-v2/1412
[The Hiveeyes Project]: https://hiveeyes.org/

[OpenStreetMap]: https://en.wikipedia.org/wiki/OpenStreetMap
[Nominatim]: https://wiki.openstreetmap.org/wiki/Nominatim
[Geohash]: https://en.wikipedia.org/wiki/Geohash
[dataset]: https://dataset.readthedocs.io/
[SQLAlchemy]: https://www.sqlalchemy.org/
[RDBMS]: https://en.wikipedia.org/wiki/Relational_database_management_system
