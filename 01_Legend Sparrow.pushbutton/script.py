# -*- coding: utf-8 -*-
__title__ = "Legend Sparrow"
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
from pyrevit import forms, script

#.NET Imports
import clr
clr.AddReference('System')
from System.Collections.Generic import List
from Autodesk.Revit.UI.Selection import ISelectionFilter

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

legends = [
    v for v in FilteredElementCollector(doc).OfClass(View)
    if v.ViewType == ViewType.Legend
]

legend = forms.SelectFromList.show(
    legends,
    name_attr='Name',
    title='Select Legend'
)

if not legend:
    script.exit()

selected_sheets = forms.select_sheets(
    title='Select Sheets'
)

if not selected_sheets:
    script.exit()

placement_method = forms.CommandSwitchWindow.show(
    ['Center', 'Match Existing Legend'],
    message='Choose Placement Method'
)



from rpw.ui.forms import (FlexForm, Label, ComboBox, TextBox, Separator, Button, CheckBox)
components = [Label('X OFFSET (RIGHT TO LEFT) INTEGER:'), TextBox('x_offset', Text='110'),
              Label('Y OFFSET (TOP TO DOWN) INTEGER:'), TextBox('y_offset', Text='10'),
              Separator(), Button('Set Offset Rules')]


form = FlexForm('Click Counter Rules', components)
form.show()

if not form.values:
    forms.alert('No Naming rules Provided try again', exitscript=True)

input    = form.values

offset_x = float(input['x_offset'])
offset_y = float(input['y_offset'])

t = Transaction(doc, "Place Legend on Sheets")
t.Start()


viewports = FilteredElementCollector(doc)\
    .OfClass(Viewport)\
    .ToElements()

for sheet in selected_sheets:

    outline = sheet.Outline
    center_x = (outline.Max.U + outline.Min.U) / 2
    center_y = (outline.Max.V + outline.Min.V) / 2
    point = XYZ(center_x, center_y, 0)


    work_area_max_x = (outline.Max.U - (offset_x/304.8))
    work_area_max_y = (outline.Max.V - (offset_y/304.8))


    already_exists = False

    for vp in viewports:
        if vp.SheetId == sheet.Id and vp.ViewId == legend.Id:
            already_exists = True
            break

    if not already_exists:
        l_vp = Viewport.Create(
            doc,
            sheet.Id,
            legend.Id,
            point
        )

        l_vp_outline = l_vp.GetBoxOutline()
        l_vp_center = l_vp.GetBoxCenter()

        
        off_center_x = (l_vp_outline.MaximumPoint.X - l_vp_center.X)
        off_center_y = (l_vp_outline.MaximumPoint.Y - l_vp_center.Y)


        new_center = XYZ(
            work_area_max_x - off_center_x,
            work_area_max_y - off_center_y,
            0
        )

        l_vp.SetBoxCenter(new_center)    

t.Commit()
