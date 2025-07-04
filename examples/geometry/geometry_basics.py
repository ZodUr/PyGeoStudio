"""
Geometry basics
===============

"""

# %%
# Open example GeoStudio study
import PyGeoStudio as pgs

# Check main path
main_path = "C:/Users/WQ5783/OneDrive - ENGIE/5_PyProjects/PyGeoStudio"

# Open file
src_file = "examples/GeoStudio_files/test.gsz"
geofile = pgs.GeoStudioFile(main_path+"/"+src_file)

# %%
# Show the geometries defined in the study and select the one with ID 1 to draw it
geofile.showGeometries()
geometry = geofile.getGeometryByID(1)
geometry.draw()

# %%
# Add new point
geometry.addPoints([[2, 0], [2.5, -0.5]])
geometry.draw()

# %%
# Create a new region from point IDs:
new_region = [2,5,4]
geometry.addRegions(new_region)
geometry.draw()

# %%
# Write modified study under new file:
out_file = "./test2.gsz"
geofile.saveAs(out_file)
  
