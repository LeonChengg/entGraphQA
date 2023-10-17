import json
import torch
import argparse
import code
import prettytable
import logging
import drqa
from termcolor import colored
from drqa import pipeline
from drqa.retriever import utils

logger = logging.getLogger()
logger.setLevel(logging.INFO)
fmt = logging.Formatter('%(asctime)s: [ %(message)s ]', '%m/%d/%Y %I:%M:%S %p')
console = logging.StreamHandler()
console.setFormatter(fmt)
logger.addHandler(console)

parser = argparse.ArgumentParser()
parser.add_argument('--reader-model', type=str, default=None,
                    help='Path to trained Document Reader model')
parser.add_argument('--retriever-model', type=str, default=None,
                    help='Path to Document Retriever model (tfidf)')
parser.add_argument('--doc-db', type=str, default=None,
                    help='Path to Document DB')
parser.add_argument('--tokenizer', type=str, default=None,
                    help=("String option specifying tokenizer type to "
                          "use (e.g. 'corenlp')"))
parser.add_argument('--candidate-file', type=str, default=None,
                    help=("List of candidates to restrict predictions to, "
                          "one candidate per line"))
parser.add_argument('--no-cuda', action='store_true',
                    help="Use CPU only")
parser.add_argument('--gpu', type=int, default=-1,
                    help="Specify GPU device id to use")
args = parser.parse_args()

args.cuda = not args.no_cuda and torch.cuda.is_available()
drqa.tokenizers.set_default('corenlp_classpath', "your_path/DrQA/data/corenlp/*")
if args.cuda:
    torch.cuda.set_device(args.gpu)
    logger.info('CUDA enabled (GPU %d)' % args.gpu)
else:
    logger.info('Running on CPU only.')

if args.candidate_file:
    logger.info('Loading candidates from %s' % args.candidate_file)
    candidates = set()
    with open(args.candidate_file) as f:
        for line in f:
            line = utils.normalize(line.strip()).lower()
            candidates.add(line)
    logger.info('Loaded %d candidates.' % len(candidates))
else:
    candidates = None

logger.info('Initializing pipeline...')
DrQA = pipeline.DrQA(
    cuda=args.cuda,
    fixed_candidates=candidates,
    reader_model=args.reader_model,
    ranker_config={'options': {'tfidf_path': args.retriever_model}},
    db_config={'options': {'db_path': args.doc_db}},
    tokenizer=args.tokenizer
)

def read_queries(trex_file):
    with open(trex_file, 'r') as f:
        lines = f.readlines()
    for line in lines:
        js = json.loads(line)
        

def retrieve_doc(trex_file, candidates=None, top_n=1, n_docs=5):
    queries = []
    with open(trex_file, 'r') as f:
        lines = f.readlines()
    for line in lines:
        js = json.loads(line)
        queries.append(js)
    
    f = open("retrieve_trex_doc.json",'w')
    articleId = 1
    date = "Feb 12, 2013 12:00:00 AM"
    for query in queries:
        q = query['question']
        docids, result_5 = DrQA.search_retrived_document([q], candidates, top_n, n_docs, return_context=True)
        for i in range(n_docs):
            json.dump({"question": q, "title":docids[i], "retrieved_doc":docids[i] +' '+ result_5[i], "articleId": articleId, "sub-obj": query["sub-obj"], "pred": query["pred"], "types":query["types"]}, f)
            f.write('\n')
            articleId+=1
    f.close()          
    

def process(question, candidates=None, top_n=1, n_docs=5):
    predictions = DrQA.process(
        question, candidates, top_n, n_docs, return_context=True
    )
    
    for p in predictions:
        text = p['context']['text']
        start = p['context']['start']
        end = p['context']['end']
        output = (text[:start] +
                  colored(text[start: end], 'green', attrs=['bold']) +
                  text[end:])
        #print('[ Doc = %s ]' % p['doc_id'])
        #print(output + '\n')
        title = p['doc_id']
    return title, output   

def process_batch(questions):
    content_list = []
    for question in questions:
        content = process(question, candidates=None, top_n=1, n_docs=5)
        content_list.append(content)
    print(content_list)

def retrive_doc_para(queries, candidates=None, top_n=1, n_docs=5):
    crawl = []
    f = open("retrieve_gr_para.json",'w')
    articleId = 1
    date = "Feb 12, 2013 12:00:00 AM"
    for query in queries:
        q = query["query"]
        title, content = process(q, candidates=None, top_n=1, n_docs=5)
        print(title)
        
        json.dump({"question":q, "title":title, "retrieved_doc":content, "articleId":articleId, "raw_data":query["raw_data"], "rel":query["rel"]}, f)
        f.write('\n')
        articleId+=1
    f.close()
   
print("Running retrive_doc_para ................................")
retrieve_doc("your_path/boolQA/data/trex.json")