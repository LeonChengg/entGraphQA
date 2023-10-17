import os
import json
import networkx as nx


def testEntity2Types(path):
    with open(path,'r') as f:
        lines = f.readlines()
    HashMap = {}
    for line in lines:
        entity_id = line.split("\t")[0]
        entity_name = line.split("\t")[1].lower()
        if line.split("\t")[2] == "":
            entity_type = line.split("\t")[4].split('/')[1]
        else:
            entity_type = line.split("\t")[2].split('/')[1]
        HashMap[entity_name] = entity_type
        print({entity_name: entity_type})
        print(len(HashMap))
        
    return HashMap

# read the types from freebase
def get_type(entity_name,HashMap):
    if (entity_name.isdigit()) and (len(entity_name)==4):
        return "time"
    key = HashMap.get(entity_name)
    if key == None:
        return "None" 
    else:
        return key

# builda directed graph to save the knowledge
def build_Graph(DG, lines, HashMap):
    count = 0
    length = len(lines)
    for line in lines:
        print(count, length)
        count+=1
        if "articleId" not in line:
            continue
        js = json.loads(line)
        rels = js["rels"]
        for i in rels:
            r = i["r"][1:-1].split("::")
            ge_1 = r[4][0]
            ge_2 = r[4][1]
            pred = r[0]
            n_1 = r[1].replace("_"," ").lower()
            n_2 = r[2].replace("_"," ").lower()
            type1 = get_type(n_1, HashMap)
            type2 = get_type(n_2, HashMap)
            
            DG.add_node(n_1, Type=type1+"::"+ge_1)
            DG.add_node(n_2, Type=type2+"::"+ge_2)
            
            if n_2 not in DG.adj[n_1]:
                DG.add_edge(n_1, n_2, weight={pred:1})
            else:
                if pred in DG[n_1][n_2]["weight"]:
                    DG[n_1][n_2]["weight"][pred] = DG[n_1][n_2]["weight"][pred] + 1
                else:
                    DG[n_1][n_2]["weight"][pred] = 1            
    return DG

def run():
    with open('your_path/gen.json', 'r') as f:
        lines = f.readlines()
    HashMap = testEntity2Types("freebase_types/entity2Types.txt")
    print(len(HashMap))
    #MDG = nx.MultiDiGraph()
    DG = nx.DiGraph()
    DG = build_Graph(DG, lines, HashMap)
    print(len(DG.nodes()))
    print(len(DG.edges()))
    nx.write_gpickle(DG, "KG/KG.gpickle")
    print("finish")

run()