import numpy as np
import tools as to
import troubles as tr
import classification as cls
import writer
import neighbor as nb

import matplotlib.pyplot as plt

from osgeo import gdal

gdal.UseExceptions()

# Classes
# Unknown 0
# Cloud 1
# Water 2
# Non fire 3
# Fire 4

# Data
modis_path = 'C:\\Users\\aital\\Downloads\\20220407_081730_TERRA_MOD021KM.hdf'  # DONT CHANGE THIS!
mod03_path = '.C:\\Users\\aital\\Downloads\\20220407_081730_TERRA_MOD03.hdf'  # DONT CHANGE THIS!
data = to.get_data('./files/mod1.hdf', './files/mod03.hdf')  # DONT CHANGE THIS!
print('Got data')
day_time = 'day'

raw_class = cls.classify_fires(data, day_time)

fires = tr.get_ma(raw_class['fires'])
fires.mask = data['all_mask']

t4 = raw_class['t4']
t4.mask = t4.mask | data['all_mask']
t11 = data['t11']
t11.mask = t11.mask | data['all_mask']

classed = raw_class['classed']
classed.mask = classed.mask | data['all_mask']

classed = classed == 0 & (~classed.mask)

plt_fires = data['r085']
plt_fires[fires == 4] = 5
tr.img(plt_fires, 'Fires final')

# nb.neighbors_procces(classed, t4, data['t11'], day_time)
writer.array2file(fires, 'GTiff', 'fires.tif', modis_path)

print('Fires final:', tr.counter(fires))
fires_ij = np.dstack(np.where(fires == 1))[0]
fires_latlon = to.get_fires_latlon(fires_ij)
fires_polygons = to.get_polygons(fires_ij)

writer.write_answer('kalin?', data['imageid'], fires_ij,
                    fires_latlon, fires_polygons, t4, data['t11'])
