from QualitativeEvaluation import Aggravation, Intervention, execute_query
import matplotlib.pyplot as plt
from scipy.interpolate import spline
import numpy as np


class HierarchicalIntervention:
    def __init__(self, results_filename, headers_filename, attribute_index):
        headers_file = open(headers_filename, 'r')
        self.attributes = [x.strip() for x in headers_file.readline().split(',')]
        self.observation = self.attributes[attribute_index]
        headers_file.close()

        results = []

        # Load results
        observation_attribute = self.observation
        for explanation_attribute in self.attributes:
            if explanation_attribute == observation_attribute:
                continue

            results_file = open('results/heiint/%s/%s_%s' %
                                (results_filename, observation_attribute, explanation_attribute), 'r')

            # skip header
            results_file.readline()

            for line in results_file:
                fields = line.split(',')

                results.append({
                    'attribute': explanation_attribute,
                    'start': float(fields[4]),
                    'end': float(fields[5]),
                    'degree': float(fields[2]),
                    'cluster': [int(x) for x in fields[1].split('|')],
                    'level': int(fields[0])
                })

        self.results = results

    def top_explanation(self, level=-1):
        # TODO Get top explanation for given level(or all levels)
        filtered_explanations=self.results
        if level != -1:
            filtered_explanations = [x for x in self.results if x['level']==level]

        top_explanation = sorted(filtered_explanations, key=lambda x:x['degree'])
        if len(top_explanation) > 0:
            top_explanation = top_explanation[0]
        else:
            top_explanation = None

        return top_explanation

    def plot_evaluation(self):
        y_axis_influence = []
        y_axis_intensity = []

        x_axis = []

        min_level = min([x['level'] for x in self.results])
        max_level = max([x['level'] for x in self.results])

        observation_value = execute_query('avg(%s)' % self.observation, '1=1')
        max_observation_value = execute_query('max(%s)' % self.observation, '1=1')
        min_observation_value = execute_query('min(%s)' % self.observation, '1=1')

        observation_value_range = max_observation_value - min_observation_value

        for level in range(min_level, max_level+1):
            top_expl = self.top_explanation(level)
            influence = Intervention().judge('avg(%s)' % self.observation, top_expl['attribute'], top_expl['cluster'],
                                             top_expl['start'], top_expl['end'])
            influence = abs(influence - observation_value)/observation_value_range
            y_axis_influence.append(influence)

            itensity = Aggravation().judge('avg(%s)' % self.observation, top_expl['attribute'], top_expl['cluster'],
                                             top_expl['start'], top_expl['end'])
            intensity = abs(intensity - observation_value)/observation_value_range
            y_axis_intensity.append(intensity)

            x_axis.append(level)

        x_smooth = np.linspace(min_level, max_level, 300)
        intensity_smooth = spline(x_axis, intensity, x_smooth)
        influence_smooth = spline(x_axis, influence, x_smooth)

        plt.plot(x_smooth, intensity_smooth, color='r')
        plt.plot(x_smooth, influence_smooth, color='b')

        plt.show()


if __name__ == "__main__":
    hi = HierarchicalIntervention('yellowdata_pickup.csv', 'yellowdata.header', 5)
    hi.plot_evaluation()
