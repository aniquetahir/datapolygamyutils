import sys
import matplotlib.pyplot as plt

def translate_index(index, intensity=2):
    if index==4:
        return intensity
    elif index==2:
        return -intensity
    else:
        return 0

def seperate_neg_pos(time,values):
    negative = [[],[]]
    positive = [[],[]]
    for i in range(len(values)):
        if values[i]<0:
            negative[0].append(time[i])
            negative[1].append(-values[i])
        else:
            positive[0].append(time[i])
            positive[1].append(values[i])

    return negative, positive

def plot_index(index_filename, temporal_res, spatial_res, spatial_index, attribute_index):
    index_file = open(index_filename, 'r')

    data = []
    start = 0
    end = 0
    step = 0

    for line in index_file:
        [key, value] = [x.strip() for x in line.split('\t', 2) if x]
        keys = key.split(',')
        values = value.split(',')

        line_att_index = int(keys[1])
        line_temp_res = int(keys[2])
        line_spatial_res = int(keys[3])
        line_spatial_index = int(values[1])
        outlier = values[2]
        if line_temp_res == temporal_res and line_spatial_res == spatial_res and \
                        line_spatial_index == spatial_index and line_att_index == attribute_index and outlier == 'false':
            start = int(values[3])
            end = int(values[4])
            data = list(map(lambda x: int(x), values[5:]))
            break

    step = (end - start) / len(data)
    index_file.close()

    data = list(map(translate_index, data))
    x = list(range(start, end, int(step)))[:len(data)]

    negative, positive = seperate_neg_pos(x, data)
    plt.title('Index for resolution(t/s):%i/%i at spatial index %i' % (temporal_res, spatial_res, spatial_index))
    plt.ylabel('Tip Percentage')
    plt.xlabel('Time(seconds from enoch)')

    plt.tick_params(labelleft='off')
    pos_bar = plt.bar(positive[0], positive[1], step, label="Positive Salient Features", color='g')
    neg_bar = plt.bar(negative[0], negative[1], step, label="Negative Salient Features", color='r')
    if len(negative[0]) != 0 and len(positive[0]) != 0:
        plt.legend((pos_bar, neg_bar), ("Positive Features", "Negative Features"))

def plot_aggregates(aggregate_filename, temporal_res, spatial_res, spatial_index, attribute_index):
    aggregate_file = open(aggregate_filename, 'r')
    points = []
    max_val = -float('inf')
    for line in aggregate_file:
        [key, value] = [x.strip() for x in line.split('\t') if x]
        keys = key.split(',')
        values = value.split(',')
        line_temp_index = int(keys[0])
        line_spatial_index = int(keys[1])
        line_temp_res = int(keys[3])
        line_spatial_res = int(keys[4])

        attribute_value = float(values[attribute_index])
        if line_temp_res == temporal_res and line_spatial_res == spatial_res and line_spatial_index == spatial_index:
            if attribute_value>max_val:
                max_val = attribute_value
            points.append({'x': line_temp_index, 'y': attribute_value})

    aggregate_file.close()
    points = sorted(points, key=lambda e: e['x'])
    x = list( map(lambda e: e['x'], points) )
    y = list( map(lambda e: (e['y']/max_val) * 2, points) )
    plt.plot(x, y)

if __name__ == "__main__":
    index_filename = sys.argv[1]
    aggregate_filename = sys.argv[2]
    temporal_res = int(sys.argv[3])
    spatial_res = int(sys.argv[4])
    spatial_index = int(sys.argv[5])
    attribute_index = int(sys.argv[6])

    plot_index(index_filename, temporal_res, spatial_res, spatial_index, attribute_index)
    plot_aggregates(aggregate_filename, temporal_res, spatial_res, spatial_index, attribute_index)

    plt.show()