#!/usr/bin/env python
# -*- coding: utf-8; -*-
#
# This file is part of Newsroom.
#
# Copyright 2021 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import os

from .factory import get_app


app = get_app()

if __name__ == "__main__":
    host = "0.0.0.0"
    port = int(os.environ.get("MGMTAPI_PORT", "5500"))
    app.run(host=host, port=port, debug=True, use_reloader=True)
