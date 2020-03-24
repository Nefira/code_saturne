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
This module defines the UserControlCustom View 
"""

import os, sys, logging
try:
    import ConfigParser
    configparser = ConfigParser
except Exception:
    import configparser

#-------------------------------------------------------------------------------
# Standard modules
#-------------------------------------------------------------------------------

import os, sys, logging
try:
    import ConfigParser
    configparser = ConfigParser
except Exception:
    import configparser

#-------------------------------------------------------------------------------
# Third-party modules
#-------------------------------------------------------------------------------

from code_saturne.Base.QtCore    import *
from code_saturne.Base.QtGui     import *
from code_saturne.Base.QtWidgets import *

#-------------------------------------------------------------------------------
# Application modules import
#-------------------------------------------------------------------------------

from code_saturne.model.Common import GuiParam
#from code_saturne.Base.QtPage import ComboModel, DoubleValidator, RegExpValidator, IntValidator
#from code_saturne.Base.QtPage import from_qvariant, to_text_string
from code_saturne.Pages.UserSolverCustomForm import Ui_UserSolverCustomForm
from code_saturne.model.UserSolverModel import RelOrAbsPath, UserSolverModel, UserSolverCustomModel

#-------------------------------------------------------------------------------
# log config
#-------------------------------------------------------------------------------

logging.basicConfig()
log = logging.getLogger("UserSolverCustomView")
log.setLevel(GuiParam.DEBUG)


#-------------------------------------------------------------------------------
# File dialog to select either file or directory
#-------------------------------------------------------------------------------

# Copied from MeshInputDialog in SolutionDomainView
class SolverInputDialog(QFileDialog):

    def __init__(self,
                 parent = None,
                 search_dirs = []):

        if len(search_dirs) == 0:
            directory = ""
        else:
            directory = str(search_dirs[0])

        try:
            QFileDialog.__init__(self,
                                 parent = parent,
                                 directory = directory)
        except (AttributeError, TypeError):
            QFileDialog.__init__(self)  # for older PyQt versions

        # Self.tr is only available once the parent class __init__ has been called,
        # so we may now set the caption, filter, and selection label

        caption =  self.tr("Select input solver file")
        self.setWindowTitle(caption)

        self.name_filter = str(self.tr("C user solver routine (*.c)"))
        self.setNameFilter(self.name_filter)

        self.select_label = str(self.tr("Select"))
        self.setLabelText(QFileDialog.Accept, self.select_label)

        if hasattr(QFileDialog, 'ReadOnly'):
            options  = QFileDialog.DontUseNativeDialog | QFileDialog.ReadOnly
        else:
            options  = QFileDialog.DontUseNativeDialog
        if hasattr(self, 'setOptions'):
            self.setOptions(options)
        search_urls = []
        for d in search_dirs:
            search_urls.append(QUrl.fromLocalFile(d))
        self.setSidebarUrls(search_urls)

        self.currentChanged[str].connect(self._selectChange)

        self.setFileMode(QFileDialog.ExistingFile)


    def _selectChange(self, spath):
        mode = QFileDialog.ExistingFile
        path = str(spath)
#        if os.path.basename(path) == 'mesh_input':
#            if os.path.isdir(path):
#                mode = QFileDialog.Directory
        if os.path.exists(path):
            mode = QFileDialog.ExistingFiles
        self.setFileMode(mode)
        self.setNameFilter(self.name_filter)
        self.setLabelText(QFileDialog.Accept, self.select_label)


#-------------------------------------------------------------------------------
# This class defines the welcome page
#-------------------------------------------------------------------------------

class UserSolverCustomView(QWidget, Ui_UserSolverCustomForm):
    """
    Class for custom user solver (i.e. defined through a cs_user_solver
    routine) 
    """
    def __init__(self, parent, case, stbar, tree):
        """
        Constructor
        """
        # TODO check if all input arguments are necessary
        QWidget.__init__(self)
        Ui_UserSolverCustomForm.__init__(self)
        self.setupUi(self)

        self.root = parent #TODO : is this necessary ?
        self.stbar = stbar #TODO : is this necessary ?
        self.case = case
        self.browser = tree #TODO : is this necessary ?

        self.case.undoStopGlobal # TODO : what does this do ? Is it necessary ?
        self.mdl = UserSolverCustomModel(self.case)

        self.solver_file = self.mdl.getSolverFile()

        # Load user routine 
        f = self.mdl.getSolverFile()
        if f:
            if os.path.exists(f):
                self.solver_file = f
                self.lineEditSolverFile.setText(f)
                self.case['solver_file'] = f

        self.toolButtonSolverFile.clicked.connect(self.slotSetSolverFile)
        self.lineEditSolverFile.textChanged[str].connect(self.modifySolverFile)
        self.toolButtonSolverFileClear.clicked.connect(self.slotClearSolverFile)
        self.pushButtonSolverFileEdit.clicked.connect(self.slotEditSolverFile)

    def slotSetSolverFile(self):
        '''
        Open a file dialog in order to search and select user solver file
        '''
        search_dirs = []
        study_dir = os.path.split(self.case['case_path'])[0]
        for d in [os.path.join(study_dir, 'RESU_COUPLING'),
                  os.path.join(self.case['case_path'], 'RESU'),
                  study_dir]:
            if os.path.isdir(d):
                search_dirs.append(d)

        dialog = SolverInputDialog(search_dirs = search_dirs)

        if dialog.exec_() == 1:

            s = dialog.selectedFiles()

            mi = str(s[0])
            mi = os.path.abspath(mi)
            mi = RelOrAbsPath(mi, self.case['case_path'])

            self.modifySolverFile(mi)

        

        return None

    def modifySolverFile(self, text):
        """
        Modify the input user solver path
        """
        self.lineEditSolverFile.setText(text)
        self.mdl.setSolverFile(text)
        self.solver_file = text
        return None

    def slotClearSolverFile(self):
        """
        Clear the input solver file info.
        """
        self.lineEditSolverFile.setText('')
        if self.case['solver_file'] != None:
            self.solver_file = None
            self.mdl.setSolverFile(None)


    def slotEditSolverFile(self):
        """
        TODO ?
        """
        return None
       

#-------------------------------------------------------------------------------
# End
#-------------------------------------------------------------------------------
