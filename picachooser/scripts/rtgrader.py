#!/usr/bin/env python
# -*- coding: latin-1 -*-
#
#   Copyright 2020 Blaise Frederick
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
#
# $Author: frederic $
# $Date: 2016/07/11 14:50:43 $
# $Id: tidepool,v 1.28 2016/07/11 14:50:43 frederic Exp $
#
# -*- coding: utf-8 -*-

"""
A simple GUI for rating timecoursese by whatever metric you want
"""

import argparse
import os
import sys

import numpy as np
from pyqtgraph.Qt import QtCore, QtWidgets
from scipy.stats import pearsonr

import picachooser.colormaps as cm
import picachooser.io as io
import picachooser.LightboxItem as lb
import picachooser.util as pica_util

try:
    from PyQt6.QtCore import QT_VERSION_STR
except ImportError:
    pyqtversion = 5
else:
    pyqtversion = 6

# fix for Big Sur on macOS
os.environ["QT_MAC_WANTS_LAYER"] = "1"

# global defaults
DEFAULT_LAG_MIN = -5.0
DEFAULT_LAG_MAX = 10.0
DEFAULT_STRENGTH_MIN = 0.0
DEFAULT_STRENGTH_MAX = 0.75


class KeyPressWindow(QtWidgets.QMainWindow):
    sigKeyPress = QtCore.pyqtSignal(object)
    sigResize = QtCore.pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def closeEvent(self, event):
        pass

    def keyPressEvent(self, ev):
        self.sigKeyPress.emit(ev)

    def resizeEvent(self, ev):
        self.sigResize.emit(ev)


def selectsort():
    global sorttype, sortnames, indexmap, thecorrcoeffs

    print("setting sort type to", sortnames[sorttype])

    if sortnames[sorttype] == "file 1 order":
        indexmap = sorted(indexmap)
    elif sortnames[sorttype] == "correlation coefficient":
        # print(thecorrcoeffs)
        indexmap = [x for _, x in sorted(zip(thecorrcoeffs, indexmap), reverse=True)]
    else:
        print("illegal sort type")

    print(indexmap)

    updateTCinfo()
    updateLightboxes()


def incrementgrade():
    global grades, whichcomponent

    grades[whichcomponent] = not grades[whichcomponent]


def decrementgrade():
    global grades, whichcomponent

    grades[whichcomponent] = not grades[whichcomponent]


def windowResized(evt):
    global lbwin1, lbwin2, verbose

    if verbose:
        print("handling window resize")

    if lbwin1 is not None and lbwin2 is not None:
        updateLightboxes()


def keyPressed(evt):
    global whichcomponent, numelements, lbwin1, lbwin2, verbose, domotion, dotimecourse
    global leftinfo, rightinfo, blinkstatus
    global datasetlabels, grades, gradefile

    if verbose:
        print("processing keypress event")

    keymods = None
    if evt.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier:
        keymods = "shift"
    elif evt.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier:
        keymods = "ctrl"

    badindices = np.where(grades == False)[0]
    goodindices = np.where(grades == True)[0]

    if evt.key() == QtCore.Qt.Key.Key_Up:
        incrementgrade()
    elif evt.key() == QtCore.Qt.Key.Key_Down:
        decrementgrade()
    elif evt.key() == QtCore.Qt.Key.Key_Left:
        if keymods == "shift":
            whichcomponent = pica_util.nextmatch(whichcomponent, badindices, backwards=True)
        elif keymods == "ctrl":
            whichcomponent = pica_util.nextmatch(whichcomponent, goodindices, backwards=True)
        else:
            whichcomponent = (whichcomponent - 1) % numelements
        print(f"Index is {whichcomponent}, label is {datasetlabels[whichcomponent]}")
    elif evt.key() == QtCore.Qt.Key.Key_Right:
        if keymods == "shift":
            whichcomponent = pica_util.nextmatch(whichcomponent, badindices, backwards=False)
        elif keymods == "ctrl":
            whichcomponent = pica_util.nextmatch(whichcomponent, goodindices, backwards=False)
        else:
            whichcomponent = (whichcomponent + 1) % numelements
        print(f"Index is {whichcomponent}, label is {datasetlabels[whichcomponent]}")
    elif evt.key() == QtCore.Qt.Key.Key_A:
        for thewin in [lbwin1, lbwin2]:
            thewin.setorient("ax")
            thewin.resetWinProps()
        print("Setting orientation to axial")
    elif evt.key() == QtCore.Qt.Key.Key_C:
        for thewin in [lbwin1, lbwin2]:
            thewin.setorient("cor")
            thewin.resetWinProps()
        print("Setting orientation to coronal")
    elif evt.key() == QtCore.Qt.Key.Key_S:
        for thewin in [lbwin1, lbwin2]:
            thewin.setorient("sag")
            thewin.resetWinProps()
        print("Setting orientation to sagittal")
    elif evt.key() == QtCore.Qt.Key.Key_D:
        print("Dumping main window information")
        for thewin in [lbwin1, lbwin2]:
            thewin.printWinProps()
    elif evt.key() == QtCore.Qt.Key.Key_B:
        print("Blinking")
        blinkstatus = not blinkstatus
        if blinkstatus:
            lbwin1.setviewinfo(rightinfo)
            lbwin2.setviewinfo(leftinfo)
        else:
            lbwin1.setviewinfo(leftinfo)
            lbwin2.setviewinfo(rightinfo)
    elif evt.key() == QtCore.Qt.Key.Key_R:
        whichcomponent = 0
        print(f"Index is {whichcomponent}, label is {datasetlabels[whichcomponent]}")
    elif evt.key() == QtCore.Qt.Key.Key_Escape:
        goodindices = []
        goodlabels = []
        badindices = []
        badlabels = []
        for idx in range(numelements):
            if grades[idx]:
                goodindices.append(idx)
                goodlabels.append(datasetlabels[idx])
            else:
                badindices.append(idx)
                badlabels.append(datasetlabels[idx])
        badindexfilename = gradefile
        goodindexfilename = gradefile.replace("badindices", "goodindices")
        badlabelfile = badindexfilename.replace("badindices", "badlabels")
        goodlabelfile = goodindexfilename.replace("goodindices", "goodlabels")
        io.writevec(goodindices, goodindexfilename)
        io.writevec(badindices, badindexfilename)
        io.writevec(goodlabels, goodlabelfile)
        io.writevec(badlabels, badlabelfile)
        print("grade files written")
    else:
        pass

    updateTCinfo()
    updateLightboxes()


def updateTCinfo():
    global whichcomponent, indexmap, sorttype, sortnames, blinkstatus
    global alldata1, alldata2, namelist, datasetlabels, win, numelements, verbose

    if verbose:
        print("entering updateTCinfo")
    pane1title = alldata1["filelabel"] + ": " + datasetlabels[whichcomponent]
    pane2title = alldata2["filelabel"] + ": " + datasetlabels[whichcomponent]

    if blinkstatus:
        ui.pane1_label.setText(pane2title)
        ui.pane2_label.setText(pane1title)
    else:
        ui.pane1_label.setText(pane1title)
        ui.pane2_label.setText(pane2title)

    win.setWindowTitle(f"rtgrader: sorting by {sortnames[sorttype]}")


def updateLightboxes():
    global lbwin1, lbwin2, whichcomponent, indexmap, verbose, alldata1, alldata2, namelist, grades, datasetlabels
    global keepcolor, discardcolor

    if verbose:
        print("entering updateLightboxes")

    thelabel1 = f"{alldata1['filelabel']} {datasetlabels[whichcomponent]}"
    thelabel2 = f"{alldata2['filelabel']} {datasetlabels[whichcomponent]}"
    if grades[whichcomponent]:
        thecolor = config["keepcolor"]
    else:
        thecolor = config["discardcolor"]
    lbwin1.setTpos(whichcomponent)
    lbwin2.setTpos(whichcomponent)
    for thewin in [lbwin1, lbwin2]:
        thewin.getWinProps()
        thewin.resetWinProps()
    lbwin1.setLabel(thelabel1, thecolor)
    lbwin2.setLabel(thelabel2, thecolor)

    # ui.correlation_label.setText("thecorrcoeff")


def main():
    global ui, win, lbwin1, lbwin2
    global namelist, grades, datasetlabels, gradefile, alldata1, alldata2, motion, whichcomponent
    global indexmap, sorttype, sortnames, thecorrcoeffs, numelements
    global verbose
    global config
    global leftinfo, rightinfo, blinkstatus
    global Funcfile, Mixfile, filteredfile
    global domotion, dotimecourse

    lbwin1 = None
    lbwin2 = None
    verbose = False
    domotion = True
    dotimecourse = True

    parser = argparse.ArgumentParser(
        prog="rtgrader",
        description="A program to rate sets of rapidtide runs.",
        usage="%(prog)s lagtimes strengths regressors labels",
    )

    # Required arguments
    parser.add_argument(
        "lagtimes",
        action="store",
        type=lambda x: pica_util.is_valid_file(parser, x),
        help=(
            "The 4D NIFTI of the concatenated lag time or timepercentile maps for all subjects.  Maps need to be in the same order as the label file."
        ),
        default=None,
    )
    parser.add_argument(
        "strengths",
        action="store",
        type=lambda x: pica_util.is_valid_file(parser, x),
        help=(
            "The 4D NIFTI of the concatenated correlation strength maps for all subjects.  Maps need to be in the same order as the label file."
        ),
        default=None,
    )
    """parser.add_argument(
        "regressors",
        action="store",
        type=lambda x: pica_util.is_valid_file(parser, x),
        help=(
            "The json/tsv.gz file containing the concatenated sLFO regressors for all subjects.  Columns to be in the same order as the label file."
        ),
        default=None,
    )"""
    parser.add_argument(
        "labels",
        action="store",
        type=lambda x: pica_util.is_valid_file(parser, x),
        help=("The text file containing the labels for all scans, one per line."),
        default=None,
    )
    # optional arguments
    other = parser.add_argument_group("Other arguments")
    other.add_argument(
        "--startindex",
        dest="startindex",
        action="store",
        metavar="INDEX",
        type=lambda x: pica_util.is_int(parser, x),
        help=("The index to start at (0-based)."),
        default=0,
    )
    other.add_argument(
        "--mapmask",
        dest="mapmask",
        action="store",
        metavar="MASKFILE",
        type=lambda x: pica_util.is_valid_file(parser, x),
        help=("The 3D or 4D NIFTI to mask all maps."),
        default=None,
    )
    other.add_argument(
        "--spatialroi",
        dest="spatialroi",
        type=int,
        nargs=6,
        metavar=("XMIN", "XMAX", "YMIN", "YMAX", "ZMIN", "ZMAX"),
        help=(
            "Only read in image data within the specified ROI.  Set MAX to -1 to go to the end of that dimension."
        ),
        default=(0, -1, 0, -1, 0, -1),
    )

    other.add_argument(
        "--outputroot",
        type=str,
        help=(
            "Root name for reading and writing the lists of good and bad component indices "
            "(default is 'rtgrader', resulting in 'rtgrader_goodindices.txt' and 'rtgrader_badindices.txt')"
            "in the current working directory."
        ),
        default="rtgrader",
    )
    other.add_argument(
        "--lagrange",
        dest="lagrange",
        action="store",
        nargs=2,
        type=float,
        metavar=("MINLAG", "MAXLAG"),
        help=f"Lag time range to display.  Default is {DEFAULT_LAG_MIN} to {DEFAULT_LAG_MAX}.",
        default=(DEFAULT_LAG_MIN, DEFAULT_LAG_MAX),
    )
    other.add_argument(
        "--strengthrange",
        dest="strengthrange",
        action="store",
        nargs=2,
        type=float,
        metavar=("MINSTRENGTH", "MAXSTRENGTH"),
        help=f"Strength range to display.  Default is {DEFAULT_STRENGTH_MIN} to {DEFAULT_STRENGTH_MAX}.",
        default=(DEFAULT_STRENGTH_MIN, DEFAULT_STRENGTH_MAX),
    )

    misc = parser.add_argument_group("Miscellaneous arguments")
    misc.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {pica_util.version()[0]}",
    )
    misc.add_argument(
        "--detailedversion",
        action="version",
        version=f"%(prog)s {pica_util.version()}",
    )

    debugging = parser.add_argument_group("Debugging arguments")
    debugging.add_argument(
        "--verbose",
        action="store_true",
        help=(
            "Output exhaustive amounts of information about the internal workings of rtgrader. "
            "You almost certainly don't want this."
        ),
        default=False,
    )

    try:
        args = parser.parse_args()
    except SystemExit:
        print("Use --help option for detailed information on options.")
        raise

    # make sure we can find the required input files
    # first see if there are specific overrides
    lagtimefile = args.lagtimes
    strengthsfile = args.strengths
    #regressorsfile = args.regressors
    labelfile = args.labels
    mapmask = args.mapmask

    if mapmask is None:
        print("No mask provided. ")

    if args.outputroot is not None:
        gradefile = f"{args.outputroot}_badindices.txt"
    else:
        gradefile = "rtgrader_badindices.txt"
    if os.path.isfile(gradefile):
        initfileexists = True
        print(f"gradfile {gradefile} exists - reading initial grade file")
        badindices = io.readvec(gradefile, isint=True)
        if args.verbose:
            print(badindices)
    else:
        initfileexists = False
        print(f"gradfile {gradefile} does not exist - will initialize.")

    if verbose:
        print(f"lagtimes: {lagtimefile}")
        print(f"strengths: {strengthsfile}")
        #print(f"regressors: {regressorsfile}")
        print(f"labels: {labelfile}")
        print(f"gradefile: {gradefile}")

    # set the configurable options
    def initconfig():
        print("initializing preferences")
        config = {
            "prefsversion": 1,
            "keepcolor": "g",
            "discardcolor": "r",
        }
        return config

    configfile = os.path.join(os.environ["HOME"], ".rtgrader.json")
    if not os.path.isfile(configfile):
        config = initconfig()
        io.writedicttojson(config, configfile, sort_keys=False)
    else:
        config = io.readdictfromjson(configfile)
        try:
            prefsversion = config["prefsversion"]
        except KeyError:
            prefsversion = 0
        if prefsversion < 1:
            config = initconfig()
            io.writedicttojson(config, configfile)

    # read in the information for both datasets
    alldata1 = {}
    alldata2 = {}
    alldata1["filelabel"] = "Lag times"
    alldata2["filelabel"] = "Correlation coefficients"

    dummy, numelements = io.fmritimeinfo(args.lagtimes)
    dummy, numelements2 = io.fmritimeinfo(args.strengths)
    if numelements2 != numelements:
        print("lagtimes and strengths files do not have the same number of elements - exiting")
        sys.exit()

    thecorrcoeffs = np.ones((numelements), dtype=np.float64)

    datasetlabels = io.readlabels(args.labels)
    namelist = []
    print("reading info on lag time file...")
    for idx in range(numelements):
        theIC = str(idx + 1)
        namelist.append(theIC)
        alldata1[theIC] = {}
        thecorrcoeffs[idx] = 1.0
    grades = np.ones((numelements), dtype=bool)
    print("Read in", numelements, "lag time maps")
    print("reading info on strengths file...")
    for idx in range(numelements):
        theIC = str(idx + 1)
        alldata2[theIC] = {}
    print("Read in", numelements, "strength maps")
    whichcomponent = args.startindex
    print(f"starting with index set to {whichcomponent}")
    indexmap = np.arange(0, numelements, dtype=int)
    sorttype = 0
    sortnames = ["file 1 order", "correlation coefficient"]

    if initfileexists:
        for idx in badindices:
            grades[idx] = False

    # make the main window
    if pyqtversion == 5:
        import picachooser.rtgraderTemplate as uiTemplate
    else:
        import picachooser.rtgraderTemplate_qt6 as uiTemplate

    app = QtWidgets.QApplication([])
    print("setting up output window")
    win = KeyPressWindow()
    win.sigKeyPress.connect(keyPressed)
    win.sigResize.connect(windowResized)

    ui = uiTemplate.Ui_MainWindow()
    ui.setupUi(win)
    win.show()
    win.setWindowTitle("rtgrader")

    print("setting up image windows")
    if mapmask is not None:
        print("reading in masks")
        geommaskimage = lb.imagedataset(
            "mapmask",
            mapmask,
            "mapmask",
            xlims=args.spatialroi[0:2],
            ylims=args.spatialroi[2:4],
            zlims=args.spatialroi[4:6],
            lut_state=cm.mask_state,
        )
        thegeommask = geommaskimage.data

    print("reading in lags")
    fgimage1 = lb.imagedataset(
        "Lagtimes",
        args.lagtimes,
        "Lagtimes",
        xlims=args.spatialroi[0:2],
        ylims=args.spatialroi[2:4],
        zlims=args.spatialroi[4:6],
        lut_state=cm.viridis_state,
        geommask=thegeommask,
    )
    fgimage1.setFuncMaskByThresh(threshval=-100.0, maskdata=False)
    # fgimage1.setFuncMask(geommaskimage.data)

    print("reading in strengths")
    fgimage2 = lb.imagedataset(
        "CorrelationStrengths",
        args.strengths,
        "CorrelationStrengths",
        xlims=args.spatialroi[0:2],
        ylims=args.spatialroi[2:4],
        zlims=args.spatialroi[4:6],
        lut_state=cm.thermal_state,
        geommask=thegeommask,
    )
    fgimage2.setFuncMaskByThresh(threshval=-100.0, maskdata=False)
    # fgimage2.setFuncMask(geommaskimage.data)

    lbwin1 = lb.LightboxItem(
        fgimage1,
        ui.image_graphicsView_1,
        bidirectional=False,
        lowerthresh=args.lagrange[0],
        upperthresh=args.lagrange[1],
        verbose=verbose,
    )
    leftinfo = lbwin1.getviewinfo()
    lbwin2 = lb.LightboxItem(
        fgimage2,
        ui.image_graphicsView_2,
        bidirectional=False,
        lowerthresh=args.strengthrange[0],
        upperthresh=args.strengthrange[1],
        verbose=verbose,
    )
    rightinfo = lbwin2.getviewinfo()
    blinkstatus = False

    # initialize everything
    updateTCinfo()
    updateLightboxes()

    QtWidgets.QApplication.instance().exec()


def entrypoint():
    main()


if __name__ == "__main__":
    entrypoint()
