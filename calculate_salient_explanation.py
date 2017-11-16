import numpy as np
import json
import sys

def load_data(filename, temporal_res, spatial_res):
    file = open(filename, 'r')
    data = []
    for line in file:
        [keys, values] = [x.strip().split(',') for x in line.split('\t') if x]
        [line_dataid, line_att_index, line_temp_res, line_spatial_res] = [int(x) for x in keys]
        if line_temp_res == temporal_res and line_spatial_res == spatial_res:
            data.append({
                'attribute': line_att_index,
                'zone': int(values[1]),
                'feature': int(values[-1])
            })
    file.close()
    return data


def top_explanations(observation_att_index, index_filename):
    temporal_res = 4
    spatial_res = 3

    data = load_data(index_filename, temporal_res, spatial_res)

    attributes = set([x['attribute'] for x in data])

    zones = [x['zone'] for x in data]
    zones = set(zones)

    relationship_scores = []
    for attribute in attributes:
        if attribute == observation_att_index:
            continue

        positive_correlated_features = []
        negative_correlated_features = []
        # For each poly in space
        for zone in zones:
            # Get observation salient feature
            observation_feature = [x for x in data if x['attribute'] == observation_att_index and x['zone'] == zone]
            if len(observation_feature) > 0:
                observation_feature = observation_feature[0]
            else:
                continue

            # Get explanation feature
            explanation_feature = [x for x in data if x['attribute'] == attribute and x['zone'] == zone]
            if len(explanation_feature) > 0:
                explanation_feature = explanation_feature[0]
            else:
                continue

            if observation_feature['feature'] == 1 or explanation_feature['feature'] == 1:
                continue

            if observation_feature['feature'] == explanation_feature['feature']:
                # Add poly to to positive_corellated_features
                positive_correlated_features.append(explanation_feature)
            else:
                # Add poly to negative correlated features
                negative_correlated_features.append(explanation_feature)

        # Relationship strength
        tau = (len(positive_correlated_features) - len(negative_correlated_features)) / len(zones)
        relationship_scores.append({
            'attribute': attribute,
            'score': tau,
            'positive': positive_correlated_features,
            'negative': negative_correlated_features
        })

    # Sort calculated data
    relationship_scores = sorted(relationship_scores, key=lambda x: np.abs(x['score']), reverse=True)

    # Print top 5 explanation
    top_five = relationship_scores[:5]

    return top_five



if __name__ == "__main__":
    data = []

    observation_att_index = int(sys.argv[1])
    index_filename = sys.argv[2]

    top_five = top_explanations(observation_att_index, index_filename)

    encoder = json.JSONEncoder()
    json_results = encoder.encode(top_five)
    print(json_results)
