import numpy as np
import tools as to
import troubles as tr
import classification as cls
import writer

import matplotlib.pyplot as plt

from osgeo import gdal
gdal.UseExceptions()


# Classes
# Unknown 0
# Cloud or water 1
# Non fire 2
# 100Fire 3

# Data
modis_path = './files/mod1.hdf'  # DONT CHANGE THIS!
mod03_path = './files/mod03.hdf'  # DONT CHANGE THIS!
data = to.get_data('./files/mod1.hdf', './files/mod03.hdf')  # DONT CHANGE THIS!
print('Got data')
day_time = 'day'

fires = cls.classify_fires(data, day_time)

writer.arrays2file([fires], 'GTiff', 'fires.tif', modis_path)
