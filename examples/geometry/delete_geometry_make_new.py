"""
Delete geometry and make new one
=================================

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
# Show the geometries defined in the study and select the one with ID 1 to draw & list it
geofile.showGeometries()
geometry = geofile.getGeometryByID(1)
geometry.draw(listProperties=True)
geometry.delete()
geometry.listProperties()
geometry.draw()
