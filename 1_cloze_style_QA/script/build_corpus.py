import nltk
import json
import random
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"


def findAllFile(base):
    path_list = []
    for root, ds, fs in os.walk(base):
        for f in fs:
            fullname = os.path.join(root, f)
            path_list.append(fullname)
    return path_list
    
def build_raw_crawl(path_list, output_path):
    outputs = []
    f_write = open(output_path, 'w')
    count = 0
    for path in path_list:
        #print(path)  
        with open(path, 'r') as f:
            lines = f.readlines()   
        for line in lines:
            js = json.loads(line)
            if (js["text"] == '') or (js["text"] == ' ') or (len(js["text"]) == 1):
                continue
            count = count + 1
            date = "Feb 12, 2013 12:00:00 AM"
            #print("articleId", count)
            json.dump({"date":date, "title":js["title"], "url":js["url"], "text": js["text"], "articleId":count}, f_write)
            f_write.write('\n')
    f_write.close()
    return outputs
    
def run():
    # get all wiki data in List
    output = findAllFile('your_path/wiki/wiki_data/')
    #for i in output:
    #    print(i)
    print(len(output))
    
    # take random articles 15843
    #L = random.sample(output, 4000)
    raw = build_raw_crawl(output[0:-1], "crawl")
    print(len(raw))
    
run()