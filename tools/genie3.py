__author__ = 'WonhoShin, JongminLee'

from sklearn.tree.tree import BaseDecisionTree
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor
from sklearn.ensemble import GradientBoostingRegressor, AdaBoostRegressor
from sklearn.tree import DecisionTreeRegressor
from numpy import *
import pandas as pd
import time
from operator import itemgetter
import csv
import numpy as np

def compute_feature_importances(estimator):

    if isinstance(estimator,GradientBoostingRegressor):
        print "compute GB feature importance score"
        total_sum = zeros((estimator.n_features,),dtype=float64)
        weighted_sum = 0
        for i,stage in enumerate(estimator.estimators_):
            stage_sum = sum(tree.tree_.compute_feature_importances(normalize=False) for tree in stage) / len(stage)
            total_sum += stage_sum
        importances = total_sum/len(estimator.estimators_)
        return importances

    elif isinstance(estimator,AdaBoostRegressor):
        print "compute AB feature importance score"
        importances = [e.tree_.compute_feature_importances(normalize=False)
                       for e in estimator.estimators_]
        importances = asarray(importances)
        if importances.shape[0] == len(estimator.estimator_weights_):
            estimator_weights = estimator.estimator_weights_[:,newaxis]
        else:
            estimator_weights = estimator.estimator_weights_[estimator.estimator_weights_!=0][:,newaxis]

        importances = importances  * estimator_weights
        return sum(importances,axis=0) / len(estimator)

    elif isinstance(estimator, BaseDecisionTree):
        return estimator.tree_.compute_feature_importances(normalize=False)
    else:
        importances = [e.tree_.compute_feature_importances(normalize=False)
                       for e in estimator.estimators_]
        importances = asarray(importances)
        return sum(importances, axis=0) / len(estimator)

def get_link_list(VIM, gene_names=None, regulators='all', maxcount='all', adj=None, file_name=None):
    """Gets the ranked list of (directed) regulatory links.

    Parameters
    ----------

    VIM: numpy array
        Array as returned by the function genie3(), in which the element (i,j) is the score
        of the edge directed from the i-th gene to the j-th gene.

    gene_names: list of strings, optional
        List of length p, where p is the number of rows/columns in VIM, containing the names of the genes.
        The i-th item of gene_names must correspond to the i-th row/column of VIM.
        When the gene names are not provided, the i-th gene is named Gi.
        default: None

    regulators: list of strings, optional
        List containing the names of the candidate regulators.
        When a list of regulators is provided, the names of all the genes must be provided (in gene_names),
        and the returned list contains only edges directed from the candidate regulators.
        When regulators is set to 'all', any gene can be a candidate regulator.
        default: 'all'

    maxcount: 'all' or positive integer, optional
        Writes only the first maxcount regulatory links of the ranked list.
        When maxcount is set to 'all', all the regulatory links are written.
        default: 'all'

    file_name: string, optional
        Writes the ranked list of regulatory links to the file file_name.
        default: None




    Returns
    -------

    The list of regulatory links, ordered according to the edge score.
    Auto-regulations do not appear in the list.
    Regulatory links with a score equal to zero are randomly permuted.
    In the ranked list of edges, each line has format:

        regulator   target gene     score of edge



    """

    # Check input arguments
    if not isinstance(VIM, ndarray):
        raise ValueError('VIM must be a square array')
    elif VIM.shape[0] != VIM.shape[1]:
        raise ValueError('VIM must be a square array')

    ngenes = VIM.shape[0]

    if gene_names is not None:
        if not isinstance(gene_names, (list, tuple)):
            raise ValueError('input argument gene_names must be a list of gene names')
        elif len(gene_names) != ngenes:
            raise ValueError(
                'input argument gene_names must be a list of length p, where p is the number of columns/genes in the expression data')

    if regulators is not 'all':
        if not isinstance(regulators, (list, tuple)):
            raise ValueError('input argument regulators must be a list of gene names')

        if gene_names is None:
            raise ValueError('the gene names must be specified (in input argument gene_names)')
        else:
            sIntersection = set(gene_names).intersection(set(regulators))
            if not sIntersection:
                raise ValueError('The genes must contain at least one candidate regulator')

    if maxcount is not 'all' and not isinstance(maxcount, int):
        raise ValueError('input argument maxcount must be "all" or a positive integer')

    if file_name is not None and not isinstance(file_name, str):
        raise ValueError('input argument file_name must be a string')

    # Get the indices of the candidate regulators
    if regulators == 'all':
        input_idx = range(ngenes)
    else:
        input_idx = [i for i, gene in enumerate(gene_names) if gene in regulators]

    nTFs = len(input_idx)

    # Get the non-ranked list of regulatory links
    vInter = []
    for i in input_idx:
        for j in range(ngenes):
            if i != j:
                vInter.append((i, j, VIM[i, j]))

    # Rank the list according to the weights of the edges
    vInter_sort = sorted(vInter, key=itemgetter(2), reverse=True)
    nInter = len(vInter_sort)

    # Random permutation of edges with score equal to 0
    flag = 1
    i = 0
    while flag and i < nInter:
        (TF_idx, target_idx, score) = vInter_sort[i]
        if score == 0:
            flag = 0
        else:
            i += 1

    if not flag:
        items_perm = vInter_sort[i:]
        items_perm = random.permutation(items_perm)
        vInter_sort[i:] = items_perm

    # Write the ranked list of edges
    nToWrite = nInter
    if isinstance(maxcount, int) and maxcount >= 0 and maxcount < nInter:
        nToWrite = maxcount

    if gene_names is not None:
        for i in range(nToWrite):
            (TF_idx, target_idx, score) = vInter_sort[i]
            TF_idx = int(TF_idx)
            target_idx = int(target_idx)
            adj.iloc[gene_names[TF_idx]][gene_names[target_idx]] = score
            print '%s\t%s\t%.6f' % (gene_names[TF_idx], gene_names[target_idx], score)
    else:
        for i in range(nToWrite):
            (TF_idx, target_idx, score) = vInter_sort[i]
            TF_idx = int(TF_idx)
            target_idx = int(target_idx)
            adj.iloc[TF_idx][target_idx] = score
            print 'G%d\tG%d\t%.6f' % (TF_idx + 1, target_idx + 1, score)

def genie3(expr_data, gene_names=None, regulators='all', tree_method='RF', K='sqrt', ntrees=1000):
    '''Computation of tree-based scores for all putative regulatory links.

    Parameters
    ----------

    expr_data: numpy array
        Array containing gene expression values.
        Each row corresponds to a condition and each column corresponds to a gene.

    gene_names: list of strings, optional
        List of length p, where p is the number of columns in expr_data, containing the names of the genes.
        The i-th item of gene_names must correspond to the i-th column of expr_data.
        default: None

    regulators: list of string, optional
        List containing the names of the candidate regulators.
        When a list of regulators is provided, the names of all the genes must be provided (in gene_names).
        When regulators is set to 'all', any gene can be a candidate regulator.
        default: 'all'

    tree-method: 'RF' or 'ET', optional
        Specifies which tree-based procedure is used: either Random Forest ('RF') or Extra-Trees ('ET')
        default: 'RF'

    K: 'sqrt', 'all' or a positive integer, optional
        Specifies the number of selected attributes at each node of one tree:
        either the square root of the number of candidate regulators ('sqrt'),
        the number of candidate regulators ('all'),
        or any positive integer.
        default: 'sqrt'

    ntrees: positive integer, optional
        Specifies the number of trees grown in an ensemble.
        default: 1000


    Returns
    -------

    An array in which the element (i,j) is the score of the edge directed from the i-th gene to the j-th gene.
    All diagonal elements are set to zero (auto-regulations are not considered).
    When a list of candidate regulators is provided, all the edges directed from a gene that is not a candidate regulator are set to zero.

    '''

    time_start = time.time()

    # Check input arguments
    if not isinstance(expr_data, ndarray):
        raise ValueError(
            'expr_data must be an array in which each row corresponds to a condition/sample and each column corresponds to a gene')

    ngenes = expr_data.shape[1]

    if gene_names is not None:
        if not isinstance(gene_names, (list, tuple)):
            raise ValueError('input argument gene_names must be a list of gene names')
        elif len(gene_names) != ngenes:
            raise ValueError(
                'input argument gene_names must be a list of length p, where p is the number of columns/genes in the expression data')

    if regulators is not 'all':
        if not isinstance(regulators, (list, tuple)):
            raise ValueError('input argument regulators must be a list of gene names')

        if gene_names is None:
            raise ValueError('the gene names must be specified (in input argument gene_names)')
        else:
            sIntersection = set(gene_names).intersection(set(regulators))
            if not sIntersection:
                raise ValueError('The genes must contain at least one candidate regulator')

    if tree_method is not 'RF' and tree_method is not 'ET':
        raise ValueError('input argument tree_method must be "RF" (Random Forests) or "ET" (Extra-Trees)')

    if K is not 'sqrt' and K is not 'all' and not isinstance(K, int):
        raise ValueError('input argument K must be "sqrt", "all" or a stricly positive integer')

    if isinstance(K, int) and K <= 0:
        raise ValueError('input argument K must be "sqrt", "all" or a stricly positive integer')

    if not isinstance(ntrees, int):
        raise ValueError('input argument ntrees must be a stricly positive integer')
    elif ntrees <= 0:
        raise ValueError('input argument ntrees must be a stricly positive integer')

    # Get the indices of the candidate regulators
    if regulators == 'all':
        input_idx = range(ngenes)
    else:
        input_idx = [i for i, gene in enumerate(gene_names) if gene in regulators]

    # Learn an ensemble of trees for each target gene, and compute scores for candidate regulators
    VIM = zeros((ngenes, ngenes))

    for i in range(ngenes):
        print 'Gene %d...' % (i + 1)

        vi = genie3_single(expr_data, i, input_idx, tree_method, K, ntrees)
        VIM[i, :] = vi

    VIM = transpose(VIM)

    time_end = time.time()
    print "Elapsed time: %.2f seconds" % (time_end - time_start)

    return VIM

def genie3_single(expr_data, output_idx, input_idx, tree_method, K, ntrees):
    ngenes = expr_data.shape[1]

    # Normalize output data
    output = expr_data[:, output_idx]
    output = output / std(output)

    # Remove target gene from candidate regulators
    input_idx = input_idx[:]
    if output_idx in input_idx:
        input_idx.remove(output_idx)

    expr_data_input = expr_data[:, input_idx]

    # Parameters of the tree-based method
    if tree_method == 'RF':
        print_method = 'Random Forests'
        if K == 'sqrt':
            print_K = round(sqrt(len(input_idx)))
            treeEstimator = RandomForestRegressor(n_estimators=ntrees, max_features="sqrt")
        elif K == 'all':
            print_K = len(input_idx)
            treeEstimator = RandomForestRegressor(n_estimators=ntrees, max_features="auto")
        else:
            if K < len(input_idx):
                print_K = K
                treeEstimator = RandomForestRegressor(n_estimators=ntrees, max_features=K)
            else:
                print_K = len(input_idx)
                treeEstimator = RandomForestRegressor(n_estimators=ntrees, max_features="auto")

    elif tree_method == 'ET':
        print_method = 'Extra Trees'
        if K == 'sqrt':
            print_K = round(sqrt(len(input_idx)))
            treeEstimator = ExtraTreesRegressor(n_estimators=ntrees, max_features="sqrt")
        elif K == 'all':
            print_K = len(input_idx)
            treeEstimator = ExtraTreesRegressor(n_estimators=ntrees, max_features="auto")
        else:
            if K < len(input_idx):
                print_K = K
                treeEstimator = ExtraTreesRegressor(n_estimators=ntrees, max_features=K)
            else:
                print_K = len(input_idx)
                treeEstimator = ExtraTreesRegressor(n_estimators=ntrees, max_features="auto")

    print "Tree method = %s, K = %d, %d trees" % (print_method, print_K, ntrees)

    # Learn ensemble of trees
    treeEstimator.fit(expr_data_input, output)

    # Compute importance scores
    feature_importances = compute_feature_importances(treeEstimator)
    vi = zeros(ngenes)
    vi[input_idx] = feature_importances

    return vi

def genie3_time(TS_data, gene_names=None, regulators='all', tree_method='GB', K='sqrt',
                ntrees=1000, h=1):
    '''Computation of tree-based scores for all putative regulatory links.

    Parameters
    ----------

    TS_data: list of numpy arrays
        Each array of the list contains a time series of gene expression values.
        Each row of the array corresponds to a time point and each column corresponds to a gene.
        All the arrays of the list must contain the same number of genes/columns.

    gene_names: list of strings, optional
        List of length p, where p is the number of columns in the arrays of TS_data, containing the names of the genes.
        The i-th item of gene_names must correspond to the i-th column of each array of TS_data.
        default: None

    regulators: list of string, optional
        List containing the names of the candidate regulators.
        When a list of regulators is provided, the names of all the genes must be provided (in gene_names).
        When regulators is set to 'all', any gene can be a candidate regulator.
        default: 'all'

    tree-method: 'RF' or 'ET', optional
        Specifies which tree-based procedure is used: either Random Forest ('RF') or Extra-Trees ('ET')
        default: 'RF'

    K: 'sqrt', 'all' or a positive integer, optional
        Specifies the number of selected attributes at each node of one tree:
        either the square root of the number of candidate regulators ('sqrt'),
        the number of candidate regulators ('all'),
        or any positive integer.
        default: 'sqrt'

    ntrees: positive integer, optional
        Specifies the number of trees grown in an ensemble.
        default: 1000

    h: positive integer, optional
        Specifies the time lag.
        Each tree model that is learned predicts the expression of the target gene at time t_{k+h},
        from the expression levels of the candidate regulators and the target gene at time t_k.


    Returns
    -------

    An array in which the element (i,j) is the score of the edge directed from the i-th gene to the j-th gene.
    All diagonal elements are set to zero (auto-regulations are not considered).
    When a list of candidate regulators is provided, all the edges directed from a gene that is not a candidate regulator are set to zero.

    '''

    time_start = time.time()

    # Check input arguments
    if not isinstance(TS_data, ndarray):
        raise ValueError(
            'TS_data must be a list of arrays, where each row of an array corresponds to a time point and each column corresponds to a gene')

    ngenes = TS_data[0].shape[1]

    if gene_names is not None:
        if not isinstance(gene_names, (list, tuple)):
            raise ValueError('input argument gene_names must be a list of gene names')
        elif len(gene_names) != ngenes:
            raise ValueError(
                'input argument gene_names must be a list of length p, where p is the number of columns/genes in the expression data')

    if regulators is not 'all':
        if not isinstance(regulators, (list, tuple)):
            raise ValueError('input argument regulators must be a list of gene names')

        if gene_names is None:
            raise ValueError('the gene names must be specified (in input argument gene_names)')
        else:
            sIntersection = set(gene_names).intersection(set(regulators))
            if not sIntersection:
                raise ValueError('The genes must contain at least one candidate regulator')

    if tree_method is not 'RF' and tree_method is not 'ET' and tree_method is not 'AB' and tree_method is not 'GB':
        raise ValueError('input argument tree_method must be "RF" (Random Forests) or "ET" (Extra-Trees)')

    if K is not 'sqrt' and K is not 'all' and not isinstance(K, int):
        raise ValueError('input argument K must be "sqrt", "all" or a stricly positive integer')

    if isinstance(K, int) and K <= 0:
        raise ValueError('input argument K must be "sqrt", "all" or a stricly positive integer')

    if not isinstance(ntrees, int):
        raise ValueError('input argument ntrees must be a stricly positive integer')
    elif ntrees <= 0:
        raise ValueError('input argument ntrees must be a stricly positive integer')

    ntimepoints_min = TS_data[0].shape[0]
    print "SHAPE", TS_data.shape, TS_data[0].shape, TS_data[0].shape[0], len(TS_data)
    for k in range(1, len(TS_data)):
        if TS_data[k].shape[0] < ntimepoints_min:
            ntimepoints_min = TS_data[k].shape[0]

    if not isinstance(h, int):
        raise ValueError('input argument h must be a stricly positive integer')
    elif h <= 0:
        raise ValueError('input argument h must be a stricly positive integer')
    elif h >= ntimepoints_min:
        print "MARKERRRRRR", ntimepoints_min, h
        raise ValueError(
            'input argument h must be stricly smaller than the number of time points in the shortest time series')

    # Get the indices of the candidate regulators
    if regulators == 'all':
        input_idx = range(ngenes)
    else:
        input_idx = [i for i, gene in enumerate(gene_names) if gene in regulators]

    # Learn an ensemble of trees for each target gene, and compute scores for candidate regulators
    VIM = zeros((ngenes, ngenes))

    for i in range(ngenes):
        print 'Gene %d...' % (i + 1)

#        if(i==3):
#            print "expr_data :", TS_data
#            print "input_idx", input_idx


        vi = genie3_time_single(TS_data, i, input_idx, tree_method, K, ntrees, h)
        if vi[0] is None:
            return [[None], [None]]
        VIM[i, :] = vi

    VIM = transpose(VIM)

    time_end = time.time()
    print "Elapsed time: %.2f seconds" % (time_end - time_start)

#    print VIM[0][0]

    return VIM

def genie3_time_single(TS_data, output_idx, input_idx, tree_method, K, ntrees, h):
    ngenes = TS_data[0].shape[1]
    nexp = len(TS_data)

    nsamples = 0
    for iexp in range(nexp):
        nsamples += TS_data[iexp].shape[0]

    # Add target gene to candidate regulators
    input_idx = input_idx[:]
    if output_idx not in input_idx:
        input_idx.append(output_idx)

    ninputs = len(input_idx)

    matrix_input = zeros((nsamples - h * nexp, ninputs))
    output = zeros(nsamples - h * nexp)
    
    nsamples_count = 0

    for iexp in range(nexp):
        current_timeseries = TS_data[iexp]
        npoints = current_timeseries.shape[0]
        current_timeseries_input = current_timeseries[:npoints - h, input_idx]
        current_timeseries_output = current_timeseries[h:, output_idx]
        nsamples_current = current_timeseries_input.shape[0]
        matrix_input[nsamples_count:nsamples_count + nsamples_current, :] = current_timeseries_input
        output[nsamples_count:nsamples_count + nsamples_current] = current_timeseries_output
        nsamples_count += nsamples_current
    # if(output_idx == 3):
    #     print "output:", output

    normValue = std(output)
    
    if not normValue:
        print "normValue non difined"
#        return [None, None]
    else:
        # print "normValue exist"
        output = output / normValue

    # Parameters of the tree-based method
    if tree_method == 'RF':
        print_method = 'Random Forests'
        if K == 'sqrt':
            print_K = round(sqrt(ninputs))
            treeEstimator = RandomForestRegressor(n_estimators=ntrees, max_features="sqrt")
        elif K == 'all':
            print_K = ninputs
            treeEstimator = RandomForestRegressor(n_estimators=ntrees, max_features="auto")
        else:
            if K < ninputs:
                print_K = K
                treeEstimator = RandomForestRegressor(n_estimators=ntrees, max_features=K)
            else:
                print_K = ninputs
                treeEstimator = RandomForestRegressor(n_estimators=ntrees, max_features="auto")

    elif tree_method == 'ET':
        print_method = 'Extra Trees'
        if K == 'sqrt':
            print_K = round(sqrt(ninputs))
            treeEstimator = ExtraTreesRegressor(n_estimators=ntrees, max_features="sqrt")
        elif K == 'all':
            print_K = ninputs
            treeEstimator = ExtraTreesRegressor(n_estimators=ntrees, max_features="auto")
        else:
            if K < ninputs:
                print_K = K
                treeEstimator = ExtraTreesRegressor(n_estimators=ntrees, max_features=K)
            else:
                print_K = ninputs
                treeEstimator = ExtraTreesRegressor(n_estimators=ntrees, max_features="auto")

    elif tree_method == 'GB':
        print "Gradient Boosting"
        treeEstimator = GradientBoostingRegressor(n_estimators=ntrees)

    elif tree_method =='AB':
        #Adaboost
        print "AbaBoost"
        treeEstimator = AdaBoostRegressor(DecisionTreeRegressor(),n_estimators=ntrees)


    #print "Tree method = %s, K = %d, %d trees, time lag = %d" % (print_method, print_K, ntrees, h)

    # Learn ensemble of trees
    treeEstimator.fit(matrix_input, output)

    # Compute importance scores
    feature_importances = compute_feature_importances(treeEstimator)

    vi = zeros(ngenes)
    vi[input_idx] = feature_importances
    vi[output_idx] = 0
    if(sum(vi) == 0):
        return vi

    vi = vi / sum(vi)
    return vi

def cutoff_by_threshold(TFlist, _adj, threshold):
    adj = pd.DataFrame(data=array(zeros((len(TFlist), len(TFlist)), dtype=float32)), columns=TFlist, index=TFlist, dtype=int)
    for tf1 in TFlist:
        for tf2 in TFlist:
            if _adj[tf1][tf2] >= threshold:
                adj[tf1][tf2] = 1
            else:
                adj[tf1][tf2] = 0
    return adj

def cutoff_by_percentage(TFlist, _adj, threshold):
    adj = pd.DataFrame(data=array(zeros((len(TFlist), len(TFlist)), dtype=float32)), columns=TFlist, index=TFlist, dtype=int)
    edge_list = []
    for tf1 in TFlist:
        for tf2 in TFlist:
            edge_list.append([tf1, tf2, _adj[tf1][tf2]])

    edge_list = sorted(edge_list, key=lambda k: -k[2])
    for i in range(int(threshold * len(edge_list))):
        tf1 = edge_list[i][0]
        tf2 = edge_list[i][1]
        adj[tf1][tf2] = 1
    return adj

def run_GENIE3(TS_data, gene_names=None,ntrees=100 ,start_point = None ,end_point = None, cutoff='realvalue', threshold = 0.3, except_list = []):

    # Current Form
    # TF1  #.###  #.###  #.###  ...
    # TF2  #.###  #.###  #.###  ...
    # TF3  #.###  #.###  #.###  ...
    # ...   ...    ...    ...

    # File OPEN, need to modify to using python data structure
    # table = [row.split('\t') for row in tsdata.split('\n')]
    # # line and tabs are seperated
    # table = table[0:-1]
    # print "=====table in genie3====", table
    # valTable = []
    # TFlist = []

    if not start_point:
        start_point = 1
    if not end_point:
        end_point = int(TS_data[0].shape[0])

    # print "Table shape", asarray(TS).shape

    # for j, row in enumerate(table):
    #     print row[0], except_list
    #     if j == 0 or row[0] in except_list:
    #         continue
    #     TFlist.append(row[0])
    #     valTable.append(row[start_point:end_point+1])
    # print TFlist
    # print valTable

    print "=====start_point", start_point-1
    print "======end_point", end_point-1
    TS_data = np.asarray([TS_array[(start_point-1):(end_point)] for TS_array in TS_data])
    print "=======gene names=====", gene_names
    print "gene_names length", len(gene_names)
    _adj = pd.DataFrame(data=array(zeros((len(gene_names), len(gene_names)), dtype=float32)), columns=gene_names, index=gene_names, dtype=float32)
#    print "_adj", _adj.ix[0, 0]
#    TS_data = array([array(valTable).T])
    print _adj.shape
 
    # TS_data = array([array(valTable).T, array(valTable).T, array(valTable).T])
    # print len(TS_data), len(TS_data[0]), len(TS_data[0][0])

## check nan
#    print "TS_data", TS_data
#    print "valTable", valTable

#    print "no error, run_Geine3"
    print "====TS_data ====", TS_data
    VIM = genie3_time(TS_data, gene_names=gene_names, regulators='all', ntrees=ntrees) #ntrees should be inputted.
    print "======VIM =====", VIM[0][0]

#check error
    # if (VIM[0][0] is None):
    #     _adj.ix[0,0] = None
    #     return _adj

    # Get the ranking of network edges
    get_link_list(VIM, adj=_adj)

    adj = None
    if cutoff == 'realvalue':
        adj = cutoff_by_threshold(gene_names, _adj, threshold)
    elif cutoff == 'percentage':
        adj = cutoff_by_percentage(gene_names, _adj, threshold)
    elif cutoff == 'raw':
        adj = _adj

    for node in except_list:
        adj.loc[node] = zeros(len(adj.columns.values))
    for node in except_list:
        adj.loc[:,node] = zeros(len(adj.index))
    return adj

# def run_GENIE3_multiple_observation(rootdir, med_num = None, observation = 3, start_point = 1, end_point = 20, cutoff='realvalue', threshold = 0.05, except_list = ['NT']):
#     # if not isinstance(med_num, (int, integer)):
#     #     print "Wrong Medicine #"
#     #     return
#     adj_list = []
#     print "START:", start_point, "END:", end_point
#     for i in [med_num]: #(1,28)
#         file = open(rootdir + '/' + i, 'rb')
#         data = csv.reader(file, delimiter='\t')
#         table = [row for row in data]

#         valTable = []
#         for j in range(observation):
#             valTable.append([])
#         TFlist = []

#         for j, row in enumerate(table):
#             if j == 0 or row[0] in except_list:
#                 continue
#             TFlist.append(row[0])
#             for obs_num in range(1, observation + 1):
#                 valTable[obs_num - 1].append(row[(start_point-1) * observation + obs_num : end_point * observation + 1 : observation])
#                 print len(row), row
#                 print range(100)[(start_point-1) * observation + obs_num : end_point * observation + 1 : observation]
#                 print row[(start_point-1) * observation + obs_num : end_point * observation + 1 : observation]
#                 print "-----------------------"
#         print TFlist
#         print valTable

#         _adj = pd.DataFrame(data=array(zeros((len(TFlist), len(TFlist)), dtype=float32)), columns=TFlist, index=TFlist, dtype=float32)
#         # TS_data = array([array(valTable).T])
#         TS_data = valTable
#         for j in range(len(TS_data)):
#             TS_data[j] = array(TS_data[j]).T
#         TS_data = array(TS_data)

#         print "TSDATAINFO"
#         print len(valTable), len(valTable[0]), len(valTable[0][0])
#         print TS_data[0].shape

#         VIM = genie3_time(TS_data, gene_names=TFlist, regulators=TFlist)

#         # Get the ranking of network edges
#         get_link_list(VIM, adj=_adj)

#         adj = None
#         if cutoff == 'realvalue':
#             adj = cutoff_by_threshold(TFlist, _adj, threshold)
#         elif cutoff == 'percentage':
#             adj = cutoff_by_percentage(TFlist, _adj, threshold)
#         elif cutoff == 'raw':
#             adj = _adj

#         for node in except_list:
#             adj.loc[node] = zeros(len(adj.columns.values))
#         for node in except_list:
#             adj.loc[:,node] = zeros(len(adj.index))

#         adj_list.append(adj)
#         return adj


if __name__ == '__main__':
    rootdir = 'Q:/LCA/data/preprocess_data/06_23/drug_data_observations_merged_TSV'
    #time_point:[1-20]
    # adj = run_GENIE3(rootdir, med_num='1.tsv', start_point=1, end_point=5, cutoff='percentage', threshold=0.1)
    adj = run_GENIE3_multiple_observation(rootdir, med_num='1.tsv', observation = 2, start_point=1, end_point=10, cutoff='percentage', threshold=0.1)
    print adj