import os
import json
import networkx as nx
from collections import Counter
import argparse

def search_googlere(KG, test_data, pred_list, Type=None):
    nodes = KG.nodes()
    output = []
    print('length test dataset :', str(len(test_data)))
    if Type:
        for line in test_data:
            line = json.loads(line)
            sub = line['sub']
            obj = line['obj']
            rel = line['rel']
            if sub == '':
                continue
            sub_node = search_sub_in_KG(sub, nodes, method='exact_match')
            if sub_node:
                obj_list = []
                for obj_node in KG.adj[sub_node]:
                    obj_node_type = KG.nodes[obj_node]['Type'].split('::')[0]
                    for pred in pred_list:
                        if pred in KG[sub_node][obj_node]["weight"] and obj_node_type in Type:
                            count = KG[sub_node][obj_node]["weight"][pred]
                            output.append({'sub_node': sub_node, 'obj_node': obj_node, 'sub_truth': sub, 'obj_truth': obj, 'edge_name': pred, 'rel':rel, 'count':count})
                            break
                        else:
                            continue
                            
        print('length test dataset :' + str(len(test_data)) + '    ' + str(len(output)))
        return output


def search_trex(KG, query, pred_list, Type):
    nodes = KG.nodes()
    output = []
    print('length test dataset :', str(len(test_data)))
    if Type:
        # s p o,ts,to
        sub = query[0]
        obj = query[2]
        rel = query[1]
        if sub == '':
            continue
        sub_node = search_sub_in_KG(sub, nodes, method='exact_match')
        if sub_node:
            obj_list = []
            for obj_node in KG.adj[sub_node]:
                obj_node_type = KG.nodes[obj_node]['Type'].split('::')[0]
                for pred in pred_list:
                    if pred in KG[sub_node][obj_node]["weight"] and obj_node_type in Type:
                        count = KG[sub_node][obj_node]["weight"][pred]
                        output.append({'sub_node': sub_node, 'obj_node': obj_node, 'sub_truth': sub, 'obj_truth': obj, 'edge_name': pred, 'rel':rel, 'count':count})
                        break
                    else:
                        continue
                            
        print('length test dataset :' + str(len(test_data)) + '    ' + str(len(output)))
        return output


def search_sub_in_KG(sub, nodes, method):
    if method == 'exact_match':
        #for node in nodes:
        if sub.lower() in nodes:
            return sub.lower()
    return None    

# read the candidate list of predicate for typed entailment graphs.
def read_list(graphpath, predicate_name):
    g = nx.read_gpickle(graphpath)
    pred_types_order = '#'.join(predicate_name.split('#')[1:])
    pred = predicate_name.split('#')[0]
    if predicate_name not in g.nodes():
        return []
    nodes = g[predicate_name]
    hasmap = {}
    for node in nodes:
        if pred_types_order not in node:
            continue
        hasmap[node] = float(g[predicate_name][node]['weight'])
    a = sorted(hasmap.items(), key = lambda x:x[1], reverse=True)

    ranked_list = []
    ranked_list.append(pred)
    for i in a:
        ranked_list.append(i[0].strip(pred_types_order))
    return ranked_list   


def guery_kg(path, kg, relation, dataset):
    # the path to your knowledge graph
    KG = nx.read_gpickle(kg)
    if dataset == 'google_re':
        with open(path,'r') as f:
            test_data = f.readlines()
        if relation == 'place_of_birth':
            ents = ['(bear.2,bear.in.2)']
            print(len(ents))
            if len(ents) > 0:
                output = search_googlere(KG, test_data, ents, Type='person location')
            print(output)
        if relation == 'place_of_death':
            ents = ['(die.1,die.in.2)']
            print(len(ents))
            if len(ents) > 0:
                output = search_googlere(KG, test_data, ents, Type='person location')
            print(output)
        if relation == 'place_of_birth':
            ents = ['(bear.2,bear.in.2)']
            print(len(ents))
            if len(ents) > 0:
                output = search_googlere(KG, test_data, ents, Type='person time')
            print(output)
    if dataset == 'T-REx':
        with open(path,'r') as f:
            test_data = f.readlines()
        for query in test_data:
            query = query.split('\t')
            ents = [query[1]]
            output = search_trex(KG, query, ents, query[3]+' '+query[4])
            print(output)


def guery_eg(path, kg, eg, relation, dataset):
    # the path to your knowledge graph
    KG = nx.read_gpickle(kg)
    if dataset == 'google_re':
        with open(path,'r') as f:
            test_data = f.readlines()
        if relation == 'place_of_birth':
            ents = read_list(eg, '(bear.2,bear.in.2)#person#location')
            print(len(ents))
            if len(ents) > 0:
                output = search_googlere(KG, test_data, ents, Type='person location')
            print(output)
        if relation == 'place_of_death':
            ents = read_list(eg, '(die.1,die.in.2)#person#location')
            print(len(ents))
            if len(ents) > 0:
                output = search_googlere(KG, test_data, ents, Type='person location')
            print(output)
        if relation == 'place_of_birth':
            ents = read_list(eg, '(bear.2,bear.in.2)#person#time')
            print(len(ents))
            if len(ents) > 0:
                output = search_googlere(KG, test_data, ents, Type='person time')
            print(output)
    if dataset == 'T-REx':
        with open(path,'r') as f:
            test_data = f.readlines()
        for query in test_data:
            query = query.split('\t')
            ents = read_list(eg, query[1]+'#'query[3]+'#'+query[4])
            output = search_trex(KG, ents, [query[1]], query[3]+' '+query[4])
            print(output)


def run(args):
    KG = 'your_path/kg.gpickle'
    if args.eg == '':
        guery_kg(args.path, args.kg, args.relation, args.dataset)
    else:
        guery_eg(args.path, args.kg, args.eg, args.relation, args.dataset)
    

if __name__ == '__main__':
    my_arg = argparse.ArgumentParser('My argument parser')
    my_arg.add_argument('--path', default='', type=str, help='test set path')
    my_arg.add_argument('--kg', default='your_path/kg.gpickle', type=str, help='KG path')
    my_arg.add_argument('--eg', default='', type=str, help='EG path')
    my_arg.add_argument('--relation', default='', type=str, help='relation name')
    my_arg.add_argument('--dataset', default='google_re', type=str, help='test set name')
    args = my_arg.parse_args()
    run(args)