# -*- coding: utf-8 -*-
from Autodesk.Revit import DB
import clr
clr.AddReference("System.Windows.Forms")
from System.Windows.Forms import *

doc = __revit__.ActiveUIDocument.Document
string = "File Name\tLevel Name\tProject Base Point\tSurvey Point\tBuilding Story\n"
logs = "Таблица скопирована в буфер обмена\n\n"
FORGE_TYPE_ID = DB.ForgeTypeId("autodesk.spec.aec:length-2.0.0")
UNITS = doc.GetUnits()

def find_delta_and_convert(level, point):
    delta = level - point
    return DB.UnitFormatUtils.Format(UNITS, FORGE_TYPE_ID, delta, True)

links = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_RvtLinks).WhereElementIsNotElementType()
for link in links:
    link_type_id = doc.GetElement(link.GetTypeId()).Id
    if DB.RevitLinkType.IsLoaded(doc, link_type_id):
        link_doc = link.GetLinkDocument()
        levels = DB.FilteredElementCollector(link_doc).OfCategory(DB.BuiltInCategory.OST_Levels).WhereElementIsNotElementType()
        project_base_point_elevation = DB.BasePoint.GetProjectBasePoint(link_doc).Position.Z
        survey_point_elevation = DB.BasePoint.GetSurveyPoint(link_doc).Position.Z
        for level in levels:
            level_project_elevation = level.ProjectElevation
            project_base_point = find_delta_and_convert(level_project_elevation, project_base_point_elevation)
            survey_point = find_delta_and_convert(level_project_elevation, survey_point_elevation)
            building_story = level.Parameter[DB.BuiltInParameter.LEVEL_IS_BUILDING_STORY].AsInteger()
            building_story = "●" if building_story == 1 else "○"
            string += "{}\t{}\t{}\t{}\t{}\n".format(
            link_doc.Title,
            level.Name,
            project_base_point,
            survey_point,
            building_story
            )
    else:
        logs += "Связь {} не загружена. Не получилось её обработать\n".format(link.Name)

string = string[:-1]
Clipboard.SetText(string)
MessageBox.Show(logs, "SynSys : Create Levels for Analysis")

