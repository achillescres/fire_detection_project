import numpy as np
import troubles as tr

# Classes
# Unknown 0
# Cloud 1
# Water 2
# Non fire 3
# Fire 4


def classify_fires(data, day_time):
    # Temps
    t4_21 = data['t4_21']
    t4_22 = data['t4_22']
    t11 = data['t11']
    t12 = data['t12']

    # Refs
    r064 = data['r064']
    r085 = data['r085']
    r21 = data['r21']
    # Water mask
    water_mask = data['water_mask']

    # Customing t4
    t4 = t4_22.copy()
    t4_vrt = (t4_22 >= 331) | t4_22.mask
    t4[t4_vrt] = t4_21[t4_vrt]
    t4.mask[t4_21.mask & t4_vrt] = True
    print('Mounted data')

    # Classifying
    # Blank
    classed = tr.get_ma(np.zeros(data['shape'], dtype=int))
    print('ABS', tr.counter(classed.data))
    print('Created blank array')

    # Cloud mask 1
    classed = cloud(day_time, classed, r064, r085, t12)
    print('ABS', tr.counter(classed.data))
    print('Cloud masked')

    # Water mask 2
    classed[water_mask & (~classed.mask)] = 2
    classed.mask[water_mask & (~classed.mask)] = True
    print('ABS', tr.counter(classed.data))
    print('Water masked')

    # Show water_cloud mask
    tr.img(classed.data, 'Masked')
    tr.img(t4, 'T4')
    tr.img(t11, 'T11')
    tr.img(t12, 'T12')

    # Mark non potential fire
    classed = potential_fire(day_time, classed, t4, t11, r085)
    print('ABS', tr.counter(classed.data))
    print('Potential masked')
    tr.img(classed.data, 'PotentialFire Last')

    # Absolute temp threshold
    classed = absolute_fire(day_time, classed, t4)
    print('ABS', tr.counter(classed.data))
    print('Absolute thresholded')
    tr.img(classed.data, 'Absolute threshold')

    # Fires total
    fires = np.zeros(classed.shape, dtype=int)
    fires[classed.data == 4] = 1
    print('ABS', tr.counter(fires.data))
    print('Fires')
    tr.img(fires, 'Fires')

    return {'fires': fires, 't4': t4, 'classed': classed}


def cloud(time, classed: np.ma.masked_array, r064, r085, t12):
    if time == 'day':
        vrt = ((r064 + r085) > 0.9) | (t12 < 265) | (((r064 + r085) > 0.7) & (t12 < 285))
        classed[vrt & (~classed.mask)] = 1
        classed.mask[vrt] = True
    elif time == 'night':
        vrt = (t12 < 265)
        classed[vrt & (~classed.mask)] = 1
        classed.mask[vrt] = True
    else:
        raise RuntimeError("var time must be 'day' or 'night'!")

    return classed


def potential_fire(time, classed, t4, t11, r085):
    dT = t4 - t11
    tr.img(dT, 'Delta T')
    tr.img(r085, 'R085')
    if time == 'day':
        vrt = ~((t4 > 290) & (dT > 10) & (r085 < 0.3))
        classed[vrt] = 3
        classed.mask[vrt] = True
    elif time == 'night':
        vrt = ~((t4 > 280) & (dT > 10))
        classed[vrt & (~classed.mask)] = 3
        classed.mask[vrt] = True
    else:
        raise RuntimeError("var time must be 'day' or 'night'!")

    return classed


def absolute_fire(time, classed, t4):
    import troubles as tr
    if time == 'day':
        vrt = (t4 >= 310) & (~classed.mask)
        # tr.img(vrt.astype(int), 'VRT')
        classed[vrt & (~classed.mask)] = 4
        classed.mask[vrt & (~classed.mask)] = True
    elif time == 'night':
        vrt = (t4 > 320) & (~classed.mask)
        classed[vrt & (~classed.mask)] = 4
        classed.mask[vrt & (~classed.mask)] = True
    else:
        raise RuntimeError("var time must be 'day' or 'night'!")

    return classed