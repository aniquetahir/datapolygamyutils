#!/usr/bin/env python3
import json
import sys
import matplotlib.pyplot as plt
import numpy as np
from descartes import PolygonPatch
from shapely.geometry import Polygon
from matplotlib.collections import PatchCollection
import matplotlib as mpl
from QualitativeEvaluation import execute_zone_count_query, execute_query
from plot_hi_graph import HierarchicalIntervention

class Map:
    def __init__(self, nbhd_file):
        self.nbhds = None
        self.__load_nbhd(nbhd_file)
        pass

    def __load_nbhd(self, nbhd_file):
        """
        Loads the neighbourhood file(the polygons on the map)
        :param nbhd_file: the path to the neighbourhood file
        :return:
        """
        # TODO
        nbhds = []
        n = 2
        nbhd_file = open(nbhd_file, 'r')
        poly_id = nbhd_file.readline()

        while poly_id != '':
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
            nbhds.append({'id': poly_id, 'shape': polygons})
            poly_id = nbhd_file.readline()

        nbhd_file.close()
        self.nbhds = nbhds

    def __get_color(self, color_low, color_high, data_min, data_max, value ):
        fcolor_r = np.interp(value, [data_min, data_max], [color_low[0], color_high[0]])
        fcolor_g = np.interp(value, [data_min, data_max], [color_low[1], color_high[1]])
        fcolor_b = np.interp(value, [data_min, data_max], [color_low[2], color_high[2]])

        return (fcolor_r, fcolor_g, fcolor_b)

    def draw_data(self, data):
        """
        Produces a cartogram from the json data provided
        :param json: The json string representing zones and their corresponding values
        :return:
        """
        edge_color = '#000000'

        color_high = np.array([255, 153, 0])/255
        color_low = np.array((0, 0, 255))/255

        data_min = float('inf')
        data_max = -float('inf')

        for zone in self.nbhds:
            zone_id = zone['id']
            related_rows = [x for x in data if x['zone'] == zone_id]
            total_value = None
            if len(related_rows)>0:
                total_value = sum([x['value'] for x in related_rows])

            if total_value:
                # Set minimums and maximums
                if total_value > data_max:
                    data_max = total_value
                if total_value < data_min:
                    data_min = total_value


        # Create patches from data
        patches = []
        for zone in self.nbhds:
            zone_id = zone['id']
            zone_shape = zone['shape']

            # Get value for zone from data
            related_rows = [x for x in data if x['zone']==zone_id]
            if len(related_rows)==0:
                continue

            total_value = sum([x['value'] for x in related_rows])

            # Get color from value
            fcolor = self.__get_color(color_low, color_high, data_min, data_max, total_value)

            for idx, poly in enumerate(zone_shape):
                patches.append(PolygonPatch(poly, fc=fcolor, ec=edge_color, lw=0.2, alpha=1., zorder=1))

        # TODO Create Color line
        cbar_axis = np.arange(data_min, data_max, (data_max-data_min)/100.0)
        cbar_colors = list(map(lambda x: self.__get_color(color_low, color_high, data_min, data_max, x), cbar_axis))
        cmap = mpl.colors.ListedColormap(cbar_colors)


        fig, ax = plt.subplots()
        # lower left minx miny , upper right maxx maxy
        bounds = [-74.25, 40.5, -73.7, 40.9]
        minx, miny, maxx, maxy = bounds
        w, h = maxx - minx, maxy - miny
        ax.set_xlim(minx - 0.2 * w, maxx + 0.2 * w)
        ax.set_ylim(miny - 0.2 * h, maxy + 0.2 * h)
        ax.set_aspect(1)

        ax.add_collection(PatchCollection(patches, match_original=True))
        cax = fig.add_axes([0.90, 0.05, 0.02, 0.92])

        cbar_ticks = list(np.arange(data_min, data_max, (data_max-data_min)/5))
        norm = mpl.colors.Normalize(vmin=data_min, vmax=data_max)
        cb1 = mpl.colorbar.ColorbarBase(cax, cmap=cmap,
                                        norm=norm, orientation='vertical')
        #cb1.set_ticks(cbar_ticks)
        #cb1.ax.set_xticklabels([str(x) for x in cbar_ticks])


        plt.show()


def test_class():
    hi = HierarchicalIntervention('yellowdata_pickup.csv', 'yellowdata.header', 5)

    observation_value = execute_query('avg(%s)' % hi.observation, '1=1')

    # Plot map for top explanation
    top_explanation = hi.top_explanation(observation_value,3)

    explanation_predicate = hi.get_predicate(top_explanation['attribute'],
                                             top_explanation['cluster'],
                                             top_explanation['start'],
                                             top_explanation['end'])

    explanation_predicate = "not (%s)" % explanation_predicate
    test_data = execute_zone_count_query('zone', explanation_predicate)
    test_data = json.loads(test_data)
    test_data = [{'zone': x['zone'], 'value': x['count']} for x in test_data]

    map = Map('neighborhood.txt')
    map.draw_data(test_data)


if __name__ == "__main__":
    test_class()
    exit(0)
    json_string = ""
    if len(sys.argv)>1:
        json_file = open(sys.argv[1], 'r')
        json_string = "".join(json_file.readlines())
        json_file.close()
    else:
        for line in sys.stdin:
            json_string += line

    if json_string != '':
        map = Map("neighborhood.txt")
        map.draw_data(json.loads(json_string))
    else:
        raise Exception("Please input valid json for displaying data")

