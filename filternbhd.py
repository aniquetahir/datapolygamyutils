import sys
from shapely.geometry import Polygon, Point, MultiPolygon

def get_nbhds(filename):
    nbhds = []
    n=2
    nbhd_file = open(filename, 'r')
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

if __name__ == "__main__":
    neighbourhood_filename = sys.argv[1]
    input_filename = sys.argv[2]
    output_filename = sys.argv[3]
    lat_index = int(sys.argv[4])
    lng_index = int(sys.argv[5])
    nbdh_id = int(sys.argv[6])
    useHeader = False
    if len(sys.argv)>7:
        useHeader = bool(int(sys.argv[7]))

    nbhds = get_nbhds(neighbourhood_filename)
    req_nbhd = [x for x in nbhds if x['id'] == nbdh_id]
    if len(req_nbhd)==0:
        print('Cannot find desired nbhd')
        sys.exit(1)
    else:
        req_nbhd = req_nbhd[0]['shape']

    input = open(input_filename, 'r')
    output = open(output_filename, 'w')

    if useHeader:
        input.readline()

    for line in input:
        attrs = line.split(',')
        lat = float(attrs[lat_index])
        lng = float(attrs[lng_index])
        point = Point(lng, lat)
        if req_nbhd.contains(point):
            output.write(line)

    input.close()
    output.flush()
    output.close()

