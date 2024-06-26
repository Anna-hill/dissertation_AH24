# https://gis.stackexchange.com/questions/255833/classifying-lidar-ground-points-using-laspy
# Interesting code???


# https://laspy.readthedocs.io/en/1.x/tut_part_1.html
# laspy docs also good place to look

# np. where is faster than for loops

# https://laspy.readthedocs.io/en/latest/lessbasic.html
# add classification as an extra dim???



# pseudo code

# read las file with laspy

# run nearest neightbour
# if nearest neighbour has below threshold euclidian distance, remove point
# in such a way that does not remove all points

# pts points don't have DN???
# want lowest cluster in Z - or try to interpolate?????
# but with interpolation how to know where you are wrong???
