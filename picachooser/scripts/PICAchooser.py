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
import subprocess
import sys

import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
from scipy import fftpack
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

hammingwindows = {}
DEFAULT_RETAINTHRESH = 0.5

# fix for Big Sur on macOS
os.environ["QT_MAC_WANTS_LAYER"] = "1"


def findfromfeatdir(featdir, initBGfile, initFuncfile, initMotionfile):
    if initBGfile is None:
        bgfile = os.path.join(featdir, "reg", "example_func.nii.gz")
    else:
        bgfile = initBGfile
    if not os.path.isfile(bgfile):
        print("cannot find background image file at", bgfile)
        sys.exit()

    if initFuncfile is None:
        Funcfile = os.path.join(featdir, "filtered_func_data.nii.gz")
    else:
        Funcfile = initFuncfile
    if not os.path.isfile(Funcfile):
        print("cannot find functional data file at", Funcfile)
        sys.exit()

    if initMotionfile is None:
        motionfile = os.path.join(featdir, "mc", "prefiltered_func_data_mcf.par")
    else:
        motionfile = initMotionfile
    if not os.path.isfile(motionfile):
        print("cannot find motion parameter file at", motionfile)
        # sys.exit()

    return bgfile, Funcfile, motionfile


def findfrommelodicdir(
    melodicdir, initBGfile, initICfile, initICmask, initTCfile, initmelodicICstatsfile
):
    if initBGfile is None:
        bgfile = os.path.join(melodicdir, "mean.nii.gz")
    else:
        bgfile = initBGfile
    if not os.path.isfile(bgfile):
        print("cannot find background file at", bgfile)
        sys.exit()

    if initICfile is None:
        icfile = os.path.join(melodicdir, "melodic_IC.nii.gz")
    else:
        icfile = initICfile
    if not os.path.isfile(icfile):
        print("cannot find independent component file at", icfile)
        sys.exit()

    if initICmask is None:
        icmask = os.path.join(melodicdir, "mask.nii.gz")
    else:
        icmask = initICmask
    if not os.path.isfile(icmask):
        print("cannot find independent component file at", icmask)
        sys.exit()

    if initTCfile is None:
        tcfile = os.path.join(melodicdir, "melodic_mix")
    else:
        tcfile = initTCfile
    if not os.path.isfile(tcfile):
        print("cannot find component timecourse file at", tcfile)
        sys.exit()

    if initmelodicICstatsfile is None:
        melodicICstatsfile = os.path.join(melodicdir, "melodic_ICstats")
    else:
        melodicICstatsfile = initmelodicICstatsfile
    if not os.path.isfile(melodicICstatsfile):
        print("cannot find component stats file at", tcfile)
        sys.exit()

    return bgfile, icfile, icmask, tcfile, melodicICstatsfile


def hamming(length, debug=False):
    #   return 0.54 - 0.46 * np.cos((np.arange(0.0, float(length), 1.0) / float(length)) * 2.0 * np.pi)
    r"""Returns a Hamming window function of the specified length.  Once calculated, windows
    are cached for speed.

    Parameters
    ----------
    length : int
        The length of the window function
        :param length:

    debug : boolean, optional
        When True, internal states of the function will be printed to help debugging.
        :param debug:

    Returns
    -------
    windowfunc : 1D float array
        The window function
    """
    try:
        return hammingwindows[str(length)]
    except KeyError:
        hammingwindows[str(length)] = 0.54 - 0.46 * np.cos(
            (np.arange(0.0, float(length), 1.0) / float(length)) * 2.0 * np.pi
        )
        if debug:
            print("initialized hamming window for length", length)
        return hammingwindows[str(length)]


def spectrum(inputdata, Fs=1.0, mode="power", trim=True):
    r"""Performs an FFT of the input data, and returns the frequency axis and spectrum
    of the input signal.

    Parameters
    ----------
    inputdata : 1D numpy array
        Input data
        :param inputdata:

    Fs : float, optional
        Sample rate in Hz.  Defaults to 1.0
        :param Fs:

    mode : {'real', 'imag', 'mag', 'phase', 'power'}, optional
        The type of spectrum to return.  Default is 'power'.
        :param mode:

    trim: bool
        If True (default) return only the positive frequency values

    Returns
    -------
    specaxis : 1D float array
        The frequency axis.

    specvals : 1D float array
        The spectral data.

    Other Parameters
    ----------------
    Fs : float
        Sample rate in Hz.  Defaults to 1.0
        :param Fs:

    mode : {'real', 'imag', 'complex', 'mag', 'phase', 'power'}
        The type of spectrum to return.  Legal values are 'real', 'imag', 'mag', 'phase', and 'power' (default)
        :param mode:
    """
    if trim:
        specvals = fftpack.fft(inputdata)[0 : len(inputdata) // 2]
        maxfreq = Fs / 2.0
        specaxis = np.linspace(0.0, maxfreq, len(specvals), endpoint=False)
    else:
        specvals = fftpack.fft(inputdata)
        maxfreq = Fs
        specaxis = np.linspace(0.0, maxfreq, len(specvals), endpoint=False)
    if mode == "real":
        specvals = specvals.real
    elif mode == "imag":
        specvals = specvals.imag
    elif mode == "complex":
        pass
    elif mode == "mag":
        specvals = np.absolute(specvals)
    elif mode == "phase":
        specvals = np.angle(specvals)
    elif mode == "power":
        specvals = np.sqrt(np.absolute(specvals))
    else:
        print("illegal spectrum mode")
        specvals = None
    return specaxis, specvals


class KeyPressWindow(QtWidgets.QMainWindow):
    sigKeyPress = QtCore.pyqtSignal(object)
    sigResize = QtCore.pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def closeEvent(self, event):
        writegrades()

    def keyPressEvent(self, ev):
        self.sigKeyPress.emit(ev)

    def resizeEvent(self, ev):
        self.sigResize.emit(ev)


def checkgrade(whichcomponent):
    global alldata, namelist, retainthresh

    if alldata[namelist[whichcomponent]]["closestrefR"] > retainthresh:
        refmatch = alldata[namelist[whichcomponent]]["closestref"]
        print(f"component match to reference IC {refmatch} exceeds threshold - retaining.")
        alldata[namelist[whichcomponent]]["grade"] = 1


def incrementgrade(whichcomponent):
    global alldata, namelist, usereferencefile

    alldata[namelist[whichcomponent]]["grade"] *= -1
    if usereferencefile:
        checkgrade(whichcomponent)


def decrementgrade(whichcomponent):
    global alldata, namelist, usereferencefile

    alldata[namelist[whichcomponent]]["grade"] *= -1
    if usereferencefile:
        checkgrade(whichcomponent)


def filterdata(glmtype=None):
    denoisingcmd = makefiltercommand(debug=False)
    if denoisingcmd is not None:
        if glmtype is None:
            print()
            print()
            print(" ".join(denoisingcmd))
            print()
            print()
        elif glmtype == "fsl":
            subprocess.Popen(" ".join(denoisingcmd), shell=True)
            print("process started")
        else:
            raise (Exception("glm type not supported"))


def makegradelists():
    global alldata, namelist

    badlist = []
    goodlist = []
    for i in range(len(namelist)):
        if alldata[namelist[i]]["grade"] < 0:
            badlist.append(str(i + 1))
        else:
            goodlist.append(str(i))
    return badlist, goodlist


def makefiltercommand(debug=False):
    global Funcfile, Mixfile, filteredfile, config

    badlist, dummy = makegradelists()

    if debug:
        print("makefiltercommand:")
        print(f"\t{badlist=}")
        print(f"\t{filteredfile=}")
        print(f"\t{config['usebatch']=}")

    # Non-aggressive denoising of the data using fsl_regfilt (partial regression), if requested
    if filteredfile is not None:
        if config["usebatch"]:
            print("using batch processing")
            denoisingcmd = ["sbatch", "--mem=8G", "--cpus-per-task=1", "--time=20"]
        else:
            print("using local processing")
            denoisingcmd = []
        if len(badlist) > 0:
            print("bad components: ", badlist)
            fslDir = os.path.join(os.environ["FSLDIR"], "bin")
            if fslDir is None:
                fslregfiltcmd = "fsl_regfilt"
            else:
                fslregfiltcmd = os.path.join(fslDir, "fsl_regfilt")
            denoisingcmd += [
                fslregfiltcmd,
                "-i",
                os.path.abspath(Funcfile),
                "-d",
                os.path.abspath(Mixfile),
                "-f",
                '"' + ",".join(badlist) + '"',
                "-o",
                os.path.abspath(filteredfile),
            ]
        else:
            print("no bad components")
            denoisingcmd += [
                "cp",
                os.path.abspath(Funcfile),
                os.path.abspath(filteredfile),
            ]
        if debug:
            print("denoising command: ", " ".join(denoisingcmd))
        return denoisingcmd
    else:
        print("no filtered file")
        return None


def writegrades():
    global outputfile, runmode
    global Funcfile, Mixfile, filteredfile

    badlist, goodlist = makegradelists()

    if runmode == "groupmelodic":
        outputstring = "\n".join(goodlist)
    else:
        outputstring = ",".join(badlist)
    if runmode == "fix":
        outputstring = "[" + outputstring + "]"
    with open(outputfile, "w") as thefile:
        thefile.write(outputstring + "\n")

    denoisingcmd = makefiltercommand(debug=False)
    if denoisingcmd is not None:
        print(" ".join(denoisingcmd))


def windowResized(evt):
    global mainwin, verbose

    if verbose:
        print("handling window resize")
    if mainwin is not None:
        updateLightbox()


def keyPressed(evt):
    global whichcomponent, numelements, mainwin, verbose, domotion, dotimecourse
    global maininfo, altwin, altinfo, blinkstatus
    global usereferencefile
    global outputfile

    if verbose:
        print("processing keypress event")

    keymods = None
    if evt.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier:
        keymods = "shift"
    elif evt.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier:
        keymods = "ctrl"

    if evt.key() == QtCore.Qt.Key.Key_Up:
        incrementgrade(whichcomponent)
    elif evt.key() == QtCore.Qt.Key.Key_Down:
        decrementgrade(whichcomponent)
    elif evt.key() == QtCore.Qt.Key.Key_Left:
        whichcomponent = (whichcomponent - 1) % numelements
        print("IC set to:", whichcomponent + 1)
    elif evt.key() == QtCore.Qt.Key.Key_Right:
        whichcomponent = (whichcomponent + 1) % numelements
        print("IC set to:", whichcomponent + 1)
    elif evt.key() == QtCore.Qt.Key.Key_A:
        mainwin.setorient("ax")
        mainwin.resetWinProps()
        if usereferencefile:
            altwin.setorient("ax")
            altwin.resetWinProps()
        print("Setting orientation to axial")
    elif evt.key() == QtCore.Qt.Key.Key_C:
        mainwin.setorient("cor")
        mainwin.resetWinProps()
        if usereferencefile:
            altwin.setorient("cor")
            altwin.resetWinProps()
        print("Setting orientation to coronal")
    elif evt.key() == QtCore.Qt.Key.Key_S:
        mainwin.setorient("sag")
        mainwin.resetWinProps()
        if usereferencefile:
            altwin.setorient("sag")
            altwin.resetWinProps()
        print("Setting orientation to sagittal")
    elif evt.key() == QtCore.Qt.Key.Key_D:
        print("Dumping main window information")
        mainwin.printWinProps()
        if usereferencefile:
            print("Dumping reference window information")
            altwin.printWinProps()
    elif evt.key() == QtCore.Qt.Key.Key_B:
        if usereferencefile:
            print("Blinking")
            blinkstatus = not blinkstatus
            if blinkstatus:
                mainwin.setviewinfo(altinfo)
                altwin.setviewinfo(maininfo)
            else:
                mainwin.setviewinfo(maininfo)
                altwin.setviewinfo(altinfo)
        else:
            pass
    elif evt.key() == QtCore.Qt.Key.Key_R:
        whichcomponent = 0
    elif evt.key() == QtCore.Qt.Key.Key_Escape:
        writegrades()
        print(f"bad component list written to {outputfile}")
    elif evt.key() == QtCore.Qt.Key.Key_F:
        if keymods == "shift":
            filterdata(glmtype="fsl")
            print("ran fsl_regfilt")
        else:
            filterdata(glmtype=None)
            print("printed fsl_regfilt command")
    else:
        print(evt.key())

    updateTCinfo()
    if dotimecourse:
        updateTimecourse()
    if domotion:
        updateMotion()
    updateLightbox()


def updateTCinfo():
    global whichcomponent, alldata, namelist, win, numelements, usereferencefile, verbose

    if verbose:
        print("entering updateTCinfo")
    thiscomponent = alldata[namelist[whichcomponent]]
    windowtitle = (
        "PICAchooser - Component {0} of {1}: {2:.2f}% explained var., {3:.2f}% total var.".format(
            whichcomponent + 1,
            numelements,
            thiscomponent["explainedvar"],
            thiscomponent["totalvar"],
        )
    )
    thiscomponent = alldata[namelist[whichcomponent]]
    if thiscomponent["grade"] is not None:
        if thiscomponent["grade"] <= 0:
            windowtitle += " - marked for removal"
    if usereferencefile:
        if thiscomponent["closestref"] is not None:
            windowtitle += ". R={0:.2f} with reference component {1}.".format(
                thiscomponent["closestrefR"], thiscomponent["closestref"] + 1
            )

    win.setWindowTitle(windowtitle)


def updateTimecourse():
    global timecourse_ax, spectrum_ax, whichcomponent, alldata, namelist, win, numelements, verbose
    global config

    if verbose:
        print("entering updateTimecourse")
    thiscomponent = alldata[namelist[whichcomponent]]
    if thiscomponent["grade"] is None:
        pencolor = "w"
    elif thiscomponent["grade"] == 0:
        pencolor = "w"
    elif thiscomponent["grade"] > 0:
        pencolor = config["keepcolor"]
    else:
        pencolor = config["discardcolor"]
        # windowtitle = windowtitle + " - marked for removal"

    timecourse_ax.plot(
        thiscomponent["timeaxis"],
        thiscomponent["timecourse"],
        stepMode=False,
        fillLevel=0,
        pen=pg.mkPen(pencolor, width=config["componentlinewidth"]),
        clear=True,
    )
    timecourse_ax.setTitle(
        "Independent component " + str(whichcomponent + 1),
    )

    spectrum_ax.plot(
        thiscomponent["freqaxis"],
        thiscomponent["spectrum"],
        stepMode=False,
        fillLevel=0,
        pen=pg.mkPen(pencolor, width=config["componentlinewidth"]),
        clear=True,
    )
    spectrum_ax.setTitle("Magnitude spectrum of timecourse " + str(whichcomponent + 1))

    spectop = 1.25 * np.max(thiscomponent["spectrum"])
    spectrum_ax.setYRange(0.0, spectop, padding=0)


def updateMotion():
    global transmot_ax, rotmot_ax
    global whichcomponent, alldata, motion, namelist, win, numelements, verbose, config

    if verbose:
        print("entering updateMotion")
    thiscomponent = alldata[namelist[whichcomponent]]
    curve1 = transmot_ax.plot()
    curve1.setData(
        thiscomponent["mottimeaxis"],
        motion["xtrans"],
        stepMode=False,
        fillLevel=0,
        pen=pg.mkPen(config["motionxcolor"], width=config["motionlinewidth"]),
        clear=True,
        name="xtrans",
    )
    curve2 = transmot_ax.plot()
    curve2.setData(
        thiscomponent["mottimeaxis"],
        motion["ytrans"],
        stepMode=False,
        fillLevel=0,
        pen=pg.mkPen(config["motionycolor"], width=config["motionlinewidth"]),
        clear=True,
        name="ytrans",
    )
    curve3 = transmot_ax.plot()
    curve3.setData(
        thiscomponent["mottimeaxis"],
        motion["ztrans"],
        stepMode=False,
        fillLevel=0,
        pen=pg.mkPen(config["motionzcolor"], width=config["motionlinewidth"]),
        clear=True,
        name="ztrans",
    )
    transmot_ax.setXRange(thiscomponent["timeaxis"][0], thiscomponent["timeaxis"][-1])
    if config["motionplotstyle"] == 0:
        transmot_ax.setYRange(config["transmotlimits"][0], config["transmotlimits"][1], padding=0)
    else:
        limitpen = pg.mkPen(
            config["motionlimitcolor"],
            width=config["motionlimitlinewidth"],
            style=QtCore.Qt.PenStyle.DotLine,
        )
        transtopLine = pg.InfiniteLine(angle=0, movable=False, pen=limitpen)
        transtopLine.setZValue(20)
        transmot_ax.addItem(transtopLine)
        transtopLine.setValue(config["transmotlimits"][1])
        transbottomLine = pg.InfiniteLine(angle=0, movable=False, pen=limitpen)
        transbottomLine.setZValue(20)
        transmot_ax.addItem(transbottomLine)
        transbottomLine.setValue(config["transmotlimits"][0])

        if config["scalemotiontodata"]:
            transmin = np.min(
                [
                    np.min(motion["xtrans"]),
                    np.min(motion["ytrans"]),
                    np.min(motion["ztrans"]),
                ]
            )
            transmax = np.max(
                [
                    np.max(motion["xtrans"]),
                    np.max(motion["ytrans"]),
                    np.max(motion["ztrans"]),
                ]
            )
        else:
            transmin = config["transmotlimits"][0]
            transmax = config["transmotlimits"][1]
        transrange = transmax - transmin
        transmin -= transrange * 0.1
        transmax += transrange * 0.1
        transmot_ax.setYRange(transmin, transmax, padding=0)

    transcorrs = "{:.2f}({:.2f}), {:.2f}({:.2f}), {:.2f}({:.2f})".format(
        alldata[namelist[whichcomponent]]["motioncorrs"]["xtrans"],
        alldata[namelist[whichcomponent]]["motioncorrps"]["xtrans"],
        alldata[namelist[whichcomponent]]["motioncorrs"]["ytrans"],
        alldata[namelist[whichcomponent]]["motioncorrps"]["ytrans"],
        alldata[namelist[whichcomponent]]["motioncorrs"]["ztrans"],
        alldata[namelist[whichcomponent]]["motioncorrps"]["ztrans"],
    )
    print("\ttranscorrs for component", whichcomponent + 1, transcorrs)

    curve4 = rotmot_ax.plot()
    curve4.setData(
        thiscomponent["mottimeaxis"],
        motion["xrot"],
        stepMode=False,
        fillLevel=0,
        pen=pg.mkPen(config["motionxcolor"], width=config["motionlinewidth"]),
        clear=True,
        name="xrot",
    )
    curve5 = rotmot_ax.plot()
    curve5.setData(
        thiscomponent["mottimeaxis"],
        motion["yrot"],
        stepMode=False,
        fillLevel=0,
        pen=pg.mkPen(config["motionycolor"], width=config["motionlinewidth"]),
        clear=True,
        name="yrot",
    )
    curve6 = rotmot_ax.plot()
    curve6.setData(
        thiscomponent["mottimeaxis"],
        motion["zrot"],
        stepMode=False,
        fillLevel=0,
        pen=pg.mkPen(config["motionzcolor"], width=config["motionlinewidth"]),
        clear=True,
        name="ztrans",
    )
    rotmot_ax.setXRange(thiscomponent["timeaxis"][0], thiscomponent["timeaxis"][-1])
    if config["motionplotstyle"] == 0:
        rotmot_ax.setYRange(config["rotmotlimits"][0], config["rotmotlimits"][1], padding=0)
    else:
        limitpen = pg.mkPen(
            config["motionlimitcolor"],
            width=config["motionlimitlinewidth"],
            style=QtCore.Qt.PenStyle.DotLine,
        )
        rottopLine = pg.InfiniteLine(angle=0, movable=False, pen=limitpen)
        rottopLine.setZValue(20)
        rotmot_ax.addItem(rottopLine)
        rottopLine.setValue(config["rotmotlimits"][1])
        rotbottomLine = pg.InfiniteLine(angle=0, movable=False, pen=limitpen)
        rotbottomLine.setZValue(20)
        rotmot_ax.addItem(rotbottomLine)
        rotbottomLine.setValue(config["rotmotlimits"][0])

        if config["scalemotiontodata"]:
            rotmin = np.min(
                [np.min(motion["xrot"]), np.min(motion["yrot"]), np.min(motion["zrot"])]
            )
            rotmax = np.max(
                [np.max(motion["xrot"]), np.max(motion["yrot"]), np.max(motion["zrot"])]
            )
        else:
            rotmin = config["rotmotlimits"][0]
            rotmax = config["rotmotlimits"][1]
        rotrange = rotmax - rotmin
        rotmin -= rotrange * 0.1
        rotmax += rotrange * 0.1
        rotmot_ax.setYRange(rotmin, rotmax, padding=0)

    rotcorrs = "{:.2f}({:.2f}), {:.2f}({:.2f}), {:.2f}({:.2f})".format(
        alldata[namelist[whichcomponent]]["motioncorrs"]["xrot"],
        alldata[namelist[whichcomponent]]["motioncorrps"]["xrot"],
        alldata[namelist[whichcomponent]]["motioncorrs"]["yrot"],
        alldata[namelist[whichcomponent]]["motioncorrps"]["yrot"],
        alldata[namelist[whichcomponent]]["motioncorrs"]["zrot"],
        alldata[namelist[whichcomponent]]["motioncorrps"]["zrot"],
    )
    print("\trotcorrs for component", whichcomponent + 1, rotcorrs)


def updateLightbox():
    global mainwin, winlist, whichcomponent, verbose, alldata, namelist
    global keepcolor, discardcolor

    if verbose:
        print("entering updateLightbox")

    thiscomponent = alldata[namelist[whichcomponent]]
    if thiscomponent["grade"] == 1:
        thelabel = "Keeping IC {0}".format(whichcomponent + 1)
        thecolor = config["keepcolor"]
    else:
        thelabel = "Discarding IC {0}".format(whichcomponent + 1)
        thecolor = config["discardcolor"]
    for idx, thewin in enumerate(winlist):
        if idx == 0:
            if len(winlist) > 1:
                thewin.setLabel("Data view: " + thelabel, thecolor)
            else:
                thewin.setLabel(thelabel, thecolor)
        else:
            thewin.setLabel("Reference view: " + thelabel, thecolor)
        thewin.setTpos(whichcomponent)
        thewin.getWinProps()
        thewin.resetWinProps()


def main():
    global ui, win, mainwin, winlist
    global namelist, outputfile, alldata, motion, whichcomponent, numelements, runmode
    global mainwin, verbose
    global usereferencefile, retainthresh
    global config
    global Funcfile, Mixfile, filteredfile
    global domotion, dotimecourse
    global maininfo, altwin, altinfo, blinkstatus

    mainwin = None
    verbose = False
    usereferencefile = False
    dotimecourse = True
    retainthresh = DEFAULT_RETAINTHRESH

    parser = argparse.ArgumentParser(
        prog="PICAchooser",
        description="A program to review (and alter) melodic component selections.",
        allow_abbrev=False,
    )

    # Required arguments
    parser.add_argument(
        "runmode",
        action="store",
        type=str,
        help=(
            'Analysis mode.  Valid choices are "melodic", "melodic_dataex", "groupmelodic" "aroma", and "fix".  '
            'In melodic mode, the default output file is named "badcomponents.txt" and will be written to MELODICDIR '
            'as comma separated integers. In melodic_dataex mode, we assume this is a feat run with "melodic data "'
            'exploration" selected - if you specify the featdir, it should find everything.  Otherwise it acts like '
            'melodic mode.  In groupmelodic mode, the default output file is named "goodcomponents.txt" '
            "(you are more interested in which components should be retained) and will be written to MELODICDIR as newline "
            'separated integers (starting from 0). In aroma mode, the file "classified_motion_ICs.txt" must exist in the parent of '
            'MELODICDIR; by default the output will be written to "classified_motion_ICs_revised.txt" in the same '
            'directory.  In fix mode, the default output file is named "hand_labels_noise.txt" and will be written '
            "to MELODICDIR as comma separated integers with square brackets surrounding the line."
        ),
        default=None,
    )

    # input file specification
    hlfilespec = parser.add_argument_group(
        "Standard input file location specification.  For certain runmodes, one of these will be sufficient to fully specify all file locations."
    )
    hlfilespec.add_argument(
        "--featdir",
        dest="featdir",
        type=lambda x: pica_util.is_valid_dir(parser, x),
        help="The FEAT directory associated with this MELODIC run.",
        default=None,
    )

    hlfilespec.add_argument(
        "--melodicdir",
        dest="melodicdir",
        type=lambda x: pica_util.is_valid_dir(parser, x),
        help="The .ica directory for this MELODIC run.",
        default=None,
    )

    llfilespec = parser.add_argument_group(
        "Nonstandard input file location specification.  Setting any of these overrides any location inferred from --melodicdir or --featdir."
    )
    llfilespec.add_argument(
        "--backgroundfile",
        dest="specBGfile",
        metavar="BGFILE",
        type=lambda x: pica_util.is_valid_file(parser, x),
        help=(
            "The anatomic file on which to display the ICs (usually found in FEATDIR/reg/example_func.nii.gz),"
        ),
        default=None,
    )

    llfilespec.add_argument(
        "--funcfile",
        dest="specFuncfile",
        metavar="FUNCFILE",
        type=lambda x: pica_util.is_valid_file(parser, x),
        help=(
            "The functional file to be filtered (usually found in FEATDIR/filtered_func_data.nii.gz),"
        ),
        default=None,
    )

    llfilespec.add_argument(
        "--motionfile",
        dest="specMotionfile",
        metavar="MOTIONFILE",
        type=lambda x: pica_util.is_valid_file(parser, x),
        help=(
            "The anatomic file on which to display the ICs (usually found in FEATDIR/mc/prefiltered_func_data_mcf.par). "
            "If the file has a .tsv extension, assume it is an fmriprep confounds file."
        ),
        default=None,
    )

    llfilespec.add_argument(
        "--ICfile",
        dest="specICfile",
        metavar="ICFILE",
        type=lambda x: pica_util.is_valid_file(parser, x),
        help="The independent component file produced by MELODIC (usually found in MELODICDIR/melodic_IC.nii.gz).",
        default=None,
    )

    llfilespec.add_argument(
        "--ICmask",
        dest="specICmask",
        metavar="ICMASK",
        type=lambda x: pica_util.is_valid_file(parser, x),
        help=(
            "The independent component mask file produced by MELODIC (usually found in MELODICDIR/mask.nii.gz)."
        ),
        default=None,
    )

    llfilespec.add_argument(
        "--timecoursefile",
        dest="specMixfile",
        metavar="MIXFILE",
        type=lambda x: pica_util.is_valid_file(parser, x),
        help=(
            "The timecourses of the independent components (usually found in MELODICDIR/melodic_mix),"
        ),
        default=None,
    )

    llfilespec.add_argument(
        "--ICstatsfile",
        dest="melodicICstatsfile",
        metavar="STATSFILE",
        type=lambda x: pica_util.is_valid_file(parser, x),
        help=("The melodic stats file (usually found in MELODICDIR/melodic_ICstats),"),
        default=None,
    )

    referencefile = parser.add_argument_group("Reference file arguments")
    referencefile.add_argument(
        "--usereferencefile",
        action="store_true",
        help=("Compare ICs to those in a reference file to flag 'real' components."),
        default=False,
    )
    referencefile.add_argument(
        "--refdisplaythresh",
        type=lambda x: pica_util.is_float(parser, x),
        metavar=("THRESH"),
        help="z threshold for the displayed reference ICA components.  Default is 7.",
        default=7,
    )
    referencefile.add_argument(
        "--retainthresh",
        action="store",
        type=lambda x: pica_util.is_float(parser, x),
        metavar=("THRESH"),
        help=(
            "If an IC is correlated by more than THRESH with any reference IC, it will be retained. "
            f"Default is {DEFAULT_RETAINTHRESH}"
        ),
        default=DEFAULT_RETAINTHRESH,
    )
    referencefile.add_argument(
        "--ICreffile",
        dest="referenceICfile",
        metavar="ICFILE",
        type=lambda x: pica_util.is_valid_file(parser, x),
        help=(
            "The reference file to check for 'real' networks.  Default is the Smith D50 reference file."
        ),
        default=None,
    )

    # optional arguments
    other = parser.add_argument_group("Other arguments")
    other.add_argument(
        "--initfile",
        type=lambda x: pica_util.is_valid_file(parser, x),
        help="The name of an initial bad component file (in aroma mode, this overrides the default input file for AROMA).",
        default=None,
    )
    other.add_argument(
        "--outputfile",
        type=str,
        help="Where to write the bad component file (this overrides the default output file name).",
        default=None,
    )
    other.add_argument(
        "--filteredfile",
        type=str,
        help=(
            "The name of the filtered NIFTI file.  If this is set, then when the bad component file is written, "
            "the command to generate the filtered file will be printed to the terminal window."
        ),
        default=None,
    )
    other.add_argument(
        "--displaythresh",
        type=lambda x: pica_util.is_float(parser, x),
        metavar=("THRESH"),
        help="z threshold for the displayed ICA components.  Default is 2.3.",
        default=2.3,
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

    configuration = parser.add_argument_group("Configuration arguments")
    configuration.add_argument(
        "--keepcolor",
        type=str,
        help=('Set the color of timecourses to be kept (default is "g").'),
        default=None,
    )
    configuration.add_argument(
        "--discardcolor",
        type=str,
        help=('Set the color of timecourses to discard (default is "r").'),
        default=None,
    )
    configuration.add_argument(
        "--transmotlimits",
        action="store",
        nargs=2,
        type=lambda x: pica_util.is_float(parser, x),
        metavar=("LOWERLIM", "UPPERLIM"),
        help=(
            'Override the "normal" limits of translational motion from the values in the configuration '
            "file to LOWERLIM-UPPERLIM mm."
        ),
        default=(None, None),
    )
    configuration.add_argument(
        "--rotmotlimits",
        action="store",
        nargs=2,
        type=lambda x: pica_util.is_float(parser, x),
        metavar=("LOWERLIM", "UPPERLIM"),
        help=(
            'Override the "normal" limits of rotations motion from the values in the configuration '
            "file to LOWERLIM-UPPERLIM radians."
        ),
        default=(None, None),
    )
    configuration.add_argument(
        "--scalemotiontodata",
        action="store_true",
        help=(
            "Scale motion plots to the motion timecourse values rather than to the limit lines."
        ),
        default=None,
    )
    configuration.add_argument(
        "--componentlinewidth",
        action="store",
        type=lambda x: pica_util.is_float(parser, x),
        metavar=("LINEWIDTH"),
        help=(
            "Override the component line width (in pixels) in the configuration "
            "file with LINEWIDTH."
        ),
        default=None,
    )
    configuration.add_argument(
        "--motionlinewidth",
        action="store",
        type=lambda x: pica_util.is_float(parser, x),
        metavar=("LINEWIDTH"),
        help=(
            "Override the motion timecourse line widths (in pixels) in the configuration "
            "file with LINEWIDTH."
        ),
        default=None,
    )
    configuration.add_argument(
        "--motionlimitlinewidth",
        action="store",
        type=lambda x: pica_util.is_float(parser, x),
        metavar=("LINEWIDTH"),
        help=(
            "Override the line widths of the motion limit lines (in pixels) in the configuration "
            "file with LINEWIDTH."
        ),
        default=None,
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
        "--nomotion",
        dest="domotion",
        action="store_false",
        help=("Turn off motion timecourse tracking."),
        default=True,
    )
    debugging.add_argument(
        "--verbose",
        action="store_true",
        help=(
            "Output exhaustive amounts of information about the internal workings of PICAchooser. "
            "You almost certainly don't want this."
        ),
        default=False,
    )
    debugging.add_argument(
        "--debug",
        action="store_true",
        help=("Turn on debugging output."),
        default=False,
    )

    try:
        args = parser.parse_args()
    except SystemExit:
        print("Use --help option for detailed information on options.")
        raise

    runmode = args.runmode
    verbose = args.verbose
    usereferencefile = args.usereferencefile
    retainthresh = args.retainthresh
    domotion = args.domotion

    # make sure we can find the required input files
    # first see if there are specific overrides
    BGfile = args.specBGfile
    Funcfile = args.specFuncfile
    Motionfile = args.specMotionfile
    ICfile = args.specICfile
    Mixfile = args.specMixfile
    ICmask = args.specICmask
    melodicICstatsfile = args.melodicICstatsfile
    ICreffile = args.referenceICfile

    if args.featdir is not None:
        BGfile, Funcfile, Motionfile = findfromfeatdir(args.featdir, BGfile, Funcfile, Motionfile)
        if runmode == "melodic_dataex":
            BGfile, ICfile, ICmask, Mixfile, melodicICstatsfile = findfrommelodicdir(
                os.path.join(args.featdir, "filtered_func_data.ica"),
                BGfile,
                ICfile,
                ICmask,
                Mixfile,
                melodicICstatsfile,
            )

    if args.melodicdir is not None:
        BGfile, ICfile, ICmask, Mixfile, melodicICstatsfile = findfrommelodicdir(
            args.melodicdir, BGfile, ICfile, ICmask, Mixfile, melodicICstatsfile
        )
        if runmode == "groupmelodic":
            Funcfile = None
            Motionfile = None
        removefiledir = args.melodicdir

    if Funcfile is None and runmode != "groupmelodic":
        print("Cannot set functional file.  Use either the --featdir or --Funcfile option.")
        sys.exit()

    if Motionfile is None and domotion and runmode != "groupmelodic":
        print(
            "Cannot set motion timecourse file.  Use either the --featdir or --motionfile option."
        )
        sys.exit()

    if BGfile is None:
        print("Cannot set background file.  Use either the --featdir or --backgroundfile option.")
        sys.exit()

    if ICfile is None:
        print("Cannot set IC file.  Use either the --melodicdir or --ICfile option.")
        sys.exit()
    removefiledir = os.path.dirname(ICfile)

    if ICmask is None:
        print("Cannot set IC mask.  Use either the --melodicdir or --ICmask option.")
        sys.exit()

    if Mixfile is None:
        print(
            "Cannot set timecourse file.  Use either the --melodicdir or --timecoursefile option."
        )
        sys.exit()

    if ICreffile is None:
        ICreffile = os.path.join(pica_util.getrefdir(), "Smith_D50_Subset_ICs.nii.gz")

    # there are 5 modes at the moment - groupmelodic, melodic, melodic_dataex, aroma, and fix
    if runmode == "melodic" or runmode == "melodic_dataex":
        if args.initfile is not None:
            Removefile = args.initfile
        else:
            Removefile = os.path.join(removefiledir, "badcomponents.txt")
        if not os.path.isfile(Removefile):
            print(
                "cannot find existing removed component file at",
                Removefile,
                "- will create new one",
            )
            if args.outputfile is None:
                outputfile = Removefile.replace(".txt", "_revised.txt")
            else:
                outputfile = args.outputfile
            initfileexists = False
        else:
            print("will create new removed component file at", Removefile)
            if args.outputfile is None:
                outputfile = Removefile
            else:
                outputfile = args.outputfile
            print("will create new removed component file at", outputfile)
            initfileexists = True
    elif runmode == "groupmelodic":
        domotion = False
        dotimecourse = False
        if args.initfile is not None:
            Removefile = args.initfile
        else:
            Removefile = os.path.join(removefiledir, "goodcomponents.txt")
        if not os.path.isfile(Removefile):
            print(
                "cannot find existing good component file at",
                Removefile,
                "- will create new one",
            )
            if args.outputfile is None:
                outputfile = Removefile.replace(".txt", "_revised.txt")
            else:
                outputfile = args.outputfile
            initfileexists = False
        else:
            print("will create new good component file at", Removefile)
            if args.outputfile is None:
                outputfile = Removefile
            else:
                outputfile = args.outputfile
            print("will create new good component file at", outputfile)
            initfileexists = True
    elif runmode == "aroma":
        aromadir = os.path.dirname(removefiledir)
        if args.initfile is not None:
            Removefile = args.initfile
        else:
            Removefile = os.path.join(aromadir, "classified_motion_ICs.txt")
        if not os.path.isfile(Removefile):
            print("cannot find removed component file at", Removefile)
            sys.exit()
        if args.outputfile is None:
            outputfile = Removefile.replace(".txt", "_revised.txt")
        else:
            outputfile = args.outputfile
        initfileexists = True
    elif runmode == "fix":
        if args.initfile is not None:
            Removefile = args.initfile
        else:
            Removefile = os.path.join(removefiledir, "hand_labels_noise.txt")
        if not os.path.isfile(Removefile):
            print(
                "cannot find existing removed component file at",
                Removefile,
                "- will create new one",
            )
            if args.outputfile is None:
                outputfile = Removefile.replace(".txt", "_revised.txt")
            else:
                outputfile = args.outputfile
            initfileexists = False
        else:
            print("will create new removed component file at", Removefile)
            if args.outputfile is None:
                outputfile = Removefile
            else:
                outputfile = args.outputfile
            print("will create new removed component file at", outputfile)
            initfileexists = True
    else:
        print(
            "Illegal runmode",
            runmode,
            '.  Legal runmodes are "melodic", "melodic_dataex", "groupmelodic", "aroma", and "fix".  Exiting',
        )
        sys.exit()

    if args.filteredfile is not None:
        filteredfile = args.filteredfile
    else:
        if runmode != "groupmelodic":
            FuncfileDir, FuncfileName = os.path.split(os.path.abspath(Funcfile))
            filteredfile = os.path.join(FuncfileDir, "filtered_func_data_picachooserglm.nii.gz")
        else:
            filteredfile = None

    if verbose:
        print(f"ICfile: {ICfile}")
        if args.usereferencefile:
            print(f"ICreffile: {ICreffile}")
        print(f"ICmask: {ICmask}")
        print(f"BGfile: {BGfile}")
        print(f"Funcfile: {Funcfile}")
        print(f"Mixfile: {Mixfile}")
        print(f"Motionfile: {Motionfile}")
        print(f"Removefile: {Removefile}")
        print(f"filteredfile: {filteredfile}")
        print(f"melodicICstatsfile: {melodicICstatsfile}")

    # set the configurable options
    def initconfig():
        print("initializing preferences")
        config = {
            "prefsversion": 5,
            "componentlinewidth": 2,
            "keepcolor": "g",
            "discardcolor": "r",
            "motionxcolor": "#ff8888",
            "motionycolor": "#88ff88",
            "motionzcolor": "#8888ff",
            "motionlinewidth": 2,
            "transmotlimits": (-2.5, 2.5),
            "rotmotlimits": (-0.04, 0.04),
            "motionlimitcolor": "#cccccc",
            "motionlimitlinewidth": 4,
            "motionplotstyle": 1,
            "scalemotiontodata": False,
            "usebatch": False,
        }
        return config

    configfile = os.path.join(os.environ["HOME"], ".picachooser.json")
    if not os.path.isfile(configfile):
        config = initconfig()
        io.writedicttojson(config, configfile, sort_keys=False)
    else:
        config = io.readdictfromjson(configfile)
        try:
            prefsversion = config["prefsversion"]
        except KeyError:
            prefsversion = 0
        if prefsversion < 5:
            config = initconfig()
            io.writedicttojson(config, configfile)

    if args.keepcolor is not None:
        print("setting keepcolor to", args.keepcolor)
        config["keepcolor"] = args.keepcolor

    if args.discardcolor is not None:
        print("setting dicardcolor to", args.discardcolor)
        config["discardcolor"] = args.discardcolor

    if args.transmotlimits[0] is not None:
        print(
            "setting transmotlimits to",
            (args.transmotlimits[0], args.transmotlimits[1]),
        )
        config["transmotlimits"] = (args.transmotlimits[0], args.transmotlimits[1])

    if args.rotmotlimits[0] is not None:
        print("setting rotmotlimits to", (args.rotmotlimits[0], args.rotmotlimits[1]))
        config["rotmotlimits"] = (args.rotmotlimits[0], args.rotmotlimits[1])

    if args.scalemotiontodata is not None:
        print("will scale motion to data")
        config["scalemotiontodata"] = True

    if args.componentlinewidth is not None:
        print("setting componentlinewidth to", args.componentlinewidth)
        config["componentlinewidth"] = args.componentlinewidth

    if args.motionlinewidth is not None:
        print("setting motionlinewidth to", args.motionlinewidth)
        config["motionlinewidth"] = args.motionlinewidth

    if args.motionlimitlinewidth is not None:
        print("setting motionlimitlinewidth to", args.motionlimitlinewidth)
        config["motionlimitlinewidth"] = args.motionlimitlinewidth

    # set the sample rate
    # if domotion:
    #    tr, timepoints = io.fmritimeinfo(Funcfile)
    # else:
    #    tr = 1.0
    if Funcfile is not None:
        tr, timepoints = io.fmritimeinfo(Funcfile)
    else:
        tr = 1.0
    samplerate = 1.0 / tr

    # read in the timecourses and their current labels
    alldata = {}
    numelements = 0
    alltcs = io.readvecs(Mixfile, debug=args.debug)
    numelements = alltcs.shape[0]
    grades = np.ones(numelements, dtype=np.int16)
    if initfileexists:
        print(f"reading initfile {Removefile}...")
        with open(Removefile, "r") as thefile:
            inline = thefile.readline().replace("[", "").replace("]", "")
        if inline.find(",") > -1:
            inlist = inline.split(",")
        else:
            inlist = inline.split()
        for component in inlist:
            grades[int(component) - 1] = -1
    else:
        grades = None

    # read in the motion timecourses
    if domotion:
        print("reading motion timecourses...")
        filebase, extension = os.path.splitext(Motionfile)
        if extension == ".par":
            allmotion = io.readvecs(Motionfile, debug=args.debug)
            motion = {}
            motion["xtrans"] = allmotion[3, :] * 1.0
            motion["ytrans"] = allmotion[4, :] * 1.0
            motion["ztrans"] = allmotion[5, :] * 1.0
            motion["maxtrans"] = np.max(
                [
                    np.max(motion["xtrans"]),
                    np.max(motion["ytrans"]),
                    np.max(motion["ztrans"]),
                ]
            )
            motion["mintrans"] = np.min(
                [
                    np.min(motion["xtrans"]),
                    np.min(motion["ytrans"]),
                    np.min(motion["ztrans"]),
                ]
            )
            motion["xrot"] = allmotion[0, :] * 1.0
            motion["yrot"] = allmotion[1, :] * 1.0
            motion["zrot"] = allmotion[2, :] * 1.0
            motion["maxrot"] = np.max(
                [np.max(motion["xrot"]), np.max(motion["yrot"]), np.max(motion["zrot"])]
            )
            motion["minrot"] = np.min(
                [np.min(motion["xrot"]), np.min(motion["yrot"]), np.min(motion["zrot"])]
            )
        elif extension == ".tsv":
            allmotion = io.readfmriprepconfounds(filebase)
            motion = {}
            motion["xtrans"] = allmotion["trans_x"] * 1.0
            motion["ytrans"] = allmotion["trans_y"] * 1.0
            motion["ztrans"] = allmotion["trans_z"] * 1.0
            motion["maxtrans"] = np.max(
                [
                    np.max(motion["xtrans"]),
                    np.max(motion["ytrans"]),
                    np.max(motion["ztrans"]),
                ]
            )
            motion["mintrans"] = np.min(
                [
                    np.min(motion["xtrans"]),
                    np.min(motion["ytrans"]),
                    np.min(motion["ztrans"]),
                ]
            )
            motion["xrot"] = allmotion["rot_x"] * 1.0
            motion["yrot"] = allmotion["rot_y"] * 1.0
            motion["zrot"] = allmotion["rot_z"] * 1.0
            motion["maxrot"] = np.max(
                [np.max(motion["xrot"]), np.max(motion["yrot"]), np.max(motion["zrot"])]
            )
            motion["minrot"] = np.min(
                [np.min(motion["xrot"]), np.min(motion["yrot"]), np.min(motion["zrot"])]
            )
        else:
            print("cannot read files with extension", extension)
            sys.exit()
        motionlen = motion["xtrans"].shape[0]

    # read in the variance percents
    melodicICstats = io.readvecs(melodicICstatsfile, debug=args.debug)

    namelist = []
    print("reading timecourses...")
    for idx in range(numelements):
        theIC = str(idx + 1)
        namelist.append(theIC)
        if grades is not None:
            thegrade = grades[idx]
        else:
            thegrade = 1
        thesamplerate = samplerate
        alldata[theIC] = {}
        invec = alltcs[idx, :]
        alldata[theIC]["timecourse"] = invec * 1.0
        alldata[theIC]["motioncorrs"] = {}
        alldata[theIC]["motioncorrps"] = {}
        tclen = alldata[theIC]["timecourse"].shape[0]
        if domotion:
            alldata["componentstartpoint"] = motionlen - tclen
            for component in ["xtrans", "ytrans", "ztrans", "xrot", "yrot", "zrot"]:
                (
                    alldata[theIC]["motioncorrs"][component],
                    alldata[theIC]["motioncorrps"][component],
                ) = pearsonr(
                    motion[component][alldata["componentstartpoint"] :],
                    alldata[theIC]["timecourse"],
                )
            alldata[theIC]["mottimeaxis"] = (
                np.linspace(0.0, 1.0 * (motionlen - 1), num=motionlen, endpoint=True)
                / thesamplerate
            )
        else:
            alldata["componentstartpoint"] = 0

        alldata[theIC]["totalvar"] = melodicICstats[1, idx]
        alldata[theIC]["explainedvar"] = melodicICstats[0, idx]
        alldata[theIC]["timeaxis"] = (
            np.linspace(
                1.0 * alldata["componentstartpoint"],
                1.0 * (len(invec) - 1),
                num=len(invec),
                endpoint=True,
            )
            / thesamplerate
        )
        alldata[theIC]["freqaxis"], alldata[theIC]["spectrum"] = spectrum(
            hamming(len(invec)) * invec, Fs=thesamplerate, mode="mag"
        )
        alldata[theIC]["grade"] = thegrade
        alldata[theIC]["samplerate"] = thesamplerate
        if verbose:
            print(theIC, thegrade, thesamplerate)
    print("Read in", numelements, "files")
    if domotion:
        motion["maxtime"] = alldata["1"]["timeaxis"][-1] + 0.0
    whichcomponent = 0

    # make the main window
    if pyqtversion == 5:
        if dotimecourse:
            import picachooser.picachooserTemplate as uiTemplate
        else:
            import picachooser.picachooser_imonlyTemplate as uiTemplate
    else:
        if dotimecourse:
            import picachooser.picachooserTemplate_qt6 as uiTemplate
        else:
            import picachooser.picachooser_imonlyTemplate_qt6 as uiTemplate

    app = QtWidgets.QApplication([])
    print("setting up output window")
    win = KeyPressWindow()
    win.sigKeyPress.connect(keyPressed)
    win.sigResize.connect(windowResized)

    ui = uiTemplate.Ui_MainWindow()
    ui.setupUi(win)
    win.show()
    win.setWindowTitle("PICAchooser")

    if dotimecourse:
        # set up the regressor timecourse window
        print("about to set up the timecourse")
        global timecourse_ax
        timecoursewin = ui.timecourse_graphicsView
        timecourse_ax = timecoursewin.addPlot(
            title="Independent component",
            labels={"left": "Intensity (a.u.)", "bottom": "Time (s)"},
        )

        # set up the regressor spectrum window
        print("about to set up the spectrum")
        global spectrum_ax
        spectrumwin = ui.spectrum_graphicsView
        spectrum_ax = spectrumwin.addPlot(
            title="Magnitude spectrum of timecourse",
            labels={"left": "Power (a.u.)", "bottom": "Frequency (Hz)"},
        )

    if domotion:
        global transmot_ax, rotmot_ax
        # set up the translational motion window
        print("about to set up the translational motion")
        transmotwin = ui.translation_graphicsView
        transmot_ax = transmotwin.addPlot(
            title="Translation timecourses",
            labels={"left": "Displacement (mm)", "bottom": "Time (s)"},
        )

        # set up the rotational motion window
        print("about to set up the rotational motion")
        rotmotwin = ui.rotation_graphicsView
        rotmot_ax = rotmotwin.addPlot(
            title="Rotation timecourses",
            labels={"left": "Rotation (radians)", "bottom": "Time (s)"},
        )

    print("setting up image window")
    geommaskimage = lb.imagedataset(
        "ICmask",
        ICmask,
        "ICmask",
        xlims=args.spatialroi[0:2],
        ylims=args.spatialroi[2:4],
        zlims=args.spatialroi[4:6],
        lut_state=cm.mask_state,
    )
    fgimage = lb.imagedataset(
        "IC",
        ICfile,
        "IC",
        xlims=args.spatialroi[0:2],
        ylims=args.spatialroi[2:4],
        zlims=args.spatialroi[4:6],
        lut_state=cm.redyellow_state,
        geommask=geommaskimage.data,
    )
    fgimage.setFuncMaskByThresh(threshval=args.displaythresh)
    bgimage = lb.imagedataset(
        "BG",
        BGfile,
        "background",
        xlims=args.spatialroi[0:2],
        ylims=args.spatialroi[2:4],
        zlims=args.spatialroi[4:6],
        lut_state=cm.gray_state,
    )

    if usereferencefile:
        refnim, refdata, refheader, refdims, refsizes = io.readfromnifti(ICreffile)
        refimage = lb.imagedataset(
            "Reference",
            ICreffile,
            "Reference",
            xlims=args.spatialroi[0:2],
            ylims=args.spatialroi[2:4],
            zlims=args.spatialroi[4:6],
            lut_state=cm.redyellow_state,
            geommask=geommaskimage.data,
        )
        refimage.setFuncMaskByThresh(threshval=args.refdisplaythresh)
        if args.debug:
            print(f"{(refimage.data).shape=}")

        if io.checkspacematch(refheader, fgimage.header):
            print(f"Matching ICs to maps in {ICreffile}")
            thecorrs, thebestmatches = pica_util.calccorrs(ICfile, ICreffile, ICmask, debug=True)
            for idx in range(numelements):
                theIC = str(idx + 1)
                if args.debug:
                    print(f"{idx=}, {thebestmatches[idx]=}")
                alldata[theIC]["closestref"] = thebestmatches[idx]
                alldata[theIC]["closestrefR"] = thecorrs[idx, thebestmatches[idx]]
            for idx in range(numelements):
                checkgrade(idx)
        else:
            print("No matching reference IC file found")
            usereferencefile = False
            for idx in range(numelements):
                theIC = str(idx + 1)
                alldata[theIC]["closestref"] = None

    mainwin = lb.LightboxItem(fgimage, ui.image_graphicsView, bgmap=bgimage, verbose=verbose)
    maininfo = mainwin.getviewinfo()
    winlist = [mainwin]
    if usereferencefile:
        altwin = lb.LightboxItem(
            refimage, ui.image_altgraphicsView, bgmap=bgimage, verbose=verbose
        )
        altwin.settmapping(thebestmatches)
        altinfo = altwin.getviewinfo()
        ui.label.setText(
            'Right and left arrows step through components. Up and down arrows toggle component retention.  "r" to reset component.  "a", "c", and "s" select axial, coronal, or sagittal views.  "b" to blink.  ESC to write component file.'
        )
        winlist.append(altwin)
    else:
        altwin = None

    blinkstatus = False
    # initialize everything
    updateTCinfo()
    if dotimecourse:
        updateTimecourse()
    if domotion:
        updateMotion()
    updateLightbox()

    QtWidgets.QApplication.instance().exec()


def entrypoint():
    main()


if __name__ == "__main__":
    entrypoint()
