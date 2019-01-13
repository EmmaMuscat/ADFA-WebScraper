from bs4 import BeautifulSoup, NavigableString
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
def splitSectionHeading(body_text) :
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

    chapter_dict = {}
    section_dict = {}
    group_dict = {}
    paragraph_dict = {}

    #html_doc = "V04S05C04 - AUSTRALIAN STANDARD MATERIEL ISSUE AND MOVEMENT PRIORITY SYSTEM.htm"
    #test_doc = 'sample_2.html'
    doc = "ESCMCDVersion/204_1.htm"
    with open(doc) as fp:
        soup = BeautifulSoup(fp, 'lxml')

    # Init vars for dict
    chapter_heading = getChapterHeading(soup)
    section_heading = getSectionHeading(soup)

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


        # final body1 reached, append into section dict
        else :

            paragraph_key = "Para" + str(paragraph_counter)
            paragraph_dict[paragraph_key] = paragraph.get_text()

            section_key = "Section" + str(section_counter)
            section_counter += 1
            print(section_key)

            # split on section title, and assign section title for next iteration
            splitSectionHeading(paragraph)

            section_dict[section_key] = {
                "Heading" : section_heading,
            }
            section_dict[section_key].update(paragraph_dict)

            #oerwrite sectiontitle with next_sectiontitle
            section_heading = next_section_heading
            group_heading = next_group_heading

            #reset parapgraph vars
            paragraph_counter = 1
            paragraph_dict = {}

    chapter_dict[chapter_heading] = section_dict
    #pp.pprint(chapter_dict)

    import json
    with open('data.json', 'w') as outfile:
        json.dump(chapter_dict, outfile)
