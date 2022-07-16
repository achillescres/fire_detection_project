import numpy as np
from math import isinf

import troubles as tr

from osgeo import gdal
gdal.UseExceptions()


def get_data(file_path, file03_path):
    from osgeo import gdal
    gdal.UseExceptions()

    # Preparing values
    sds = gdal.Open(file_path).GetSubDatasets()

    # ref_ds = gdal.Open(sds[0][0])
    # ref_meta = ref_ds.GetMetadata_Dict()

    # Temperatures
    emis_ds = gdal.Open(sds[2][0])
    emis_meta = emis_ds.GetMetadata_Dict()

    # IMAGEID
    imageid = emis_meta['LOCALGRANULEID']
    sat_title = imageid.find('MOD')
    if sat_title == -1:
        print('WARNING: EMPTY IMAGE ID!')
        imageid = ''
    else:
        imageid = imageid[:sat_title - 1]

    def get_temperature(band, n, length, meta):  # ##!!!
        try:
            offset = float(meta['radiance_offsets'].split(',')[n])
        except ValueError:
            offset = 0
        try:
            scale = float(meta['radiance_scales'].split(',')[n])
        except ValueError:
            scale = 1

        band_si = tr.get_ma(band.ReadAsArray())

        # print(band_si.mask)
        vrt = ~((0 <= band_si) & (band_si <= 32767))

        # y = np.copy(vrt).astype(int)
        # tr.img(y)
        # band_si.data[vrt] = 0
        band_si[vrt] = 0
        band_si.mask = vrt

        L = brightness(band_si, scale, offset)
        # tr.img(L, "L")
        T = temperature(L, length)
        # tr.img(T, 'T')
        # print(tr.counter(L))
        return T

    # T4 21
    T4_21_n = 1
    T4_21_length = 3.959

    T4_21_band = emis_ds.GetRasterBand(T4_21_n + 1)
    T4_21 = get_temperature(T4_21_band, T4_21_n, T4_21_length, emis_meta)
    # tr.hist(T4_21)
    print('t4 21')

    # T4 22
    T4_22_n = 2
    T4_22_length = 3.959

    T4_22_band = emis_ds.GetRasterBand(T4_22_n + 1)
    T4_22 = get_temperature(T4_22_band, T4_22_n, T4_22_length, emis_meta)
    print('t4 22')

    # T11
    T11_n = 10
    T11_length = 11.03

    T11_band = emis_ds.GetRasterBand(T11_n + 1)
    T11 = get_temperature(T11_band, T11_n, T11_length, emis_meta)
    print('t11')

    # T12
    T12_n = 11
    T12_length = 12.02

    T12_band = emis_ds.GetRasterBand(T12_n + 1)
    T12 = get_temperature(T12_band, T12_n, T12_length, emis_meta)
    print('t12')

    ###

    # Refs
    ref250_ds = gdal.Open(sds[4][0])
    ref250_meta = ref250_ds.GetMetadata_Dict()

    print('re250')

    global_zenith = zenith(
        gdal.Open(sds[14][0]),
        # get_zenith_array(sds[14][0]),
        ref250_ds.GetRasterBand(1).ReadAsArray().shape
    )
    print('Zenith')

    ref500_ds = gdal.Open(sds[7][0])
    ref500_meta = ref500_ds.GetMetadata_Dict()
    print('ref500')

    def get_reflectance(band, n, zenith, meta):
        scale = meta['reflectance_scales'].split(',')[n]
        try:
            scale = 1 if scale in ('-', '-0', '0-') else float(scale)
        except ValueError:
            scale = 1

        offset = meta['reflectance_offsets'].split(',')[n]
        try:
            offset = 0 if offset in ('-', '-0', '0-') else float(offset)
        except ValueError:
            offset = 0

        band_si = tr.get_ma(band.ReadAsArray())
        band_si.mask = ~((0 <= band_si) & (band_si <= 32767))

        R = reflectance(band_si, offset, scale, zenith)

        return R

    # 0.645 250 [0] (645)
    R064_n = 0
    R064_length = 0.645
    R064_band = ref250_ds.GetRasterBand(R064_n + 1)
    R064 = get_reflectance(R064_band, R064_n, global_zenith, ref250_meta)
    print('r064')

    # 0.859 250 [1] (859)
    R085_n = 1
    R085_length = 0.859
    R085_band = ref250_ds.GetRasterBand(R085_n + 1)
    R085 = get_reflectance(R085_band, R085_n, global_zenith, ref250_meta)
    print('r085')

    # 2.1 500 [6] (2130)
    R21_n = 4
    R21_length = 2.13
    R21_band = ref500_ds.GetRasterBand(R21_n + 1)
    R21 = get_reflectance(R21_band, R21_n, global_zenith, ref500_meta)
    print('r21')

    ###

    # Land water mask
    def get_land_sea_mask(path):
        path = gdal.Open(path).GetSubDatasets()[6][0]

        mask = gdal.Open(path).ReadAsArray()

        print(tr.counter(mask))
        mask = tr.get_ma(mask)
        mask.data[mask == 221] = 0
        mask.mask[mask == 221] = True

        def create_mask(mask, nums):
            new_mask = np.zeros(mask.shape) == 1
            for i in range(len(nums)):
                new_mask = np.logical_or(new_mask, mask == nums[i])

            return new_mask

        numbers = tuple(int(s) for s in input('Enter land sea mask nums: ').split()) or (2, 3)
        water_mask = create_mask(mask, numbers)
        tr.img(water_mask.astype(int), title='watermask')
        return water_mask

    water_mask = get_land_sea_mask(file03_path)
    print('water mask')
    ###

    # Shape
    if R064_band.ReadAsArray().shape != T12_band.ReadAsArray().shape:
        raise RuntimeError('shapes not same')
    else:
        global_shape = R064_band.ReadAsArray().shape
    print('shape')

    emis_ds = None
    ref250_ds = None
    ref500_ds = None

    all_mask = T4_21.mask | T4_22.mask | T11.mask | T12.mask | R064.mask | R085.mask | R21.mask

    return {
        't4_21': T4_21, 't4_22': T4_22, 't11': T11, 't12': T12,
        'r064': R064, 'r085': R085, 'r21': R21,
        'water_mask': water_mask,
        'shape': global_shape,
        'imageid': imageid,
        'all_mask': all_mask
    }


def zenith(band, shape):
    band = band.ReadAsArray()
    band = tr.get_ma(band / 100)

    vrt = ~((-180 <= band) & (band <= 180))
    band.data[vrt] = 0
    band.mask[vrt] = True

    coz = np.cos(np.radians(band))

    Z = np.kron(
        coz,
        tr.get_ma(np.ones(
            (round(shape[0] / band.shape[0]), round(shape[1] / band.shape[1]))
        ))
    )

    if shape != Z.shape:
        if shape[0] > Z.shape[0]:
            Z = np.concatenate((Z.flatten(), np.tile(Z[-1, :], shape[0] - Z.shape[0]))) \
                .reshape((shape[0], Z.shape[1]))
        elif shape[0] < Z.shape[0]:
            Z = Z[:shape[0], :]

        if shape[1] > Z.shape[1]:
            Z = np.append(Z, np.tile(Z[:, [-1]], shape[1] - Z.shape[1]), axis=1)
        elif shape[1] < Z.shape[1]:
            Z = Z[:, :shape[1]]

    return Z


def get_latlon(mod03_path: str):
    lat = gdal.Open(f'HDF4_EOS:EOS_SWATH_GEOL:"{mod03_path}":MODIS_Swath_Type_GEO:Latitude').ReadAsArray()
    lon = gdal.Open(f'HDF4_EOS:EOS_SWATH_GEOL:"{mod03_path}":MODIS_Swath_Type_GEO:Longitude').ReadAsArray()

    return {'lat': lat, 'lon': lon}


def get_fires_latlon(fires_ij, mod03_path: str):
    latlon = get_latlon(mod03_path)
    # print(latlon)

    # print(fires_ij)
    fire_latlon = np.zeros((fires_ij.shape[0], 2))
    for index, [i, j] in enumerate(fires_ij):
        fire_latlon[index] = np.array(
            [latlon['lat'][i, j], latlon['lon'][i, j]]
        )

    return fire_latlon


def brightness(band_si, scale, offset):  # RADIANCE
    L = scale * (band_si - offset)

    vrt = L <= 0
    L.data[vrt] = 0.0001
    L.mask[vrt] = True

    return L


def temperature(band_L, length):  # RADIANCE
    c1b = 1.19104282 * 10 ** 8
    c2 = 1.4387752 * 10 ** 4
    length5 = length ** (-5)

    band_T = (c2 / length) / np.log(1 + (c1b * length5) / band_L)

    return band_T


def reflectance(band_si, ref_offset, ref_scale, zenith):
    return (ref_scale * (band_si - ref_offset)) / np.cos(np.radians(zenith))


def calculate_polygon(i, j, latlon):
    lat, lon = latlon['lat'][i, j], latlon['lon'][i, j]

    try:
        up = latlon['lat'][i - 1, j]
        up = abs(lat - up) / 2
    except Exception:
        up = float('inf')

    try:
        down = latlon['lat'][i + 1, j]
        down = abs(lat - down) / 2
    except Exception:
        down = float('inf')

    if isinf(up):
        up = down
    elif isinf(down):
        down = up

    try:
        left = latlon['lon'][i, j - 1]
        left = abs(lon - left) / 2
    except Exception:
        left = float('inf')

    try:
        right = latlon['lon'][i, j + 1]
        right = abs(lon - right) / 2
    except Exception:
        right = float('inf')

    if isinf(right):
        right = left
    elif isinf(left):
        left = right

    polygon = np.zeros((4 + 1, 2))
    polygon[0] = np.array([lon - left, lat + up])
    polygon[1] = np.array([lon + right, lat + up])
    polygon[2] = np.array([lon + right, lat - down])
    polygon[3] = np.array([lon - left, lat - down])
    polygon[4] = np.array([lon - left, lat + up])

    return polygon


def get_polygons(fires_ij, mod03_path: str):
    latlon = get_latlon(mod03_path)

    fires_polygons = np.zeros((fires_ij.shape[0], 5, 2))
    for index, [i, j] in enumerate(fires_ij):
        fires_polygons[index] = calculate_polygon(i, j, latlon)

    return fires_polygons
