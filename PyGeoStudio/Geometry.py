# This file is part of PyGeoStudio, an interface to GeoStudio 
# hydrogeotechnical software.
# Copyright (C) 2023, Moïse Rousseau
# 
# PyGeoStudio is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# PyGeoStudio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xml.etree.ElementTree as ET
from prettytable import PrettyTable


# We do not use the BasePropertiesClass as there is too much specificities here.
# Or maybe the base class is not general enough ... ?
# noinspection PyUnresolvedReferences
from PyGeoStudio import Mesh


class Geometry:
  """
  :param Points: XY coordinates of the points in the geometry
  :type Points: numpy array
  :param Lines: List of lines in the geometry
  :type Lines: list
  :param Regions: List of regions in the geometry
  :type Regions: list
  :param MeshId: Index of the mesh associated with the geometry (do not change)
  :type MeshId: int
  :param Mesh: Mesh associated with the geometry
  :type Mesh: PyGeoStudio.Mesh object
  :param Name: Name of the geometry
  :type Name: str
  """

  def __init__(self):
    self.points = None
    self.point_table = pd.DataFrame(columns=["Index", "ID label", "X-co", "Y-co", "Note"])
    self.lines = None
    self.mesh_id = None
    self.mesh = None
    self.name = None
    self.regions = {}
    self.other_elem = []
    return

  def __getitem__(self, parameter):
    if parameter == "Points":
        return self.points
    elif parameter == "Lines":
        return self.lines
    elif parameter == "Regions":
        return self.regions
    elif parameter == "MeshId":
        return None if self.mesh_id is None else int(self.mesh_id)
    elif parameter == "Mesh":
        return self.mesh
    elif parameter == "Name":
        return self.name
    else:
        raise KeyError(f"There is no item \"{parameter}\" accessible through Geometry class")

  def draw(self, pointLabels=True, listProperties=False, figsize=(10, 5)):
      """
      Draw the geometry using matplotlib and label each point with its ID.
      :param pointLabels:     Show point ids as labels in plot
      :param listProperties:  Show list all points, lines, and regions in the geometry in a formatted way.
      :param figsize:         Tuple defining the size of the figure (width, height)
      :return:                Matplotlib figure and axis containing the plotted geometry
      :rtype:                 [fig, ax]
      """
      if listProperties:
          self.listProperties()
      if self.points is None:
          print("No geometry available to draw!")
          return
      fig, ax = plt.subplots(figsize=figsize)
      ax.scatter(self.points[:, 0], self.points[:, 1], color='k')
      if pointLabels:
        for idx, row in self.point_table.iterrows():
            label = f"{idx + 1}"
            if row["Note"]:
                label += f"\n({row['Note']})"
            ax.text(row["X-co"], row["Y-co"], label, fontsize=9, ha='right', va='bottom', color='blue')
      for region in self.regions.values():
          region = region[0]
          for i in range(len(region) - 1):
              X1, Y1 = self.points[region[i] - 1]
              X2, Y2 = self.points[region[i + 1] - 1]
              ax.plot([X1, X2], [Y1, Y2], 'k')
          X1, Y1 = self.points[region[-1] - 1]
          X2, Y2 = self.points[region[0] - 1]
          ax.plot([X1, X2], [Y1, Y2], 'k')
      return fig, ax

  def read(self, element):
      for property_ in element:
          if property_.tag == "Points":
              point_data = []
              for point in property_:
                  idx = int(point.attrib["ID"]) - 1
                  x = float(point.attrib["X"])
                  y = float(point.attrib["Y"])
                  point_data.append([idx, f"Point-{idx+1}", x, y, ""])
              self.point_table = pd.DataFrame(point_data, columns=["Index", "ID label", "X-co", "Y-co", "Note"])
              self.points = self.point_table[["X-co", "Y-co"]].to_numpy()
          elif property_.tag == "Lines":
              self.lines = np.zeros((int(property_.attrib["Len"]), 2), dtype='i8') - 1
              for line in property_:
                  self.lines[int(line[0].text) - 1] = [int(line[1].text) - 1, int(line[2].text) - 1]
          elif property_.tag == "Regions":
              for region in property_:
                  for x in region:
                      other_attrib = []
                      if x.tag == "ID":
                          id_ = x.text
                      if x.tag == "PointIDs":
                          pts = [int(y) for y in x.text.split(',')]
                      else:
                          other_attrib.append(x)
                  self.regions[f"Regions-{id_}"] = [pts, other_attrib]
          elif property_.tag == "MeshId":
              self.mesh_id = property_.text
          elif property_.tag == "ResultGraphs":
              pass  # do not parse result graphics
          elif property_.tag == "Name":
              self.name = property_.text
          # elif property_.tag == "MeshDefaultEdgeLength":
          #  pass
          else:
              self.other_elem.append(property_)
      return

  def listProperties(self):
    """
    List all points, lines, and regions in the geometry in a formatted way.
    """
    print("\n"+"Geometry properties lists:")
    print("--------------------------")
    # 1. List all points
    print("Points:")
    if self.points is not None and len(self.points) > 0:
        table_points = PrettyTable()
        table_points.field_names = ["Index", "Point ID label", "X-co", "Y-co", "Note"]
        for _, row in self.point_table.iterrows():
            table_points.add_row(row.tolist())
        print(table_points)
    else:
        print("No points defined.")

    # 2. List all lines
    print("\nLines:")
    if self.lines is not None and len(self.lines) > 0:
        table_lines = PrettyTable()
        table_lines.field_names = ["Line Index", "Start Index", "End Index", "Start Label", "End Label",
                                 "Start coords", "End coords"]
        for idx, (start, end) in enumerate(self.lines):
            start_coords = tuple(self.points[start])
            end_coords = tuple(self.points[end])
            table_lines.add_row([
              idx,
              start, end,
              f"Point-{start + 1}", f"Point-{end + 1}",
              f"({start_coords[0]:.2f},{start_coords[1]:.2f})",
              f"({end_coords[0]:.2f},{end_coords[1]:.2f})"
            ])
        print(table_lines)
    else:
      print("\nNo lines defined.")

    # 3. List all regions
    print("\nRegions:")
    if self.regions:
        table_regions = PrettyTable()
        table_regions.field_names = ["Region Index", "Region Label", "Point labels", "Point coordinates"]
        for idx, (label, region_data) in enumerate(self.regions.items()):
            pt_ids = region_data[0]
            pt_labels = [f"Point-{pt_id}" for pt_id in pt_ids]
            pt_coords = [f"({self.points[pt_id - 1][0]:.2f},{self.points[pt_id - 1][1]:.2f})" for pt_id in pt_ids]
            coord_str = ">".join(pt_coords)
            table_regions.add_row([idx, label, ", ".join(pt_labels), coord_str])
        print(table_regions)
    else:
        print("No regions defined.")

  def delete(self, points=True, lines=True, regions=True):
    """
    Delete all points, lines and / or regions in geometry.
    If points are deleted, all lines & regions will be too.
    """
    if points:
      regions, lines = True, True
      self.points = None
      self.point_table = pd.DataFrame(columns=["Index", "ID label", "X-co", "Y-co", "Note"])
      print("All  points deleted!")
    if regions:
      self.regions = {}
      print("All regions deleted!")
    if lines:
      self.lines = None
      print("All lines deleted!")

  def addPoints(self, pts, notes=None):
      """
      Add points to the geometry.
      :param pts: XY coordinates of the points
      :type pts: numpy array or list of list
      :param notes: Optional list of notes
      :type notes: list of str or None
      """
      if isinstance(pts, list):
          pts = np.array(pts, dtype=float)
      if pts.ndim != 2 or pts.shape[1] != 2:
          raise ValueError("Points must be a (n, 2) array.")
      start_idx = len(self.point_table)
      new_data = {
          "Index": list(range(start_idx, start_idx + len(pts))),
          "ID label": [f"Point-{i + 1}" for i in range(start_idx, start_idx + len(pts))],
          "X-co": pts[:, 0],
          "Y-co": pts[:, 1],
          "Note": notes if notes else ["" for _ in range(len(pts))]
      }
      new_df = pd.DataFrame(new_data)
      self.point_table = pd.concat([self.point_table, new_df], ignore_index=True)
      self.points = self.point_table[["X-co", "Y-co"]].to_numpy()  # Update self.points for compatibility
      return

  def addLines(self, new_lines):
      """
      Add lines to the geometry.
      :param new_lines: Start-end ID of the point labels that form the lines (point IDs start from 1)
      :type new_lines: numpy array or list of list
      """
      if isinstance(new_lines, np.ndarray):
          if new_lines.ndim != 2 or new_lines.shape[1] != 2:
              raise ValueError("Input numpy array must have shape (n, 2).")
          arr = new_lines
      elif isinstance(new_lines, list):
          try:
              arr = np.array(new_lines, dtype=int)
              if arr.ndim != 2 or arr.shape[1] != 2:
                  raise ValueError
          except Exception:
              raise ValueError("Input list must be in format: [[start1, end1], [start2, end2], ...]")
      else:
          raise TypeError("Input must be a list of lists or a numpy array with shape (n, 2).")
      # Adjust indices to be zero-based if they are one-based
      if np.any(arr > len(self.points)):
          raise ValueError("Line indices refer to non-existent points.")
      arr = arr - 1  # Convert to zero-based indexing
      if self.lines is None:
          self.lines = arr
      else:
          self.lines = np.vstack([self.lines, arr])
      return

  def addRegions(self, pt_ids):
    """
    Create region with existing point given

    :param pt_ids: Indices of the point
    :type pt_ids: list of int
    """
    new_id = len(self.regions) + 1
    new_reg = [pt_ids, []]
    self.regions[f"Region-{new_id}"] = new_reg
    return

  def createRegion(self, pts):
    """
    Create new points, new lines and a region based on the point coordinates given.
    Must be given in order so they form a convex and non-intersecting polygon when joined successively.

    :param pts: The coordinate of the points to create a region
    :type pts: numpy array or list of list
    """
    n_pts_ini = len(self.points)
    self.addPoints(pts)
    new_lines = [[x + n_pts_ini + 1, x + n_pts_ini + 2] for x in range(len(pts))]
    new_lines[-1][1] = n_pts_ini + 1
    self.addLines(new_lines)
    new_region = [x + n_pts_ini + 1 for x in range(len(pts))]
    self.addRegions(new_region)
    return

  def __write__(self, et):
    # points
    sub = ET.SubElement(et, "Points")
    sub.attrib = {"Len": str(len(self.points))}
    for i, pt in enumerate(self.points):
        sub_pt = ET.SubElement(sub, "Point")
        sub_pt.attrib = {"ID": str(i + 1), "X": str(pt[0]), 'Y': str(pt[1])}
    # lines
    sub = ET.SubElement(et, "Lines")
    sub.attrib = {"Len": str(len(self.lines))}
    for i, line in enumerate(self.lines):
        sub_line = ET.SubElement(sub, "Line")
        sub_sub_line = ET.SubElement(sub_line, "ID")
        sub_sub_line.text = str(i + 1)
        sub_sub_line = ET.SubElement(sub_line, "PointID1")
        sub_sub_line.text = str(line[0] + 1)
        sub_sub_line = ET.SubElement(sub_line, "PointID2")
        sub_sub_line.text = str(line[1] + 1)
    # regions
    sub = ET.SubElement(et, "Regions")
    sub.attrib = {"Len": str(len(self.regions))}
    for id_, region in self.regions.items():
        sub_reg = ET.SubElement(sub, "Region")
        sub_sub_reg = ET.SubElement(sub_reg, "ID")
        sub_sub_reg.text = id_.split('-')[-1]
        sub_sub_reg = ET.SubElement(sub_reg, "PointIDs")
        sub_sub_reg.text = ','.join([str(x) for x in region[0]])
        for x in region[1]:
            sub_sub_reg = ET.SubElement(sub_reg, x.tag)
            sub_sub_reg.text = x.text
            sub_sub_reg.attrib = x.attrib
    # mesh id
    sub = ET.SubElement(et, "MeshId")
    sub.text = self.mesh_id
    # name
    sub = ET.SubElement(et, "Name")
    sub.text = self.name
    # others
    for prop in self.other_elem:
        et.append(prop)
    return
