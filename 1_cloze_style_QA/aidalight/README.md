AIDALight
=========
AIDA-light is a new NED system that reconciles high output quality with fast run-time. Our experiments have shown that AIDA-light consistently 
performs as well as or better than state-of-the-art competitors, over a variety of corpora including news (CoNLL), difficult and short contexts (WP), 
Web pages (Wiki-links), and Wikipedia articles. 

Download required data
=========
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
	   This asks AIDALight to disambiguate a sample sentence: "With United, Beckham won the Premier League title 6 times.".
	   The results will be in format of "mention \t Wikipedia-url":
	   		United	http://en.wikipedia.org/wiki/Manchester_United_F.C.
			Premier League	http://en.wikipedia.org/wiki/Premier_League
			Beckham	http://en.wikipedia.org/wiki/David_Beckham
We remark that the "partlyMatchingMentionEntitySearch" is to improve recall over a variety of input texts, especially Web pages where many out-of-dictionary mentions occur.
We apply Locality Sensitive Hashing (LSH) in combination with a min-wise permutation scheme to cover more spelling variations among these mentions. 
That is, once an out-of-dictionary mention occurs, AIDA-light first attempts to find similar mentions for it via LSH. 
Second, all possible entity candidates of these similar mentions are assigned to this mention as candidate entities. 

Run your own examples
=========
What you need to do is take a look at mpi.aidalight.rmi.AIDALight_client class and modify/call the disambiguate function.
	AIDALight_client.disambiguate(String text, List<Mention> mentions, String host);
	For example: AIDALight_client.disambiguate("With United, Beckham won the Premier League title 6 times.", null, null);
	Notice:
		1. The "host" must be set to null because we only work with the localhost servers.
		2. If you want to use your own NER tool, you can pass the mention list... Otherwise, the StanfordNER will be applied to recognize mentions.

Experimental data in AIDALight's paper (http://events.linkeddata.org/ldow2014/papers/ldow2014_paper_03.pdf)
=========
Due to problems with license, we can not make all corpora used in AIDALight's paper available here. However, we will guide you how to get them.
	1. CoNLL testb corpus and WP corpus are taken from AIDA, and thus, we refer to AIDA page https://www.mpi-inf.mpg.de/yago-naga/aida/index.html
	2. Wikipedia corpus is already in ./data/experiment/WIKIPEDIA folder.
	3. Wiki-links corpus
		3.1. Download & extract the data-00007-of-00010.gz file from https://code.google.com/p/wiki-links/downloads/list
		3.2. java -Xmx10G -cp ".:./bin:./lib/*" mpi.aidalight.exp.WikiLinkWrapper "path-to-data-00007-of-00010-file" ./data/file_names/wiki-links ./data/experiment/WIKI-LINKS/WIKI-LINKS.tsv
		We remark that we can not guarantee you can get all the data because the code have to gather the data from a variety of sources in the Internet. 
		This might lead to problems when a web-site/a server is down!
After you have these corpora, you can run AIDALight on them by:
	./scripts/run_experiments.sh CoNLL testb ------ for CoNLL
	./scripts/run_experiments.sh WP --------------- for WP
	./scripts/run_experiments.sh Wikipedia -------- for Wikipedia
	./scripts/run_experiments.sh Wiki-links ------- for Wiki-links