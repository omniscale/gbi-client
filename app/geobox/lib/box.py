# This file is part of the GBI project.
# Copyright (C) 2013 Omniscale GmbH & Co. KG <http://omniscale.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Import features from GBI-Server coverage/area box into CouchDB layers.
"""

from collections import namedtuple
import json
import requests

from geobox.lib.couchdb import UnexpectedResponse, VectorCouchDB

feature = namedtuple('feature', ['id', 'rev', 'layer', 'properties', 'geometry'])

def feature_from_document(document):
    """
    Takes couchdb document and returns a feature if
    the document has a layer and geometry.
    """
    if 'geometry' not in document or 'layer' not in document:
        return None

    if document['_id'].startswith('schema_'):
        return None

    return feature(
        id=document['_id'],
        rev=document['_rev'],
        properties=document.get('properties', {}),
        geometry=document['geometry'],
        layer=document['layer'],
    )


class FeatureInserter(object):
    """
    Insert features into CouchDB at `url`. It inserts each feature
    into a database named after `feature.layer`. Existing features
    with the same `feature.id` are overwritten. Missing databases
    are created.
    """
    def __init__(self, url, auth=None):
        self.url = url
        self.session = requests.Session()
        self.inserted_layers = set()
        if auth:
            self.session.auth = auth

    def from_source(self, source):
        for doc in source.load_records():
            f = feature_from_document(doc)
            if f:
                self.insert(f)

        for layer in self.inserted_layers:
            self._check_metadata_doc(layer, source)

    def insert(self, feature):
        couch = VectorCouchDB(self.url, feature.layer )
        feature_dict = {
            'geometry': feature.geometry,
            'properties': feature.properties,
            'type': 'Feature',
        }
        existing_feature = couch.get(feature.id)
        if existing_feature:
            feature_dict['_rev'] = existing_feature['_rev']

        couch.put(feature.id, feature_dict)

        self.inserted_layers.add(feature.layer)

    def _check_metadata_doc(self, layer, source):
        metadata_url = self.url + '/' + layer + '/metadata'
        resp = self.session.get(metadata_url)
        if resp.status_code == 404:
            source_md = source.load_record('schema_' + layer)
            md_doc = {
                'title': source_md.get('title', layer) if source_md else layer,
                'type': 'GeoJSON',
            }
            resp = self.session.put(metadata_url,
                headers=[('Content-type', 'application/json')],
                data=json.dumps(md_doc),
            )
            if resp.status_code != 201:
                raise UnexpectedResponse('unable to insert metadata at %s: %s %s' % (
                    metadata_url, resp, resp.content))
