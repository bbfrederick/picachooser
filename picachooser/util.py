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

import os

import numpy as np
from scipy.stats import pearsonr

import picachooser._version as pica_versioneer
import picachooser.io as io


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


def is_valid_dir(parser, arg):
    """
    Check if argument is existing file.
    """
    if not os.path.isdir(arg) and arg is not None:
        parser.error("The directory {0} does not exist!".format(arg))

    return arg


def is_valid_file(parser, arg):
    """
    Check if argument is existing file.
    """
    if not os.path.isfile(arg) and arg is not None:
        parser.error("The file {0} does not exist!".format(arg))

    return arg


def invert_float(parser, arg):
    """
    Check if argument is float or auto.
    """
    if arg != "auto":
        try:
            arg = float(arg)
        except parser.error:
            parser.error('Value {0} is not a float or "auto"'.format(arg))

    if arg != "auto":
        arg = 1.0 / arg
    return arg


def is_float(parser, arg):
    """
    Check if argument is float or auto.
    """
    if arg != "auto":
        try:
            arg = float(arg)
        except parser.error:
            parser.error('Value {0} is not a float or "auto"'.format(arg))

    return arg


def getrefdir():
    return os.path.join(
        os.path.split(os.path.split(__file__)[0])[0],
        "picachooser",
        "data",
        "reference",
    )


def calccorrs(file1, file2, mask, debug=False):
    dummy, indata1, header1, dims1, dummy = io.readfromnifti(file1)
    dummy, indata2, header2, dims2, dummy = io.readfromnifti(file2)
    dummy, maskdata, maskheader, maskdims, dummy = io.readfromnifti(mask)
    if io.checkspacematch(header1, header2) and io.checkspacematch(header1, maskheader):
        numelements1 = dims1[4]
        numelements2 = dims2[4]
        # first calculate all correlations
        thecorrmat = np.zeros((numelements1, numelements2), dtype=np.float64)
        print("matching components")
        for i in range(numelements1):
            if debug:
                print(f"index {i}")
            maskedcomponent1 = (indata1[:, :, :, i][np.where(maskdata > 0)]).flatten()
            for j in range(numelements2):
                maskedcomponent2 = (indata2[:, :, :, j][np.where(maskdata > 0)]).flatten()
                thecorrmat[i, j], dummy = pearsonr(maskedcomponent1, maskedcomponent2)

        # now find the best match for each element of the first data array
        thebestmatches = np.argmax(thecorrmat, axis=1)
        if debug:
            for i in range(numelements1):
                print(
                    f"component {i}: best match of {thecorrmat[i, thebestmatches[i]]} at component {thebestmatches[i]}"
                )
        return thecorrmat, thebestmatches
    else:
        print("data or mask dimensions do not match")
        return None, None
