from random import shuffle, randint
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.collections import PatchCollection
# from mpl_toolkits.basemap import Basemap
#from shapely.geometry import Point, MultiPoint, MultiPolygon, Polygon
from descartes import PolygonPatch
import sys
import json

def get_nbhds(nf):
    nbhds = []
    n=2
    nbhd_file = open(nf, 'r')
    poly_id = nbhd_file.readline()

    while poly_id!='':
        poly_id = int(poly_id)
        polygons = []
        num_polys = int(nbhd_file.readline())

        for i_poly in range(num_polys):
            points = []
            num_points = int(nbhd_file.readline())

            for i_point in range(num_points):
                point_coords = [float(x) for x in nbhd_file.readline().split(' ')]
                points.append((point_coords[0], point_coords[1]))

            polygons.append(points)
        nbhds.append({'id': poly_id, 'shape': polygons})
        poly_id = nbhd_file.readline()

    nbhd_file.close()
    return nbhds

def plot_regions(aggregate_data, steps, nf):
    data_min = float('inf')
    data_max = -float('inf')
    # Get value bounds
    for datum in aggregate_data:
        if datum['value'] > data_max:
            data_max = datum['value']
        if datum['value'] < data_min:
            data_min = datum['value']

    data_diff = data_max - data_min

    # lower left minx miny , upper right maxx maxy
    # bounds = [-74.25, 40.5, -73.7, 40.9]
    # minx, miny, maxx, maxy = bounds
    # w, h = maxx - minx, maxy - miny

    # Get a few Polygons
    neighborhoods = get_nbhds(nf)

    # fig = plt.figure()
    # w, h = maxx - minx, maxy - miny

    max_sig_avg = float('inf')
    min_sig_avg = -float('inf')

    timeline = []
    for time_step in range(steps):
        patches=[]
        # filter data for time step
        filtered_data = [x for x in aggregate_data if x['step'] == time_step]
        for zone in neighborhoods:

            # get tuple for this zone
            this_zone = [x for x in filtered_data if x['zone'] == zone['id']]
            edge_color = '#000000'
            if len(this_zone) > 0:
                this_zone = this_zone[0]
                this_zone_value = this_zone['value']
                this_zone_feature = this_zone['feature']

                if this_zone_feature == 4:
                    if this_zone_value > min_sig_avg:
                        min_sig_avg = this_zone_value
                elif this_zone_feature == 2:
                    if this_zone_value < max_sig_avg:
                        max_sig_avg = this_zone_value
            if zone['id'] == 137:
                edge_color = '#ff0000'
            for idx, poly in enumerate(zone['shape']):
                patches.append({
                    'id': zone['id'],
                    'shape': poly,
                    'feature': this_zone_feature,
                    'value': this_zone_value
                })
        timeline.append({
            'timestep': time_step,
            'patches': patches
        })

    data = {
        'timeline': timeline,
        'stats': {
            'min': data_min,
            'max': data_max,
            'salient_min': min_sig_avg,
            'salient_max': max_sig_avg
        }
    }

    print(json.dumps(data))


if __name__ == "__main__":
    aggregates_filename = sys.argv[1]
    index_filename = sys.argv[2]
    temporal_res = int(sys.argv[3])
    spatial_res = 3 # 3-nbhd, 6-zipcode
    attribute_index = int(sys.argv[4])
    neighborhood_filename = sys.argv[5]

    # filter out desired data
    data_index = []
    index_file = open(index_filename, 'r')
    for line in index_file:
        [keys, values] = [x.strip().split(',') for x in line.split('\t') if x]
        [line_dataid, line_att_index, line_temp_res, line_spatial_res] = [int(x) for x in keys]
        if temporal_res == line_temp_res and spatial_res == line_spatial_res \
                and attribute_index == line_att_index and values[2] == 'false':
            line_spatial_index = int(values[1])
            line_start = int(values[3])
            line_end = int(values[4])
            line_values = [int(x) for x in values[5:]]
            data_index.append({
                'start': line_start,
                'end': line_end,
                'zone': line_spatial_index,
                'data': line_values
            })
    index_file.close()

    data_aggregates = []
    aggregates_file = open(aggregates_filename, 'r')
    for line in aggregates_file:
        [keys, values] = [x.strip().split(',') for x in line.split('\t') if x]
        keys = [int(x) for x in keys]
        values = [float(x) for x in values]
        [line_temporal_index, line_spatial_index, dataset_index, line_temp_res, line_spatial_res] = keys
        line_attribute_value = values[attribute_index]
        if line_temp_res == temporal_res and line_spatial_res == spatial_res:
            data_aggregates.append({
                'zone': line_spatial_index,
                'time': line_temporal_index,
                'value': line_attribute_value
            })
    aggregates_file.close()

    num_steps = len(data_index[0]['data'])
    start = data_index[0]['start']
    step_size = (data_index[0]['end']-start)/num_steps
    if step_size == 0:
        step_size = 1

    # Add feature data in aggregates
    for aggregate in data_aggregates:
        step = np.floor( (aggregate['time']-start)/step_size )
        step = int(step)
        if step == num_steps:
            step = step-1

        aggregate['step'] = int(step)
        for d_index in data_index:
            if d_index['zone'] == aggregate['zone']:
                if 'feature' in aggregate:
                    print('feature already exists.')
                aggregate['feature'] = d_index['data'][step]
                aggregate['step'] = step

    # Interpolation
    plot_regions(data_aggregates, num_steps, neighborhood_filename)

