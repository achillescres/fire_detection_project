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

raw_class = cls.classify_fires(data, day_time)
fires = raw_class['fires']
t4 = raw_class['t4']

plt_fires = data['r085']
plt_fires[fires == 1] = 2
tr.img(plt_fires, 'Fires final')

# driver = gdal.GetDriverByName('GTiff')

# [cols, rows] = fires.shape
# out_ds = driver.Create("fires.tif", cols, rows, 1, gdal.GDT_Float32)
# print('t4_22', tr.counter(data['t4_22'].data))
# writer.arrays2file(
#     [fires, data['t4_21'], data['t4_22'], data['r064'], data['r085']],
#     'GTiff', 'fires.tif', modis_path
# )

writer.array2file(fires, 'GTiff', 'fires.tif', modis_path)
# fires = writer.cut(fires, './files/reg.sph')

print('Fires final:', tr.counter(fires))
fires_ij = np.dstack(np.where(fires == 1))[0]
fires_latlon = to.get_fires_latlon(fires_ij)
fires_polygons = to.get_polygons(fires_ij)

cut = writer.cut(fires, modis_path)
writer.write_answer('kalin?', data['imageid'], fires_ij,
                    fires_latlon, fires_polygons, t4, data['t11'])
# print(writer.get_fires_latlon(fires))
