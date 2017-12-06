import calculate_salient_explanation, \
    top_aggravation_explanations, \
    top_intervention_explanations, \
    top_heiint_explanations
import subprocess
import matplotlib.pyplot as plt
import numpy as np

attributes = []
processor_home = '/home/anique/IdeaProjects/yellowtaxi'
data_file = "yellowdata_pickup.csv"
observation_att = 3


def execute_query(observation, predicate):
    query = subprocess.run([
        'java',
        '-cp',
        '%s/target/yellowtaxi-1.0-SNAPSHOT-jar-with-dependencies.jar' % processor_home,
        'edu.asu.query.Query',
        "%s/data/%s" % (processor_home, data_file),
        predicate,
        observation
    ], stdout=subprocess.PIPE)

    return float(query.stdout.decode('utf-8'))


def plot_explanations(data, ylabel, title):
    fig, ax = plt.subplots()

    xaxis = list(range(1, len(data)+1))
    width = 0.75

    rects = ax.bar(xaxis, data, width, color='b')
    ax.set_ylabel(ylabel)
    ax.set_xlabel("rank")
    ax.set_title(title)
    fig.savefig("evaluation/%s/%s.svg" % (ylabel, title))


def plot_explanation_comparison(datum, ylabel, title, legend):
    fig, ax = plt.subplots()

    colors = ['r', 'g', 'b', 'y']

    d_width = 0.9
    width = d_width/len(datum)
    xaxis = np.array(list(range(1, 5 + 1)))

    rects_array = []
    legend_label_array = []
    for i, data in enumerate(datum):

        rects = ax.bar(xaxis+i*width, data, width, color=colors[i])
        rects_array.append(rects)
        legend_label_array.append(legend[i])

    ax.legend(rects_array, legend_label_array)
    ax.set_ylabel(ylabel)
    ax.set_xticks(xaxis + d_width / 2)
    ax.set_xticklabels(('1', '2', '3', '4', '5'))
    ax.set_xlabel("rank")
    ax.set_title(title)
    fig.savefig("evaluation/%s/%s.eps" % (ylabel, title))


class Aggravation:
    def __init__(self):
        pass

    def judge(self, observation, attribute, zones, min, max):
        """
        :param attribute: the attribute in the explanation predicate
        :param zones: the zones in the explanation predicate
        :param buckets: the bucket for the explanation predicate
        :return: the degree of explanation by aggravation(intensity) for the provided input
        """
        # Create predicate
        predicate = ",".join([str(x) for x in zones])
        if predicate is '':
            predicate = '1==1'
        else:
            predicate = "zone in (%s)" % predicate
        if min:
            predicate = "%s and %s>%f" % (predicate, attribute, min)

        if max:
            predicate = "%s and %s<%f" % (predicate, attribute, max)

        # Create subprocess
        query = subprocess.run([
            'java',
            '-cp',
            '%s/target/yellowtaxi-1.0-SNAPSHOT-jar-with-dependencies.jar'%processor_home,
            'edu.asu.query.Query',
            "%s/data/%s" % (processor_home, data_file),
            predicate,
            observation
        ], stdout=subprocess.PIPE)

        # Return subprocess output
        return float(query.stdout.decode('utf-8'))


class Intervention:
    def __init__(self):
        pass

    def judge(self, observation, attribute, zones, min, max):
        """
        :param attribute: the attribute in the explanation predicate
        :param zones: the zones in the explanation predicate
        :param buckets: the bucket for the explanation predicate
        :return: the degree of explanation by intervention(influence) for the provided input
        """
        # Create predicate
        predicate = ",".join([str(x) for x in zones])
        if predicate is '':
            predicate = '1==1'
        else:
            predicate = "zone in (%s)" % predicate
        if min:
            predicate = "%s and %s>%f" % (predicate, attribute, min)

        if max:
            predicate = "%s and %s<%f" % (predicate, attribute, max)

        predicate = "not (%s)" % predicate

        # Create subprocess
        query = subprocess.run([
            'java',
            '-cp',
            '%s/target/yellowtaxi-1.0-SNAPSHOT-jar-with-dependencies.jar'%processor_home,
            'edu.asu.query.Query',
            "%s/data/%s" % (processor_home, data_file),
            predicate,
            observation
        ], stdout=subprocess.PIPE)

        # Return subprocess output
        return float(query.stdout.decode('utf-8'))


def evaluate_salient_features():
    # Evaluate tip percentage

    # Get Top 5 explanations
    top_five = calculate_salient_explanation.top_explanations(observation_att, 'index/data')
    intensity = []
    influence = []
    observation = "avg(%s)" % attributes[observation_att]
    for explanation in top_five:
        if explanation['score'] > 0:
            zones = list(map(lambda x: x['zone'], explanation['positive']))
        else:
            zones = list(map(lambda x: x['zone'], explanation['negative']))

        attribute = attributes[explanation['attribute']]

        intensity.append(Aggravation().judge(observation, attribute, list(zones), None, None))
        influence.append(Intervention().judge(observation, attribute, list(zones), None, None))

    # TODO Draw Graph
    method_name = "Salient Features"
    # plot_explanations(intensity, "intensity", "Top explanations for %s[%s]" % (observation, method_name))
    # plot_explanations(influence, "influence", "Top explanations for %s[%s]" % (observation, method_name))
    return {
        'intensity': intensity,
        'influence': influence,
        'observation': observation,
        'method': method_name
    }


def evaluate_aggravation():
    # Evaluate tip percentage

    # Get top 5 explanations
    intensity = []
    influence = []
    top_five = top_aggravation_explanations.top_explanations(observation_att, 'yellowdata.header',
                                                             'yellowdata_pickup.csv', None)
    observation = "avg(%s)" % attributes[observation_att]

    for explanation in top_five['high']:
        agg_index = Aggravation().judge(observation,
                            explanation['attribute'],
                            [explanation['zone']],
                            explanation['start'],
                            explanation['end'])
        intensity.append(agg_index)

        int_index = Intervention().judge(observation,
                            explanation['attribute'],
                            [explanation['zone']],
                            explanation['start'],
                            explanation['end'])
        influence.append(int_index)

    # TODO plot graph
    method_name = "Aggravation"
    # plot_explanations(intensity, "intensity", "Top explanations for %s[%s]" % (observation, method_name))
    # plot_explanations(influence, "influence", "Top explanations for %s[%s]" % (observation, method_name))
    return {
        'intensity': intensity,
        'influence': influence,
        'observation': observation,
        'method': method_name
    }


def evaluate_intervention():
    # Evaluate tip percentage

    # Get top 5 explanations
    intensity = []
    influence = []
    top_five = top_intervention_explanations.top_explanations(observation_att, 'yellowdata.header',
                                                             'yellowdata_pickup.csv', None)
    observation = "avg(%s)" % attributes[observation_att]

    for explanation in top_five['high']:
        agg_index = Aggravation().judge(observation,
                            explanation['attribute'],
                            [explanation['zone']],
                            explanation['start'],
                            explanation['end'])
        intensity.append(agg_index)

        int_index = Intervention().judge(observation,
                            explanation['attribute'],
                            [explanation['zone']],
                            explanation['start'],
                            explanation['end'])
        influence.append(int_index)

    # TODO plot graph
    method_name = "Intervention"
    # plot_explanations(intensity, "intensity", "Top explanations for %s[%s]" % (observation, method_name))
    # plot_explanations(influence, "influence", "Top explanations for %s[%s]" % (observation, method_name))
    return {
        'intensity': intensity,
        'influence': influence,
        'observation': observation,
        'method': method_name
    }


def evaluate_heirarchical_intervention():
    # Evaluate tip percentage

    # Get top 5 explanations
    intensity = []
    influence = []
    top_five = top_heiint_explanations.top_explanations(observation_att, 'yellowdata.header',
                                                             'yellowdata_pickup.csv', None)
    observation = "avg(%s)" % attributes[observation_att]

    for explanation in top_five['high']:
        agg_index = Aggravation().judge(observation,
                            explanation['attribute'],
                            explanation['zones'],
                            explanation['start'],
                            explanation['end'])
        intensity.append(agg_index)

        int_index = Intervention().judge(observation,
                            explanation['attribute'],
                            explanation['zones'],
                            explanation['start'],
                            explanation['end'])
        influence.append(int_index)

    # TODO plot graph
    method_name = "Hierarchical Intervention"
    # plot_explanations(intensity, "intensity", "Top explanations for %s[%s]" % (observation, method_name))
    # plot_explanations(influence, "influence", "Top explanations for %s[%s]" % (observation, method_name))
    return {
        'intensity': intensity,
        'influence': influence,
        'observation': observation,
        'method': method_name
    }


def evaluate_nonspatial_aggravation():
    # Get top 5 explanations
    intensity = []
    influence = []
    top_five = top_aggravation_explanations.top_nonspatial_explanations(observation_att, 'yellowdata.header',
                                                             'yellowdata_pickup.csv')
    observation = "avg(%s)" % attributes[observation_att]

    for explanation in top_five['high']:
        agg_index = Aggravation().judge(observation,
                            explanation['attribute'],
                            [],
                            explanation['start'],
                            explanation['end'])
        intensity.append(agg_index)

        int_index = Intervention().judge(observation,
                            explanation['attribute'],
                            [],
                            explanation['start'],
                            explanation['end'])
        influence.append(int_index)

    # TODO plot graph
    method_name = "Non Spatial Aggravation"
    # plot_explanations(intensity, "intensity", "Top explanations for %s[%s]" % (observation, method_name))
    # plot_explanations(influence, "influence", "Top explanations for %s[%s]" % (observation, method_name))
    return {
        'intensity': intensity,
        'influence': influence,
        'observation': observation,
        'method': method_name
    }


def evaluate_nonspatial_intervention():
    intensity = []
    influence = []
    top_five = top_intervention_explanations.top_nonspatial_explanations(observation_att, 'yellowdata.header',
                                                             'yellowdata_pickup.csv')
    observation = "avg(%s)" % attributes[observation_att]

    for explanation in top_five['high']:
        agg_index = Aggravation().judge(observation,
                            explanation['attribute'],
                            [],
                            explanation['start'],
                            explanation['end'])
        intensity.append(agg_index)

        int_index = Intervention().judge(observation,
                            explanation['attribute'],
                            [],
                            explanation['start'],
                            explanation['end'])
        influence.append(int_index)

    # TODO plot graph
    method_name = "Non Spatial Intervention"

    # plot_explanations(intensity, "intensity", "Top explanations for %s[%s]" % (observation, method_name))
    # plot_explanations(influence, "influence", "Top explanations for %s[%s]" % (observation, method_name))
    return {
        'intensity': intensity,
        'influence': influence,
        'observation': observation,
        'method': method_name
    }



if __name__ == "__main__":
    # Evaluate yellowcab data
    # Load attributes
    headers_filename = "yellowdata.header"
    headers_file = open(headers_filename, 'r')
    attributes = [x.strip() for x in headers_file.readline().split(',')]
    headers_file.close()

    # Get value of observation without filtering
    observation_val = execute_query("avg(%s)" % attributes[observation_att], '1=1')

    # Evaluation for non spatial explanations
    # evaluate_nonspatial_aggravation()
    # evaluate_nonspatial_intervention()

    # Evaluation for spatial explanations
    agg = evaluate_aggravation()
    int = evaluate_intervention()
    hieint = evaluate_heirarchical_intervention()
    salient = evaluate_salient_features()

    datum = [agg, int, hieint, salient]

    for d in datum:
        d['influence'] = list(map(lambda x: abs(x-observation_val),d['influence']))
        d['intensity'] = list(map(lambda x: abs(x - observation_val), d['influence']))

    plot_explanation_comparison(list(map(lambda x: x['intensity'], datum)), 'intensity',
                                "Top explanations for %s" % (datum[0]['observation']),
                                list(map(lambda x: x['method'], datum)))

    plot_explanation_comparison(list(map(lambda x: x['influence'], datum)), 'influence',
                                "Top explanations for %s" % (datum[0]['observation']),
                                list(map(lambda x: x['method'], datum)))


