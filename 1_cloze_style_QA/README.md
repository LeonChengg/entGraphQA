# Enhanced knowledge graphs Using Typed Entailment Graphs
This is an implementation of the paper Enhanced knowledge graphs Using Typed Entailment Graphs. The step of constructing entailment graphs is followed [Javad's entGraph](https://github.com/mjhosseini/entGraph.git) work, so it needs Java environment (Java SE 8).

## data prepare
The training dataset can be download:
Wikicorpus: https://dumps.wikimedia.org/enwiki/20220101/enwiki-20220101-pages-articles-multistream.xml.bz2
NewsSpike dataset can be downloaded from links http://www.cs.washington.edu/ai/clzhang/release.tar.gz

After downloading the Wikicorpus, we use the [WikiExtractor](https://github.com/attardi/wikiextractor.git). Follow the steps of WikiExtractor, we will get the extracted clean text.

Run `python script/build_corpus.py`. The text wiki will be transferred into the standard input format for training knowledge graphs.  

copy the output file `crawl` to path entGraph/data/release/


## Extract triples by graph-parser
Step1: Download the lib_data, data, lib files from [link](https://worksheets.codalab.org/worksheets/0x8684ad8e95e24c4d80074278bce37ba4/)

Step2: Compile the Java files. 

Step3: cd `entGraph/` 
       run `java -cp lib/*:bin entailment.Util data/release/crawl 1>raw.json`

Step4: Run `sh prArgs.sh`. You can change the input file name. The script extract binary relations from the input json file(This takes about 12 hours on the servers I used with 20 threads.)


## Entity-linking
This part is using aidalight to map tokens in triples into entities. The details of AidaLight can read the README.md in `aidalight` folder.

cd `../aidalight` 
Download bned.zip at http://download.mpi-inf.mpg.de/d5/aida/bned.zip, unzip bned.zip and put the folder bned in the "path-to-aidalight"/data 

Set up RMI servers
=========
The minimum number of main memory required to run AIDALight is 25GB, however, we strongly recommend a server with 35-40GB to run the best setting of AIDALight.
Set up AIDALight Server by:
    1. Go to the AIDALight folder
	2. Set up AIDALight server
	   ./scripts/setup_aidalight_server.sh 
	   or java -Xmx30G -cp ".:./bin:./lib/*" mpi.aidalight.rmi.AIDALight_main  // set up AIDAlight server in localhost, with "partlyMatchingMentionEntitySearch" option.
	   or java -Xmx30G -cp ".:./bin:./lib/*" mpi.aidalight.rmi.AIDALight_main localhost false // set up AIDAlight server without "partlyMatchingMentionEntitySearch" option.
	3. If you set up AIDALight server with "partlyMatchingMentionEntitySearch" option, you then need to set up the LSH Server
	   ./scripts/setup_lsh_server.sh
	4. Run an example
	   java -cp ".:./bin:./lib/*" mpi.aidalight.rmi.AIDALight_client


## Construct knowledge graph
copy the output file of aidalight to `entGraph` folder. 

Run `java -Xmx100G -cp lib/*:bin entailment.Util predArgs_gen.txt true true 12000000 entity_linked.json 1>gen.json 2>err.txt &`

run `python script/build_type_KG.py`.

## Build entailment graphs
CNCE:
  Follow the steps of [linkpred_entgraph](https://github.com/mjhosseini/linkpred_entgraph.git)

BInc Score:
  1. Go to the entGraph folder
  2. Run `java -Xmx100G -cp lib/*:bin entailment.vector.EntailGraphFactoryAggregator` get the local BInc score of predicates.
  3. Run `java -Xmx220G -cp lib/*:bin graph.softConst.TypePropagateMN` for global learning

Build entailment graphs for query. Run `python script/build_type_KG.py`

## query by entailmemnt graphs
  The Google-RE and YAGO3-10 could directly be used for query. T-REx be constructed as (Subject, Predicate, Object) for query.
  The steps has shown in chapter ``Extract triples by graph-parser``
  
  Run `python eval.py`