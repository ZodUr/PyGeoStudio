"""
Delete geometry and read excel, then make dike profile
======================================================

"""
import pandas as pd

# %%
# Open example GeoStudio study
import PyGeoStudio as pgs

# Check main path
main_path = "C:/Users/WQ5783/OneDrive - ENGIE/5_PyProjects/PyGeoStudio"

# Open file
src_file = "examples/GeoStudio_files/test.gsz"
geofile = pgs.GeoStudioFile(main_path+"/"+src_file)

# Delete all
geofile.showGeometries()
geometry = geofile.getGeometryByID(1)
geometry.delete()

# Load the Excel file
df = pd.read_excel(main_path+"/"+"examples/geometry/cross_sections_schelde_quantiles.xlsx", engine="openpyxl")


def get_points_for_fid(fid_value):
    """
    Extracts a list of [x, y] points for a given fid from the Excel data.
    :param fid_value: The fid value to filter the data.
    :return: List of [x, y] coordinate pairs.
    """
    row = df[df['fid'] == fid_value]
    if row.empty:
        raise ValueError(f"No data found for fid {fid_value}")
    row = row.iloc[0]
    points = [[row[f'x{i}'], row[f'y{i}']] for i in range(1, 8)]
    return points


# %%
# Add points of dike
points = get_points_for_fid(0.5)
geometry.addPoints(points)
lines = [[i, i+1] for i in range(1, len(geometry.points))]
geometry.addLines(lines)

geometry.draw(listProperties=True)


# %%
# Write modified study under new file:
out_file = "examples/GeoStudio_files/test-dike-geom.gsz"
geofile.saveAs(main_path+"/"+out_file)
