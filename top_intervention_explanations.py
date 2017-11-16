import sys
import os
import json


def top_explanations(observation_index, header_filename, dataset_name, zones):
    header_file = open(header_filename, 'r')

    header_columns = header_file.readline()
    attributes = [x.strip() for x in header_columns.split(',') if x]
    header_file.close()

    observation_attribute = attributes[observation_index]

    scripts_directory = os.path.dirname(os.path.realpath(sys.argv[0]))

    explanations = []
    # Literally just get all the files and return the top 5 entries
    for i, attribute in enumerate(attributes):
        if i == observation_index or attribute == 'count':
            continue

        # Get file for observation_attribute/attribute
        explanation_file = open('%s/results/intervention/nonspatial_spatial/%s/%s_%s.csv'
                                % (scripts_directory, dataset_name, observation_attribute, attribute), 'r')

        explanation_headers = explanation_file.readline()
        for line in explanation_file:
            explanation_fields = line.split(',')
            explanations.append({
                'zone': int(explanation_fields[0]),
                'attribute': attribute,
                'attribute_id': i,
                'observation_value': float(explanation_fields[1]),
                'start': float(explanation_fields[3]),
                'end': float(explanation_fields[4])
            })

        explanation_file.close()

    sorted_explanations = sorted(explanations, key=lambda x: x['observation_value'])

    top_explanations_results = {
        'high': sorted_explanations[:5],
        'low': sorted_explanations[max(0, len(sorted_explanations)-5):]
    }

    return top_explanations_results

if __name__ == "__main__":
    observation_index = int(sys.argv[1])
    header_filename = sys.argv[2]
    dataset_name = sys.argv[3]
    zones = None
    observation_type = "nonspatial"
    if len(sys.argv) > 4:
        zones = sys.argv[4:]
        zones = [int(z) for z in zones]
        observation_type = "spatial"

    encoder = json.JSONEncoder()

    print(encoder.encode(top_explanations(observation_index, header_filename, dataset_name, zones)))




