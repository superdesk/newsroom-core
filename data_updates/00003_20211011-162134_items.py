# -*- coding: utf-8; -*-
# This file is part of Superdesk.
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
#
# Author  : MarkLark86
# Creation: 2021-10-11 16:21

from flask import current_app as app
from superdesk.commands.data_updates import DataUpdate as _DataUpdate


class DataUpdate(_DataUpdate):
    """Adds ``original_id`` mapping to the ``items`` resource

    This is done in a ``DataUpdate`` so a complete re-index is not required
    As this is a new field and not used in previous versions, we can safely add the mapping
    Otherwise a re-index will require a longer down-time when upgrading NewsHub

    We're also adding this mapping manually otherwise Elasticsearch will
    set it as text with keyword sub mapping.
    """

    resource = 'items'

    def forwards(self, _mongodb_collection, _mongodb_database):
        es = app.data.elastic.elastic('items')
        index = app.data.elastic._resource_index('items')
        es.indices.put_mapping(index=index, body={'properties': {'original_id': {'type': 'keyword'}}})

    def backwards(self, mongodb_collection, mongodb_database):
        pass
