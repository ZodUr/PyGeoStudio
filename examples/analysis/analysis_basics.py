"""
Analysis - basics
=================
"""
import PyGeoStudio as pgs

# Check main path
main_path = "C:/Users/WQ5783/OneDrive - ENGIE/5_PyProjects/PyGeoStudio"

# test 1 #####################################################################
# Open simple test example GeoStudio study
src_file1 = "examples/GeoStudio_files/test.gsz"
geofile1 = pgs.GeoStudioFile(main_path+"/"+src_file1)

# Show tree
geofile1.showAnalysisTree()

# Show properties first analysis
analysis11 = geofile1.getAnalysisByID(1)
print(analysis11.getAllProperties())

# Show problem
analysis11.showProblem()


# test 2 #####################################################################
# Open dike example GeoStudio study
src_file2 = "examples/GeoStudio_files/Dike Schelde T4000 Transient 25min-interval.gsz"
geofile2 = pgs.GeoStudioFile(main_path+"/"+src_file2)

# Show tree
geofile2.showAnalysisTree()

# Show properties first analysis
analysis21 = geofile2.getAnalysisByID(1)
print(analysis21.getAllProperties())

# Show problem
analysis21.showProblem()


