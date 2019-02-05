"""This program will first store and then analyse the context of a given hyperlink
using the surrounding paragraph text given a htm page to process. It is
based on the ADF supply chain manual"""


#imports
import os
from bs4 import BeautifulSoup, NavigableString
from collections import OrderedDict
import pprint as pp
import json

###################################FUNCTIONS###################################

#scrape page
"""gets the chapter heading of the page given a soup object"""
def getChapterHeading(soup):
    try:
        #dealing with headings that contain unencodeable ascii namely, "<?>"
        chap_head = soup.find('h4').get_text()
        chap_head=chap_head.encode('ascii',errors='ignore')
        return chap_head
    except Exception as e:
        return False

"""scrape the page: store the chapter title, hyperlink and the hyperlinks
 surrounding pragraph text in JSON format(hyperlink_htm_format.json)"""
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
            href_id = link['href'] + str(href_counter)

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
    chapter_dict[chapt_head] = hyperlink_dict

    #user notifications
    print(str(chapt_head) + " HAS " + str(href_counter) + " hyperlink(s)")
    print("see " + str(chapt_head)[:12] + ".json for results" )

    #output to JSON in chosen directory
    out_directory = '/Users/emma/Desktop/ADFA work/processed_hyperlink_chapters/'
    with open(out_directory + chapt_head[:12] + '.json', 'w') as outfile:
        json.dump(chapter_dict, outfile)



"""returns the chapter heading of a JSON result of the format seen in hyperlink_htm_format
given a document object"""
def getJsonChaptHead(document):
    for key,value in document.items():
        return key

"""return the hyperlinks display texts of a JSON result, of the format seen in hyperlink_htm_format,
given a document object and return the list as a dictionary"""
def getJsonHyperlinkTexts(document):
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

"""return the hyperlinks id's/routing address of a JSON result, of the format seen in hyperlink_htm_format,
given a document object and return the list as a dictionary"""
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

"""This function will take in the json result file name, format seen in hyperlink_htm_format.json, and return the
key terms in the paragraph in an attempt to give the reader an idea of the purpose of the hyperlink"""
def analyseText(json_result):

    #open the file
    with open(json_result) as f:
        print("\n")
        data = json.load(f)

    #store the chapter title
    chapt_title = getJsonChaptHead(data)

    #get the hyperlink texts
    hyperlink_texts = getJsonHyperlinkTexts(data)

    #get the hyperlink id's
    hyperlink_ids = getJsonHyperlinkIds(data)

    #check if the id of the hyperlink is a htm file we can access and get that title!

    #use the text thats right before the hyperink (just the sentence before)


#store results of analysis in csv format

"""This program will process every htm page in the given in_directory and output
the results to the chosen out_directory specified in scrapePage"""
def processHtmPages(directory_name):
    file_counter = 0

    print("Main function starting...")
    for htm_page in os.listdir(directory_name):
        if("htm" in str(htm_page)):
            file_counter+=1
            print(htm_page)
            scrapePage(str(directory_name) + '/' + htm_page)
    print("Amount of files processed: " + str(file_counter))



"""main function"""
if __name__ == '__main__':
    #processHtmPages('ESCMCDVersion')
    analyseText("/Users/emma/Desktop/ADFA work/processed_hyperlink_chapters/V04S13C02 - .json")
