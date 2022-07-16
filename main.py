import numpy as np
import tools as to
import troubles as tr
import classification as cls
import writer

from osgeo import gdal

gdal.UseExceptions()

# Classes
# Unknown 0
# Cloud 1
# Water 2
# Non fire 3
# Fire 4

# Data
modis_path = input('Modis main product path: ') or './example/20220716_075533_AQUA_MOD021KM.hdf'
mod03_path = input('Mod03 product path: ') or './example/20220716_075533_AQUA_MOD03.hdf'
aoi_path = input('Aoi (must be .shp) path: ') or ''

data = to.get_data(modis_path, mod03_path)
print('Got data')

if input('Your image must be daytime! Y/n: ').strip().lower() not in ['y', '', ' ']:
    exit(-1)

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
fires_latlon = to.get_fires_latlon(fires_ij, mod03_path)
fires_polygons = to.get_polygons(fires_ij, mod03_path)

writer.write_answer('kalin?', data['imageid'], fires_ij,
                    fires_latlon, fires_polygons, t4, data['t11'], aoi_path)

print('\nSuccess!')