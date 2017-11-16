from random import shuffle, randint
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.collections import PatchCollection
from mpl_toolkits.basemap import Basemap
from shapely.geometry import Point, MultiPoint, MultiPolygon, Polygon
from descartes import PolygonPatch
import sys

def get_nbhds():
    nbhds = []
    n=2
    nbhd_file = open('neighborhood.txt', 'r')
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

            polygons.append(Polygon(points))
        mp = MultiPolygon(polygons=polygons)
        nbhds.append({'id': poly_id, 'shape': mp})
        poly_id = nbhd_file.readline()

    nbhd_file.close()
    return nbhds

def plot_regions(aggregate_data, steps):
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
    bounds = [-74.25, 40.5, -73.7, 40.9]
    minx, miny, maxx, maxy = bounds
    w, h = maxx - minx, maxy - miny

    # Get a few Polygons
    neighborhoods = get_nbhds()

    fig = plt.figure()
    w, h = maxx - minx, maxy - miny

    max_sig_avg = float('inf')
    min_sig_avg = -float('inf')

    # Plot observation
    ax = fig.add_subplot(121)
    ax.set_xlim(minx - 0.2 * w, maxx + 0.2 * w)
    ax.set_ylim(miny - 0.2 * h, maxy + 0.2 * h)
    ax.set_aspect(1)

    patches = []
    for zone in neighborhoods:
        edge_color = '#000000'
        if zone['id'] == 137:
            edge_color = '#ff0000'
        for idx, poly in enumerate(zone['shape']):
            patches.append(PolygonPatch(poly, fc=edge_color, ec=edge_color, lw=0.2, alpha=1., zorder=1))

    ax.add_collection(PatchCollection(patches, match_original=True))
    ax.set_xticks([])
    ax.set_yticks([])
    plt.title("Observation(Pickup Location)")

    time_step=0
    ax = None
    # if steps == 1:
    ax = fig.add_subplot(122)
    # else:
    #     ax = fig.add_subplot(1, 2, time_step+1)
    ax.set_xlim(minx - 0.2 * w, maxx + 0.2 * w)
    ax.set_ylim(miny - 0.2 * h, maxy + 0.2 * h)
    ax.set_aspect(1)

    # filter data for time step
    filtered_data = [x for x in aggregate_data if x['step'] == time_step]

    cm = plt.get_cmap('RdYlGn')
    #num_colours = len(neighborhoods)

    patches = []
    for zone in neighborhoods:

        # get tuple for this zone
        this_zone = [x for x in filtered_data if x['zone'] == zone['id']]
        edge_color = '#000000'
        if len(this_zone) > 0:
            this_zone = this_zone[0]
            this_zone_value = this_zone['value']
            this_zone_feature = this_zone['feature']
            # color = cm(1. * zone['id'] / num_colours)
            color = cm((this_zone_value - data_min)/data_diff)

            if this_zone_feature == 4:
                edge_color = '#005ef7' #blue
                if this_zone_value > min_sig_avg:
                    min_sig_avg = this_zone_value
            elif this_zone_feature == 2:
                edge_color = '#e600f7' #violet
                if this_zone_value < max_sig_avg:
                    max_sig_avg = this_zone_value

        for idx, poly in enumerate(zone['shape']):
            patches.append(PolygonPatch(poly, fc=edge_color, ec=edge_color, lw=0.2, alpha=1., zorder=1))

    ax.add_collection(PatchCollection(patches, match_original=True))
    ax.set_xticks([])
    ax.set_yticks([])
    plt.title("Explanation(Dropoff Locations)")
    # plt.tight_layout()

    positive_salient_patch = mpatches.Patch(color='#005ef7', label='Positive Zone')
    negative_salient_patch = mpatches.Patch(color='#e600f7', label='Negative Zone')
    insig_salient_patch = mpatches.Patch(color='#000000', label='Insignificant Zone')
    observation_patch = mpatches.Patch(color='#ff0000')

    fig.legend((positive_salient_patch, negative_salient_patch, observation_patch),
               ('Tip Percentage <≈ %.2f' % (min_sig_avg*100), 'Tip Percentage >≈ %.2f' % (max_sig_avg*100), 'Observation'),
               loc='lower right')
    plt.show()


if __name__ == "__main__":
    aggregates_filename = sys.argv[1]
    index_filename = sys.argv[2]
    temporal_res = int(sys.argv[3])
    spatial_res = 3 # 3-nbhd, 6-zipcode
    attribute_index = int(sys.argv[4])

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
    plot_regions(data_aggregates, num_steps)

