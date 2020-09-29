#!/usr/bin/env python
# coding: utf-8

# In[9]:


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


# In[11]:


def preprocess(text):
    p = Parser()
    w = text.casefold()
    w = p.tokenize(w)
    w = p.stemming(w)
    return w

def create_query_dict(query):
    query_dict = {'t':[], 'i':[], 'b':[], 'c':[], 'l':[], 'r':[]}
    query_list = query.split(' ')
    for word in query_list:
        if ':'in word:
            tag = word.split(':')[0]
            w = preprocess(word.split(':')[1])
            query_dict[tag].append(w[0])
        else:
            w = preprocess(word)
            query_dict[tag].append(w[0])
    return query_dict

def create_global_dict(filename):
    global_dict = {}
    file = open(filename, 'r')
    line = file.readline()
    while line :
        global_dict[line.split(':')[0]] = line.split(':')[1]
        line = file.readline()
    return global_dict

if (__name__=="__main__"):
    query = sys.argv[2:]
    query = ' '.join(query)
    global_dict = create_global_dict(sys.argv[1]+'index_file.txt')

    check_field_query = ':' in query
    if check_field_query:
        query_dict = create_query_dict(query)
        for k,v in query_dict.items():
            for i in v:
                if i in global_dict.keys() and str(k) in global_dict[i]:
                    print(i+':'+global_dict[i])
                else:
                    print(i+':'+'')
    else:
        query_list = preprocess(query)
        for word in query_list:
            if word in global_dict:
                print(word+':'+global_dict[word])
            else:
                print(word+':'+'')
    
    


# In[ ]:





# In[ ]:




