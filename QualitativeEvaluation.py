import calculate_salient_explanation

class Aggravation:
    def __init__(self):
        pass

    def judge(self, attribute, zones, bucket):
        """
        :param attribute: the attribute in the explanation predicate
        :param zones: the zones in the explanation predicate
        :param buckets: the bucket for the explanation predicate
        :return: the degree of explanation by aggravation(intensity) for the provided input
        """
        pass


class Intervention:
    def __init__(self):
        pass

    def judge(self, attribute, zones, bucket):
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
    top_five = calculate_salient_explanation.top_explanations(5, 'index/data')
    intensity = []
    influence = []
    for explanation in top_five:
        if explanation['score'] > 0:
            zones = map(lambda x: x['zone'], explanation['positive'])
        else:
            zones = map(lambda x: x['zone'], explanation['negative'])

        attribute = explanation['attribute']

        intensity.append(Aggravation().judge(attribute, zones, None))
        influence.append(Intervention().judge(attribute, zones, None))

    # TODO Draw Graph
    pass


def evaluate_aggravation():

    pass


def evaluate_intervention():
    pass


def evaluate_heirarchical_intervention():
    pass


if __name__ == "__main__":
    #

    pass
