#!/usr/bin/env python
# -*- coding: latin-1 -*-
#
#   Copyright 2016-2021 Blaise Frederick
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

import picachooser._version as pica_versioneer

# ------------------------------------------ Version function ----------------------------------
def version():
    """

    Returns
    -------

    """
    try:
        versioninfo = pica_versioneer.get_versions()

    except:
        return "UNKNOWN", "UNKNOWN", "UNKNOWN", "UNKNOWN"

    version = versioninfo["version"]
    if version is None:
        version = "UNKNOWN"
    longgittag = versioninfo["full-revisionid"]
    if longgittag is None:
        longgittag = "UNKNOWN"
    thedate = versioninfo["date"]
    if thedate is None:
        thedate = "UNKNOWN"
    isdirty = versioninfo["dirty"]
    if isdirty is None:
        isdirty = "UNKNOWN"
    return version, longgittag, thedate, isdirty


