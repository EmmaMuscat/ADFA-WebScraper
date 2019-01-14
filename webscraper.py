"""
This program will extract the chapter heading, section title and subtitles for each
 htm page in the given folder with its corresponding text in the format shown
in htm_format.json and output this to a json file.
"""
import os
from bs4 import BeautifulSoup, NavigableString
from collections import OrderedDict
import pprint as pp
import json

# gets chapter heading
def getChapterHeading(soup):
    chap_head = soup.find('h4')
    return chap_head.get_text()

def getFinalSectionHeading(soup):
    return soup.find_all("p", {"class": "sectiontitle"})[-1].get_text()

def getFinalBody1(soup):
    return soup.find_all("li", {"class": "body1"})[-1].get_text()

# gets section heading, checks if exists, else returns False
def getSectionHeading(soup):
    try :
        return soup.find("p", {"class": "sectiontitle"}).get_text()
    except Exception as e:
        return False

# extracts section heading from body1
def extractSectionHeading(body_text):
    try :
        element = body_text.find("p", {"class": "sectiontitle"})
        element.extract()
    except Exception as e:
        pass

# gets group heading, check if exists, else returns False
def getGroupHeading(soup):
    try :
        return soup.find("p", {"class" : "grouptitle"}).get_text()
    except Exception as e:
        return False

#scrapes a given page
def scrapePage(htm_path):
    chapter_dict = OrderedDict()
    section_dict = OrderedDict()
    group_dict = OrderedDict()
    paragraph_dict = OrderedDict()

    #doc = "ESCMCDVersion/1154_1.htm"
    doc = htm_path
    with open(doc) as fp:
        soup = BeautifulSoup(fp, 'lxml')

    # Init vars for dict
    chapter_heading = getChapterHeading(soup)
    section_heading = getSectionHeading(soup)
    final_section_heading = getFinalSectionHeading(soup)
    final_paragraph_text = getFinalBody1(soup)
    group_heading = False
     # EDGE CASE: A GROUP TITLE IN THE FIRST PARAGRAPH WILL NOT BE CAUSE, NEED A METHOD OF INITIALIZING VARIABLE

    section_group_bool = False

    #Counter variables for key creation
    section_counter = 1
    group_counter = 1
    paragraph_counter = 1

    #print(soup.find_all("li", {"class": "body1"})[-1]).get_text()


    for paragraph in soup.find_all("li", {"class": "body1"}):
        # check for section heading in paragraph
        next_section_heading = getSectionHeading(paragraph)
        next_group_heading = getGroupHeading(paragraph)


        # if multiple body1 in a section, this condition until final body1 reached
        if next_section_heading == False:

            paragraph_key = "Para" + str(paragraph_counter)
            paragraph_dict[paragraph_key] = paragraph.get_text()

            paragraph_counter += 1

        # new group
        if group_heading != False:

            group_key = "Group" + str(group_counter)
            group_dict[group_key] = {
                "Heading" : group_heading
            }

            section_group_bool = True
            #pp.pprint(group_dict)


        group_heading = next_group_heading

        # dump paragraphs to group
        if next_group_heading != False and section_group_bool == True:
            group_key = "Group" + str(group_counter)
            group_dict[group_key].update(paragraph_dict)

            group_counter += 1

            #reset parapgraph vars
            paragraph_counter = 1
            paragraph_dict = OrderedDict()

        #special conditon for final paragraph
        if paragraph.get_text() == final_paragraph_text:
            # extract section title from end of paragraph
            extractSectionHeading(paragraph)

            # assign text and keys
            paragraph_key = "Para" + str(paragraph_counter)
            paragraph_dict[paragraph_key] = paragraph.get_text()

            section_key = "Section" + str(section_counter)
            section_counter += 1


            section_dict[section_key] = {
                "Heading" : section_heading
            }

            if section_group_bool :
                group_dict[group_key].update(paragraph_dict)
                section_dict[section_key].update(group_dict)
            else :
                section_dict[section_key].update(paragraph_dict)

            #oerwrite sectiontitle with next_sectiontitle
            section_heading = next_section_heading

            #check if this is the last section


            #reset parapgraph vars
            paragraph_counter = 1
            paragraph_dict = OrderedDict()

            # reset group vars
            group_counter = 1
            group_dict = OrderedDict()
            section_group_bool = False


        # final body1 reached, append into section dict)
        if next_section_heading != False:

            # extract section title from end of paragraph
            extractSectionHeading(paragraph)

            # assign text and keys
            paragraph_key = "Para" + str(paragraph_counter)
            paragraph_dict[paragraph_key] = paragraph.get_text()

            section_key = "Section" + str(section_counter)
            section_counter += 1


            section_dict[section_key] = {
                "Heading" : section_heading
            }

            if section_group_bool :
                group_dict[group_key].update(paragraph_dict)
                section_dict[section_key].update(group_dict)
            else :
                section_dict[section_key].update(paragraph_dict)

            #oerwrite sectiontitle with next_sectiontitle
            section_heading = next_section_heading

            #check if this is the last section


            #reset parapgraph vars
            paragraph_counter = 1
            paragraph_dict = OrderedDict()

            # reset group vars
            group_counter = 1
            group_dict = OrderedDict()
            section_group_bool = False


    chapter_dict[chapter_heading] = section_dict
    chapter_dict = OrderedDict(chapter_dict)

    #dump to
    with open('test_file.json', 'a+') as outfile:
        json.dump(chapter_dict, outfile)

################################################################################

"""
Simply give the program your directory full of htm files and it will process each
web page and store these by chapter, section and subtitle
and store them in a json file for you
"""

for htm_page in os.listdir('htm_pages'):
    if("htm" in str(htm_page)):
        print(htm_page)
        scrapePage('htm_pages/' + htm_page)
