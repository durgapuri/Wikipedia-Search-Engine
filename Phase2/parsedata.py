#!/usr/bin/env python
# coding: utf-8

# In[1]:


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


# In[ ]:


class Parser:
    
    def tokenize(self,sentence):
        tokens = re.findall("\d+|[\w]+",sentence)
        tokens = [t for t in tokens]
        return tokens

    #remove urls
    #remove css
    #remove punctuations
    #remove [[file:]]
    #remove <..> tags from text
    def parse(self,sentence):
        re1 = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',re.DOTALL) 
        sentence = re1.sub('',sentence)
        re2 = re.compile(r'{\|(.*?)\|}',re.DOTALL)
        sentence = re2.sub(' ',sentence)
        re4 = re.compile(r'[.,;_()"/\']',re.DOTALL)
        sentence = re4.sub('',sentence)
        re5 = re.compile(r'\[\[file:(.*?)\]\]',re.DOTALL)
        sentence = re5.sub('',sentence)
        re6 = re.compile(r'<(.*?)>',re.DOTALL)
        sentence = re6.sub('',sentence)
        sentence = re.sub("^\d+\s|\s\d+\s|\s\d+$", " ", sentence)
        return sentence

    def remove_stopwords(self,tokens):
        stop_words = set(stopwords.words('english'))
        tokens = [t for t in tokens if t not in stop_words]
        return tokens

    def stemming(self,tokens):
#         stemmer = SnowballStemmer("english")
#         stemmer = PorterStemmer()
        stemmer = Stemmer.Stemmer('english')
        tokens = [stemmer.stemWord(w) for w in tokens]
        return tokens

    def tokenize_and_clean_title(self,title):
        title = title.casefold()
        title = self.parse(title)
        title = self.tokenize(title)
        title_tokens = len(title)
        title = self.remove_stopwords(title)
        title = self.stemming(title)
        return title, title_tokens

    # covert to lower
    # remove regex
    # tokenize
    # remove stop words
    # stemming
    def preprocessTitle(self,title):
        title, title_tokens = self.tokenize_and_clean_title(title)
        
        # create dictionary for title
        titledict = {}
        for t in title:
            if len(t)<=2:
                continue
            elif t.isdecimal() and len(t)>4:
                continue
            elif t not in titledict:
                titledict[t] = 1
            else:
                titledict[t] += 1
        return titledict, title_tokens

    def initialize_lists(self,text):
        infobox = list()
        body = list()
        category = list()
        references = list()
        return infobox, body, category, references

    def check_ex_links(self, data):
        if '==external links==' in data or '== external links ==' in data or '== external links==' in data or '==external links ==' in data:
            return True
        return False
    
    def check_references(self, data):
        if '==references==' in data or '== references ==' in data or '== references=='in data or '==references ==' in data:
            return True
        return False
    
    def classify_text(self,data):
        infobox, body, category,  references= self.initialize_lists(data)
        text = data.split('\n')
        reached_links=1
        i=0
        while i<len(text):
            
            if '{{infobox' in text[i]:
                diff = 0
#                 infobox.extend(text[i].split('{{infobox')[1:])
                while i<len(text):
                    if '{{' in text[i]:
                        diff += text[i].count('{{')
                    if '}}' in text[i]:
                        diff -= text[i].count('}}')
                    if diff>0:
                        splitline = text[i].split('{{infobox')
                        if("{{infobox" in text[i] and len(splitline) >= 2 and len(splitline[1])>0):
                            infobox.append(splitline[1])
                        else :
                            infobox.append(text[i])
                    else:
                        break
                    i+=1
                    
            elif "==references==" in text[i] or "== references ==" in text[i] or "==references ==" in text[i] or "== references==" in text[i]:
                i += 1
                while i<len(text) and '[[category' not in text[i] and '==' not in text[i]:
                    if '{{cite' in text[i] or '{{vcite' in text[i]:
                        l = text[i].split('title=')
                        if(len(l) > 1):
                            references.extend(l[1].split('|')[0].split(' '))
                            
                    elif '{{reflist' in text[i] or '{{redirect' in text[i]:
                        pass
                        
                    elif '{{' in text[i]:
                        l = text[i].split('{{')[1].split('}}')[0]
                        references.extend(l.split(' '))
                    i+=1
                    
            elif reached_links==1:
                if '[[category' in text[i] or self.check_ex_links(text[i]):
                    reached_links=0    
                body.append(text[i])
            
            elif '[[category:' in text[i]:
                cat = text[i].split('[[category:')
                if len(cat)>1:
                    category.append(cat[1].split(']]')[0])
                    
            i+=1

        return infobox, body, category, references


    def extract_links(self,text):
        links = list()
        text = text.split('\n')
        i=0
        while i < len(text):
            if self.check_ex_links(text[i]):
                i+=1
                while i<len(text):
                    if "*[" in text[i] or "* [" in text[i]:
                        links.extend(text[i].split(' '))
                    i+=1
            i+=1
        return links
    
    def preprocess_and_create_dict(self, text):
        text = self.tokenize(' '.join(text))
        text_tokens = len(text)
        text = self.remove_stopwords(text)
        text = self.stemming(text)
        temp = {}
        for k in text:
            if len(k)<=2:
                continue
            elif k.isdecimal() and len(k)>4:
                continue
            elif k in temp:
                temp[k] += 1
            else:
                temp[k]=1;
        return temp, text_tokens   
    
    def preprocessText(self,text):
        tokens_page = 0
        text = text.casefold()
        text = self.parse(text)
        links = self.extract_links(text)
        infobox, body, category, references = self.classify_text(text)
        # preprocess and create dictionary for each
        infobox, text_tokens = self.preprocess_and_create_dict(infobox)
        tokens_page += text_tokens
        body, text_tokens = self.preprocess_and_create_dict(body)
        tokens_page += text_tokens
        category, text_tokens = self.preprocess_and_create_dict(category)
        tokens_page += text_tokens
        links, text_tokens = self.preprocess_and_create_dict(links)
        tokens_page += text_tokens
        references, text_tokens = self.preprocess_and_create_dict(references)
        tokens_page += text_tokens
        return infobox, body, category, links, references, tokens_page
    

