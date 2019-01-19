# -*- coding: utf-8 -*-
# (c) 2019 Andreas Motl <andreas@hiveeyes.org>
# License: GNU Affero General Public License, Version 3
from jinja2 import Template
from pkg_resources import resource_string


def get_artefact(kind, name, variables=None):
    variables = variables or {}
    filename = '{}-{}.json'.format(kind, name)
    template = Template(load_file(filename))
    payload = template.render(variables)
    return payload


def load_file(filename):
    return resource_string('luftdatenpumpe.grafana', filename).decode('utf-8')
