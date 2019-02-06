#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This program will first store and then analyse the context of a given hyperlink
using the surrounding paragraph text given a htm page to process. It is
based on the ADF supply chain manual"""


#imports
import os
import re
import nltk
import numpy as np
import pandas as pd
import string
import pprint as pp
import json
from bs4 import BeautifulSoup, NavigableString
from collections import OrderedDict
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer


###################################FUNCTIONS###################################

#scrape page
"""gets the chapter heading of the page given a soup object"""
def getChapterHeading(soup):
    try:
        #dealing with headings that contain unencodeable ascii namely, "<?>"
        chap_head = soup.find('h4').get_text()
        chap_head=chap_head.encode('ascii',errors='ignore')
        return str(chap_head)
    except Exception as e:
        return False

"""
scrape the page: store the chapter title, hyperlink and the hyperlinks
 surrounding pragraph text in JSON format(hyperlink_htm_format.json)
"""
def scrapePage(htm_path):
    #dictionary declarations
    chapter_dict = OrderedDict()
    hyperlink_dict = OrderedDict()

    #counter/flag variables
    href_counter = 0


    #open the page
    doc = htm_path
    with open(doc) as fp:
        soup = BeautifulSoup(fp, 'lxml')

    #get the chapter heading and store it
    chapt_head = getChapterHeading(soup)

    #some chapters dont have a chapter_heading...
    if(chapt_head == False):
        chapt_head = htm_path


    #search each body paragraph within the container body1 to avoid headers/footers etc
    for paragraph in soup.find_all("li", {"class": "body1"}):
        paragraph_text = paragraph.get_text()

        #go through each link if they exist
        for link in paragraph.find_all('a',href = True):
            #there are hyperlink(s) in this paragraph, store them in hyperlink dict
            hasHyper=True
            href_counter+=1
            hyperlink_title = link.get_text()
            href_id = link['href']

            #store the paragraphs relevant info in a dictionary
            hyperlink_dict["Hyperlink" + str(href_counter)] = {
                "title" : hyperlink_title,
                "id" : href_id,
                "paragraph_text" : paragraph_text
            }

    #check if the page contains ANY hyperlinks
    if(href_counter == 0):
        print(str(chapt_head) +  " contained no hyperlinks or is not a relevant chapter, and has been skipped")
        return False


    #store each chapters hyperlinks in one dictionary
    chapter_dict[str(chapt_head)] = hyperlink_dict

    #user notifications
    print(str(chapt_head) + " HAS " + str(href_counter) + " hyperlink(s)")
    print("see " + str(chapt_head)[:12] + ".json for results" )

    #output to JSON in chosen directory
    out_directory = '/Users/emma/Desktop/ADFA work/processed_hyperlink_chapters/'
    with open(out_directory + str(chapt_head)[:12] + '.json', 'w') as outfile:
        json.dump(chapter_dict, outfile)



"""
returns the chapter heading of a JSON result of the format seen in hyperlink_htm_format
given a document object
"""
def getJsonChaptHead(document):
    for key,value in document.items():
        return key

"""
return the hyperlinks display texts of a JSON result, of the format seen in hyperlink_htm_format,
given a document object and return the list as a dictionary
"""
def getJsonHyperlinkTitles(document):
    hyperlink_titles = dict()
    hyperlink_counter = 0

    #iterate through the JSON
    for key,value in document.items():
        chapt_title = key
        for k,v in value.items():
            hyperlink_counter+=1
            #k = hyperlinks

    #get the hyperlink texts and store them in a dictionary
    for i in range(hyperlink_counter):
        #print(document[chapt_title]["Hyperlink" + str(i+1)]["title"])
        hyperlink_titles[i+1] = document[chapt_title]["Hyperlink" + str(i+1)]["title"]

    return hyperlink_titles

"""
return the hyperlinks id's/routing address of a JSON result, of the format seen in hyperlink_htm_format,
given a document object and return the list as a dictionary
"""
def getJsonHyperlinkIds(document):
    hyperlink_ids = dict()

    hyperlink_counter = 0

    #iterate through the JSON
    for key,value in document.items():
        chapt_title = key
        for k,v in value.items():
            hyperlink_counter+=1
            #k = hyperlinks

    #get the hyperlink id's and store them in a dictionary
    for i in range(hyperlink_counter):
        hyperlink_ids[i+1] = document[chapt_title]["Hyperlink" + str(i+1)]["id"]

    return hyperlink_ids

"""
This function will check if the chapters hyperlink_ids are local htm files we can access
and instead store the corresponding chapters title instead of "1234.htm"
"""
def checkHyperlinkIds(hyper_ids):
    for i in range(len(hyper_ids)):
        if("htm" in hyper_ids[i+1]):
            print('ugly')


        return hyper_ids


"""
This function will return a list of the hyperlinks paragraph texts cut down to only the
text BEFORE the hyperlink is referenced of a JSON result, of the format seen in hyperlink_htm_format,
given a document object and return the list as a dictionary.
"""
def getJsonHyperlinkParagraphs(document,hyperlink_titles):
    hyperlink_sentences = dict()

    hyperlink_counter = 0

    #iterate through the JSON
    for key,value in document.items():
        chapt_title = key
        for k,v in value.items():
            hyperlink_counter+=1
            #k = hyperlinks

    #get the hyperlink sentences and store them in a dictionary
    for i in range(hyperlink_counter):
        hyperlink_sentences[i+1] = document[chapt_title]["Hyperlink" + str(i+1)]["paragraph_text"]

    #we only want the text BEFORE the given hyperlink
    #update the dictionary to reflect this
    for i in range(len(hyperlink_sentences)):
        #set the paragraph text
        para_text = hyperlink_sentences[i+1]
        #split on the hyperlink
        first_split = para_text.split(hyperlink_titles[i+1])
        #get the closest words to the hyperlink
        text = first_split[0]
        hyperlink_sentences[i+1] = text
        #print(hyperlink_sentences[i+1])
        #print("\n")

    return hyperlink_sentences

"""This function will handle the list of paragraphs for each hyperlink and preprocess them
ready for analysis, it is a bit slow and takes a dictionary"""

def preProcess(hyper_paras):
    new_hyper_paras = dict()

    for i in range(len(hyper_paras)):
        #convert all to lower case
        hyper_paras[i+1] = hyper_paras[i+1].lower()

        #remove punctuation
        hyper_paras[i+1] = re.sub(r'[^\w\s]','',hyper_paras[i+1])

        #remove numbers
        hyper_paras[i+1] = re.sub(r'\d+', '', hyper_paras[i+1])

        #return the closest 25 words
        split_paras = hyper_paras[i+1].split()

        if(len(split_paras) > 50):
            start_point = len(split_paras) - 50
        else:
            start_point = 0

        for j in range(50):
            if start_point < len(split_paras):
                if j==0:
                    hyper_paras[i+1] = split_paras[start_point]
                else:
                    hyper_paras[i+1] = hyper_paras[i+1] + ' ' + split_paras[start_point]

            start_point+=1

        #tokenise words
        #hyper_paras[i+1] =  word_tokenize(hyper_paras[i+1])

        #remove stop words
        #hyper_paras[i+1]  = [w for w in hyper_paras[i+1] if not w in stopwords.words()]

        #lemmatise
        #lemmatizer = WordNetLemmatizer()

        #hyper_paras[i+1] = [ lemmatizer.lemmatize(word) for word in hyper_paras[i+1] ]

        #print(hyper_paras[i+1])

        #print(i)

    return hyper_paras

"""
This function will take in ONE json result file name, format seen in hyperlink_htm_format.json,
and create a correspodning csv result in an attempt to give the reader an idea
of the purpose of the hyperlink.
"""
def processHyperlink(json_result):

    #open the file
    with open(json_result) as f:
        print("\n")
        data = json.load(f)

    #store the chapter title
    chapt_title = getJsonChaptHead(data)

    #get the hyperlink_titles/display text
    hyperlink_titles = getJsonHyperlinkTitles(data)

    #get the hyperlink id's
    hyperlink_ids_1 = getJsonHyperlinkIds(data)

    #refine the hyperlink_ids
    hyperlink_ids = checkHyperlinkIds(hyperlink_ids_1)

    #get the text thats right before the hyperink as multiple often reside in one paragraph and will yield the same results otherwise
    hyperlink_paragraphs = getJsonHyperlinkParagraphs(data,hyperlink_titles)

    #analyse/process the paragraph texts
    processed_hyper_paras = preProcess(hyperlink_paragraphs)

    #[print(processed_hyper_paras[i],'\n') for i in processed_hyper_paras]

    #output results to csv file
    data = [hyperlink_titles,hyperlink_ids,processed_hyper_paras]
    df = pd.DataFrame(data)
    df_transposed = df.T
    df_transposed.columns = ['Display Title','URL','Surrounding Terms']
    df_transposed.to_csv("/Users/emma/Desktop/ADFA work/hyperlink_results/" + chapt_title + ".csv")



"""This program will process every htm page in the given in_directory and output
the results to the chosen out_directory specified in scrapePage"""
def processHtmPages(directory_name):
    file_counter = 0

    print("Main function starting...")
    for htm_page in os.listdir(directory_name):
        if("htm" in str(htm_page)):
            file_counter+=1
            print(htm_page + " is being processed")
            scrapePage(str(directory_name) + '/' + htm_page)
    print("Amount of files processed: " + str(file_counter))



"""main function"""
if __name__ == '__main__':
    #processHtmPages('ESCMCDVersion')
    processHyperlink("/Users/emma/Desktop/ADFA work/processed_hyperlink_chapters/V04S13C02 - .json")
