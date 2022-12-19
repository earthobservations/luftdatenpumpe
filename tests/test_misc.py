def test_import_all():
    """
    Only here to have correct coverage reporting until the test suite will be extended.
    """
    from luftdatenpumpe import commands, engine, geo, util  # noqa:F401
    from luftdatenpumpe.source import common, eea, irceline, luftdaten_info, openaq  # noqa:F401
    from luftdatenpumpe.source import rdbms as source_rdbms  # noqa:F401
    from luftdatenpumpe.target import stream  # noqa:F401
    from luftdatenpumpe.target import influxdb, json, mqtt  # noqa:F401
    from luftdatenpumpe.target import rdbms as target_rdbms  # noqa:F401
