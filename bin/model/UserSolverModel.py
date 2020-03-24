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
This module defines the user solver model management

This module contains the following classes and function:
- UserSolverModel
"""

#-------------------------------------------------------------------------------
# Library modules import
#-------------------------------------------------------------------------------

import os

#-------------------------------------------------------------------------------
# Application modules import
#-------------------------------------------------------------------------------

from code_saturne.model.Common import *
from code_saturne.model.XMLvariables import Variables, Model

#-------------------------------------------------------------------------------
# Utility function
#-------------------------------------------------------------------------------

def RelOrAbsPath(path, case_dir):
    """
    Return a relative filepath in a same study, an absolute path otherwise.
    """

    study_dir = os.path.split(case_dir)[0]

    if path.find(study_dir) == 0:

        if hasattr(os.path, 'relpath'):
            return os.path.relpath(path, case_dir)

        elif path.find(case_dir) == 0:
            return path[len(case_dir)+1:]

        else:
            return os.path.join('..', path[len(study_dir)+1:])

    else:
        return path

#-------------------------------------------------------------------------------
# User Solver model class
#-------------------------------------------------------------------------------

class UserSolverModel(Variables, Model):
    """
    Enable User solver model
    """

    def __init__(self, case):
        """
        Initialize User solver
        """
        self.case = case
        self.node_models  = self.case.xmlGetNode("thermophysical_models")
        self.node_usolver = self.node_models.xmlInitNode('usolver_model')
        self.usolver_choice = ["off", "custom_solver", "predef_solver"]


    def __defaultValues(self):
        """
        Returns a dictionary with default values
        """
        default = {}
        default['activation'] = 'off'
        return default


    @Variables.undoGlobal
    def setUserSolverModel(self, model):
        """
        Enable or disable user solver model
        """
        self.isInList(model, self.usolver_choice)
        self.node_usolver['model'] = model


    @Variables.noUndo
    def getUserSolverModel(self):
        """
        Return model
        """
        node = self.node_models.xmlInitNode("usolver_model")
        status = node["model"]
        if status not in self.usolver_choice:
            status = self.__defaultValues()["activation"]
            self.setUserSolverModel(status)
        return status


    def __removeVariablesAndProperties(self):
        """
        Remove variables and properties associated to current model.
        """


class UserSolverCustomModel(Variables, Model):
    """
    Load or create user solver routine
    Available only if 'custom user solver' mode is activated
    """

    def __init__(self, case):
        """
        Initialize User solver
        """
        self.case = case
        self.node_models  = self.case.xmlGetNode('thermophysical_models')
        self.node_loadsolver = self.node_models.xmlInitNode("load_usolver")
        self.node_solverfile = self.node_loadsolver.xmlInitNode("solver_file", "path")

    def getSolverFile(self):
        """
        Return the user solver file.
        """
        solver_file = self.node_loadsolver.xmlGetNode("solver_file", "path")
        if solver_file:
            return solver_file['path']
        else:
            return None

    def setSolverFile(self, solver_file):
        """
        Add solver file path in xml file.
        """

        if solver_file == '':
            solver_file = None

        node = self.node_loadsolver.xmlInitNode("solver_file", "path")
        if solver_file:
            node['path'] = solver_file
        else:
            node.xmlRemoveNode()


class SolverPropertyModel(Variables, Model):
    """
    Manage the list of properties relative to predefined user solvers.
    """

    def __init__(self, case):
        """
        Initialize
        """

        self.case = case
        self._node_models  = self.case.xmlGetNode('thermophysical_models')
        self._node_usolver = self.case.xmlGetNode('usolver_model')
        self._node_usolverprop = self._node_usolver.xmlInitNode("usolver_properties")
        self._authorized_types = ["Isotropic", "Orthotropic", "Anisotropic"]


    def defaultValues(self):
        """
        Returns a dictionary with default values
        """
        default = {}
        default['property_name'] = 'MyProperty'
        default['property_type'] = 'Isotropic'
        return default


    #------------------------------------------------------------------
    # Helper function
    #------------------------------------------------------------------
    def __getStringData(self, index, name, setFunction):
        """
        Get string value from xml file.
        """
        self.isLowerOrEqual(index+1, self.getNumberOfProperties())
        node = self._node_usolverprop.xmlGetNodeList('solverprop')[index]
        value = node.xmlGetString(name)
        return self.__getDefaultDataIfNone(index, value, name, setFunction)


    def __getDefaultDataIfNone(self, index, value, name, setFunction):
        """
        Get default value if value is none.
        """
        if value == None or value == "":
            value = self.defaultValues()[name]
            setFunction(index+1, value)
        return value


    def tr(self, text):
        """
        Translation
        """
        return text


    @Variables.noUndo
    def getPropertiesList(self):
        """
        @return: list of user solver properties (CDO style)
        @rtype: C{list}
        """
        node_list = self._node_usolverprop.xmlGetNodeList("solverprop")
        prop_list = []
        for index in range(len(node_list)):
            num = index+1
            current_prop = [self.getPropertyName(num),
                            self.getPropertyType(num)]
            prop_list.append(current_prop)
        return prop_list


    def getNumberOfProperties(self):
        return len(self._node_usolverprop.xmlGetNodeList("solverprop"))


    @Variables.undoLocal #?
    def setPropertyName(self, num, value):
        """
        Copy-pasted from setCathareEltName
        TODO check if this needs to be modified
        """
        self.isLowerOrEqual(num, self.getNumberOfProperties())
        self.isStr(value)
        node = self._node_usolverprop.xmlGetNodeList("solverprop")[num-1]
        node.xmlSetData("property_name", value)


    @Variables.noUndo
    def getPropertyName(self, num):
        """
        Get property name
        """
        return self.__getStringData(num-1, "property_name", self.setPropertyName)


    @Variables.undoLocal #?
    def setPropertyType(self, num, value):
        """
        Copy-pasted from setCathareEltName
        TODO check if this needs to be modified
        """
        self.isLowerOrEqual(num, self.getNumberOfProperties())
        self.isStr(value)
        # TODO check that value is in [istropic, orthotropic, anisotropic]
        self.isInList(value, self._authorized_types)
        node = self._node_usolverprop.xmlGetNodeList("solverprop")[num-1]
        node.xmlSetData("property_type", value)


    @Variables.noUndo
    def getPropertyType(self, num):
        """
        Get property name
        """
        return self.__getStringData(num-1, "property_type", self.setPropertyType)


    @Variables.undoGlobal
    def addProperty(self, property_name, property_type):
        """
        Add a new solver property

        @type property_name : C{String}
        @param property_name : property name
        @type property_type : C{String}
        @param property_type : property type (iso-, ortho-, aniso-tropic)
        """
        num = len(self._node_usolverprop.xmlGetNodeList("solverprop"))
        node_new  = self._node_usolverprop.xmlAddChild("solverprop")
        num = num+1
        self.setPropertyName(num, property_name)
        self.setPropertyType(num, property_type)
        return num


    @Variables.undoLocal
    def deleteProperty(self, num):
        """
        Delete a solver property

        @type num: C{Int}
        @param num: Property number
        """
        self.isLowerOrEqual(num, self.getNumberOfProperties())
        node_list = self._node_usolverprop.xmlGetNodeList('solverprop')
        node = node_list[num-1]
        node.xmlRemoveNode()

#-------------------------------------------------------------------------------
# End
#-------------------------------------------------------------------------------
