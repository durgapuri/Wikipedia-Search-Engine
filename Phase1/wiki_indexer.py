#!/usr/bin/env python
# coding: utf-8

# In[21]:


import xml.sax
import sys
import collections
import os
import os.path
import re
import re
from collections import defaultdict
import Stemmer
# from nltk.stem.snowball import SnowballStemmer
# from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import timeit
from parsedata import Parser


# In[22]:


curr_id = 1
id_titlemap = dict()
global_dict = dict() 
total_tokens = 0
inverted_index_file_path = ""


# In[23]:


def createPageDict(title, infobox, body, category, link, references):
    pagedict = dict()
    
    # list format title, infobox, body, category, link, references
    # create local dictionary pagedict for entire page.. keep updating counts
    li = [0, 0, 0 ,0, 0 ,0]
    for i in title.keys():
        if i not in pagedict:
            pagedict[i]=[0, 0, 0 ,0, 0 ,0]
        pagedict[i][0]+=title[i]
            
    for i in infobox.keys():
        if i not in pagedict:
            pagedict[i]=[0, 0, 0 ,0, 0 ,0]
        pagedict[i][1]+=infobox[i]
    
    for i in body.keys():
        if i not in pagedict:
            pagedict[i]=[0, 0, 0 ,0, 0 ,0]
        pagedict[i][2]+=body[i]
            
    for i in category.keys():
        if i not in pagedict:
            pagedict[i]=[0, 0, 0 ,0, 0 ,0]
        pagedict[i][3]+=category[i]
            
    for i in link.keys():
        if i not in pagedict:
            pagedict[i]=[0, 0, 0 ,0, 0 ,0]
        pagedict[i][4]+=link[i]
            
    for i in references.keys():
        if i not in pagedict:
            pagedict[i]=[0, 0, 0 ,0, 0 ,0]
        pagedict[i][5]+=references[i]
        
    return pagedict

def mergeGlobalDict(currid, pagedict):
    global global_dict
    
    # if w already present in global dict then add new doc dictionary to it
    for w in pagedict:
        lt = pagedict[w]
        tmpdict = {}
        if w in global_dict:
            tmpdict = global_dict[w]
        tmpdict[currid] = lt
        global_dict[w] = tmpdict
      
    
def flushGlobalToFile():
    # format word:doc_id#tag_freq+tag_freq|doc_id#tag_freq+tag_freq
    # format word:d1#t2+i4|d3#t5+l4
    global global_dict
    inverted_index_file_path
    taglist = ['t', 'i', 'b', 'c', 'l', 'r']
    with open(inverted_index_file_path,"a") as of:
        for word,docs in sorted(global_dict.items()):
            if not(re.match('^[a-zA-Z0-9]+$',word)) or re.match('^[0]+$',word):
                continue
            docdict = docs
            docfreq = []
            for k,v in sorted(docdict.items()):
                docdet = "d"+str(k)+"#"
                for i in range(6):
                    if v[i]>0:
                        docdet += taglist[i]+str(v[i])+"+"
                docdet = docdet[:-1]                             # remove last +
                docfreq.append(docdet)
            docfreqstr = '|'.join(docfreq)
            of.write(word+":"+docfreqstr+"\n")  
    of.close()         
            

class XMLHandler(xml.sax.ContentHandler):
    
    global curr_id
    global id_titlemap
    
    def __init__(self):
        self.currenttag = ""
        self.title = ""
        self.text = ""
        self.obj = Parser()
        
    def startElement(self, tag, attributes):
        self.currenttag = tag
        if self.currenttag == "page":
            self.text = ""
            self.title = ""
            
    def characters(self, content):
        # collect data between <tag>..</tag>
        if self.currenttag == "title":
            self.title += content                   
        elif self.currenttag == "text":
            self.text += content

            
    def endElement(self, tag):
        global curr_id
        global global_dict
        global total_tokens
        if tag == "page":
            curr_id += 1
        if tag == "text":
#             id_titlemap[curr_id] = self.title
            
            # parse and preprocess title --> returns dictionary for title
            processed_title, title_tokens = self.obj.preprocessTitle(self.title)
            total_tokens += title_tokens
            
            # parse and preprocess text --> returns dictionary for infobox, body, category, links, references
            processed_infobox, processed_body, processed_category, processed_links,  processed_references, text_tokens= self.obj.preprocessText(self.text)
            total_tokens += text_tokens
            
#             print("--------------------")
#             print(curr_id, "title ", processed_title)
#             print("infobox ", processed_infobox)
#             print("body ", processed_body)
#             print("category ", processed_category)
#             print("links ", processed_links)
#             print("references ", processed_references)
#             print("---------------------------")

            # combined page dictionary with title, infobox, body, category, links, references dict merged
            pagedict = createPageDict(processed_title, processed_infobox, processed_body, processed_category, processed_links, processed_references)
            
            #merge local dict with global dictionary
            mergeGlobalDict(curr_id, pagedict)
            
        if curr_id%50000 == 0:
            #write global dictionary to file
            flushGlobalToFile()
            global_dict.clear()
            id_titlemap.clear()
#             sys.exit()
        self.currenttag = ""
        


# In[24]:


def createParser(xml_input):
    
    parserobj = xml.sax.make_parser()
    contenthandler = XMLHandler()
    
    # content handler for parser
    parserobj.setContentHandler(contenthandler)
    parserobj.parse(xml_input)
   


# In[25]:


if (__name__=="__main__"):
    
    # global inverted_index_file_path
    xml_input = sys.argv[1]
    inverted_index_file_path = sys.argv[2]+'index_file.txt'
    stat_file_path = sys.argv[3]
    start = timeit.default_timer()
    createParser(xml_input)
    
    #write remaning global dict to file
    # global global_dict
    if bool(global_dict):
        flushGlobalToFile()
    
    with open(stat_file_path,"a") as of:
        of.write(str(total_tokens)+'\n')
        of.write(str(len(global_dict))+'\n')
    of.close()
    
    stop = timeit.default_timer()
    print('Time: ', stop - start)
    


# In[26]:





# In[ ]:




