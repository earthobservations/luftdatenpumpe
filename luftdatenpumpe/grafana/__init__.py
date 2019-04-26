# -*- coding: utf-8 -*-
# (c) 2019 Andreas Motl <andreas@hiveeyes.org>
# License: GNU Affero General Public License, Version 3
import json
import logging
from jinja2 import Template
from pkg_resources import resource_string


log = logging.getLogger(__name__)


def get_artefact(kind, name, variables=None, fields=None):
    log.info(f'Generating Grafana artefact '
             f'kind={kind}, name={name}, variables={json.dumps(variables)}, fields={json.dumps(fields)}')
    variables = variables or {}
    fields = fields or {}
    variables['fields'] = fields
    filename = '{}-{}.json'.format(kind, name)
    template = Template(load_file(filename))
    payload = template.render(variables)
    return payload


def load_file(filename):
    return resource_string('luftdatenpumpe.grafana', filename).decode('utf-8')
