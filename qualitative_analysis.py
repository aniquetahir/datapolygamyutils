import matplotlib.pyplot as plt
import numpy as np


class Evaluation:
    def __init__(self, results_file, q_value_index, groundtruth_file, groundtruth_index,
                 result_predicate_indices=[], groundtruth_predicate_indices=[]):
        raise NotImplementedError("Evaluation not initialized")

    def calculate(self, n=5, dir='high'):
        raise NotImplementedError("calculate function not implemented")


class Relevance(Evaluation):
    def __init__(self, results_file, q_value_index, aggravation_file, aggravation_index,
                 result_predicate_indices=[], aggravation_predicate_indices=[]):
        self.aggravation = None
        self.results = None
        self.__load_aggravation__(aggravation_file, aggravation_index, aggravation_predicate_indices)
        self.__load_results__(results_file, q_value_index, result_predicate_indices)

    def __load_aggravation__(self, aggravation_filename, aggravation_index, aggravation_predicate_indices):
        """
        Loads the aggravation results in an array
        :param aggravation_filename:
        :param aggravation_index:
        :param aggravation_predicate_indices:
        :return: the values in the aggravation file stored in an array
        """
        # TODO
        file = open(aggravation_filename, 'r')
        results = []
        file.readline() # skip header line
        for line in file:
            fields = line.split(",")
            aggravation = fields[aggravation_index]
            results.append({
                "aggravation": float(aggravation),
                "predicates": list(map(lambda x:fields[x].strip(), aggravation_predicate_indices))
            })

        file.close()
        self.aggravation = results

    def __load_results__(self, results_filename, results_index, results_predicate_indices):
        """
        Loads the results in an array
        :param results_filename:
        :param results_index:
        :param results_predicate_indices:
        :return:  The values in the results file as an array
        """
        # TODO
        file = open(results_filename, 'r')
        results = []
        file.readline() #skip header line
        for line in file:
            fields = line.split(",")
            qvalue = float(fields[results_index])
            results.append({
                "q-value": qvalue,
                "predicates": [fields[x].strip() for x in results_predicate_indices]
            })
        file.close()
        self.results = sorted(results, key=lambda x: x["q-value"])

    def calculate(self, n=5, dir='high'):
        """
        Calculate the value of relevance
        :param n: the number of top results to consider
        :param dir: 'high' or 'low' value
        :return: the value of relevance
        """
        # TODO
        if n>len(self.results):
            n=len(self.results)
        # Get top results
        top_results = []
        if dir == 'low':
            top_results=self.results[:n]
        else:
            top_results=self.results[len(self.results)-n:]

        # Find aggegation value average of the top results
        aggravation_values = []
        for result in top_results:
            aggravation = [x for x in self.aggravation if x['predicates'] == result['predicates']]
            if len(aggravation) > 0:
                aggravation_values.append({'eval':aggravation[0]['aggravation'], 'qval':result['q-value']})
            else:
                print("missing value for predicate:")
                print(result['predicates'])

        return aggravation_values

class Impact(Evaluation):
    def __init__(self, results_file, q_value_index, groundtruth_file, groundtruth_index, result_predicate_indices=[],
                 groundtruth_predicate_indices=[]):
        # TODO
        pass

    def calculate(self, n=5, dir='high'):
        # TODO
        pass




def test_relevance():
    rel = Relevance('intervention/int_nonspatial_spatial/extra_fare_amount.csv', 1,
                  'aggravation/nonspatial_spatial/extra_fare_amount.csv/part-00000-47ad0933-6d4b-48d5-86f1-3fd36a1d19f3.csv',
                  1, [0, 2], [0, 2])

    print(rel.calculate())

def readcolumns():
    file = open("yellowdata.columns",'r')
    line = file.readline()
    fields = [x.strip() for x in line.split(",")]
    file.close()
    return fields

if __name__ == "__main__":
    evaluations = ["Relevance", "Impact"]
    taxonomies = ["nonspatial_spatial"]
    methods = ["aggravation", "intervention"] # TODO add heirarchical
    method_colors = ['b', 'g']

    observation = 'passenger_count'

    # Read columns
    columns = readcolumns()
    columns = set(filter(lambda x: not x==observation, columns))
    fig = plt.figure()

    explanation_direction_high = True
    # For each Taxonomy
    #    For each field as observation
    #      Get top 5 explanations for observation
    #      For each field as explanation
    #
    for i,evaluation in enumerate(evaluations):
        if evaluation=="Relevance":
            gt="aggravation"
        elif evaluation=="Impact":
            gt="intervention"
        for j,taxonomy in enumerate(taxonomies):
            if taxonomy=="nonspatial_spatial":
                result_pred_indices = [0, 2]
                gt_pred_indices = [0, 2]
            ax=fig.add_subplot(i+1+(j*len(evaluations)), len(evaluations), len(taxonomies))
            for m_index, method in enumerate(methods):
                all_evals = []
                calculate_dir = 'high'
                do_reverse = explanation_direction_high
                if method=="intervention":
                    do_reverse = not do_reverse
                    calculate_dir = 'low'
                for column in columns:
                    eval = Relevance("%s/%s/%s.csv"%(method,taxonomy,observation+"_"+column),
                              1, "%s/%s/%s.csv"%(gt,taxonomy,observation+"_"+column),
                              1, result_pred_indices, gt_pred_indices)
                    [all_evals.append(x) for x in eval.calculate(dir=calculate_dir)]


                all_evals = sorted(all_evals, key=lambda x: x["qval"], reverse=do_reverse)[:5]
                # Finally plot the results
                index = np.array(range(1, len(all_evals)+1))+(5*m_index)
                ax.bar(index,[x['eval'] for x in all_evals],0.8,color=method_colors[m_index],label=method)

    plt.show()