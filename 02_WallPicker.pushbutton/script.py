# -*- coding: utf-8 -*-
__title__   = "Wall Picker"
__doc__     = """Version = 1.0
Date    = 01.01.2026
________________________________________________________________
Description:
Placeholder for pyRevit .pushbutton.
Use it as a base for your new pyRevit tool.

________________________________________________________________
How-To:
1. Step 1...
2. Step 2...
3. Step 3...

________________________________________________________________
To-Do:
[FEATURE] - Describe Your Feature...
[BUG]     - Describe Your BUG...

________________________________________________________________
Last Updates:
- [01.01.2026] v1.0 Change Description
- [01.01.2026] v0.5 Change Description
- [01.01.2026] v0.1 Change Description 
________________________________________________________________
Author: Erik Frits (from LearnRevitAPI.com)"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝
#░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
from Autodesk.Revit.DB import *

#pyRevit
from pyrevit import forms, script, revit

#.NET Imports
import clr
clr.AddReference('System')
from System.Collections.Generic import List


# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝
#░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
doc    = __revit__.ActiveUIDocument.Document #type:Document
uidoc  = __revit__.ActiveUIDocument          # __revit__ is internal variable in pyRevit
app    = __revit__.Application
output = script.get_output()                 # pyRevit Output Menu

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝
#░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
#🤖 Automate Your Boring Work Here

dict_cats = {'Walls' : BuiltInCategory.OST_Walls,
             'Floors' : BuiltInCategory.OST_Floors,
             'Rooms' : BuiltInCategory.OST_Rooms,
             'Generic Models' : BuiltInCategory.OST_GenericModel,
             'Doors' : BuiltInCategory.OST_Doors,
             'Windows' : BuiltInCategory.OST_Windows,
             'Structural Columns' : BuiltInCategory.OST_StructuralColumns}


#0 Numbering Rules
from rpw.ui.forms import (FlexForm, Label, ComboBox, TextBox, Separator, Button, CheckBox)
components = [Label('PICK CATEGORY:'), ComboBox('category', dict_cats),
              Label('PREFIX:'), TextBox('prefix'),
              Label('COUNT (int)'), TextBox('count'),
              Label('SUFFIX:'), TextBox('suffix'),
              Label('PARAMETER NAME:'), TextBox('p_name'),
              Separator(), Button('Set Renumberng Rules')]

form = FlexForm('Click Counter Rules', components)
form.show()

if not form.values:
    forms.alert('No Naming rules Provided try again', exitscript=True)


input       = form.values
PREFIX      = input['prefix']
COUNT_START = int(input['count'])
SUFFIX      = input['suffix']
p_name      = input['p_name']
cat         = input['category']

#except:
#    forms.alert('COUNT START should be an integer. Please Try Again', exitscript=True)

#1️⃣ Pick Element
with forms.WarningBar(title='Select Doors To Renumber or hit [ESC] To STOP.'):
    while True:
        elem = revit.pick_element_by_category(cat)
        if not elem:
            break

        #2️⃣ Create New Value
        value = "{}{:02d}{}".format(PREFIX, COUNT_START, SUFFIX)
        COUNT_START += 1

        # Transaction To Allow Changes
        t = Transaction(doc, 'Click Counter')
        t.Start()  # 🔓

        #3️⃣ Get Shared Parameter
        #p_name = 'DoorNumber'
        p_door_num = elem.LookupParameter(p_name)

        #🚨 Ensure Parameter Exists
        if not p_door_num:
            t.RollBack()
            forms.alert('Missing Shared Parameter: "{}"'.format(p_name), exitscript=True)

        #4️⃣ Set New Value
        p_door_num.Set(value)

        t.Commit()  #🔒