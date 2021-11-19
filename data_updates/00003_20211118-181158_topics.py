# -*- coding: utf-8; -*-
# This file is part of Superdesk.
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
#
# Author  : marklark
# Creation: 2021-11-18 18:11

from superdesk.commands.data_updates import DataUpdate as _DataUpdate


class DataUpdate(_DataUpdate):

    resource = 'topics'

    def forwards(self, mongodb_collection, mongodb_database):
        raise NotImplementedError()

    def backwards(self, mongodb_collection, mongodb_database):
        raise NotImplementedError()
