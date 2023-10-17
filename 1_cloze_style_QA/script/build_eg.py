import networkx as nx
import os
import json

# read all entailment graphs of a dir
def findAllFile(base):
    path_list = []
    for root, ds, fs in os.walk(base):
        for f in fs:
            print(f)
            if '_sim.txt' in f:
                fullname = os.path.join(root, f)
                path_list.append(fullname)
    return path_list

def extract_eg_1(filename):
    s = open(filename,'r')
    q = s.read()
    f = q.split('predicate: ')[1:]
    TypesEn_name = os.path.basename(filename)[:-len('_sim.txt')]
    #TypesEn_name = filename.split('/')[-1].strip('gsim.txt')
    # the graph is used to save the thing#thing file
    graph = {}
    for blocks in f:
        block = blocks.split('\n\n')[:-1]
        '''
        read block:
        ['(beasts.of.1,beasts.of.2)#art_2#art_1\nnum max neighbors: 10', "local sims\n(beasts.of.1,beasts.of.2)#art_2#art_1 1.0\n('s.1,'s.2)#art_2#art_1 0.2068385"]
        '''
        predicate = block[0].split('\n')[0]

        local_entail_pred = []
        for lines in block[1].split('\n'):
            #print(lines)
            if 'local sims' in lines:
                continue
            if 'iter 0 sims' in lines:
                continue
            if 'BInc sims' in lines:
                continue
            if 'contextualized sims' in lines:
                continue
            local_score = float(lines.split(' ')[1])
            if local_score == 1:
                continue
            pred = lines.split(' ')[0]
            local_entail_pred.append({'pred': pred, 'score':local_score})
           
        graph[predicate] = {'sim': local_entail_pred}

    return graph, TypesEn_name

def build_eg_1(graph, TypesEn_name, local_path):
    DG_l = nx.DiGraph()
    # item name
    for item in graph:
        #if item not in graph.nodes():
        DG_l.add_node(item)
        local_list = graph[item]['sim']
        # build local graph
        for local_ in local_list:
            pred = local_['pred']
            local_score = local_['score']
            DG_l.add_node(pred)
            if item not in DG_l.adj[pred]:
                DG_l.add_edge(pred, item, weight=local_score)
    print("length DG l :")
    print(len(DG_l.nodes()))
    print(len(DG_l.edges()))


    nx.write_gpickle(DG_l, local_path + TypesEn_name + ".gpickle")
    
def run():
    output = findAllFile("your_path/")
    for path in output:
        graph, TypesEn_name = extract_eg_1(path)
        build_eg_1(graph, TypesEn_name, "your_path/")

run()