# -*- coding: utf-8 -*-
__title__ = "Column Numbering"
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
from Autodesk.Revit.UI.Selection import ObjectType
from Autodesk.Revit.DB import BuiltInCategory
#pyRevit
from pyrevit import revit, forms, script

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

#param_name = forms.ask_for_string(
#    default="Column Number",
#    prompt="Enter Parameter Name",
#    title="Column Numbering"
#)
#
#prefix = forms.ask_for_string(
#    default="C",
#    prompt="Enter Prefix",
#    title="Column Numbering"
#)
#
#row_tol_mm = forms.ask_for_string(
#    default="1000",
#    prompt="Enter Row Tolerance (mm)",
#    title="Column Numbering"
#)
#
#row_tol_mm = float(row_tol_mm)


dict_cats = {'Structural Columns' : BuiltInCategory.OST_StructuralColumns}




#0 Numbering Rules
from rpw.ui.forms import (FlexForm, Label, ComboBox, TextBox, Separator, Button, CheckBox)
components = [Label('PICK CATEGORY:'), ComboBox('category', dict_cats),
              Label('PREFIX:'), TextBox('prefix', Text='C'),
              Label('COUNT (int)'), TextBox('count', Text='1'),
              Label('MIN. ROW OFFSET:'), TextBox('min_row_offset', Text='1000'),
              Label('PARAMETER NAME:'), TextBox('p_name', Text='RBG_CO_MarkNo'),
              Label('TYPE KEYWORD:'), TextBox('keyword', Text='RC'),
              #Label('NUMBERING METHOD:'), ComboBox('sort_method',{'Rows (Left → Right, Top → Bottom)' : 'ROWS',
              #      'Column Bands (Top → Bottom, Left → Right)' : 'BANDS'}),
              Separator(), Button('Set Renumberng Rules')]


form = FlexForm('Click Counter Rules', components)
form.show()


if not form.values:
    forms.alert('No Naming rules Provided try again', exitscript=True)




input       = form.values
PREFIX      = input['prefix']
COUNT_START = int(input['count'])
row_toll    = int(input['min_row_offset'])
p_name      = input['p_name']
cat         = input['category']
keyword     = input['keyword'].upper()
#SORT_METHOD = input['sort_method']


# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝
#░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
#🤖 Automate Your Boring Work Here
# --------------------------------------------------
# SETTINGS
# --------------------------------------------------

PARAMETER_NAME = p_name   # Change this

# 100 mm tolerance
TOLERANCE_X_MM = 100
TOLERANCE_X = TOLERANCE_X_MM / 304.8  # Revit feet
TOLERANCE_Y_MM = 150
TOLERANCE_Y = TOLERANCE_Y_MM / 304.8  # Revit feet
# --------------------------------------------------
# COLLECT COLUMNS
# --------------------------------------------------

#columns = list(
#    FilteredElementCollector(doc)
#    .OfCategory(BuiltInCategory.OST_StructuralColumns)
#    .WhereElementIsNotElementType()
#)
#


# Get selected elements
#selection_ids = uidoc.Selection.GetElementIds()

class CategoryFilter(ISelectionFilter):

    def __init__(self, bic):
        self.bic = bic

    def AllowElement(self, element):
        return (
            element.Category
            and element.Category.Id.IntegerValue == int(self.bic)
        )

    def AllowReference(self, reference, point):
        return False


with forms.WarningBar(title='Select Columns and click Finish'):
    
    refs = uidoc.Selection.PickObjects(
        ObjectType.Element,
        CategoryFilter(cat),
        "Select Structural Columns"
    )

columns = [doc.GetElement(r.ElementId) for r in refs]


print("Selected Columns: {}".format(len(columns)))

if not columns:
    print("No structural columns found.")
    raise SystemExit

filtered_columns = []

for col in columns:

    col_type = doc.GetElement(col.GetTypeId())
    type_name = Element.Name.GetValue(col_type)

    if keyword in type_name.upper():
        filtered_columns.append(col)

print("Filtered Columns: {}".format(len(filtered_columns)))

# --------------------------------------------------
# CREATE STACKS
# --------------------------------------------------

stacks = []

for f_col in filtered_columns:

    loc = f_col.Location

    if not hasattr(loc, "Point"):
        continue

    pt = loc.Point

    found_stack = False

    for stack in stacks:

        ref_pt = stack["point"]

        if (
            abs(pt.X - ref_pt.X) <= TOLERANCE_X and
            abs(pt.Y - ref_pt.Y) <= TOLERANCE_Y
        ):

            stack["columns"].append(f_col)
            found_stack = True
            break

    if not found_stack:

        stacks.append({
            "point": pt,
            "columns": [f_col]
        })

print("Stacks Found : {}".format(len(stacks)))

# --------------------------------------------------
# CREATE ROWS
# --------------------------------------------------

ROW_TOL = row_toll / 304.8

# Sort stacks by Y descending first
stacks.sort(key=lambda s: -s["point"].Y)

rows = []

for stack in stacks:

    y = stack["point"].Y

    found_row = False

    for row in rows:

        if abs(y - row["y"]) <= ROW_TOL:

            row["stacks"].append(stack)
            found_row = True
            break

    if not found_row:

        rows.append({
            "y": y,
            "stacks": [stack]
        })

# --------------------------------------------------
# SORT ROWS TOP TO BOTTOM
# --------------------------------------------------

rows.sort(
    key=lambda r: -r["y"]
)

# --------------------------------------------------
# SORT STACKS LEFT TO RIGHT
# --------------------------------------------------

for row in rows:

    row["stacks"].sort(
        key=lambda s: s["point"].X
    )

# --------------------------------------------------
# CREATE FINAL NUMBERING ORDER
# --------------------------------------------------

sorted_stacks = []

for row in rows:

    sorted_stacks.extend(
        row["stacks"]
    )

print("Numbered Stacks: {}".format(len(sorted_stacks)))

print("-" * 50)

for i, stack in enumerate(sorted_stacks, start=COUNT_START):

    x = round(stack["point"].X * 304.8)
    y = round(stack["point"].Y * 304.8)

    print(
        "{} | X={} | Y={}".format(
            i,
            x,
            y
        )
    )

print("-" * 50)

# --------------------------------------------------
# WRITE NUMBER
# --------------------------------------------------

t = Transaction(doc, "Column Numbering")
t.Start()

for index, stack in enumerate(sorted_stacks, start=COUNT_START):

    col_number = "{}{}".format(
        PREFIX,
        index
    )

    for f_col in stack["columns"]:

        param = f_col.LookupParameter(
            PARAMETER_NAME
        )

        if param and not param.IsReadOnly:

            param.Set(col_number)

t.Commit()