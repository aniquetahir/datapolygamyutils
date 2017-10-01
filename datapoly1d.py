import matplotlib.pyplot as plt
import sys
import numpy as np
from io import StringIO
from datetime import datetime, timedelta

class DataPolygamy:
    def __init__(self, aggregates_filename, headers_filename, temporal_resolution, observation):
        self.observation_index = observation
        self.aggregates = []
        self.headers = []
        self.temporal_resolution = int(temporal_resolution)
        self.__load_header(headers_filename)
        self.__load_aggregates(aggregates_filename)

    def __load_header(self, filename):
        header_file = open(filename, 'r')
        line = header_file.readline()
        self.headers = line.split(',')
        header_file.close()

    def __load_aggregates(self, filename):
        aggregates_file = open(filename, 'r')
        for line in aggregates_file:
            [keys, values] = [x.strip().split(',') for x in line.split('\t') if x]
            [time, zone, dataset, temp_res, spatial_res] = [int(x) for x in keys]
            row_count = int(float(values[0]))
            row_averages = [float(x) for x in values]
            self.aggregates.append({
                'time': time,
                'zone': zone,
                'temp_res': temp_res,
                'spatial_res': spatial_res,
                'count': row_count,
                'averages': row_averages
            })
        aggregates_file.close()

    def plot_attributes(self):
        fig = plt.figure()
        num_attrs = len(self.aggregates[0]['averages'])

        # Filter the temporal resolution
        filtered_data = [
            x for x in self.aggregates
            if x['temp_res'] == self.temporal_resolution and x['spatial_res'] == 3 ]

        #filtered_data = sorted(filtered_data, key=lambda x: x['time'])
        x_axis = [x['time'] for x in filtered_data]
        x_axis = set(x_axis)
        plot_data = []
        for time_value in x_axis:
            y_values = [x for x in filtered_data if x['time'] == time_value]
            sums = [np.array(x['averages'])*x['count'] for x in y_values]
            total_count = sum([x['count'] for x in y_values])
            total_sum = np.sum(sums, axis=0)
            avg_vals = total_sum/total_count
            plot_data.append({
                'x': time_value,
                'y': list(avg_vals)
            })

        plot_data = sorted(plot_data, key= lambda x: x['x'])

        num_columns = np.ceil(num_attrs/2)

        for i in range(num_attrs):
            ax = fig.add_subplot(num_columns, 2, i+1)
            x_axis = [x['x'] for x in plot_data]
            y_axis = [x['y'][i] for x in plot_data]
            maxval = max(y_axis)
            minval = min(y_axis)
            valdiff = maxval-minval

            for j, val in enumerate(y_axis):
                epoch = datetime.utcfromtimestamp(0)
                date = epoch + timedelta(seconds=x_axis[j])
                if date.day == 23:
                    ax.annotate('blizzard/travel ban', xy=(x_axis[j], val), xytext=(x_axis[j], minval-valdiff*0.25),
                                arrowprops=dict(arrowstyle="->",
                                                connectionstyle="arc3"),)
                if date.day == 4:
                    ax.annotate('CN Market Crash\nFirearm Exc. Order', xy=(x_axis[j], val), xytext=(x_axis[j], minval-valdiff*0.25),
                                arrowprops=dict(arrowstyle="->",
                                                connectionstyle="arc3"), bbox=dict(fc='green'))
                # elif date.day == 24:
                #     ax.annotate('blizzard/travel ban end', xy=(x_axis[j], val),
                #                xytext=(x_axis[j], minval - valdiff * 0.5),
                #                arrowprops=dict(facecolor='black', shrink=0.05), )
                if val>minval+((maxval-minval)*0.90) or val<minval+((maxval-minval)*0.10):
                    # Get time

                    # Print data
                    print('%s\nDate:%s, Value:%.2f\n' % (self.headers[i], date.strftime('%x'), val))
            if i == self.observation_index:
                ax.plot(x_axis, y_axis, color='red')
            else:
                ax.plot(x_axis, y_axis)
            ax.set_xlabel('time')
            ax.set_xticks([])
            ax.set_ylabel(self.headers[i])
        plt.tight_layout()

        img_data = StringIO()

        plt.savefig(img_data, transparent=True, format='svg')
        #img_data.seek(0)
        print(img_data.getvalue())

if __name__ == '__main__':
    aggregates_filename = sys.argv[1]
    headers_filename = sys.argv[2]
    temp_res = sys.argv[3]
    observation_attribute = int(sys.argv[4])
    dp = DataPolygamy(aggregates_filename, headers_filename, temp_res, observation_attribute)
    dp.plot_attributes()
