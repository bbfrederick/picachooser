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


import rapidtide.io as tide_io
import rapidtide.stats as tide_stats


g2y2r_state = {'ticks': [(0.5, (255, 255, 0, 255)), (1.0, (255, 0, 0, 255)), (0.0, (0, 255, 0, 255))], 'mode': 'rgb'}
ry_blb_state = {'ticks': [(0.0, (128, 128, 255, 255)), (0.499, (0, 0, 255)), (0.501, (128, 0, 0, 255)), (1.0, (255, 255, 0))], 'mode': 'rgb'}
gray_state = {'ticks': [(1.0, (255, 255, 255, 255)), (0.0, (0, 0, 0, 255))], 'mode': 'rgb'}
mask_state = {'ticks': [(0.0, (0, 0, 0, 255)), (1, (255, 255, 255, 0))], 'mode': 'rgb'}

thermal_state = {'ticks': [(0.3333, (185, 0, 0, 255)), (0.6666, (255, 220, 0, 255)),
                           (1, (255, 255, 255, 255)), (0, (0, 0, 0, 255))], 'mode': 'rgb'}
flame_state = {'ticks': [(0.2, (7, 0, 220, 255)), (0.5, (236, 0, 134, 255)), (0.8, (246, 246, 0, 255)),
                         (1.0, (255, 255, 255, 255)), (0.0, (0, 0, 0, 255))], 'mode': 'rgb'}
yellowy_state = {'ticks': [(0.0, (0, 0, 0, 255)), (0.2328863796753704, (32, 0, 129, 255)),
                           (0.8362738179251941, (255, 255, 0, 255)), (0.5257586450247, (115, 15, 255, 255)),
                           (1.0, (255, 255, 255, 255))], 'mode': 'rgb'}
bipolar_state = {'ticks': [(0.0, (0, 255, 255, 255)), (1.0, (255, 255, 0, 255)), (0.5, (0, 0, 0, 255)),
                           (0.25, (0, 0, 255, 255)), (0.75, (255, 0, 0, 255))], 'mode': 'rgb'}
spectrum_state = {'ticks': [(1.0, (255, 0, 255, 255)), (0.0, (255, 0, 0, 255))], 'mode': 'hsv'}
cyclic_state = {'ticks': [(0.0, (255, 0, 4, 255)), (1.0, (255, 0, 0, 255))], 'mode': 'hsv'}
greyclip_state = {'ticks': [(0.0, (0, 0, 0, 255)), (0.99, (255, 255, 255, 255)), (1.0, (255, 0, 0, 255))],
                  'mode': 'rgb'}
grey_state = {'ticks': [(0.0, (0, 0, 0, 255)), (1.0, (255, 255, 255, 255))], 'mode': 'rgb'}
viridis_state = {'ticks': [(0.000, (68, 1, 84)), (0.004, (68, 2, 86)), (0.008, (69, 4, 87)), (0.012, (69, 5, 89)),
                           (0.016, (70, 7, 90)), (0.020, (70, 8, 92)), (0.024, (70, 10, 93)), (0.027, (70, 11, 94)),
                           (0.031, (71, 13, 96)),
                           (0.035, (71, 14, 97)), (0.039, (71, 16, 99)), (0.043, (71, 17, 100)), (0.047, (71, 19, 101)),
                           (0.051, (72, 20, 103)),
                           (0.055, (72, 22, 104)), (0.059, (72, 23, 105)), (0.063, (72, 24, 106)),
                           (0.067, (72, 26, 108)), (0.071, (72, 27, 109)),
                           (0.075, (72, 28, 110)), (0.078, (72, 29, 111)), (0.082, (72, 31, 112)),
                           (0.086, (72, 32, 113)), (0.090, (72, 33, 115)),
                           (0.094, (72, 35, 116)), (0.098, (72, 36, 117)), (0.102, (72, 37, 118)),
                           (0.106, (72, 38, 119)), (0.110, (72, 40, 120)),
                           (0.114, (72, 41, 121)), (0.118, (71, 42, 122)), (0.122, (71, 44, 122)),
                           (0.125, (71, 45, 123)), (0.129, (71, 46, 124)),
                           (0.133, (71, 47, 125)), (0.137, (70, 48, 126)), (0.141, (70, 50, 126)),
                           (0.145, (70, 51, 127)), (0.149, (70, 52, 128)),
                           (0.153, (69, 53, 129)), (0.157, (69, 55, 129)), (0.161, (69, 56, 130)),
                           (0.165, (68, 57, 131)), (0.169, (68, 58, 131)),
                           (0.173, (68, 59, 132)), (0.176, (67, 61, 132)), (0.180, (67, 62, 133)),
                           (0.184, (66, 63, 133)), (0.188, (66, 64, 134)),
                           (0.192, (66, 65, 134)), (0.196, (65, 66, 135)), (0.200, (65, 68, 135)),
                           (0.204, (64, 69, 136)), (0.208, (64, 70, 136)),
                           (0.212, (63, 71, 136)), (0.216, (63, 72, 137)), (0.220, (62, 73, 137)),
                           (0.224, (62, 74, 137)), (0.227, (62, 76, 138)),
                           (0.231, (61, 77, 138)), (0.235, (61, 78, 138)), (0.239, (60, 79, 138)),
                           (0.243, (60, 80, 139)), (0.247, (59, 81, 139)),
                           (0.251, (59, 82, 139)), (0.255, (58, 83, 139)), (0.259, (58, 84, 140)),
                           (0.263, (57, 85, 140)), (0.267, (57, 86, 140)),
                           (0.271, (56, 88, 140)), (0.275, (56, 89, 140)), (0.278, (55, 90, 140)),
                           (0.282, (55, 91, 141)), (0.286, (54, 92, 141)),
                           (0.290, (54, 93, 141)), (0.294, (53, 94, 141)), (0.298, (53, 95, 141)),
                           (0.302, (52, 96, 141)), (0.306, (52, 97, 141)),
                           (0.310, (51, 98, 141)), (0.314, (51, 99, 141)), (0.318, (50, 100, 142)),
                           (0.322, (50, 101, 142)), (0.325, (49, 102, 142)),
                           (0.329, (49, 103, 142)), (0.333, (49, 104, 142)), (0.337, (48, 105, 142)),
                           (0.341, (48, 106, 142)), (0.345, (47, 107, 142)), (0.349, (47, 108, 142)),
                           (0.353, (46, 109, 142)), (0.357, (46, 110, 142)),
                           (0.361, (46, 111, 142)), (0.365, (45, 112, 142)), (0.369, (45, 113, 142)),
                           (0.373, (44, 113, 142)), (0.376, (44, 114, 142)),
                           (0.380, (44, 115, 142)), (0.384, (43, 116, 142)), (0.388, (43, 117, 142)),
                           (0.392, (42, 118, 142)), (0.396, (42, 119, 142)),
                           (0.400, (42, 120, 142)), (0.404, (41, 121, 142)), (0.408, (41, 122, 142)),
                           (0.412, (41, 123, 142)), (0.416, (40, 124, 142)),
                           (0.420, (40, 125, 142)), (0.424, (39, 126, 142)), (0.427, (39, 127, 142)),
                           (0.431, (39, 128, 142)), (0.435, (38, 129, 142)),
                           (0.439, (38, 130, 142)), (0.443, (38, 130, 142)), (0.447, (37, 131, 142)),
                           (0.451, (37, 132, 142)), (0.455, (37, 133, 142)),
                           (0.459, (36, 134, 142)), (0.463, (36, 135, 142)), (0.467, (35, 136, 142)),
                           (0.471, (35, 137, 142)), (0.475, (35, 138, 141)),
                           (0.478, (34, 139, 141)), (0.482, (34, 140, 141)), (0.486, (34, 141, 141)),
                           (0.490, (33, 142, 141)), (0.494, (33, 143, 141)),
                           (0.498, (33, 144, 141)), (0.502, (33, 145, 140)), (0.506, (32, 146, 140)),
                           (0.510, (32, 146, 140)), (0.514, (32, 147, 140)),
                           (0.518, (31, 148, 140)), (0.522, (31, 149, 139)), (0.525, (31, 150, 139)),
                           (0.529, (31, 151, 139)), (0.533, (31, 152, 139)),
                           (0.537, (31, 153, 138)), (0.541, (31, 154, 138)), (0.545, (30, 155, 138)),
                           (0.549, (30, 156, 137)), (0.553, (30, 157, 137)),
                           (0.557, (31, 158, 137)), (0.561, (31, 159, 136)), (0.565, (31, 160, 136)),
                           (0.569, (31, 161, 136)), (0.573, (31, 161, 135)),
                           (0.576, (31, 162, 135)), (0.580, (32, 163, 134)), (0.584, (32, 164, 134)),
                           (0.588, (33, 165, 133)), (0.592, (33, 166, 133)),
                           (0.596, (34, 167, 133)), (0.600, (34, 168, 132)), (0.604, (35, 169, 131)),
                           (0.608, (36, 170, 131)), (0.612, (37, 171, 130)),
                           (0.616, (37, 172, 130)), (0.620, (38, 173, 129)), (0.624, (39, 173, 129)),
                           (0.627, (40, 174, 128)), (0.631, (41, 175, 127)),
                           (0.635, (42, 176, 127)), (0.639, (44, 177, 126)), (0.643, (45, 178, 125)),
                           (0.647, (46, 179, 124)), (0.651, (47, 180, 124)),
                           (0.655, (49, 181, 123)), (0.659, (50, 182, 122)), (0.663, (52, 182, 121)),
                           (0.667, (53, 183, 121)), (0.671, (55, 184, 120)),
                           (0.675, (56, 185, 119)), (0.678, (58, 186, 118)), (0.682, (59, 187, 117)),
                           (0.686, (61, 188, 116)), (0.690, (63, 188, 115)),
                           (0.694, (64, 189, 114)), (0.698, (66, 190, 113)), (0.702, (68, 191, 112)),
                           (0.706, (70, 192, 111)), (0.710, (72, 193, 110)),
                           (0.714, (74, 193, 109)), (0.718, (76, 194, 108)), (0.722, (78, 195, 107)),
                           (0.725, (80, 196, 106)), (0.729, (82, 197, 105)),
                           (0.733, (84, 197, 104)), (0.737, (86, 198, 103)), (0.741, (88, 199, 101)),
                           (0.745, (90, 200, 100)), (0.749, (92, 200, 99)),
                           (0.753, (94, 201, 98)), (0.757, (96, 202, 96)), (0.761, (99, 203, 95)),
                           (0.765, (101, 203, 94)), (0.769, (103, 204, 92)),
                           (0.773, (105, 205, 91)), (0.776, (108, 205, 90)), (0.780, (110, 206, 88)),
                           (0.784, (112, 207, 87)), (0.788, (115, 208, 86)),
                           (0.792, (117, 208, 84)), (0.796, (119, 209, 83)), (0.800, (122, 209, 81)),
                           (0.804, (124, 210, 80)), (0.808, (127, 211, 78)),
                           (0.812, (129, 211, 77)), (0.816, (132, 212, 75)), (0.820, (134, 213, 73)),
                           (0.824, (137, 213, 72)), (0.827, (139, 214, 70)),
                           (0.831, (142, 214, 69)), (0.835, (144, 215, 67)), (0.839, (147, 215, 65)),
                           (0.843, (149, 216, 64)), (0.847, (152, 216, 62)),
                           (0.851, (155, 217, 60)), (0.855, (157, 217, 59)), (0.859, (160, 218, 57)),
                           (0.863, (162, 218, 55)), (0.867, (165, 219, 54)),
                           (0.871, (168, 219, 52)), (0.875, (170, 220, 50)), (0.878, (173, 220, 48)),
                           (0.882, (176, 221, 47)), (0.886, (178, 221, 45)),
                           (0.890, (181, 222, 43)), (0.894, (184, 222, 41)), (0.898, (186, 222, 40)),
                           (0.902, (189, 223, 38)), (0.906, (192, 223, 37)),
                           (0.910, (194, 223, 35)), (0.914, (197, 224, 33)), (0.918, (200, 224, 32)),
                           (0.922, (202, 225, 31)), (0.925, (205, 225, 29)),
                           (0.929, (208, 225, 28)), (0.933, (210, 226, 27)), (0.937, (213, 226, 26)),
                           (0.941, (216, 226, 25)), (0.945, (218, 227, 25)),
                           (0.949, (221, 227, 24)), (0.953, (223, 227, 24)), (0.957, (226, 228, 24)),
                           (0.961, (229, 228, 25)), (0.965, (231, 228, 25)),
                           (0.969, (234, 229, 26)), (0.973, (236, 229, 27)), (0.976, (239, 229, 28)),
                           (0.980, (241, 229, 29)), (0.984, (244, 230, 30)),
                           (0.988, (246, 230, 32)), (0.992, (248, 230, 33)), (0.996, (251, 231, 35)),
                           (1.000, (253, 231, 37))], 'mode': 'rgb'}


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
    theviewbox.setRange(QtCore.QRectF(0, 0, imgxsize, imgysize), padding=0., disableAutoRange=False)
    theviewbox.setBackgroundColor([50, 50, 50])

    theviewfgwin = pg.ImageItem()
    theviewbox.addItem(theviewfgwin)
    theviewfgwin.setZValue(10)
    theviewfgwin.translate(left, top)

    theviewbgwin = pg.ImageItem()
    theviewbox.addItem(theviewbgwin)
    theviewbgwin.setZValue(0)
    theviewbgwin.translate(left, top)

    return theviewfgwin, theviewbgwin, theviewbox


class imagedataset:
    "Store and image dataset and some information about it"

    def __init__(self, name, filename, namebase,
                 mask=None,
                 label=None,
                 isaMask=False,
                 lut_state=gray_state,
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
        self.readImageData(isaMask=self.isaMask)
        self.mask = mask
        self.maskeddata = None
        self.maskData()
        self.updateStats()
        self.gradient = pg.GradientWidget(orientation='right', allowAdd=True)
        self.lut_state = lut_state
        self.theLUT = None
        self.setLUT(self.lut_state)
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
        calcmaskeddata = self.maskeddata
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

    def setMask(self, mask):
        self.mask = mask
        self.maskData()

    def readImageData(self, isaMask=False):
        if self.verbose:
            print('entering readImageData')
        self.nim, self.data, self.header, self.dims, self.sizes = tide_io.readfromnifti(self.filename)
        if isaMask:
            self.data[np.where(self.data < 0.5)] = 0.0
            self.data[np.where(self.data > 0.5)] = 1.0
        if self.verbose:
            print('imagedata data range:', np.min(self.data), np.max(self.data))
            print('header', self.header)
        self.xdim, self.ydim, self.zdim, self.tdim = \
            tide_io.parseniftidims(self.dims)
        self.xsize, self.ysize, self.zsize, self.tr = \
            tide_io.parseniftisizes(self.sizes)
        self.toffset = self.header['toffset']
        if self.verbose:
            print('imagedata dims:', self.xdim, self.ydim, self.zdim, self.tdim)
            print('imagedata sizes:', self.xsize, self.ysize, self.zsize, self.tr)
            print('imagedata toffset:', self.toffset)

    def setLabel(self, label):
        if self.verbose:
            print('entering setLabel')
        self.label = label

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

    def maskData(self):
        self.maskeddata = self.data.copy()
        if self.mask is not None:
            self.maskeddata[np.where(self.mask < 0.5)] = 0.0
        self.updateStats()

    def setTR(self, trval):
        self.tr = trval

    def settoffset(self, toffset):
        self.toffset = toffset

    def setLUT(self, lut_state):
        self.lut_state = lut_state
        self.gradient.restoreState(lut_state)
        self.theLUT = self.gradient.getLookupTable(512, alpha=True)

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

        self.thisviewwin, self.thisviewbgwin, self.thisviewbox = \
            newViewWindow(self.thisview,
                          self.xdim, self.ydim,
                          self.imgxsize, self.imgysize,
                          enableMouse=self.enableMouse)
        if self.enableMouse:
            self.thisviewbox.keyPressEvent = self.handlekey
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
        print(self.startslice, self.endslice, self.slicestep)
        print('slicelist', slicelist)
        numslices = len(slicelist)
        theaspect = (self.xdim * 14.0) / (self.ydim * 9.0)
        numinx, numiny = self.optmatrix(numslices, self.xdim, self.ydim, theaspect)
        tiledimage = np.zeros((numinx * self.xdim, numiny * self.ydim))
        print('input image shape:', inputimage.shape)
        print('tiled image shape:', tiledimage.shape)
        for whichslice in range(np.min([numslices, numinx * numiny])):
            xpos = (numinx - (whichslice % numinx) - 1) * self.xdim
            ypos = (int(whichslice // numinx)) * self.ydim
            #print(whichslice, slicelist[whichslice], numinx, numiny, xpos, ypos)
            tiledimage[xpos:xpos + self.xdim, ypos:ypos + self.ydim] = inputimage[:, :, slicelist[whichslice]]
        return tiledimage

    def updateAllViews(self):
        #print('tiling foreground image')
        if self.tdim == 1:
            tiledfgimage = self.tileSlices(self.fgmap.maskeddata[:, :, :])
        else:
            tiledfgimage = self.tileSlices(self.fgmap.maskeddata[:, :, :, self.tpos])
        thisviewdata = tiledfgimage

        #print('tiling mask image')
        if self.fgmap.mask is None:
            thisviewmask = tiledfgimage * 0.0 + 1.0
        else:
            if len(self.fgmap.mask.shape) < 4:
                tiledmaskimage = self.tileSlices(self.fgmap.mask[:, :, :])
            else:
                tiledmaskimage = self.tileSlices(self.fgmap.mask[:, :, :, self.tpos])
            thisviewmask = tiledmaskimage

        #print('tiling background image')
        if self.bgmap is None:
            thisviewbg = None
        else:
            tiledbgimage = self.tileSlices(self.bgmap.maskeddata[:, :, :])
            thisviewbg = tiledbgimage

        self.updateOneView(thisviewdata, thisviewmask, thisviewbg, self.fgmap.theLUT, self.thisviewwin, self.thisviewbgwin)


    def updateOneView(self, data, mask, background, theLUT, thefgwin, thebgwin):
        print('setting min and max to', -self.fgmap.dispmaxmag, self.fgmap.dispmaxmag)
        im = self.applyLUT(data, mask, theLUT, -self.fgmap.dispmaxmag, self.fgmap.dispmaxmag)
        thefgwin.setImage(im.astype('float'), levels=(-self.fgmap.dispmaxmag, self.fgmap.dispmaxmag))
        if background is not None:
            thebgwin.setImage(background.astype('float'), autoLevels=True)


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
        self.saveandcomposite(self.thisviewwin, self.thisviewbgwin, thename, thedir, self.impixpervoxx, self.impixpervoxy)
        with open(os.path.join(thedir, thename + '_lims.txt'), 'w') as FILE:
            FILE.writelines(str(self.fgmap.dispmin) + '\t' + str(self.fgmap.dispmax))
            # img_colorbar.save(thedir + self.map.name + '_colorbar.png')

    def summarize(self):
        if self.fgmap is not None:
            # print('LightboxItem[', self.map.name, ']: map is set')
            pass
