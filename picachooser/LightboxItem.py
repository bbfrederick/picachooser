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
# $Date: 2016/04/07 21:46:54 $
# $Id: LightboxItem.py,v 1.13 2016/04/07 21:46:54 frederic Exp $
#
# -*- coding: utf-8 -*-

"""
A widget for displaying 3 and 4 dimensional data in a lightbox
"""

from __future__ import division, print_function

import os

import numpy as np
import pyqtgraph as pg
from nibabel.affines import apply_affine
from pyqtgraph.Qt import QtCore, QtGui

try:
    from PIL import Image

    PILexists = True
except ImportError:
    PILexists = False


import picachooser.colormaps as cm
import picachooser.io as io
import picachooser.stats as stats


def newColorbar(view, left, top, impixpervoxx, impixpervoxy, imgsize):
    cb_xdim = imgsize // 10
    cb_ydim = imgsize
    theviewbox = pg.ViewBox(enableMouse=False)
    theviewbox.setRange(
        QtCore.QRectF(0, 0, cb_xdim, cb_ydim),
        xRange=(0, cb_xdim - 1),
        yRange=(0, cb_ydim - 1),
        padding=0.0,
        disableAutoRange=False,
    )
    theviewbox.setAspectLocked()

    thecolorbarwin = pg.ImageItem()
    theviewbox.addItem(thecolorbarwin)
    thecolorbarwin.translate(left, top)
    thecolorbarwin.scale(impixpervoxx, impixpervoxy)

    colorbarvals = np.zeros((cb_xdim, cb_ydim), dtype=np.float64)
    for i in range(0, cb_ydim):
        colorbarvals[:, i] = i * (1.0 / (cb_ydim - 1.0))
    thecolorbarwin.setImage(colorbarvals, levels=[0.0, 1.0])
    return thecolorbarwin, theviewbox


def newViewWindow(view, winwidth, winheight, enableMouse=False):
    theviewbox = view.addViewBox(enableMouse=enableMouse, enableMenu=False)
    theviewbox.autoRange(padding=0.02)
    theviewbox.setRange(
        QtCore.QRectF(0, 0, winwidth, winheight), padding=0.0, disableAutoRange=False
    )
    theviewbox.setBackgroundColor([50, 50, 50])
    theviewbox.setAspectLocked()

    theviewfgposwin = pg.ImageItem()
    theviewbox.addItem(theviewfgposwin)
    theviewfgposwin.setZValue(10)

    theviewfgnegwin = pg.ImageItem()
    theviewbox.addItem(theviewfgnegwin)
    theviewfgnegwin.setZValue(5)

    theviewbgwin = pg.ImageItem()
    theviewbox.addItem(theviewbgwin)
    theviewbgwin.setZValue(0)

    thelabel = pg.TextItem(anchor=(0.0, 1.0))
    theviewbox.addItem(thelabel)
    thelabel.setZValue(20)

    return theviewfgposwin, theviewfgnegwin, theviewbgwin, thelabel, theviewbox


class imagedataset:
    "Store and image dataset and some information about it"

    def __init__(
        self,
        name,
        filename,
        namebase,
        mask=None,
        label=None,
        isaMask=False,
        geommask=None,
        funcmask=None,
        flipx=True,
        xlims=[0, -1],
        ylims=[0, -1],
        zlims=[0, -1],
        lut_state=cm.gray_state,
        verbose=False,
    ):
        self.verbose = verbose
        self.name = name
        if label is None:
            self.label = name
        else:
            self.label = label
        self.filename = filename
        self.namebase = namebase
        if self.verbose:
            print("reading map ", self.name, " from ", self.filename, "...")
        self.isaMask = isaMask
        self.gradient = pg.GradientWidget(orientation="right", allowAdd=True)
        self.ry_gradient = pg.GradientWidget(orientation="right", allowAdd=True)
        self.blb_gradient = pg.GradientWidget(orientation="right", allowAdd=True)
        self.lut_state = lut_state
        self.theLUT = None
        self.theRedyellowLUT = None
        self.theBluelightblueLUT = None
        self.setLUT(self.lut_state)
        self.flipx = flipx
        self.xlims = xlims
        self.ylims = ylims
        self.zlims = zlims
        self.readImageData(isaMask=self.isaMask)
        self.mask = None
        self.maskeddata = None
        self.setFuncMask(funcmask, maskdata=False)
        self.setGeomMask(geommask, maskdata=False)
        self.maskData()
        self.updateStats()
        self.space = "unspecified"
        if (self.header["sform_code"] == 4) or (self.header["qform_code"] == 4):
            if ((self.xdim == 61) and (self.ydim == 73) and (self.zdim == 61)) or (
                (self.xdim == 91) and (self.ydim == 109) and (self.zdim == 91)
            ):
                self.space = "MNI152"
            else:
                self.space = "MNI152NLin2009cAsym"
        if self.header["sform_code"] != 0:
            self.affine = self.header.get_sform()
        elif self.header["qform_code"] != 0:
            self.affine = self.header.get_qform()
        else:
            self.affine = self.header.get_base_affine()
        self.invaffine = np.linalg.inv(self.affine)
        self.xpos = 0
        self.ypos = 0
        self.zpos = 0
        self.tpos = 0
        self.xcoord = 0.0
        self.ycoord = 0.0
        self.zcoord = 0.0
        self.tcoord = 0.0

        if self.verbose:
            print(
                "imagedata initialized:",
                self.name,
                self.filename,
                self.minval,
                self.dispmin,
                self.dispmax,
                self.maxval,
            )
            self.summarize()

    def duplicate(self, newname, newlabel):
        return imagedataset(
            newname,
            self.filename,
            self.namebase,
            label=newlabel,
            lut_state=self.lut_state,
        )

    def updateStats(self):
        if self.verbose:
            print("entering updateStats")
        if self.mask is None:
            calcmaskeddata = self.maskeddata
        else:
            calcmaskeddata = self.maskeddata[np.where(self.mask > 0.0)]
        self.numstatvoxels = len(calcmaskeddata)
        self.minval = calcmaskeddata.min()
        self.maxval = calcmaskeddata.max()
        (
            self.robustmin,
            self.pct25,
            self.pct50,
            self.pct75,
            self.robustmax,
        ) = stats.getfracvals(calcmaskeddata, [0.02, 0.25, 0.5, 0.75, 0.98], nozero=False)
        self.dispmin = self.robustmin
        self.dispmax = self.robustmax
        self.dispmaxmag = np.max([self.dispmax, -self.dispmin])
        self.histy, self.histx = np.histogram(
            calcmaskeddata, bins=np.linspace(self.minval, self.maxval, 200)
        )
        self.quartiles = [self.pct25, self.pct50, self.pct75]
        if self.verbose:
            print(
                self.name,
                ":",
                self.minval,
                self.maxval,
                self.robustmin,
                self.robustmax,
                self.quartiles,
            )

    def setData(self, data, isaMask=False):
        if self.verbose:
            print("entering setData")
        self.data = data.copy()
        if isaMask:
            self.data[np.where(self.data < 0.5)] = 0.0
            self.data[np.where(self.data > 0.5)] = 1.0
        self.updateStats()

    def setFuncMask(self, funcmask, maskdata=True):
        self.funcmask = funcmask
        if self.funcmask is None:
            if self.tdim == 1:
                self.funcmask = 1.0 + 0.0 * self.data
            else:
                self.funcmask = 1.0 + 0.0 * self.data[:, :, :, 0]
        else:
            self.funcmask = funcmask.copy()
        if self.verbose:
            print("setFuncMask - mask dims", self.funcmask.shape)
        if maskdata:
            self.maskData()

    def setFuncMaskByThresh(self, threshval=2.3, maskdata=True):
        self.funcmask = np.where(np.fabs(self.data) > threshval, 1.0, 0.0)
        if maskdata:
            self.maskData()

    def setGeomMask(self, geommask, maskdata=True):
        self.geommask = geommask
        if self.geommask is None:
            self.geommask = 1.0 + 0.0 * self.data
        else:
            self.geommask = geommask.copy()
        if self.verbose:
            print("setGeomMask - mask dims", self.geommask.shape)
        if maskdata:
            self.maskData()

    def maskData(self):
        if len(self.funcmask.shape) == 3:
            self.mask = self.funcmask * self.geommask
        else:
            self.mask = self.funcmask * self.geommask[:, :, :, None]
        if self.verbose:
            if self.mask is None:
                print("self.mask is None")
            if self.funcmask is None:
                print("self.funcmask is None")
            if self.geommask is None:
                print("self.geommask is None")
        self.maskeddata = self.data.copy()
        self.maskeddata[np.where(self.mask < 0.5)] = 0.0
        self.updateStats()

    def readImageData(self, isaMask=False):
        if self.verbose:
            print("entering readImageData")
        self.nim, indata, self.header, self.dims, self.sizes = io.readfromnifti(self.filename)
        self.xdim, self.ydim, self.zdim, self.tdim = io.parseniftidims(self.dims)
        self.xsize, self.ysize, self.zsize, self.tr = io.parseniftisizes(self.sizes)
        if self.tdim > 1:
            if self.flipx:
                self.data = np.flip(
                    indata[
                        self.xlims[0] : self.xlims[1],
                        self.ylims[0] : self.ylims[1],
                        self.zlims[0] : self.zlims[1],
                        :,
                    ],
                    axis=0,
                )
            else:
                self.data = indata[
                    self.xlims[0] : self.xlims[1],
                    self.ylims[0] : self.ylims[1],
                    self.zlims[0] : self.zlims[1],
                    :,
                ]
        else:
            if self.flipx:
                self.data = np.flip(
                    indata[
                        self.xlims[0] : self.xlims[1],
                        self.ylims[0] : self.ylims[1],
                        self.zlims[0] : self.zlims[1],
                    ],
                    axis=0,
                )
            else:
                self.data = indata[
                    self.xlims[0] : self.xlims[1],
                    self.ylims[0] : self.ylims[1],
                    self.zlims[0] : self.zlims[1],
                ]
        self.xdim, self.ydim, self.zdim = (
            self.data.shape[0],
            self.data.shape[1],
            self.data.shape[2],
        )
        if isaMask:
            self.data[np.where(self.data < 0.5)] = 0.0
            self.data[np.where(self.data > 0.5)] = 1.0
        if self.verbose:
            print("imagedata data range:", np.min(self.data), np.max(self.data))
            print("header", self.header)
        self.toffset = self.header["toffset"]
        if self.verbose:
            print("imagedata dims:", self.xdim, self.ydim, self.zdim, self.tdim)
            print("imagedata sizes:", self.xsize, self.ysize, self.zsize, self.tr)
            print("imagedata toffset:", self.toffset)

    def real2tr(self, time):
        return np.round((time - self.toffset) / self.tr, 0)

    def tr2real(self, tpos):
        return self.toffset + self.tr * tpos

    def real2vox(self, xcoord, ycoord, zcoord, time):
        x, y, z = apply_affine(self.invaffine, [xcoord, ycoord, zcoord])
        t = self.real2tr(time)
        return (
            int(np.round(x, 0)),
            int(np.round(y, 0)),
            int(np.round(z, 0)),
            int(np.round(t, 0)),
        )

    def vox2real(self, xpos, ypos, zpos, tpos):
        return np.concatenate(
            (apply_affine(self.affine, [xpos, ypos, zpos]), [self.tr2real(tpos)]),
            axis=0,
        )

    def setXYZpos(self, xpos, ypos, zpos):
        self.xpos = int(xpos)
        self.ypos = int(ypos)
        self.zpos = int(zpos)

    def setTpos(self, tpos):
        if tpos > self.tdim - 1:
            self.tpos = int(self.tdim - 1)
        else:
            self.tpos = int(tpos)

    def getFocusVal(self):
        if self.tdim > 1:
            return self.maskeddata[self.xpos, self.ypos, self.zpos, self.tpos]
        else:
            return self.maskeddata[self.xpos, self.ypos, self.zpos]

    def setTR(self, trval):
        self.tr = trval

    def settoffset(self, toffset):
        self.toffset = toffset

    def setLUT(self, lut_state):
        self.lut_state = lut_state
        self.gradient.restoreState(lut_state)
        self.theLUT = self.gradient.getLookupTable(512, alpha=True)

        self.ry_gradient.restoreState(cm.redyellow_state)
        self.theRedyellowLUT = self.ry_gradient.getLookupTable(512, alpha=True)

        self.blb_gradient.restoreState(cm.bluelightblue_state)
        self.theBluelightblueLUT = self.blb_gradient.getLookupTable(512, alpha=True)

    def summarize(self):
        print()
        print("imagedata name:       ", self.name)
        print("    label:            ", self.label)
        print("    filename:         ", self.filename)
        print("    namebase:         ", self.namebase)
        print("    xdim:             ", self.xdim)
        print("    ydim:             ", self.ydim)
        print("    zdim:             ", self.zdim)
        print("    tdim:             ", self.tdim)
        print("    space:            ", self.space)
        print("    toffset:          ", self.toffset)
        print("    tr:               ", self.tr)
        print("    min:              ", self.minval)
        print("    max:              ", self.maxval)
        print("    robustmin:        ", self.robustmin)
        print("    robustmax:        ", self.robustmax)
        print("    dispmin:          ", self.dispmin)
        print("    dispmax:          ", self.dispmax)
        print("    xlims:            ", self.xlims)
        print("    ylims:            ", self.ylims)
        print("    zlims:            ", self.zlims)
        print("    data shape:       ", np.shape(self.data))
        print("    masked data shape:", np.shape(self.maskeddata))
        if self.geommask is None:
            print("    geometric mask not set")
        else:
            print("    geometric mask is set")
        if self.funcmask is None:
            print("    functional mask not set")
        else:
            print("    functional mask is set")
        if self.mask is None:
            print("    overall mask not set")
        else:
            print("    overall mask is set")


class LightboxItem(QtGui.QWidget):
    updated = QtCore.pyqtSignal()

    def __init__(
        self,
        fgmap,
        thisview,
        orientation="ax",
        enableMouse=False,
        button=None,
        winwidth=64,
        winheight=64,
        bgmap=None,
        verbose=False,
    ):
        QtGui.QWidget.__init__(self)
        self.fgmap = fgmap
        self.bgmap = bgmap
        self.thisview = thisview
        self.button = button
        self.verbose = verbose
        self.enableMouse = enableMouse
        self.xdim = self.fgmap.xdim  # this is the number of voxels along this axis
        self.ydim = self.fgmap.ydim  # this is the number of voxels along this axis
        self.zdim = self.fgmap.zdim  # this is the number of voxels along this axis
        self.tdim = self.fgmap.tdim  # this is the number of voxels along this axis
        self.xsize = self.fgmap.xsize  # this is the mapping between voxel and physical space
        self.ysize = self.fgmap.ysize  # this is the mapping between voxel and physical space
        self.zsize = self.fgmap.zsize  # this is the mapping between voxel and physical space
        self.xfov = self.xdim * self.xsize
        self.yfov = self.ydim * self.ysize
        self.zfov = self.zdim * self.zsize
        self.xpos = int(self.xdim // 2)
        self.ypos = int(self.ydim // 2)
        self.zpos = int(self.zdim // 2)
        self.tpos = int(0)
        self.orientation = orientation
        self.forcerecalc = False

        self.thresh = 2.3
        self.windowaspectpix = 0.0
        self.winwidth = winwidth
        self.winheight = winheight

        self.numperrow = 1
        self.numpercol = 1

        self.setorient(self.orientation)

        if self.verbose:
            print("LightboxItem intialization:")
            print("    Dimensions:", self.xdim, self.ydim, self.zdim)
            print("    Voxel sizes:", self.xsize, self.ysize)
            print("    FOVs:", self.xfov, self.yfov)
            print(
                "    maxfov, winwidth, winheight:",
                self.maxfov,
                self.winwidth,
                self.winheight,
            )
            print("    scale factors:", self.hscale, self.vscale)
        self.buttonisdown = False

        self.thisview.setBackground(None)
        self.thisview.setRange(padding=0.02)
        self.thisview.ci.layout.setContentsMargins(0, 0, 0, 0)
        self.thisview.ci.layout.setSpacing(5)

        (
            self.thisviewposwin,
            self.thisviewnegwin,
            self.thisviewbgwin,
            self.thislabel,
            self.thisviewbox,
        ) = newViewWindow(
            self.thisview,
            self.numperrow * self.hdim,
            self.numpercol * self.vdim,
            enableMouse=self.enableMouse,
        )
        self.resetWinProps()

        if self.enableMouse:
            # self.thisviewbox.keyPressEvent = self.handlekey
            self.thisviewbox.mousePressEvent = self.handleclick
            self.thisviewbox.mouseMoveEvent = self.handlemousemove
            self.thisviewbox.mouseReleaseEvent = self.handlemouseup

        self.enableView()
        self.updateAllViews()

    def getviewinfo(self):
        return (
            self.thisview,
            self.thisviewposwin,
            self.thisviewnegwin,
            self.thisviewbgwin,
            self.thislabel,
            self.thisviewbox,
        )

    def setviewinfo(self, theinfo):
        self.thisview = theinfo[0]
        self.thisviewposwin = theinfo[1]
        self.thisviewnegwin = theinfo[2]
        self.thisviewbgwin = theinfo[3]
        self.thislabel = theinfo[4]
        self.thisviewbox = theinfo[5]

    def setorient(self, orientation):
        self.orientation = orientation
        if self.orientation == "ax":
            self.hdim = self.xdim
            self.hfov = self.xfov
            self.hsize = self.xsize
            self.vdim = self.ydim
            self.vfov = self.yfov
            self.vsize = self.ysize
            self.slicedim = self.zdim
        elif self.orientation == "cor":
            self.hdim = self.xdim
            self.hfov = self.xfov
            self.hsize = self.xsize
            self.vdim = self.zdim
            self.vfov = self.zfov
            self.vsize = self.zsize
            self.slicedim = self.ydim
        elif self.orientation == "sag":
            self.hdim = self.ydim
            self.hfov = self.yfov
            self.hsize = self.ysize
            self.vdim = self.zdim
            self.vfov = self.zfov
            self.vsize = self.zsize
            self.slicedim = self.xdim
        else:
            print("illegal orientation")

        self.startslice = 0
        self.slicestep = 1
        self.endslice = self.slicedim
        self.slicelist = range(self.startslice, self.endslice, self.slicestep)
        self.numslices = len(self.slicelist)

        self.maxfov = np.max([self.hfov, self.vfov])
        self.forcerecalc = True

        self.getWinProps()
        self.tiledbackground = None
        self.tiledmasks = {}
        self.tiledforegrounds = {}

    def hvox2pix(self, hpos):
        return int(np.round(self.offseth + self.impixpervoxh * hpos))

    def vvox2pix(self, vpos):
        return int(np.round(self.offsetv + self.impixpervoxv * vpos))

    """def zvox2pix(self, zpos):
        return int(np.round(self.offsetz + self.impixpervoxz * zpos))"""

    def hpix2vox(self, hpix):
        thepos = (hpix - self.offseth) / self.impixpervoxh
        if thepos > self.hdim - 1:
            thepos = self.hdim - 1
        if thepos < 0:
            thepos = 0
        return int(np.round(thepos))

    def vpix2vox(self, vpix):
        thepos = (vpix - self.offsetv) / self.impixpervoxv
        if thepos > self.vdim - 1:
            thepos = self.vdim - 1
        if thepos < 0:
            thepos = 0
        return int(np.round(thepos))

    """def zpix2vox(self, zpix):
        thepos = (zpix - self.offsetz) / self.impixpervoxz
        if thepos > self.zdim - 1:
            thepos = self.zdim - 1
        if thepos < 0:
            thepos = 0
        return int(np.round(thepos))"""

    def optmatrix(self, horizontalmm, verticalmm, targetaspectratio, verbose=False):
        # first find all the combinations of x and y that will minimally hold all the images
        numrows = np.arange(2, int(self.numslices // 2), 1, dtype=np.int)
        numcols = numrows * 0
        for i in range(len(numcols)):
            numcols[i] = int(np.ceil(self.numslices / numrows[i]))

        # now calculate the aspect ratios of all of these combinations
        theaspectratios = (horizontalmm * numcols) / (verticalmm * numrows)
        theindex = np.argmin(np.fabs(theaspectratios - targetaspectratio))
        if verbose:
            for i in range(len(numcols)):
                if i == theindex:
                    print(
                        "columns, rows, positions, numslices, aspect, target:",
                        numcols[i],
                        numrows[i],
                        numcols[i] * numrows[i],
                        theaspectratios[i],
                        targetaspectratio,
                        "***",
                    )
                else:
                    print(
                        "columns, rows, positions, aspect, target:",
                        numcols[i],
                        numrows[i],
                        numcols[i] * numrows[i],
                        theaspectratios[i],
                        targetaspectratio,
                    )
        if verbose:
            print(
                "optmatrix: horizontalmm, verticalmm, thisaspectratio, targetapectratio, numcols, numrows:",
                horizontalmm,
                verticalmm,
                theaspectratios[theindex],
                targetaspectratio,
                numcols[theindex],
                numrows[theindex],
            )
        return numcols[theindex], numrows[theindex]

    def getWinProps(self):
        self.winwidth = self.thisview.frameGeometry().width()
        self.winheight = self.thisview.frameGeometry().height()
        self.impixpervoxh = self.winwidth * (self.hfov / self.maxfov) / self.hdim
        self.impixpervoxv = self.winheight * (self.vfov / self.maxfov) / self.vdim
        self.offseth = self.winwidth * (0.5 - self.hfov / (2.0 * self.maxfov))
        self.offsetv = self.winheight * (0.5 - self.vfov / (2.0 * self.maxfov))
        self.offseth = self.winwidth * (0.5 - self.hfov / (2.0 * self.maxfov))

        newaspectpix = (1.0 * self.winwidth) / self.winheight
        if (newaspectpix != self.windowaspectpix) or self.forcerecalc:
            self.aspectchanged = True
            self.numperrow, self.numpercol = self.optmatrix(
                self.hdim * self.hsize, self.vdim * self.vsize, newaspectpix
            )
            self.imwidthpix = self.numperrow * self.hdim
            self.imheightpix = self.numpercol * self.vdim
            self.imwidthmm = self.imwidthpix * self.hsize
            self.imheightmm = self.imheightpix * self.vsize
            self.hscale = self.imwidthmm / self.winwidth
            self.vscale = self.imheightmm / self.winheight
            self.forcerecalc = False
        else:
            self.aspectchanged = False
        self.windowaspectpix = newaspectpix
        if self.verbose:
            print(
                "current lightbox dimensions, aspect ratio, changed:",
                self.winwidth,
                self.winheight,
                self.windowaspectpix,
                self.aspectchanged,
            )

    def printWinProps(self):
        print("\nLightbox window properties:")
        print("\tOrientation:", self.orientation)
        print("\thdim, vdim:", self.hdim, self.vdim)
        print("\thsize, vsize:", self.hsize, self.vsize)
        print("\thfov, vfov:", self.hfov, self.vfov)

        print("\tnumperrow, numpercol:", self.numperrow, self.numpercol)
        print(
            "\twinwidth, winheight, windowaspectpix, aspectchanged:",
            self.winwidth,
            self.winheight,
            self.windowaspectpix,
            self.aspectchanged,
        )
        print("\timwidthpix, imheightpix:", self.imwidthpix, self.imheightpix)
        print("\timwidthmm, imheightmm:", self.imwidthmm, self.imheightmm)
        print("\thscale, vscale:", self.hscale, self.vscale)

    def resetWinProps(self):
        self.tiledbackground = None
        self.tiledmasks = {}
        self.tiledforegrounds = {}
        if self.hscale > self.vscale:
            voffset = self.imheightpix * (1.0 - self.hscale / self.vscale) / 2.0
            if self.verbose:
                print("image needs vertical padding")
                print("voffset is:", voffset)
            self.thisviewbox.setRange(
                QtCore.QRectF(
                    0,
                    voffset,
                    self.numperrow * self.hdim,
                    (self.hscale / self.vscale) * self.numpercol * self.vdim,
                ),
                padding=0.0,
            )
        else:
            hoffset = self.imwidthpix * (1.0 - self.vscale / self.hscale) / 2.0
            if self.verbose:
                print("image needs horizontal padding")
                print("hoffset is:", hoffset)
            self.thisviewbox.setRange(
                QtCore.QRectF(
                    hoffset,
                    0,
                    (self.vscale / self.hscale) * self.numperrow * self.hdim,
                    self.numpercol * self.vdim,
                ),
                padding=0.0,
            )
        self.thisviewbox.setAspectLocked(lock=False, ratio=(self.vsize / self.hsize))
        # self.thisviewbox.setAspectLocked(lock=False, ratio=(self.imheightmm / self.imwidthmm))
        self.aspectchanged = True

    def tileSlices(self, inputimage):
        tiledimage = np.zeros((self.numperrow * self.hdim, self.numpercol * self.vdim))
        for whichslice in range(np.min([self.numslices, self.numperrow * self.numpercol])):
            hpos = (self.numperrow - (whichslice % self.numperrow) - 1) * self.hdim
            vpos = (int(whichslice // self.numperrow)) * self.vdim
            if self.orientation == "ax":
                tiledimage[hpos : hpos + self.hdim, vpos : vpos + self.vdim] = inputimage[
                    :, :, self.slicelist[whichslice]
                ]
            elif self.orientation == "cor":
                tiledimage[hpos : hpos + self.hdim, vpos : vpos + self.vdim] = inputimage[
                    :, self.slicelist[whichslice], :
                ]
            elif self.orientation == "sag":
                tiledimage[hpos : hpos + self.hdim, vpos : vpos + self.vdim] = inputimage[
                    self.slicelist[whichslice], :, :
                ]
            else:
                print("illegal orientation in tileSlices")

        return tiledimage

    def updateAllViews(self):
        self.getWinProps()
        if self.aspectchanged:
            self.resetWinProps()
        try:
            thisviewdata = self.tiledforegrounds[str(self.tpos)]
            if self.verbose:
                print("using precached tiled foreground image")
        except KeyError:
            if self.verbose:
                print("tiling foreground image")
            self.tiledforegrounds[str(self.tpos)] = self.tileSlices(
                self.fgmap.maskeddata[:, :, :, self.tpos]
            )
            thisviewdata = self.tiledforegrounds[str(self.tpos)]

        if self.bgmap is None:
            thisviewbg = None
        else:
            if self.tiledbackground is None:
                if self.verbose:
                    print("tiling background image")
                self.tiledbackground = self.tileSlices(self.bgmap.maskeddata[:, :, :])
            else:
                if self.verbose:
                    print("using precached tiled background image")
            thisviewbg = self.tiledbackground

        self.updateOneView(
            thisviewdata,
            thisviewbg,
            self.thisviewposwin,
            self.thisviewnegwin,
            self.thisviewbgwin,
        )

    def updateOneView(self, data, background, thefgposwin, thefgnegwin, thebgwin):
        if self.verbose:
            print(
                "setting min and max to",
                -self.fgmap.dispmaxmag,
                self.fgmap.dispmaxmag,
                "(",
                self.fgmap.numstatvoxels,
                ")",
            )
        impos = self.applyLUT(
            data,
            np.where(data >= self.thresh, 1, 0),
            self.fgmap.theRedyellowLUT,
            self.thresh,
            self.fgmap.dispmaxmag,
        )
        thefgposwin.setImage(impos.astype("float"))
        imneg = self.applyLUT(
            data,
            np.where(data <= -self.thresh, 1, 0),
            self.fgmap.theBluelightblueLUT,
            self.thresh,
            self.fgmap.dispmaxmag,
        )
        thefgnegwin.setImage(imneg.astype("float"))
        if background is not None:
            thebgwin.setImage(background.astype("float"), autoLevels=True)

    def setLabel(self, label, color):
        if self.verbose:
            print("entering setLabel")
        self.thislabel.setText(label)
        self.thislabel.setColor(color)

    def setMap(self, themap):
        self.fgmap = themap
        self.tdim = self.fgmap.tdim

    def enableView(self):
        if self.button is not None:
            self.button.setText(self.fgmap.label)
            self.button.setDisabled(False)
            self.button.show()
        self.thisview.show()

    def applyLUT(self, theimage, mask, theLUT, dispmin, dispmax):
        offset = dispmin
        if dispmax - dispmin > 0:
            scale = len(theLUT) / (dispmax - dispmin)
        else:
            scale = 0.0
        scaleddata = np.rint((theimage - offset) * scale).astype("int32")
        scaleddata[np.where(scaleddata < 0)] = 0
        scaleddata[np.where(scaleddata > (len(theLUT) - 1))] = len(theLUT) - 1
        mappeddata = theLUT[scaleddata]
        mappeddata[:, :, 3][np.where(mask < 1)] = 0
        return mappeddata

    def updateCursors(self):
        xpix = self.hvox2pix(self.xpos)
        ypix = self.vvox2pix(self.ypos)
        zpix = self.zvox2pix(self.zpos)
        self.thisviewvLine.setValue(xpix)
        self.thisviewhLine.setValue(ypix)

    def handlemouseup(self, event):
        self.buttonisdown = False
        self.updateCursors()
        self.updateAllViews()

    def handlemousemove(self, event):
        if self.buttonisdown:
            self.xpos = self.xpix2vox(event.pos().x() - 1)
            self.ypos = self.ypix2vox(self.winheight - event.pos().y() + 1)
            self.updateAllViews()
            self.updated.emit()

    def handlekey(self, event):
        if self.verbose:
            print(event)
        self.updateAllViews()
        self.updated.emit()

    def handleclick(self, event):
        self.xpos = self.xpix2vox(event.pos().x() - 1)
        self.ypos = self.ypix2vox(self.winheight - event.pos().y() + 1)
        self.buttonisdown = True
        self.updateAllViews()
        self.updated.emit()

    def handlerefresh(self, event):
        if self.verbose:
            print("refreshing viewbox range")
        self.getWinProps()
        self.resetWinProps()
        self.updateAllViews

    def setXYZpos(self, xpos, ypos, zpos, emitsignal=True):
        self.xpos = int(xpos)
        self.ypos = int(ypos)
        self.zpos = int(zpos)
        self.updateAllViews()
        if emitsignal:
            self.updated.emit()

    def setTpos(self, tpos, emitsignal=True):
        if tpos > self.tdim - 1:
            self.tpos = int(self.tdim - 1)
        else:
            self.tpos = int(tpos)

        self.updateAllViews()
        if emitsignal:
            self.updated.emit()

    def getFocusVal(self):
        if self.tdim > 1:
            return self.fgmap.maskeddata[self.xpos, self.ypos, self.zpos, self.tpos]
        else:
            return self.fgmap.maskeddata[self.xpos, self.ypos, self.zpos]

    def saveandcomposite(self, fg_img, bg_img, name, savedir, scalefach, scalefacv):
        if PILexists:
            print("using PIL to save ", name)
            fgname = os.path.join(savedir, name + "_foreground.png")
            bgname = os.path.join(savedir, name + "_background.png")
            compositename = os.path.join(savedir, name + ".jpg")
            fg_img.save(fgname)
            bg_img.save(bgname)
            background = Image.open(bgname)
            foreground = Image.open(fgname)
            print(foreground.getbands())
            background.paste(foreground, None, foreground)
            flipped = background.transpose(Image.FLIP_TOP_BOTTOM)
            print("scaling")
            basesize = 512
            hsize = int(basesize / scalefach)
            vsize = int(basesize / scalefacv)
            print("scaling to ", hsize, vsize)
            flipped = flipped.resize((hsize, vsize), Image.ANTIALIAS)
            print("saving to ", compositename)
            flipped.save(compositename, "jpeg")
            print("cleaning")
            os.remove(fgname)
            os.remove(bgname)
        else:
            print("saving ", name)
            fg_img.save(os.path.join(savedir, name + "_fg.png"))
            bg_img.save(os.path.join(savedir, name + "_bg.png"))

    def saveDisp(self):
        mydialog = QtGui.QFileDialog()
        options = mydialog.Options()
        thedir = str(
            mydialog.getExistingDirectory(options=options, caption="Image output directory")
        )
        if self.verbose:
            print("thedir=", thedir)
        thename = self.fgmap.namebase + self.fgmap.name
        self.saveandcomposite(
            self.thisviewposwin,
            self.thisviewbgwin,
            thename,
            thedir,
            self.impixpervoxh,
            self.impixpervoxv,
        )
        with open(os.path.join(thedir, thename + "_lims.txt"), "w") as FILE:
            FILE.writelines(str(self.fgmap.dispmin) + "\t" + str(self.fgmap.dispmax))
            # img_colorbar.save(thedir + self.map.name + '_colorbar.png')

    def summarize(self):
        if self.fgmap is not None:
            # print('LightboxItem[', self.map.name, ']: map is set')
            pass
