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
from code_saturne.Pages.UserSolverPredefPropForm import Ui_UserSolverPredefPropForm
from code_saturne.model.UserSolverModel import SolverPropertyModel

#-------------------------------------------------------------------------------
# log config
#-------------------------------------------------------------------------------

logging.basicConfig()
log = logging.getLogger("UserSolverPredefPropView")
log.setLevel(GuiParam.DEBUG)

#-------------------------------------------------------------------------------
# Define content of QTable 
#-------------------------------------------------------------------------------

# Delegates == Columns

class PropertyNameDelegate(QItemDelegate):


    def __init__(self, parent = None):
        super(PropertyNameDelegate, self).__init__(parent)
        self.parent = parent


    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        return editor


    def setEditorData(self, editor, index):
        self.value = from_qvariant(index.model().data(index, Qt.DisplayRole), to_text_string) #TODO : que fait cette ligne ?
        editor.setText(self.value)


    def setModelData(self, editor, model, index):
        value = editor.text()
        if str(value) != "":
            model.setData(index, value, Qt.DisplayRole)


class PropertyTypeDelegate(QItemDelegate): 


    def __init__(self, parent, authorized_types):
        super(PropertyTypeDelegate, self).__init__(parent)
        self.parent = parent
        self.combovalues = authorized_types 


    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        for k in self.combovalues: 
            editor.addItem(k)
        editor.installEventFilter(self)
        editor.setMinimumWidth(120)
        return editor


    def setEditorData(self, comboBox, index):
        row = index.row()
        col = index.column()
        str_model = index.model().getData(row, col)
        idx = list(self.combovalues).index(str_model)
        comboBox.setCurrentIndex(idx)


    def setModelData(self, comboBox, model, index):
        txt = str(comboBox.currentText())
        value = txt 
        selectionModel = self.parent.selectionModel()
        for idx in selectionModel.selectedIndexes():
            if idx.column() == index.column():
                model.setData(idx, value, Qt.DisplayRole)


    def tr(self, text):
        return text




# StandardItemModel == Whole table

class StandardItemModelSolverProp(QStandardItemModel):

    def __init__(self, model):
        """
        TODO
        """
        QStandardItemModel.__init__(self)

        self.setColumnCount(2)

        self.headers = [self.tr("Property Name"),
                        self.tr("Type"),]

        self.tooltip = [self.tr("Name of the defined property (choose something explicit)"),
                        self.tr("Dependency of the property to the directions in space"),]

        self.setColumnCount(len(self.headers))
        self.dataSolverProp = []
        self.model = model


    def data(self, index, role):
        """
        Directly copied from CathareCouplingView
        """
        if not index.isValid():
            return None
        if role == Qt.ToolTipRole:
            return self.tooltip[index.column()]
        if role == Qt.DisplayRole:
            return self.dataSolverProp[index.row()][index.column()]
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        return None


    def flags(self, index):
        """
        Directly copied from CathareCouplingView
        """
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
 

    def headerData(self, section, orientation, role):
        """
        Directly copied from CathareCouplingView
        """
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
        return None


    def setData(self, index, value, role):
        if not index.isValid():
            return
     
        row = index.row()
        column = index.column()
        self.dataSolverProp[row][column] = str(from_qvariant(value, to_text_string))

        num = row+1
        self.model.setPropertyName(num, self.dataSolverProp[row][0])
        self.model.setPropertyType(num, self.dataSolverProp[row][1])

        # TODO check what this does (FN)
        id1 = self.index(0, 0)
        id2 = self.index(self.rowCount(), 0)
        self.dataChanged.emit(id1, id2) # is this necessary ?
        return True


    def getData(self, row, column):
        return self.dataSolverProp[row][column]


    def addItem(self, property_name, property_type):
        """
        Add a row in the table.
        """
        self.dataSolverProp.append([property_name,
                                 property_type,])
        row = self.rowCount()
        self.setRowCount(row+1)


    def deleteRow(self, row):
        """
        Delete the row in the model
        """
        del self.dataSolverProp[row]
        row = self.rowCount()
        self.setRowCount(row-1)



#-------------------------------------------------------------------------------
# This class defines the solver properties page
#-------------------------------------------------------------------------------

class UserSolverPredefPropView(QWidget, Ui_UserSolverPredefPropForm):
    """
    Class for the welcome page
    """
    def __init__(self, parent, case):
        """
        Constructor
        """
        QWidget.__init__(self, parent)
        Ui_UserSolverPredefPropForm.__init__(self)
        self.setupUi(self)

        self.case = case
        self.case.undoStopGlobal()
        self.model = SolverPropertyModel(case)

        # Initialize table of properties
        self.modelProperties = StandardItemModelSolverProp(self.model)
        self.tableProperties.setModel(self.modelProperties)

        if QT_API == "PYQT4":
            self.tableProperties.verticalHeader().setResizeMode(QHeaderView.ResizeToContents)
            self.tableProperties.horizontalHeader().setResizeMode(QHeaderView.ResizeToContents)
            self.tableProperties.horizontalHeader().setResizeMode(1, QHeaderView.Stretch)
        elif QT_API == "PYQT5":
            self.tableProperties.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            self.tableProperties.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            self.tableProperties.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        # Initialize delegates
        delegatePropName = PropertyNameDelegate(self.tableProperties)
        delegatePropType = PropertyTypeDelegate(self.tableProperties, self.model._authorized_types)
        self.tableProperties.setItemDelegateForColumn(0, delegatePropName)
        self.tableProperties.setItemDelegateForColumn(1, delegatePropType)
        
        self.tableProperties.clicked[QModelIndex].connect(self.slotSelectPropType)

        # Connections
        self.pushButtonAdd.clicked.connect(self.slotAddUserSolverProp)
        self.pushButtonDelete.clicked.connect(self.slotDeleteUserSolverProp)

        # Display list of created properties
        for prop in self.model.getPropertiesList():
            [property_name, property_type] = prop
            self.modelProperties.addItem(property_name, property_type)

        self.case.undoStartGlobal() #TODO is this necessary ?


    @pyqtSlot()
    def slotAddUserSolverProp(self):
        """
        Add a new user solver property
        """
        property_name = self.model.defaultValues()['property_name']
        property_type = self.model.defaultValues()['property_type']
        num = self.model.addProperty(property_name, property_type)
        self.modelProperties.addItem(property_name, property_type)


    @pyqtSlot()
    def slotDeleteUserSolverProp(self):
        """
        Delete an existing user solver property
        """
        row = self.tableProperties.currentIndex().row()
        if row == -1:
            title = self.tr("Warning")
            msg   = self.tr("You must select an existing coupling")
            QMessageBox.information(self, title, msg)
        else:
            self.modelProperties.deleteRow(row)
            self.model.deleteProperty(row+1)


    @pyqtSlot("QModelIndex")
    def slotSelectPropType(self, index):
        return

#-------------------------------------------------------------------------------
# End
#-------------------------------------------------------------------------------
