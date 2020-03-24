# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------

# This file is part of Code_Saturne, a general-purpose CFD tool.
#
# Copyright (C) 1998-2020 EDF S.A.
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51 Franklin
# Street, Fifth Floor, Boston, MA 02110-1301, USA.

#-------------------------------------------------------------------------------

"""
This module defines the welcome page.
"""

#-------------------------------------------------------------------------------
# Library modules import
#-------------------------------------------------------------------------------

import os, logging

#-------------------------------------------------------------------------------
# Third-party modules
#-------------------------------------------------------------------------------

from code_saturne.Base.QtCore    import *
from code_saturne.Base.QtGui     import *
from code_saturne.Base.QtWidgets import *

#-------------------------------------------------------------------------------
# Application modules import
#-------------------------------------------------------------------------------

from code_saturne.model.Common import LABEL_LENGTH_MAX, GuiParam
from code_saturne.Base.QtPage import from_qvariant, to_text_string
from code_saturne.Base.QtPage import DoubleValidator, RegExpValidator
from code_saturne.Pages.SolverPropertyForm import Ui_SolverPropertyForm
from code_saturne.model.UserSolverModel import SolverPropertyModel

#-------------------------------------------------------------------------------
# log config
#-------------------------------------------------------------------------------

logging.basicConfig()
log = logging.getLogger("SolverPropertyView")
log.setLevel(GuiParam.DEBUG)


#-------------------------------------------------------------------------------
# Helper classes
#-------------------------------------------------------------------------------

class SolverPropValues():
    """
    Helper class containing the array of property values
    """
    default_value = 1.0
    type2len = {"Isotropic" : 1,
                "Orthotropic" : 3, 
                "Anisotropic" : 9}
    len2type = { 1 : "Isotropic",
                 3 : "Orthotropic", 
                 9 : "Anisotropic"}
    recognized_types = type2len.keys() 
    recognized_lengths = type2len.values() 


    def __init__(self, values=None):
        """
        Initialize from input values (type is automatically determined)
        """
        if values == None:
            self.type = "Isotropic"
            self.values = [self.default_value]
        else:
            nb_values = len(values)
            if nb_values in self.recognized_lengths:
                self.values = values
                self.type = self.len2type[nb_values]
            else:
                raise ValueError("Values should be of length 1, 3 or 9")
        return


    @classmethod
    def fromtype(cls, type):
        """
        Initialize a property of a given type filled with the default value
        """
        if type in cls.recognized_types:
            values = [cls.default_value 
                      for i in range(cls.type2len[type])]
        else:
            raise TypeError("Attribute type should be in {}".format(cls.recognized_types))
        return cls(values)



#-------------------------------------------------------------------------------
# Define content of QTable 
#-------------------------------------------------------------------------------


class StandardItemModelSolverProperty():
    """
    Class to display the table were values are set for user properties
    """

    def __init__(self, property_type=None):
        """
        Initialize class
        """
        QStandardItemModel.__init__(self)
        self.headers = [self.tr("Zone")]
        if property_type == "Orthotropic":
            self.nb_prop_values = 3 
            self.headers += [self.tr("Value in X"),
                             self.tr("Value in Y"),
                             self.tr("Value in Z")]
        elif property_type == "Anisotropic":
            self.nb_prop_values = 9 
            #TODO find a better way to display the matrix
            self.headers += [self.tr("Value in X-X"),
                             self.tr("Value in X-Y"),
                             self.tr("Value in X-Z"),
                             self.tr("Value in Y-X"),
                             self.tr("Value in Y-Y"),
                             self.tr("Value in Y-Z"),
                             self.tr("Value in Z-X"),
                             self.tr("Value in Z-Y"),
                             self.tr("Value in Z-Z"),
                            ]
        else: #default case is isotropic
            self.nb_prop_values = 1 
            self.headers += [self.tr("Value")]
        self.setColumnCount(len(self.headers))
        self.dataSolverProperties = []


    def data(self, index, role):
        """
        TODO what is this ?
        """
        if not index.isValid():
            return None
        if role == Qt.ToolTipRole:
            return self.tooltip[index.column()]
        if role == Qt.DisplayRole:
            return self.dataCathare[index.row()][index.column()]
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        return None
        

    def flags(self, index):
        """
        TODO what is this ?
        """
        if not index.isValid():
            return Qt.ItemIsEnabled
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable


    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
        return None


    def setData(self, index, value, role):
        if not index.isValid():
            return
        # TODO : update associated model
        self.dataChanged.emit(index, index)
        return True


    def insertItem(self, label, codeNumber, values_list):
        if (type(values_list)==list):
            line = [label, codeNumber] + values_list
            self.dataSolverProperties.append(line)
            row = self.rowCount()
            self.setRowCount(row+1)


    def getItem(self, row):
        return self.dataBoundary[row]


#-------------------------------------------------------------------------------
# Main class
#-------------------------------------------------------------------------------


class SolverPropertyView(QWidget, Ui_SolverPropertyForm):
    """
    Main class to display the values of user solver properties
    """

    def __init__(self, parent):
        """
        Initialize class
        """
        QWidget.__init__(self, parent)
        Ui_SolverPropertyForm.__init__(self)
        self.setupUi(self)

#-------------------------------------------------------------------------------
# End
#-------------------------------------------------------------------------------
