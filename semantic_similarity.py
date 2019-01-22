import spacy
from scipy.spatial.distance import cosine
import numpy as np
import logging
import sklearn
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import euclidean_distances
import json
import re
import gensim
from gensim import corpora, models, similarities
from gensim.models import Word2Vec
import nltk
from nltk.corpus import stopwords
from pprint import pprint
from nltk.tokenize import word_tokenize
import os
from docx import Document
import csv

"""
Due to the proper structuring of the JSON used future analysis is able to be
perforemed purely on paragraph text whilst avoiding false similarity measures
found in repeated section titles and subtitles (eg. INTRODUCTION)

Furthermore Chapters are properly labelled and irrelevant pages that contain
images or just links to other pages are ignored in the previous analysis

see webscraper.py
"""

##################################FUNCTIONS#####################################

#returns the chapter_name of a given JSON result
def get_chapter_name(document):
    section_counter = 0

    for key, value in document.items():
        return key
        for key2, value2 in value.items():
            #k2 = the section(section1)
            #v2 = the paragraphs
            section_counter+=1

# combines a given chapters paragraph text excluding any headings
def get_chapter_paragraph_text(document1):
    paragraph_text = ""
    section_counter = 0

    for key, value in document1.items():
        for key2, value2 in value.items():
            #k2 = the section(section1)
            #v2 = the paragraphs
            section_counter+=1

    #go through each section
    for i in range(section_counter):
        section_contents = document1[key]["Section" + str(i + 1)]
        #option to give heading more weighting or search by it

        #go through the section keys(heading,para,group) where k=key and v=value
        for k,v in section_contents.items():
            #print("key is " + k)
            if "Group" in k:
                #go through the group paragraphs
                group_paragraphs = section_contents[k]
                for para_k,para_v in group_paragraphs.items():
                    #option to give heading more weighting or search by itg
                    paragraph_text+=para_v
            #its a group heading or a paragraph
            elif "Para" in k:
                paragraph_text+=v
    return(paragraph_text)

# returns the paragraph texts of a chapter as a list
#ie. each sections paragraph texts are combined and saved in one index of the list
def get_chapter_paragraph_text_as_list(document1):
    paragraph_texts = []
    section_counter = 0

    for key, value in document1.items():
        for key2, value2 in value.items():
            #k2 = the section(section1)
            #v2 = the paragraphs
            section_counter+=1

    #go through each section
    for i in range(section_counter):
        appended_paras = ""
        section_contents = document1[key]["Section" + str(i + 1)]
        #option to give heading more weighting or search by it
        #paragraph_text+=section_contents['Heading']

        #go through the section keys(heading,para,group) where k=key and v = value
        for k,v in section_contents.items():
            #print("key is " + k)
            if "Group" in k:
                #go through the group paragraphs
                group_paragraphs = section_contents[k]
                for para_k,para_v in group_paragraphs.items():
                    #option to give heading more weighting or search by itg
                    appended_paras+=para_v
            #its a group heading or a paragraph
            elif "Para" in k:
                appended_paras+=v

        paragraph_texts.append(appended_paras)

    #for a in paragraph_texts:
    #    print(a)
    #    print("----------------------------------------")
    #    print("\n")
    #    print("\n")
    #print(paragraph_texts)

    return(paragraph_texts)

#processes given chapter_text,returns list of processed words
def tokenisation(chapter_text):
    # Cleaing the text
    chapter_text = chapter_text.lower()
    chapter_text = re.sub('[^a-zA-Z]', ' ', chapter_text )
    chapter_text = re.sub(r'\s+', ' ', chapter_text)

    # Preparing the dataset
    #convert to sentences for use in the Word2Vec model
    all_sentences = nltk.sent_tokenize(chapter_text)
    all_words = [nltk.word_tokenize(sent) for sent in all_sentences]

    # Removing Stop Words
    for i in range(len(all_words)):
        all_words[i] = [w for w in all_words[i] if w not in stopwords.words('english')]

    #returns list of processed words [[ u'maintenance', u'following', u'agencies']]
    #indexing removes the extra outer bracket
    #print(all_words[0])
    if(len(all_words)!=0):
        return (all_words[0])
    else:
        return False

#basic cleaning function
def clean_text(chapter_text):
    # Cleaing the text
    chapter_text = chapter_text.lower()
    chapter_text = re.sub('[^a-zA-Z]', ' ', chapter_text )
    chapter_text = re.sub(r'\s+', ' ', chapter_text)

    #return the cleaned paragraph text
    return chapter_text


#create the word vectors based on a given word word list
#where min_count specifies the minimum frequency for a word to appear in the corpus
def createWord2Vec(word_list):
    word2vec = Word2Vec(word_list, min_count=2)
    vocabulary = word2vec.wv.vocab
    return(vocabulary)

    #to access the most similar words
    #sim_words = word2vec.wv.most_similar('management')
    #print(sim_words)

#create a dictionary from the corpus
def create_dictionary(docList):
    dictionary = corpora.Dictionary(docList)
    return dictionary

def getFeatureLength(dictionary):
    return(len(dictionary.token2id))

def create_corpus(dictionary,docList):
    corpus = [dictionary.doc2bow(doc) for doc in docList]
    #print(corpus)
    return corpus

#The function doc2bow() simply counts the number of occurrences of each distinct word,
# converts the word to its integer word id and returns the result as a sparse vector
def create_doc_vector(dictionary,new_doc_text):
    new_vec = dictionary.doc2bow(new_doc_text.lower().split())
    return(new_vec)

#given a corpus calculate similarity between each document in the corpus
#and a given vec(query document)
def tfid_similarity(corp,vec,feature_length):
    tfidf = models.TfidfModel(corp)
    #needs to be given the feature length
    index = similarities.SparseMatrixSimilarity(tfidf[corp], num_features=feature_length)
    sims = index[tfidf[vec]]
    return sims

"""
When given the path of an individual chapter json result the program will compute
similarity between the given section name (eg. "PURPOSE") and output this to a txt file
"""
def compare_sections(path,section_name):
    #initialise variables
    para_texts = []
    cleaned_texts = []
    wordList = []
    section_counter = 0
    section_identifiers = []
    index = 0

    #open the given document
    with open(path) as doco:
        document2 = json.load(doco)
        for key, value in document2.items():
            for key2, value2 in value.items():
                #k2 = the section(section1)
                #v2 = the paragraphs
                section_counter+=1

        #have to check if there is more than one heading!!!
        if(section_counter < 2):
            print("There are not enough sections for this chapter to be compared internally.")
            return False

        #section headings are seperated in a list to be able to be compared
        section_texts = get_chapter_paragraph_text_as_list(document2)
        chapter_heading = get_chapter_name(document2)

        #go through each section individually
        for i in range(section_counter):
            section_contents = document2[key]["Section" + str(i + 1)]
            section_heading = section_contents['Heading']
            if section_heading == section_name:
                index = i
                #print(section)
            section_identifiers.append(chapter_heading[:10] + ' : ' +  section_heading)
            cleaned_text = clean_text(section_texts[i])


            if(tokenisation(cleaned_text)):
                IndividwordList = tokenisation(section_texts[i])
                wordList.append(IndividwordList)
            para_texts.append(section_texts[i])
            cleaned_texts.append(cleaned_text)


        section_contents = document2[key]["Section" + str(index + 1)]
        #section_heading = section_contents['Heading']
        individual_para_text = para_texts[index]
        individual_cleaned_text = cleaned_texts[index]
        individual_wordList = wordList[index]
        individual_id = section_identifiers[index]

        #give list of each preprocessed document
        corpus_dictionary = create_dictionary(wordList)

        #create query vector
        query_vector = create_doc_vector(corpus_dictionary,individual_cleaned_text)

        #compare the query doc to the rest of the corpus
        corpus = create_corpus(corpus_dictionary,wordList)

        #get the unique word count/feature length
        feature_length = getFeatureLength(corpus_dictionary)

        #get the similarity scores
        sims = tfid_similarity(corpus,query_vector,feature_length)

        #combine chapter headings with their scores and order them
        sim_list = []
        i = 0
        for sim in sims:
            #print chapter_names[i]
            sim_list.append((section_identifiers[i],sim))
            #print sim
            i+=1
        sim_list.sort(key=lambda tup: tup[1],reverse=True)

        #output to a results doc the top n(10 in this example) most similar chapters to the queired vec
        with open('/Users/emma/Desktop/ADFA work/similar_sections.txt', 'w') as outfile:
            outfile.write(individual_id)
            outfile.write("\n")
            outfile.write("\n")
            for i in range(section_counter):
                #chapter heading
                outfile.write("SECTION:" + str(sim_list[i][0]))
                outfile.write("\n")
                outfile.write("SIMILARITY:" + str(sim_list[i][1]))
                outfile.write("\n")


"""
when given the path to an individual chapters json result file and the directory to the residing
processed chapters the program will compare the chapter to the others in the directory
outputting the results ordered in a csv file for future analysis.
"""
def compare_chapter(individual_document_path,directory_path):
    para_texts = []
    cleaned_texts = []
    wordList = []
    chapter_names = []

    for json_page in os.listdir(directory_path):
        if('json' in str(json_page)):
            with open(directory_path + json_page) as f:
                print(json_page)
                data = json.load(f)
                para_text = get_chapter_paragraph_text(data)
                cleaned_text = clean_text(para_text)
                if(tokenisation(para_text)):
                    IndividwordList = tokenisation(para_text)
                    wordList.append(IndividwordList)
                para_texts.append(para_text)
                cleaned_texts.append(clean_text)
                name = get_chapter_name(data)
                chapter_names.append(name)


    #perform the necessary calculations to get a vector representation of the chapter to be compared
    with open(individual_document_path) as f:
        individual_data = json.load(f)
    individual_para_text = get_chapter_paragraph_text(individual_data)
    individual_cleaned_text = clean_text(individual_para_text)
    individual_wordList = tokenisation(individual_para_text)
    individual_chapter_heading = get_chapter_name(individual_data)

    #give list of each preprocessed document
    corpus_dictionary = create_dictionary(wordList)

    #create query vector
    query_vector = create_doc_vector(corpus_dictionary,individual_cleaned_text)

    #compare the query doc to the rest of the corpus
    corpus = create_corpus(corpus_dictionary,wordList)

    #get the unique word count/feature length
    feature_length = getFeatureLength(corpus_dictionary)

    #get the similarity scores
    sims = tfid_similarity(corpus,query_vector,feature_length)

    #combine chapter headings with their scores and order them
    sim_list = []
    i = 0
    for sim in sims:
        sim_list.append((chapter_names[i],sim))
        i+=1
    sim_list.sort(key=lambda tup: tup[1],reverse=True)

    #output to a results doc the top n(10 in this example) most similar chapters to the queired chapter
    with open('/Users/emma/Desktop/ADFA work/similar_chapters.txt', 'w') as outfile:
        outfile.write(individual_chapter_heading)
        outfile.write("\n")
        outfile.write("\n")
        for i in range(10):
            #chapter heading
            outfile.write("CHAPTER:" + str(sim_list[i][0]))
            outfile.write("\n")
            outfile.write("SIMILARITY:" + str(sim_list[i][1]))
            outfile.write("\n")
            outfile.write("\n")
        outfile.close()
    #sims_list = sorted(enumerate(sim_list), key=lambda item: -item[1])

    #output results to a csv file
    with open('/Users/emma/Desktop/ADFA work/Similarity Results/' + individual_chapter_heading + '.csv','w') as outFile:
        np.savetxt('/Users/emma/Desktop/ADFA work/Similarity Results/' + individual_chapter_heading + '.csv',sim_list,fmt='%s' ,delimiter =',')
    outFile.close()


"""
given a chapter path and its corresponding chosen section this program will go
through every JSON file in the given directory_path and compare the chosen section
to chapters sections with the same name
"""
def compare_alike_sections(individual_document_path,directory_path,section_name):




#compare_sections('/Users/emma/Desktop/ADFA work/processed_chapters/V14S06C03 .json',"PROCESS OVERVIEW")

compare_chapter('/Users/emma/Desktop/ADFA work/processed_chapters/V10S03C03C.json', '/Users/emma/Desktop/ADFA work/processed_chapters/')
