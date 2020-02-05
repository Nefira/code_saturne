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

import unittest
import sys

#-------------------------------------------------------------------------------
# Application modules import
#-------------------------------------------------------------------------------

from code_saturne.model.Common import *
from code_saturne.model.XMLvariables import Variables, Model

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
        self.usolver_choice = ["off", "scalar_diffusion", "scalar_convection"]


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
        old_model = self.node_usolver['model']
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


#-------------------------------------------------------------------------------
# End
#-------------------------------------------------------------------------------
