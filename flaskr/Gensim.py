import os
import tkinter as tk
from tkinter import filedialog
import docx
from gensim import corpora
from gensim import models
from gensim.utils import simple_preprocess
from gensim.corpora import MmCorpus
import logging
from flask import Flask, render_template, request, redirect, url_for, flash

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)

def getText(filename):
    doc = docx.Document(filename)
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text)
    return "".join(fullText)

def CreateStudent(stdNum, fileName):
    path = os.getenv('UPLOAD_EXTENSIVE')
    pathJoin = os.path.join(path, stdNum)

    if not os.path.exists(pathJoin):
        os.mkdir(pathJoin)
        os.mkdir(pathJoin + '/Corpus File')
        os.mkdir(pathJoin + '/Data')
    else:
        print("Directory already exists")

    print("Filename" + fileName)
    print("PathJoin: " + pathJoin)
    result = ''.join(line.strip() for line in getText("./flaskr/GensimTemp/" + fileName).splitlines())
    # print(repr(result))   
    
    #Write to Corpus File
    checkFile =  os.path.isfile(pathJoin + '/Corpus File/' + stdNum + '_corpus.txt')
    checkDoc =  os.path.isfile(pathJoin + '/Data/' + stdNum + '_docNames.txt')
    if checkFile == True and checkDoc == True:
        docCorpus = open(pathJoin + '/Corpus File/' + stdNum + '_corpus.txt', "a", encoding="utf-8")
        docCorpus.write(result + '\n')
        docCorpus.close()
        docNames = open(pathJoin + '/Data/' + stdNum + '_docNames.txt', "a", encoding="utf-8")
        docNames.write(fileName + '\n')
        docNames.close()
    else:
        docCorpus = open(pathJoin + '/Corpus File/' + stdNum + '_corpus.txt', 'w', encoding="utf-8")
        docCorpus.write(result + '\n')
        docCorpus.close()
        docNames = open(pathJoin + '/Data/' + stdNum + '_docNames.txt', "w", encoding="utf-8")
        docNames.write(fileName + '\n')
        docNames.close()

class read_multiplefiles(object):
    def __init__(self, dir_path):
        self.dir_path = dir_path
    def __iter__(self):
        for filename in os.listdir(self.dir_path):
            for line in open(os.path.join(self.dir_path, filename), encoding="utf-8"):
                yield simple_preprocess(line)

"""Compare Corpus"""
         
def CompareCorpus(stdNum, fileName):
    # Path
    path = os.getenv('UPLOAD_EXTENSIVE')
    pathJoin = os.path.join(path, stdNum)
    dictionary = corpora.Dictionary(line.lower().split() for line in open(pathJoin + '/Corpus File/' + stdNum + '_corpus.txt', encoding="utf-8"))
    # remove stop words and words that appear only once
    stoplist = set('for a of the and to in'.split())
    stop_ids = [
        dictionary.token2id[stopword]
        for stopword in stoplist
        if stopword in dictionary.token2id
    ]
    once_ids = [tokenid for tokenid, docfreq in dictionary.dfs.items() if docfreq == 1]
    dictionary.filter_tokens(stop_ids + once_ids)  # remove stop words and words that appear only once
    dictionary.compactify()  # remove gaps in id sequence after words that were removed
    print(dictionary)
    # save your dictionary to disk
    dictionary.save(pathJoin + '/Data/' + stdNum + 'dictionary.dict')
    print("Dictionary saved")

    #creating a bag-of-words corpus from multiple files in the directory provided
    corpus = [dictionary.doc2bow(token, allow_update=True) for token in read_multiplefiles(pathJoin + '/Corpus File/')]
    corpora.MmCorpus.serialize(pathJoin + '/Data/' + stdNum + 'corpus.mm', corpus)
    # print("BoW corpus saved")

    lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=2)
    result = ''.join(line.strip() for line in getText("./flaskr/GensimTemp/" + fileName).splitlines())
    print('--results--')
    #print(result)
    print('----------Data----------')
    vec_bow = dictionary.doc2bow(result.lower().split())
    vec_lsi = lsi[vec_bow]  # convert the query to LSI space
    print(vec_bow)
    print(vec_lsi)

    from gensim import similarities
    index = similarities.MatrixSimilarity(lsi[corpus])  # transform corpus to LSI space and index it

    sims = index[vec_lsi]  # perform a similarity query against the corpus
    print('-------LSI SIM-------')
    print(list(enumerate(sims)))  # print (document_number, document_similarity) 2-tuples

    #TF-IDF model
    tfidf = models.TfidfModel(corpus)
    feauture_count = len(dictionary.token2id)
    index2 = similarities.MatrixSimilarity(tfidf[corpus], num_features=feauture_count)
    sim2 = index2[tfidf[vec_bow]]
    for i in range(len(sim2)):
        print('Dcoument is similar to document %d: %.2f' % (i+1, sim2[i]))

    
    checkFile =  os.path.isfile(pathJoin + '/Corpus File/' + stdNum + '_corpus.txt')
    if checkFile == True:
        docCorpus = open(pathJoin + '/Corpus File/' + stdNum + '_corpus.txt', "a", encoding="utf-8")
        docCorpus.write(result + '\n')
        docCorpus.close()
        #print('Document added to corpus')
        docNames = open(pathJoin + '/Data/' + stdNum + '_docNames.txt', "a", encoding="utf-8")
        docNames.write(fileName + '\n')
        docNames.close()
    else:
        docCorpus = open(pathJoin + '/Corpus File/' + stdNum + '_corpus.txt', 'w', encoding="utf-8")
        docCorpus.write(result + '\n')
        docCorpus.close()
        #print('Document added to corpus')
        docNames = open(pathJoin + '/Data/' + stdNum + '_docNames.txt', "w", encoding="utf-8")
        docNames.write(fileName + '\n')
        docNames.close()

"""Update Student"""
def UpdateStudent(stdNum, fileName):
    path = os.getenv('UPLOAD_EXTENSIVE')
    pathJoin = os.path.join(path, stdNum)
    result = ''.join(line.strip() for line in getText("./flaskr/GensimTemp/" + fileName).splitlines())
    #print(repr(result))
    
    #Write to Corpus File
    checkFile =  os.path.isfile(pathJoin + '/Corpus File/' + stdNum + '_corpus.txt')
    if checkFile == True:
        docCorpus = open(pathJoin + '/Corpus File/' + stdNum + '_corpus.txt', "a", encoding="utf-8")
        docCorpus.write(result + '\n')
        docCorpus.close()
        docNames = open(pathJoin + '/Data/' + stdNum + '_docNames.txt', "a", encoding="utf-8")
        docNames.write(fileName + '\n')
        docNames.close()
        #print('corpus updated')
    else:
        docCorpus = open(pathJoin + '/Corpus File/' + stdNum + '_corpus.txt', 'w', encoding="utf-8")
        docCorpus.write(result + '\n')
        docCorpus.close()
        docNames = open(pathJoin + '/Data/' + stdNum + '_docNames.txt', "w", encoding="utf-8")
        docNames.write(fileName + '\n')
        docNames.close()
        #print('corpus updated')
    
