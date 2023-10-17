# 1. get s, o and predicate
# 2. get types pair of s, o
# 3. get correct graphs from graph_list, types order
# 4. calculate the score (binc). need to care the different types order. (1) check it the predicate in graph or candidate_graph, if not in graph or return 0.0, search candidate_graph. (2) check same types and types order.

import networkx as nx
import os
import json
import pandas as pd


def read_graphs(base):
    path_list = []
    graph_list = {}
    for root, ds, fs in os.walk(base):
        for f in fs:
            print(f)
            if '.gpickle' in f:
                fullname = os.path.join(root, f)
                print(fullname)
                graph_list[f] = nx.read_gpickle(fullname)
                #path_list.append(fullname)
    return graph_list
    

def read_triples(js, rels_hashmap):
    '''
    an example of a line:
    {"question": "Lavoisier Island is located in Antarctica .", "answer": "It should not be confused with Lavoisier Island in the Antarctica, which is also called Isla Serrano in Spanish.", "rel": "located in", "raw_data": {"sub_surface": "Lavoisier Island", "obj_surface": "Antarctica", "masked_sentence": "It should not be confused with Lavoisier Island in the [MASK], which is also called Isla Serrano in Spanish."}, "result": {"extract_sub": "lavoisier island", "extract_obj": "antarctica", "extract_predicate": "(in.1,in.2)"}, "types": "geography#location"}
    '''
    rel = js['rel']
    subject = js['result']['extract_sub']
    object = js['result']['extract_obj']
    extract_pred = js['result']['extract_predicate']
    type_sub = js['types'].split('#')[0]
    type_obj = js['types'].split('#')[1]
    question_predicate = rels_hashmap[rel]
    candidate_graph_types_sub = rels_hashmap[rel].split('#')[1]  
    candidate_graph_types_obj = rels_hashmap[rel].split('#')[2]
    return (subject, object, extract_pred), type_sub, type_obj, question_predicate, candidate_graph_types_sub, candidate_graph_types_obj

def search_graph(graph_list, type_sub, type_obj, candidate_graph_types_sub, candidate_graph_types_obj):
    t1 = type_sub + '#' + type_obj + '_gsim.gpickle'
    t2 = type_obj + '#' + type_sub + '_gsim.gpickle'

    candidate_graph_types_sub = candidate_graph_types_sub.replace('_1','').replace('_2','')
    candidate_graph_types_obj = candidate_graph_types_obj.replace('_1','').replace('_2','')
    
    tc1 = candidate_graph_types_sub + '#' + candidate_graph_types_obj + '_gsim.gpickle'
    tc2 = candidate_graph_types_obj + '#' + candidate_graph_types_sub + '_gsim.gpickle'

    if tc1 in graph_list:
        candidate_graph = graph_list[tc1]
    else:
        candidate_graph = graph_list[tc2]
    
    if t1 in graph_list:
        return graph_list[t1], candidate_graph
    if t2 in graph_list: 
        return graph_list[t2], candidate_graph
    else:
        return None, candidate_graph


def calculate_score(graph, candidate_graph, question_predicate, triple, type_sub, type_obj, candidate_graph_types_sub, candidate_graph_types_obj):
    if type_sub == type_obj:
        type_sub = type_sub+'_1'
        type_obj = type_obj+'_2'
    
    score = 0.0
    flag = True
    question_pred = question_predicate.split('#')[0]
    extract_pred = triple[2]
    
    q_extract = question_pred+'#'+type_sub+'#'+type_obj
    p_extract = extract_pred+'#'+type_sub+'#'+type_obj
    q_candidate = question_pred+'#'+candidate_graph_types_sub+'#'+candidate_graph_types_obj
    p_candidate = extract_pred+'#'+candidate_graph_types_sub+'#'+candidate_graph_types_obj
    
    
    not_found_obj = False
    
    if graph:
        if q_extract in graph.nodes():
            if p_extract in graph[q_extract]:
                score = float(graph[q_extract][p_extract]['weight'])
            else:
                not_found_obj = True
        if (not_found_obj) and (q_candidate in candidate_graph.nodes()):
            if p_candidate not in candidate_graph.nodes():
                flag = False
            if p_candidate in candidate_graph[q_candidate]:
                #print('YES')
                score = float(candidate_graph[q_candidate][p_candidate]['weight'])
        if (q_extract not in graph.nodes()) and (q_candidate not in candidate_graph.nodes()):
            flag = False
        return score, flag 
        
    else:
        if q_candidate in candidate_graph.nodes():
            if p_candidate not in candidate_graph.nodes():
                flag = False
            if p_candidate in candidate_graph[q_candidate]:
                print('YES')
                score = float(candidate_graph[q_candidate][p_candidate]['weight'])
        else:
            flag = False
        return score, flag
        
    return score, flag
    

def run(graph_dir, dataset, output_path, Type):
    # parameters: 
    # graph_dir : the path of your Entailment graphs
    # dataset: the path of retrieved sentences in T-REx or Google-RE
    # outputpath: the path of results
    
    # read rels_hashmap
    with open("token2preds_manually.json", 'r') as f:
        line = f.read()
    line = line.replace('\n', '')
    rels_hashmap = json.loads(line)
    
    # read graphs paths
    graphs_list = read_graphs(graph_dir)
    
    # read pos / neg dataset
    with open(dataset, "r") as f:
        lines = f.readlines()
    
    scores = []
    test = []
    count = 0
    length = len(lines)
    f = open('../data_trex/filtered_trex_'+Type+'_2.json', 'w')
    for line in lines:
        count += 1
        js = json.loads(line)
        triple, type_sub, type_obj, question_predicate, candidate_graph_types_sub, candidate_graph_types_obj = read_triples(js, rels_hashmap)
        graph, candidate_graph = search_graph(graphs_list, type_sub, type_obj, candidate_graph_types_sub, candidate_graph_types_obj)
        
        # if predicate not in graph, search the candidate graph...
        score, flag = calculate_score(graph, candidate_graph, question_predicate, triple, type_sub, type_obj, candidate_graph_types_sub, candidate_graph_types_obj)
        if flag == False:
            continue
        '''
        if score > 0:
            print('Good Results:\n')
            print((candidate_graph, question_predicate))
            print(score)
        '''
        json.dump(js,f)
        f.write('\n')
        scores.append(score)

    f.close()
    if Type == 'pos':
        labels = [1]*len(scores)
    if Type == 'neg':
        labels = [0]*len(scores)
    data = [labels,scores]
    row = ['labels','binc_scores']
    if os.path.exists(output_path):
        if Type == 'pos':
            pd.DataFrame(index=row,data=data).to_csv(output_path + 'pos_score_trex.csv')
        if Type == 'neg':
            pd.DataFrame(index=row,data=data).to_csv(output_path + 'neg_score_trex.csv')
    else:
        os.makedirs(output_path)
        if Type == 'pos':
            pd.DataFrame(index=row,data=data).to_csv(output_path + 'pos_score_trex.csv')
        if Type == 'neg':
            pd.DataFrame(index=row,data=data).to_csv(output_path + 'neg_score_trex.csv')
        

#run("your_path/EG/BoolQA_Task/BInc_sims/","your_path/LAMA/data/BooleanQA/data_trex/filtered_trex_pos.json", "../results/trex/eg_results/binc/", 'pos')
#run("your_path/EG/BoolQA_Task/BInc_sims/","your_path/LAMA/data/BooleanQA/data_trex/filtered_trex_neg.json", "../results/trex/eg_results/binc/", 'neg')

#run("your_path/EG/BoolQA_Task/lin_sims/","your_path/LAMA/data/BooleanQA/data_trex/filtered_trex_pos.json","../results/trex/eg_results/lin/", 'pos')
#run("your_path/EG/BoolQA_Task/lin_sims/","your_path/LAMA/data/BooleanQA/data_trex/filtered_trex_neg.json", "../results/trex/eg_results/lin/", 'neg')

#run("your_path/EG/BoolQA_Task/cos_sims/","your_path/LAMA/data/BooleanQA/data_trex/filtered_trex_pos.json","../results/trex/eg_results/cos/", 'pos')
#run("your_path/EG/BoolQA_Task/cos_sims/","your_path/LAMA/data/BooleanQA/data_trex/filtered_trex_neg.json", "../results/trex/eg_results/cos/", 'neg')

#run("your_path/EG/BoolQA_Task/weeds_pmi_precision_sims/","your_path/LAMA/data/BooleanQA/data_trex/filtered_trex_pos.json","../results/trex/eg_results/weeds_pmi_precision/", 'pos')
#run("your_path/EG/BoolQA_Task/weeds_pmi_precision_sims/","your_path/LAMA/data/BooleanQA/data_trex/filtered_trex_neg.json", "../results/trex/eg_results/weeds_pmi_precision/", 'neg')

#run("your_path/EG/BoolQA_Task/weeds_pmi_sims/","your_path/LAMA/data/BooleanQA/data_trex/filtered_trex_pos.json","../results/trex/eg_results/weeds_pmi/", 'pos')
#run("your_path/EG/BoolQA_Task/weeds_pmi_sims/","your_path/LAMA/data/BooleanQA/data_trex/filtered_trex_neg.json", "../results/trex/eg_results/weeds_pmi/", 'neg')

#run("your_path/EG/BoolQA_Task/weeds_prob_sims/","your_path/LAMA/data/BooleanQA/data_trex/filtered_trex_pos.json", "../results/trex/eg_results/weeds_prob/", 'pos')
#run("your_path/EG/BoolQA_Task/weeds_prob_sims/","your_path/LAMA/data/BooleanQA/data_trex/filtered_trex_neg.json", "../results/trex/eg_results/weeds_prob/", 'neg')

run("your_path/EG/NewsSpike/eg_ns_global/","your_path/LAMA/data/BooleanQA/data_trex/filtered_trex_pos.json","../results/trex/eg_results/global_binc/", 'pos')
run("your_path/EG/NewsSpike/eg_ns_global/","your_path/LAMA/data/BooleanQA/data_trex/filtered_trex_neg.json","../results/trex/eg_results/global_binc/", 'neg')    