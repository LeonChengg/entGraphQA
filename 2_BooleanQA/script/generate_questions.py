import json
import nltk
import nltk.data
from nltk.corpus import wordnet
import argparse
from nltk.stem import WordNetLemmatizer
import os
from os import path

def read_data(trex_dir, rels):
    Lines = []
    data = []
    for rel in rels:
        if not path.exists(trex_dir + rel + '.jsonl'):
            continue
        with open(trex_dir + rel + '.jsonl', 'r') as f:
            Lines = Lines + f.readlines()
    for line in Lines:
        js = json.loads(line)
        data.append(js)
    return data

def generate_qa_pairs(evidences, preds, template, types):
    output = []
    for evidence in evidences[:1]:
        sub = evidence["sub_surface"]
        obj = evidence["obj_surface"]
        answer = evidence["masked_sentence"].replace('[MASK]', obj)
        for pred in preds:
            question = template.replace('[X]', sub)
            question = question.replace('[Y]', obj)
            question = question.replace('[P]', pred)
            output.append({'question':question, 'answer':answer, 'pred': pred, 'raw_data':evidence, 'types':types})
    return output        

def run(args):
    # read pred_p.txt to get rels and templates
    with open(args.hypo) as f:
        line = f.read()
    line = line.replace('\n', '')
    preds_data = json.loads(line)
    data = read_data(args.trex_dir, preds_data.keys())
    
    generated_data = []
    for instance in data:
        rel = instance["predicate_id"]
        evidences = instance["evidences"]
        template = preds_data[rel]['template']
        preds = preds_data[rel]['predicate']
        types = preds_data[rel]['types']
        generated_data = generated_data + generate_qa_pairs(evidences, preds, template, types)
    
    with open(args.output, 'w') as f:
        for i in generated_data:
            json.dump(i, f)
            f.write('\n')    


if __name__ == '__main__':
    my_arg = argparse.ArgumentParser('My argument parser')
    my_arg.add_argument('--trex_dir', default="your_path/LAMA/LAMA/data/TREx/", type=str, help='data_path')
    my_arg.add_argument('--hypo', default='', type=str, help='the path to extracted hypo verbs')
    my_arg.add_argument('--output', default='', type=str, help='the path to save results')
    args = my_arg.parse_args()
    run(args)