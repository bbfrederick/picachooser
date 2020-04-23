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

from __future__ import print_function, division

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
import os

try:
    from PIL import Image

    PILexists = True
except ImportError:
    PILexists = False


import PICAchooser.io as io
import rapidtide.stats as tide_stats
import PICAchooser.colormaps as cm


def newColorbar(view, left, top, impixpervoxx, impixpervoxy, imgsize):
    cb_xdim = imgsize // 10
    cb_ydim = imgsize
    theviewbox = pg.ViewBox(enableMouse=False)
    theviewbox.setRange(QtCore.QRectF(0, 0, cb_xdim, cb_ydim),
                        xRange=(0, cb_xdim - 1), yRange=(0, cb_ydim - 1), padding=0.0,
                        disableAutoRange=True)
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

def resetRange(theviewbox, imgxsize, imgysize):
    theviewbox.setRange(QtCore.QRectF(0, 0, imgxsize, imgysize), padding=0., disableAutoRange=False)


def newViewWindow(view, left, top, imgxsize, imgysize, enableMouse=False):
    #theviewbox = view.addViewBox(enableMouse=enableMouse, enableMenu=False, lockAspect=1.0)
    theviewbox = view.addViewBox(enableMouse=False, enableMenu=False)
    theviewbox.setAspectLocked()
    theviewbox.setRange(QtCore.QRectF(0, 0, imgxsize, imgysize), padding=0.0, disableAutoRange=False)
    theviewbox.setBackgroundColor([50, 50, 50])

    theviewfgposwin = pg.ImageItem()
    theviewbox.addItem(theviewfgposwin)
    theviewfgposwin.setZValue(10)
    #theviewfgposwin.translate(left, top)

    theviewfgnegwin = pg.ImageItem()
    theviewbox.addItem(theviewfgnegwin)
    theviewfgnegwin.setZValue(5)
    #theviewfgnegwin.translate(left, top)

    theviewbgwin = pg.ImageItem()
    theviewbox.addItem(theviewbgwin)
    theviewbgwin.setZValue(0)
    #theviewbgwin.translate(left, top)

    thelabel = pg.TextItem(anchor=(0.0,1.0))
    theviewbox.addItem(thelabel)
    thelabel.setZValue(20)
    #thelabel.translate(0, -imgysize)

    return theviewfgposwin, theviewfgnegwin, theviewbgwin, thelabel, theviewbox


class imagedataset:
    "Store and image dataset and some information about it"

    def __init__(self, name, filename, namebase,
                 mask=None,
                 label=None,
                 isaMask=False,
                 geommask=None,
                 funcmask=None,
                 lut_state=cm.gray_state,
                 verbose=False):
        self.verbose = verbose
        self.name = name
        if label is None:
            self.label = name
        else:
            self.label = label
        self.filename = filename
        self.namebase = namebase
        if self.verbose:
            print('reading map ', self.name, ' from ', self.filename, '...')
        self.isaMask = isaMask
        self.gradient = pg.GradientWidget(orientation='right', allowAdd=True)
        self.ry_gradient = pg.GradientWidget(orientation='right', allowAdd=True)
        self.blb_gradient = pg.GradientWidget(orientation='right', allowAdd=True)
        self.lut_state = lut_state
        self.theLUT = None
        self.theRedyellowLUT = None
        self.theBluelightblueLUT = None
        self.setLUT(self.lut_state)
        self.readImageData(isaMask=self.isaMask)
        self.mask = None
        self.maskeddata = None
        self.setFuncMask(funcmask, maskdata=False)
        self.setGeomMask(geommask, maskdata=False)
        self.maskData()
        self.updateStats()
        self.space = 'unspecified'
        if (self.header['sform_code'] == 4) or (self.header['qform_code'] == 4):
            if ((self.xdim == 61) and (self.ydim == 73) and (self.zdim == 61)) or \
                ((self.xdim == 91) and (self.ydim == 109) and (self.zdim == 91)):
                self.space = "MNI152"
            else:
                self.space = "MNI152NLin2009cAsym"
        if self.header['sform_code'] != 0:
            self.affine = self.header.get_sform()
        elif self.header['qform_code'] != 0:
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
            print('imagedata initialized:', self.name, self.filename, self.minval, self.dispmin, self.dispmax,
                  self.maxval)
            self.summarize()

    def duplicate(self, newname, newlabel):
        return imagedataset(newname, self.filename, self.namebase,
                       label=newlabel,
                       lut_state=self.lut_state)

    def updateStats(self):
        if self.verbose:
            print('entering updateStats')
        if self.mask is None:
            calcmaskeddata = self.maskeddata
        else:
            calcmaskeddata = self.maskeddata[np.where(self.mask > 0.0)]
        self.numstatvoxels = len(calcmaskeddata)
        self.minval = calcmaskeddata.min()
        self.maxval = calcmaskeddata.max()
        self.robustmin, self.pct25, self.pct50, self.pct75, self.robustmax = tide_stats.getfracvals(calcmaskeddata, [0.02, 0.25, 0.5, 0.75, 0.98], nozero=False)
        self.dispmin = self.robustmin
        self.dispmax = self.robustmax
        self.dispmaxmag = np.max([self.dispmax, -self.dispmin])
        self.histy, self.histx = np.histogram(calcmaskeddata,
                                              bins=np.linspace(self.minval, self.maxval, 200))
        self.quartiles = [self.pct25, self.pct50, self.pct75]
        print(self.name,':',self.minval, self.maxval, self.robustmin, self.robustmax, self.quartiles)

    def setData(self, data, isaMask=False):
        if self.verbose:
            print('entering setData')
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
        print('setFuncMask - mask dims', self.funcmask.shape)
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
        print('setGeomMask - mask dims', self.geommask.shape)
        if maskdata:
            self.maskData()


    def maskData(self):
        if len(self.funcmask.shape) == 3:
            self.mask = self.funcmask * self.geommask
        else:
            self.mask = self.funcmask * self.geommask[:, :, :, None]
        if self.mask is None:
            print('self.mask is None')
        if self.funcmask is None:
            print('self.funcmask is None')
        if self.geommask is None:
            print('self.geommask is None')
        self.maskeddata = self.data.copy()
        self.maskeddata[np.where(self.mask < 0.5)] = 0.0
        self.updateStats()


    def readImageData(self, isaMask=False):
        if self.verbose:
            print('entering readImageData')
        self.nim, self.data, self.header, self.dims, self.sizes = io.readfromnifti(self.filename)
        if isaMask:
            self.data[np.where(self.data < 0.5)] = 0.0
            self.data[np.where(self.data > 0.5)] = 1.0
        if self.verbose:
            print('imagedata data range:', np.min(self.data), np.max(self.data))
            print('header', self.header)
        self.xdim, self.ydim, self.zdim, self.tdim = \
            io.parseniftidims(self.dims)
        self.xsize, self.ysize, self.zsize, self.tr = \
            io.parseniftisizes(self.sizes)
        self.toffset = self.header['toffset']
        if self.verbose:
            print('imagedata dims:', self.xdim, self.ydim, self.zdim, self.tdim)
            print('imagedata sizes:', self.xsize, self.ysize, self.zsize, self.tr)
            print('imagedata toffset:', self.toffset)

    def real2tr(self, time):
        return np.round((time - self.toffset) / self.tr, 0)

    def tr2real(self, tpos):
        return self.toffset + self.tr * tpos

    def real2vox(self, xcoord, ycoord, zcoord, time):
        x, y, z = apply_affine(self.invaffine, [xcoord, ycoord, zcoord])
        t = self.real2tr(time)
        return int(np.round(x, 0)), int(np.round(y, 0)), int(np.round(z, 0)), int(np.round(t, 0))

    def vox2real(self, xpos, ypos, zpos, tpos):
        return np.concatenate((apply_affine(self.affine, [xpos, ypos, zpos]), [self.tr2real(tpos)]), axis=0)

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
        print('imagedata name:       ', self.name)
        print('    label:            ', self.label)
        print('    filename:         ', self.filename)
        print('    namebase:         ', self.namebase)
        print('    xdim:             ', self.xdim)
        print('    ydim:             ', self.ydim)
        print('    zdim:             ', self.zdim)
        print('    tdim:             ', self.tdim)
        print('    space:            ', self.space)
        print('    toffset:          ', self.toffset)
        print('    tr:               ', self.tr)
        print('    min:              ', self.minval)
        print('    max:              ', self.maxval)
        print('    robustmin:        ', self.robustmin)
        print('    robustmax:        ', self.robustmax)
        print('    dispmin:          ', self.dispmin)
        print('    dispmax:          ', self.dispmax)
        print('    data shape:       ', np.shape(self.data))
        print('    masked data shape:', np.shape(self.maskeddata))
        if self.geommask is None:
            print('    geometric mask not set')
        else:
            print('    geometric mask is set')
        if self.funcmask is None:
            print('    functional mask not set')
        else:
            print('    functional mask is set')
        if self.mask is None:
            print('    overall mask not set')
        else:
            print('    overall mask is set')



class LightboxItem(QtGui.QWidget):
    updated = QtCore.pyqtSignal()

    def __init__(self, fgmap, thisview, startslice=0, endslice=-1, slicestep=1,
                 enableMouse=False,
                 button=None,
                 imgxsize=64, imgysize=64,
                 bgmap=None,
                 verbose=False):
        QtGui.QWidget.__init__(self)
        self.fgmap = fgmap
        self.bgmap = bgmap
        self.thisview = thisview
        self.button = button
        self.verbose = verbose
        self.enableMouse = enableMouse
        self.xdim = self.fgmap.xdim     # this is the number of voxels along this axis
        self.ydim = self.fgmap.ydim     # this is the number of voxels along this axis
        self.zdim = self.fgmap.zdim     # this is the number of voxels along this axis
        self.tdim = self.fgmap.tdim     # this is the number of voxels along this axis
        self.xsize = self.fgmap.xsize   # this is the mapping between voxel and physical space
        self.ysize = self.fgmap.ysize   # this is the mapping between voxel and physical space
        self.startslice = startslice
        if endslice == -1:
            self.endslice = self.zdim
        else:
            self.endslice = endslice
        self.slicestep = slicestep
        self.imgxsize = imgxsize
        self.imgysize = imgysize
        self.xfov = self.xdim * self.xsize
        self.yfov = self.ydim * self.ysize
        self.xpos = int(self.xdim // 2)
        self.ypos = int(self.ydim // 2)
        self.zpos = int(self.zdim // 2)
        self.tpos = int(0)
        self.maxfov = np.max([self.xfov, self.yfov])
        self.impixpervoxx = self.imgxsize * (self.xfov / self.maxfov) / self.xdim
        self.impixpervoxy = self.imgysize * (self.yfov / self.maxfov) / self.ydim
        self.offsetx = self.imgxsize * (0.5 - self.xfov / (2.0 * self.maxfov))
        self.offsety = self.imgysize * (0.5 - self.yfov / (2.0 * self.maxfov))
        self.thresh = 2.3
        self.tiledbackground = None
        self.tiledmasks = {}
        self.tiledforegrounds = {}

        if self.verbose:
            print('OrthoImageItem intialization:')
            print('    Dimensions:', self.xdim, self.ydim, self.zdim)
            print('    Voxel sizes:', self.xsize, self.ysize)
            print('    FOVs:', self.xfov, self.yfov)
            print('    Maxfov, imgxsize, imgysize:', self.maxfov, self.imgxsize, self.imgysize)
            print('    Scale factors:', self.impixpervoxx, self.impixpervoxy, self.impixpervoxz)
            print('    Offsets:', self.offsetx, self.offsety, self.offsetz)
        self.buttonisdown = False

        self.thisview.setBackground(None)
        self.thisview.setRange(padding=0.0)
        self.thisview.ci.layout.setContentsMargins(0, 0, 0, 0)
        self.thisview.ci.layout.setSpacing(5)

        self.thisviewposwin, self.thisviewnegwin, self.thisviewbgwin, self.thislabel, self.thisviewbox = \
            newViewWindow(self.thisview,
                          0, 0,
                          self.imgxsize, self.imgysize,
                          enableMouse=self.enableMouse)
        if self.enableMouse:
            #self.thisviewbox.keyPressEvent = self.handlekey
            self.thisviewbox.mousePressEvent = self.handleclick
            self.thisviewbox.mouseMoveEvent = self.handlemousemove
            self.thisviewbox.mouseReleaseEvent = self.handlemouseup

        self.enableView()
        self.updateAllViews()

    def xvox2pix(self, xpos):
        return int(np.round(self.offsetx + self.impixpervoxx * xpos))


    def yvox2pix(self, ypos):
        return int(np.round(self.offsety + self.impixpervoxy * ypos))


    def zvox2pix(self, zpos):
        return int(np.round(self.offsetz + self.impixpervoxz * zpos))


    def xpix2vox(self, xpix):
        thepos = (xpix - self.offsetx) / self.impixpervoxx
        if thepos > self.xdim - 1:
            thepos = self.xdim - 1
        if thepos < 0:
            thepos = 0
        return int(np.round(thepos))


    def ypix2vox(self, ypix):
        thepos = (ypix - self.offsety) / self.impixpervoxy
        if thepos > self.ydim - 1:
            thepos = self.ydim - 1
        if thepos < 0:
            thepos = 0
        return int(np.round(thepos))


    def zpix2vox(self, zpix):
        thepos = (zpix - self.offsetz) / self.impixpervoxz
        if thepos > self.zdim - 1:
            thepos = self.zdim - 1
        if thepos < 0:
            thepos = 0
        return int(np.round(thepos))

    def optmatrix(self, numslices, xsize, ysize, targetaspectratio, verbose=False):
        # first find all the combinations of x and y that will minimally hold all the images
        xvals = np.arange(2, int(numslices // 2), 1, dtype=np.int)
        yvals = xvals * 0
        for i in range(len(yvals)):
            yvals[i] = int(np.ceil(numslices / xvals[i]))

        # now calculate the aspect ratios of all of these combinations
        theaspectratios = (xsize * xvals) / (ysize * yvals)
        theindex = np.argmin(np.fabs(theaspectratios - targetaspectratio))
        if verbose:
            for i in range(len(yvals)):
                if i == theindex:
                    print('x, y, aspect, target:', xvals[i], yvals[i], theaspectratios[i], targetaspectratio, '***')
                else:
                    print('x, y, aspect, target:', xvals[i], yvals[i], theaspectratios[i], targetaspectratio)
        return xvals[theindex], yvals[theindex]

    def tileSlices(self, inputimage):
        slicelist = range(self.startslice, self.endslice, self.slicestep)
        numslices = len(slicelist)
        theaspect = (self.xdim * 14.0) / (self.ydim * 9.0)
        numinx, numiny = self.optmatrix(numslices, self.xdim, self.ydim, theaspect)
        tiledimage = np.zeros((numinx * self.xdim, numiny * self.ydim))
        for whichslice in range(np.min([numslices, numinx * numiny])):
            xpos = (numinx - (whichslice % numinx) - 1) * self.xdim
            ypos = (int(whichslice // numinx)) * self.ydim
            tiledimage[xpos:xpos + self.xdim, ypos:ypos + self.ydim] = inputimage[:, :, slicelist[whichslice]]
        return tiledimage

    def updateAllViews(self):
        try:
            thisviewdata = self.tiledforegrounds[str(self.tpos)]
            if self.verbose:
                print('using precached tiled foreground image')
        except KeyError:
            if self.verbose:
                print('tiling foreground image')
            self.tiledforegrounds[str(self.tpos)] = self.tileSlices(self.fgmap.maskeddata[:, :, :, self.tpos])
            thisviewdata = self.tiledforegrounds[str(self.tpos)]

        if self.fgmap.mask is None:
            if self.verbose:
                print('fyi - the mask is none - using fake mask')
            thisviewmask = self.tiledforegrounds[str(self.tpos)] * 0.0 + 1.0
        else:
            try:
                thisviewmask = self.tiledmasks[str(self.tpos)]
                if self.verbose:
                    print('using precached tiled mask image')
            except KeyError:
                if self.verbose:
                    print('tiling mask image')
                self.tiledmasks[str(self.tpos)] = self.tileSlices(self.fgmap.mask[:, :, :, self.tpos])
                thisviewmask = self.tiledmasks[str(self.tpos)]

        if self.bgmap is None:
            thisviewbg = None
        else:
            if self.tiledbackground is None:
                if self.verbose:
                    print('tiling background image')
                self.tiledbackground = self.tileSlices(self.bgmap.maskeddata[:, :, :])
            else:
                if self.verbose:
                    print('using precached tiled background image')
            thisviewbg = self.tiledbackground

        self.updateOneView(thisviewdata, thisviewbg, self.thisviewposwin, self.thisviewnegwin, self.thisviewbgwin)


    def updateOneView(self, data, background, thefgposwin, thefgnegwin, thebgwin):
        if self.verbose:
            print('setting min and max to', -self.fgmap.dispmaxmag, self.fgmap.dispmaxmag, '(', self.fgmap.numstatvoxels, ')')
        impos = self.applyLUT(data, np.where(data >= self.thresh, 1, 0), self.fgmap.theRedyellowLUT, self.thresh, self.fgmap.dispmaxmag)
        thefgposwin.setImage(impos.astype('float'))
        imneg = self.applyLUT(data, np.where(data <= -self.thresh, 1, 0), self.fgmap.theBluelightblueLUT, self.thresh, self.fgmap.dispmaxmag)
        thefgnegwin.setImage(imneg.astype('float'))
        if background is not None:
            thebgwin.setImage(background.astype('float'), autoLevels=True)


    def setLabel(self, label, color):
        if self.verbose:
            print('entering setLabel')
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
        scaleddata = np.rint((theimage - offset) * scale).astype('int32')
        scaleddata[np.where(scaleddata < 0)] = 0
        scaleddata[np.where(scaleddata > (len(theLUT) - 1))] = len(theLUT) - 1
        mappeddata = theLUT[scaleddata]
        mappeddata[:, :, 3][np.where(mask < 1)] = 0
        return mappeddata


    def updateCursors(self):
        xpix = self.xvox2pix(self.xpos)
        ypix = self.yvox2pix(self.ypos)
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
            self.ypos = self.ypix2vox(self.imgysize - event.pos().y() + 1)
            self.updateAllViews()
            self.updated.emit()


    def handlekey(self, event):
        print(event)
        self.updateAllViews()
        self.updated.emit()


    def handleclick(self, event):
        self.xpos = self.xpix2vox(event.pos().x() - 1)
        self.ypos = self.ypix2vox(self.imgysize - event.pos().y() + 1)
        self.buttonisdown = True
        self.updateAllViews()
        self.updated.emit()


    def handlerefresh(self, event):
        print('refreshing viewbox range')
        resetRange(self.thisviewbox, self.imgxsize, self.imgysize)
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
            print('using PIL to save ', name)
            fgname = os.path.join(savedir, name + '_foreground.png')
            bgname = os.path.join(savedir, name + '_background.png')
            compositename = os.path.join(savedir, name + '.jpg')
            fg_img.save(fgname)
            bg_img.save(bgname)
            background = Image.open(bgname)
            foreground = Image.open(fgname)
            print(foreground.getbands())
            background.paste(foreground, None, foreground)
            flipped = background.transpose(Image.FLIP_TOP_BOTTOM)
            print('scaling')
            basesize = 512
            hsize = int(basesize / scalefach)
            vsize = int(basesize / scalefacv)
            print('scaling to ', hsize, vsize)
            flipped = flipped.resize((hsize, vsize), Image.ANTIALIAS)
            print('saving to ', compositename)
            flipped.save(compositename, 'jpeg')
            print('cleaning')
            os.remove(fgname)
            os.remove(bgname)
        else:
            print('saving ', name)
            fg_img.save(os.path.join(savedir, name + '_fg.png'))
            bg_img.save(os.path.join(savedir, name + '_bg.png'))


    def saveDisp(self):
        print('saving main window')
        mydialog = QtGui.QFileDialog()
        options = mydialog.Options()
        thedir = str(mydialog.getExistingDirectory(options=options, caption="Image output directory"))
        print('thedir=', thedir)
        thename = self.fgmap.namebase + self.fgmap.name
        self.saveandcomposite(self.thisviewposwin, self.thisviewbgwin, thename, thedir, self.impixpervoxx, self.impixpervoxy)
        with open(os.path.join(thedir, thename + '_lims.txt'), 'w') as FILE:
            FILE.writelines(str(self.fgmap.dispmin) + '\t' + str(self.fgmap.dispmax))
            # img_colorbar.save(thedir + self.map.name + '_colorbar.png')

    def summarize(self):
        if self.fgmap is not None:
            # print('LightboxItem[', self.map.name, ']: map is set')
            pass
