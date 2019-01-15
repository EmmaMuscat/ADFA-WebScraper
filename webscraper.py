# -*- coding: utf-8 -*-

"""
This web scraping program will extract the chapter heading, section title and
subtitles for each valid htm page and store it in the given folder with its
corresponding text in the format shown in htm_format.json and output this to a
folder of seperate json files.

NOTE: The program will print out the ignored files to notify the user.
Due to inconsistent formatting and useless pages such as pages containing links,
only images or archived reports these pages are skipped in this program.
"""
import os
from bs4 import BeautifulSoup, NavigableString
from collections import OrderedDict
import pprint as pp
import json

# gets chapter heading
def getChapterHeading(soup):
    try:
        #dealing with headings that contain unencodeable ascii namely, "<?>"
        chap_head = soup.find('h4').get_text()
        chap_head=chap_head.encode('ascii',errors='ignore')
        return chap_head
    except Exception as e:
        return False

#gets the final section heading
def getFinalSectionHeading(soup):
    return soup.find_all("p", {"class": "sectiontitle"})[-1].get_text()

#gets the final body paragraph text
def getFinalBody1(soup):
    return soup.find_all("li", {"class": "body1"})[-1].get_text()

# gets section heading, checks if exists, else returns False
def getSectionHeading(soup):
    try :
        return soup.find("p", {"class": "sectiontitle"}).get_text()
    except Exception as e:
        return False

# extracts section heading from given body_text
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

#scrapes a given htm page given its path
def scrapePage(htm_path):

    #dictionary declarations for data storage
    chapter_dict = OrderedDict()
    section_dict = OrderedDict()
    group_dict = OrderedDict()
    paragraph_dict = OrderedDict()

    doc = htm_path
    with open(doc) as fp:
        soup = BeautifulSoup(fp, 'lxml')

##################################SPECIAL CASES#################################
################################################################################
    """
    Due to inconsistent formatting and useless pages such as pages containing links,
    only images, archived reports or glossaries are skipped in this program.
    """
    #no formatted chapter heading, usually these are pages containing links and no relevant info
    if(getChapterHeading(soup)==False):
        print("An irrelevant page ignored")
        return None

    #not a chapter, is an archived report summary, not relevant for semantic analysis
    if("ARCHIVED SM9 WEEKLY REPORT") in str(getChapterHeading(soup)):
        chapter_heading = getChapterHeading(soup)
        print("This archived report was skipped for semantic analysis accuracy " + chapter_heading)
        return None

    #check if the document is a report/contains no body paragraphs
    if(len(soup.find_all("li", {"class": "body1"})) == 0 ):
        if(getChapterHeading(soup) != False):
            chapter_heading = getChapterHeading(soup)
            print("This report was skipped for semantic analysis accuracy " + chapter_heading)
            return None
        else:
            print("A page only containing links was ignored")
            return None

    #not all pages have a section heading, just chapter and body text, special storage action taken
    if(len(soup.find_all("p", {"class": "sectiontitle"}))==0):
        # Init vars for dict
        chapter_heading = getChapterHeading(soup)
        section_heading = getSectionHeading(soup)
        final_paragraph_text = getFinalBody1(soup)
        group_heading = False
         # EDGE CASE: A GROUP TITLE IN THE FIRST PARAGRAPH WILL NOT BE CAUSE,
         # NEED A METHOD OF INITIALIZING VARIABLE

        section_group_bool = False

        #Counter variables for key creation
        section_counter = 1
        group_counter = 1
        paragraph_counter = 1

        #begin body paragraph iteration
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
            group_heading = next_group_heading

            # dump paragraphs to group if group has ended
            if next_group_heading != False and section_group_bool == True:
                group_key = "Group" + str(group_counter)
                group_dict[group_key].update(paragraph_dict)

                group_counter += 1

                #reset parapgraph vars
                paragraph_counter = 1
                paragraph_dict = OrderedDict()

            #special conditon for final paragraph dumping
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

                #reset parapgraph vars
                paragraph_counter = 1
                paragraph_dict = OrderedDict()

                # reset group vars
                group_counter = 1
                group_dict = OrderedDict()
                section_group_bool = False


            # final body1 reached, append into section dict
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

                #reset parapgraph vars
                paragraph_counter = 1
                paragraph_dict = OrderedDict()

                # reset group vars
                group_counter = 1
                group_dict = OrderedDict()
                section_group_bool = False


        #store the section data in the chapter dict
        chapter_dict[chapter_heading] = section_dict
        chapter_dict = OrderedDict(chapter_dict)
        #chapter_code = chapter_heading.split("-", 1)[0]

        #dump each chapter to given directory in a seperate folder identified by its
        #chapter code
        print(chapter_heading)
        with open('/Users/emma/Desktop/ADFA work/processed_chapters/chapter_' + chapter_heading[:10] + '.json', 'w') as outfile:
            json.dump(chapter_dict, outfile)
        return None

################################################################################
###########################NORMAL PAGE #########################################

    # Init vars for dict
    chapter_heading = getChapterHeading(soup)
    section_heading = getSectionHeading(soup)
    final_section_heading = getFinalSectionHeading(soup)
    final_paragraph_text = getFinalBody1(soup)
    group_heading = False
    section_group_bool = False

    # EDGE CASE: A GROUP TITLE IN THE FIRST PARAGRAPH WILL NOT BE CAUSE,
    # NEED A METHOD OF INITIALIZING VARIABLE


    #Counter variables for key creation
    section_counter = 1
    group_counter = 1
    paragraph_counter = 1



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
        group_heading = next_group_heading

        # dump paragraphs to group it has ended
        if next_group_heading != False and section_group_bool == True:
            group_key = "Group" + str(group_counter)
            group_dict[group_key].update(paragraph_dict)

            #reset variables
            group_counter += 1
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

            #reset parapgraph vars
            paragraph_counter = 1
            paragraph_dict = OrderedDict()

            # reset group vars
            group_counter = 1
            group_dict = OrderedDict()
            section_group_bool = False


    chapter_dict[chapter_heading] = section_dict
    chapter_dict = OrderedDict(chapter_dict)
    #chapter_code = chapter_heading.split("-", 1)[0]


    #dump each chapter to given directory in a seperate folder identified by its
    print(chapter_heading)
    with open('/Users/emma/Desktop/ADFA work/processed_chapters/' + chapter_heading[:10] + '.json', 'w') as outfile:
        json.dump(chapter_dict, outfile)

################################################################################

"""
Simply give the program your directory full of htm files and it will process each
web page and store these by chapter, section and subtitle
and store them in a json file for you. It is set to check for the htm keyword
to avoid weird folders you may have left inside.

Eg.
for htm_page in os.listdir('directory_name'):
    if("htm" in str(htm_page)):
        print(htm_page)
        scrapePage('directory_name/' + htm_page)
"""

scrapePage("ESCMCDVersion/22990.htm")

for htm_page in os.listdir('ESCMCDVersion'):
    if("htm" in str(htm_page)):
        print(htm_page)
        scrapePage('ESCMCDVersion/' + htm_page)
