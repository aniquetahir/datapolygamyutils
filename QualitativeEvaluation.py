import calculate_salient_explanation
import subprocess

attributes = []
processor_home = '/home/anique/IdeaProjects/yellowtaxi'
data_file = "yellowdata_pickup.csv"


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
        predicate = " or ".join(['zone=%i' % x for x in zones])
        predicate = "(%s)" % predicate
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
        pass


def evaluate_salient_features():
    # Evaluate tip percentage

    # Get Top 5 explanations
    observation_att = 5
    top_five = calculate_salient_explanation.top_explanations(observation_att, 'index/data')
    intensity = []
    influence = []
    for explanation in top_five:
        if explanation['score'] > 0:
            zones = map(lambda x: x['zone'], explanation['positive'])
        else:
            zones = map(lambda x: x['zone'], explanation['negative'])

        attribute = attributes[explanation['attribute']]

        observation = "avg(%s)" % attributes[observation_att]
        intensity.append(Aggravation().judge(observation, attribute, zones, None, None))
        influence.append(Intervention().judge(observation, attribute, zones, None, None))

    # TODO Draw Graph
    pass


def evaluate_aggravation():

    pass


def evaluate_intervention():
    pass


def evaluate_heirarchical_intervention():
    pass


if __name__ == "__main__":
    # Evaluate yellowcab data
    # Load attributes
    headers_filename = "yellowdata.header"
    headers_file = open(headers_filename, 'r')
    attributes = [x.strip() for x in headers_file.readline().split(',')]
    headers_file.close()

    evaluate_salient_features()
    evaluate_aggravation()
    evaluate_intervention()

