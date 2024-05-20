# example from https://laspy.readthedocs.io/en/latest/complete_tutorial.html


import laspy
import numpy as np

las = laspy.read(
    "/exports/csce/datastore/geos/groups/MSCGIS/s2559258/Bonaly/raw_las/NT2065_4PPM_LAS_PHASE5.las"
)
# Some notes on the code below:
# 1. las.header.maxs returns an array: [max x, max y, max z]
# 2. `|` is a numpy method which performs an element-wise "or"
#    comparison on the arrays given to it. In this case, we're interested
#    in points where a XYZ value is less than the minimum, or greater than
#    the maximum.
# 3. np.where is another numpy method which returns an array containing
#    the indexes of the "True" elements of an input array.

# Get arrays which indicate invalid X, Y, or Z values.
X_invalid = (las.header.mins[0] > las.x) | (las.header.maxs[0] < las.x)
Y_invalid = (las.header.mins[1] > las.y) | (las.header.maxs[1] < las.y)
Z_invalid = (las.header.mins[2] > las.z) | (las.header.maxs[2] < las.z)
bad_indices = np.where(X_invalid | Y_invalid | Z_invalid)

print(bad_indices)

print(las.header.maxs[2])

# Print 3d bounds of las file?
print(
    las.header.min[0],
    las.header.max[0],
    las.header.min[1],
    las.header.max[1],
    las.header.min[2],
    las.header.max[2],
)
