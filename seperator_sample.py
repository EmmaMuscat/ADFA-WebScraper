from bs4 import BeautifulSoup, NavigableString
from collections import OrderedDict
import pprint as pp

# gets chapter heading
def getChapterHeading(soup) :
    chap_head = soup.find('h4')
    return chap_head.get_text()

# gets section heading, checks if exists, else returns False
def getSectionHeading(soup) :
    try :
        return soup.find("p", {"class": "sectiontitle"}).get_text()
    except Exception as e:
        return False

# extracts section heading from body1
def extractSectionHeading(body_text) :
    try :
        element = body_text.find("p", {"class": "sectiontitle"})
        element.extract()
    except Exception as e:
        pass

# gets group heading, check if exists, else returns False
def getGroupHeading(soup) :
    try :
        return soup.find("p", {"class" : "grouptitle"}).get_text()
    except Exception as e:
        return False

#######################################################################
if __name__ == "__main__" :

    chapter_dict = OrderedDict()
    section_dict = OrderedDict()
    group_dict = OrderedDict()
    paragraph_dict = OrderedDict()

    #html_doc = "V04S05C04 - AUSTRALIAN STANDARD MATERIEL ISSUE AND MOVEMENT PRIORITY SYSTEM.htm"
    test_doc = 'sample.htm'
    doc = "ESCMCDVersion/204_1.htm"
    with open(doc) as fp:
        soup = BeautifulSoup(fp, 'lxml')

    # Init vars for dict
    chapter_heading = getChapterHeading(soup)
    section_heading = getSectionHeading(soup)
    group_heading = False # EDGE CASE: A GROUP TITLE IN THE FIRST PARAGRAPH WILL NOT BE CAUSE, NEED A METHOD OF INITIALIZING VARIABLE

    section_group_bool = False

    # Spooiky Iterations
    section_counter = 1
    group_counter = 1
    paragraph_counter = 1

    for paragraph in soup.find_all("li", {"class": "body1"}) :

        # check for section heading in paragraph
        next_section_heading = getSectionHeading(paragraph)
        next_group_heading = getGroupHeading(paragraph)


        # if multiple body1 in a section, this condition until final body1 reached
        if next_section_heading == False :

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

        # final body1 reached, append into section dict
        if next_section_heading != False :

            # extract section title from end of paragraph
            extractSectionHeading(paragraph)

            # assign text and keys
            paragraph_key = "Para" + str(paragraph_counter)
            paragraph_dict[paragraph_key] = paragraph.get_text()

            section_key = "Section" + str(section_counter)
            section_counter += 1
            print(section_key)

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
    #pp.pprint(chapter_dict)
    chapter_dict = dict(chapter_dict)
    import json
    with open('data.json', 'w') as outfile:
        json.dump(chapter_dict, outfile)
