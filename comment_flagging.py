#Use python 3.7
#emus6921 2019

#library imports
import nltk
from nltk.corpus import stopwords
from pandas import ExcelWriter
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import pandas as pd
import re
import pymysql.cursors

stopwords.words('english')

#Functions
"""
database details for direct access to the db(python 3.7 supported module used)
"""
def connect_to_database(user_m,password_m,database_m):
    con = pymysql.connect(host='itl-db-pro-2.ucc.usyd.edu.au',user=user_m,password=password_m,db=database_m,charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
    return con

def close_database(con):
    con.close()


"""
provide this function with the absolute path to your excel file you wish to have processed
(file name included) and the column name you wish to have analysed(corect spelling/casing)
"""
def load_excel_sheet(excel_sheet_path,target_column_name):
    #load the sheet into a pandas df
    print("Path you have given to load is: " + excel_sheet_path)

    if(".csv" in excel_sheet_path):
        print("Please convert your csv to an excel format(such as xls or xlsx. Raw CSV files are not supported\n")

    elif(".xls") in excel_sheet_path:
        original_df = pd.read_excel(excel_sheet_path)
        edited_df = pd.read_excel(excel_sheet_path)
    else:
        original_df = pd.read_excel(excel_sheet_path)
        edited_df = pd.read_excel(excel_sheet_path)

    #set the column we wish to search1
    target_column = target_column_name

    print("Excel sheet successfully loaded")
    print("Target column chosen is:" + target_column)

    return edited_df

    
"""
locate concerning terminology in the chosen spreadsheet in the chosen column and add these to new columns
to store a concerning comment flag and the concerning terms found
"""
def find_concerning_terms(edited_df,target_column):

    #initialise stopwords
    stopWords = set(stopwords.words('english'))

    #create new columns to store the concerning terms, one to flag, onw to store the flagged terms   
    edited_df['concerning_flag'] = 'no'
    edited_df['concerning_flagged_terms'] = ' '


    tracker = 0

    #clean each row in the df in the given column
    for row in edited_df[target_column]:
        #all to lowercase
        row = str(row).lower()    
        #remove punctuation
        row = re.sub('[^a-zA-Z]', ' ', row)
        #tokenise,lemmatise and remove stopwords
        lemmatizer = WordNetLemmatizer()
        tokenized_row = word_tokenize(row)
        filtered_sentence = []
        
        for word in tokenized_row: 
            if word not in stopWords: 
                #option to lemmatise
                word = lemmatizer.lemmatize(word)
                filtered_sentence.append(word)
        
        edited_df.loc[tracker,target_column] = str(filtered_sentence)
        tracker+=1

    #check each row of the data for flagged terms
    #set the new flagged column  to 'YES' if found or 'NO' if not
    #if flagged terms are found add them to the 'flagged_terms' list in the corresponding index if not already added

    #These terms can be edited based on the level of seriousness one wishes to search for
    high_alert_terms = ['mental','depression','depressed','bully','bullying','rape','dead','death','rapist','pedophile','pedo','violence','stalking','stalk', 'cunt', 'crime','suicide','illegal','hostile','hostility','pervasive','victimised','racist','obscene','harass','harassment','dangerous','misconduct','intimidation','intimidate','threaten','threat','threatening','sexual','sex','discrimination','discriminate','assault','abuse','porn','pornographic','abusive','abusing']
    medium_alert_terms = ['disability','disabled','anxious','stressed','lonely','isolated','belittling','belittled','attacked']

    for i in range(len(edited_df.index)):
        for j in range(len(high_alert_terms)):
            if str(high_alert_terms[j]) in edited_df.loc[i,target_column]:
                split_column = edited_df.loc[i,target_column].split(' ')
                for l in range(len(split_column)):
                    split_column[l] = split_column[l].strip(',')
                    split_column[l] = split_column[l].strip('\'')          
                    if(str(high_alert_terms[j]) == str(split_column[l])):
                        if str(high_alert_terms[j]) not in edited_df.loc[i,'concerning_flagged_terms']:
                            edited_df.loc[i,'concerning_flag'] = 'yes'
                            edited_df.loc[i,'concerning_flagged_terms'] = edited_df.loc[i,'concerning_flagged_terms'] + high_alert_terms[j] + ',' 


    #TODO 
    #concerning term count and length of comment(overall)
    #alert level(3 levels: low,medium,high)

    return edited_df

   
"""
locate abusive terminology in the chosen spreadsheet in the chosen column and add these to new columns
to store a concerning comment flag and the concerning terms found
"""
def find_abusive_terms(edited_df,target_column):

    #initialise stopwords
    stopWords = set(stopwords.words('english'))

    #create new columns to store the concerning terms, one to flag, onw to store the flagged terms   
    edited_df['abuse_flag'] = 'no'
    edited_df['abusive_flagged_terms'] = ' '

    tracker = 0
    #clean each row in the df in the given column
    for row in edited_df[target_column]:
        #all to lowercase
        row = str(row).lower()     
        #remove punctuation
        row = re.sub('[^a-zA-Z]', ' ', row)
        #tokenise,lemmatise and remove stopwords
        lemmatizer = WordNetLemmatizer()
        tokenized_row = word_tokenize(row)
        filtered_sentence = []

        for word in tokenized_row: 
            if word not in stopWords:       
                #TODO check which one is better!(lemmatised or not) -produces false positives
                word = lemmatizer.lemmatize(word)
                filtered_sentence.append(word)

        edited_df.loc[tracker,target_column] = str(filtered_sentence)
        tracker+=1

    #check each row of the data for flagged terms
    #set the new flagged column  to 'YES' if found or 'NO' if not
    #if flagged terms are found add them to the 'flagged_terms' list in the corresponding index if not already added

    staff_id_terms = ['teacher','lecturer','tutor','staff','administration','admin','coordinator','supervisor','professor']
    abusive_alert_terms = ['stupid','fucks','stupidity','idiotic','fucking','fuck','stupid','useless','idiot','dumb','die','kill','murder','hate','retarded']
    

    for i in range(len(edited_df.index)):
        for j in range(len(abusive_alert_terms)):
            #additionally checks for the mentioning of staff before adding it to abusive(need to also include staff names in the staff_id terms)
            for k in range(len(staff_id_terms)):
                if str(staff_id_terms[k]) in edited_df.loc[i,target_column]:  
                    if str(abusive_alert_terms[j]) in edited_df.loc[i,target_column]:
                        split_column = edited_df.loc[i,target_column].split(' ')
                        for l in range(len(split_column)):
                            split_column[l] = split_column[l].strip(',')
                            split_column[l] = split_column[l].strip('\'')  
                            if(str(abusive_alert_terms[j]) == str(split_column[l])):
                                if str(abusive_alert_terms[j]) not in edited_df.loc[i,'abusive_flagged_terms']:
                                    edited_df.loc[i,'abuse_flag'] = 'yes'
                                    edited_df.loc[i,'abusive_flagged_terms'] = edited_df.loc[i,'abusive_flagged_terms'] + abusive_alert_terms[j] + ',' 

    
    #put the chosen column back to normal?
    return edited_df


#concerning term count and length of comment(overall)
#alert level(3 levels: low,medium,high)

"""
Create an  excel spreadsheet given the chosen output directory for conerning student comments
"""
def create_concerning_output_excel(original_df,edited_df,output_directory,output_file_name):

    #add the new columns to original excel spreadsheet
    original_df['concerning_flag'] = 'no'
    original_df['concerning_flagged_terms'] = ' '

    #copy over the data from edited spreadhseet
    for i in range(len(edited_df.index)):
        if edited_df.loc[i,'concerning_flag'] == 'yes':
            original_df.loc[i,'concerning_flag'] = 'yes'
            terms = edited_df.loc[i,'concerning_flagged_terms']
            original_df.loc[i,'concerning_flagged_terms'] = terms


    #save the output
    writer = ExcelWriter(output_directory +  "/" + output_file_name + ".xlsx")
    original_df.to_excel(writer,'Sheet1')
    writer.save()   

    print("Concerning terms successfully added to a new excel spreadsheet")
    print("Please check your output folder for this result")

    #return the final dataframe for use by other functions
    return original_df
    
"""
Create an  excel spreadsheet given the chosen output directory for abusive nstudent comments towards staff
"""
def create_abusive_output_excel(chosen_df,edited_df,output_directory,output_file_name):

    #add the new columns to original excel spreadsheet
    chosen_df['abuse_flag'] = 'no'
    chosen_df['abusive_flagged_terms'] = ' '

    #copy over the data from edited spreadhseet
    for i in range(len(edited_df.index)):
        if edited_df.loc[i,'abuse_flag'] == 'yes':
            chosen_df.loc[i,'abuse_flag'] = 'yes'
            terms = edited_df.loc[i,'abusive_flagged_terms']
            chosen_df.loc[i,'abusive_flagged_terms'] = terms

    #save the output
    writer = ExcelWriter(output_directory +  "/" + output_file_name + ".xlsx")
    chosen_df.to_excel(writer,'Sheet1')
    writer.save()

    print("Abusive terms successfully added to a chosen excel spreadsheet")
    print("Please check your output folder for this result")
    


"""
Creates an output excel sheet from scratch with concerning student comments flagged using the users chosen excel sheet, column to analyse, output directory and file name
"""
def produce_concerning_terms_excel(excel_sheet_path,column_to_analyse,output_directory,output_file_name):
    #store the original spreadsheet/dataframe
    original_df = pd.read_excel(excel_sheet_path)

    #load in the data and select a column to be searched
    edited_df = load_excel_sheet(excel_sheet_path,column_to_analyse)

    #find concerning terminology
    edited_df = find_concerning_terms(edited_df,column_to_analyse)

    #create output spreadsheet
    student_final_df = create_concerning_output_excel(original_df,edited_df,output_directory,output_file_name)

    #return the final dataframe for use by other functions
    return student_final_df
"""
Creates an output excel sheet from scratch with concerning student comments flagged using the given sql query data, column to analyse, output directory and file name
"""
def produce_concerning_terms_excel_db_access(connection,sql_query,column_to_analyse,output_directory,output_file_name):
    #store the original spreadsheet/dataframe
    original_df = pd.read_sql(sql_query,connection)

    #load in the data and select a column to be searched
    edited_df = original_df

    #find concerning terminology
    edited_df = find_concerning_terms(edited_df,column_to_analyse)

    #create output spreadsheet
    student_final_df = create_concerning_output_excel(original_df,edited_df,output_directory,output_file_name)

    #return the final dataframe for use by other functions
    return student_final_df


"""
Creates an output excel sheet from scratch (as with student concerning comments)
Creates an output excel sheet from scratch with abusive student comments towards staff flagged using the users chosen excel sheet, column to analyse, output directory and file name
"""
def produce_abusive_terms_excel(excel_sheet_path,column_to_analyse,output_directory,output_file_name):
    #store the original spreadsheet
    original_df = pd.read_excel(excel_sheet_path)

    #load in the data and select a column to be searched
    edited_df = load_excel_sheet(excel_sheet_path,column_to_analyse)

    #find abusive terminology
    edited_df = find_abusive_terms(edited_df,column_to_analyse)

    #create output spreadsheet
    create_abusive_output_excel(original_df,edited_df,output_directory,output_file_name)


"""
Creates an output excel sheet from scratch (as with student concerning comments)
Creates an output excel sheet from scratch with abusive student comments towards staff flagged using the users chosen excel sheet, column to analyse, output directory and file name
"""
def produce_abusive_terms_excel_db_access(connection,sql_query,column_to_analyse,output_directory,output_file_name):
    #store the original spreadsheet
    original_df = pd.read_sql(sql_query,connection)

    #load in the data and select a column to be searched
    edited_df = original_df

    #find abusive terminology
    edited_df = find_abusive_terms(edited_df,column_to_analyse)

    #create output spreadsheet
    create_abusive_output_excel(original_df,edited_df,output_directory,output_file_name)

"""
Adds student abusive comments towards staff to the current excel spreadsheet
"""
def add_abusive_terms_to_excel(original_df,student_final_df,output_directory,column_to_analyse,output_file_name):

    #find abusive terminology
    #returns an edited df(search column altered)
    abusive_df = find_abusive_terms(student_final_df,column_to_analyse)

    #set abusive_df target column back to normal

    for l in range(len(abusive_df.index)):
        abusive_df.loc[l,column_to_analyse] = original_df.loc[l,column_to_analyse]

    #save the output
    writer = ExcelWriter(output_directory + "/" + output_file_name + ".xlsx")
    abusive_df.to_excel(writer,'Sheet1')
    writer.save()

    return abusive_df


"""
Given a dataframe that contains the analysis of concerning student comments and/or abusive comments towards staff,
this function will add a column that determins the severity of the chosen columns by checking the amount of
concerning terms and the length of the comment
"""
def add_severity_column(analysed_df,column_to_analyse,output_directory,output_file_name):
    if 'concerning_flagged_terms' in analysed_df.columns:
        #add the relevantr severity column/alert level
        analysed_df['concerning_alert_level'] = 0

        for m in range(len(analysed_df.index)):
            row_terms = analysed_df.loc[m,'concerning_flagged_terms']
            split_terms = row_terms.split(',')

            #count the concerning terms
            term_count = len(split_terms)

            #count the length of the comment
            comment_string = str(analysed_df.loc[m,column_to_analyse])
            comment_length = len(comment_string)

            #calculate the severity
            severity = (term_count * 300) + comment_length/2

            #set the alert level
            if analysed_df.loc[m,'concerning_flag'] == 'no':
                analysed_df.loc[m,'concerning_alert_level'] = 'n/a'
            elif(severity < 1000):
                analysed_df.loc[m,'concerning_alert_level'] = 'low'
            elif(severity > 1500):
                analysed_df.loc[m,'concerning_alert_level'] = 'high'
            else:
                analysed_df.loc[m,'concerning_alert_level'] = 'medium'

    if 'abusive_flagged_terms' in analysed_df.columns:
        #add the relevantr severity column/alert level
        analysed_df['abuse_alert_level'] = 0

        for m in range(len(analysed_df.index)):
            row_terms = analysed_df.loc[m,'abusive_flagged_terms']
            split_terms = row_terms.split(',')

            #count the concerning terms
            term_count = len(split_terms)

            #count the length of the comment
            comment_string = str(analysed_df.loc[m,column_to_analyse])
            comment_length = len(comment_string)

            #calculate the severity
            severity = (term_count * 300) + comment_length/2

            #set the alert level
            if analysed_df.loc[m,'abuse_flag'] == 'no':
                analysed_df.loc[m,'abuse_alert_level'] = 'n/a'
            elif(severity < 1000):
                analysed_df.loc[m,'abuse_alert_level'] = 'low'
            elif(severity > 1500):
                analysed_df.loc[m,'abuse_alert_level'] = 'high'
            else:
                analysed_df.loc[m,'abuse_alert_level'] = 'medium' 

    #save the output
    writer = ExcelWriter(output_directory +  "/" + output_file_name + ".xlsx")
    analysed_df.to_excel(writer,'Sheet1')
    writer.save()

    print("Alert flags successfuly added to the given dataframe,see your chosen output file for the results")

"""
located mentioning of both past and current staff in the chosen spreadhseet in the chosen column
and add these to the new columns

DISCLAIMER: There are obviously a LOT of staff and so if there are similarly a lot of comments this is a VERY slow function.
"""
def find_staff_mentions(edited_df,target_column,staff_df):
    print("Finding staff mentions, may take a while there is a lot of data! Please wait")

    #initialise stopwords
    stopWords = set(stopwords.words('english'))

    edited_df['staff_mentioned_flag'] = 'no'
    edited_df['staff_names_mentioned'] = ' '

    tracker = 0

    #clean each row in the df in the given column
    for row in edited_df[target_column]:

        row = str(row).lower()     

        row = re.sub('[^a-zA-Z]', ' ', row)

        lemmatizer = WordNetLemmatizer()
        tokenized_row = word_tokenize(row)
        filtered_sentence = []

        for word in tokenized_row: 
            if word not in stopWords:       
                word = lemmatizer.lemmatize(word)
                filtered_sentence.append(word)

        edited_df.loc[tracker,target_column] = str(filtered_sentence)
        tracker+=1

        #check each row of the data for flagged terms
        #set the new flagged column  to 'YES' if found or 'NO' if not
        #if flagged terms are found add them to the 'flagged_terms' list in the corresponding index if not already added

    #option to check thoroughly but it is VERY slow and intensive. Both however are slow they have to check 60,000 names  
    thorough_check = False

    if(thorough_check == False):
        for i in range(len(staff_df.index)):
            print("Checking row " + str(i))
            for j in range(len(edited_df.index)):
                if(str(staff_df.loc[i,'firstname']) in edited_df.loc[j,target_column] and str(staff_df.loc[i,'firstname']) not in edited_df.loc[j,'staff_names_mentioned']):
                    edited_df.loc[j,'staff_mentioned_flag'] = 'yes'
                    edited_df.loc[j,'staff_names_mentioned'] = edited_df.loc[j,'staff_names_mentioned'] + str(staff_df.loc[i,'firstname']) + ','

                if(str(staff_df.loc[i,'surname']) in edited_df.loc[j,target_column] and str(staff_df.loc[i,'surname']) not in edited_df.loc[j,'staff_names_mentioned']):
                    edited_df.loc[j,'staff_mentioned_flag'] = 'yes'
                    edited_df.loc[j,'staff_names_mentioned'] = edited_df.loc[j,'staff_names_mentioned'] + str(staff_df.loc[i,'surname']) + ','

    else:
        #option to check thoroughly but it is VERY slow and intensive...
        for i in range(len(edited_df.index)):
            for j in range(len(staff_df.index)):       
                    split_column = edited_df.loc[i,target_column].split(' ')
                    for l in range(len(split_column)):
                        split_column[l] = split_column[l].strip(',')
                        split_column[l] = split_column[l].strip('\'')

                        if(str(staff_df.loc[j,'firstname']) == str(split_column[l]) or str(staff_df.loc[j,'surname'])== str(split_column[l])):
                            if(str(staff_df.loc[j,'firstname']) not in edited_df.loc[i,'staff_names_mentioned']):
                                edited_df.loc[i,'staff_mentioned_flag'] = 'yes'
                                edited_df.loc[i,'staff_names_mentioned'] = edited_df.loc[i,'staff_names_mentioned'] + staff_df.loc[j,'firstname'] + ','

                            if(str(staff_df.loc[j,'surname']) not in edited_df.loc[i,'staff_names_mentioned']):
                                edited_df.loc[i,'staff_mentioned_flag'] = 'yes'
                                edited_df.loc[i,'staff_names_mentioned'] = edited_df.loc[i,'staff_names_mentioned'] + staff_df.loc[j,'surname'] + ','

    return edited_df
                

"""
Adds comments that mention names of staff to the current excel spreadsheet
DISCLAIMER: this is a very slow function and will take a while to run if chosen to 
"""
def add_staff_mentioned_column(analysed_df,column_to_analyse,output_directory,output_file_name,staff_excel_path): 
    analysed_df['staff_mentioned_flag'] = 'no'
    analysed_df['staff_names_mentioned'] = ' '

    #load in the staff_info
    
    staff_df = pd.read_excel(staff_excel_path)

    #check for mentions of first names and surnames
    #returns an edited df(search column altered)
    staff_edited_df = find_staff_mentions(analysed_df,column_to_analyse,staff_df)

    for l in range(len(staff_edited_df.index)):
        staff_edited_df.loc[l,column_to_analyse] = original_df.loc[l,column_to_analyse]

    #save the output
    writer = ExcelWriter(output_directory + "/" + output_file_name + ".xlsx")
    staff_edited_df.to_excel(writer,'Sheet1')
    writer.save()

    print("Mentioned Staff successfully flagged and added to excel spreadsheet!")

    return staff_edited_df

"""
Adds comments that mention names of staff to the current excel spreadsheet
For Db connections and so uses the current database of staff info (past and present staff)
DISCLAIMER: this is a very slow function and will take a while to run if chosen to 
"""
def add_staff_mentioned_column_db_access(analysed_df,column_to_analyse,output_directory,output_file_name,connection2): 
    analysed_df['staff_mentioned_flag'] = 'no'
    analysed_df['staff_names_mentioned'] = ' '

    #load in the staff_info
    
    staff_df = pd.read_sql("select * from staff",connection2)

    #check for mentions of first names and surnames
    #returns an edited df(search column altered)
    staff_edited_df = find_staff_mentions(analysed_df,column_to_analyse,staff_df)

    for l in range(len(staff_edited_df.index)):
        staff_edited_df.loc[l,column_to_analyse] = original_df.loc[l,column_to_analyse]

    #save the output
    writer = ExcelWriter(output_directory + "/" + output_file_name + ".xlsx")
    staff_edited_df.to_excel(writer,'Sheet1')
    writer.save()

    print("Mentioned Staff successfully flagged and added to excel spreadsheet!")

    return staff_edited_df            

"""
This function will remove swear/inappropriate language and staff names for anonymisation purposes
and output them to a new specified excel sheet
"""
def clean_my_result(processed_df,file_name,column_to_analyse):
    terms_to_remove = ['stupid','fucks','fuck','fucking','stupidity','fucking','fuck','stupid','idiot','retarded','cunt','dick']
    cleaned_df = processed_df
    terms_removed = []

    for l in range(len(processed_df.index)):
        if(processed_df.loc[l,'concerning_flag'] == 'yes' or processed_df.loc[l,'abuse_flag'] == 'yes'):
            for term in terms_to_remove:
                if (term in processed_df.loc[l,'concerning_flagged_terms'] or term in processed_df.loc[l,'abusive_flagged_terms']):
                    cleaned_df.loc[l,column_to_analyse] = processed_df.loc[l,column_to_analyse].replace(term,'<censored>')
                    terms_removed.append(term)

        if('staff_names_mentioned' in processed_df.columns):
            if(processed_df.loc[l,'staff_names_mentioned_flag'] == 'yes'):
                staff_names_mentioned = processed_df.loc[l,'staff_names_mentioned']
                for staff_name in staff_names_mentioned:
                    cleaned_df.loc[l,column_to_analyse] = processed_df.loc[l,column_to_analyse].replace(staff_name,'<name>')
                    terms_removed.append(term)

    print(terms_removed)
    writer = ExcelWriter(output_directory + "/" + file_name + ".xlsx")
    cleaned_df.to_excel(writer,'Sheet1')
    writer.save()

    print("Your results have also been cleaned and are stored under the chosen name " + file_name + ".xlsx" )

"""
This is the only place a user needs to modify variables, please start from the ##USER INPUT NEEDED HERE# line,
reading  the instructions carefully, and stop at the ####### line and then run the program after installing the
necessary requirements. "python3 comment_flagging.py"
"""

#main function
if __name__ == '__main__':

    #######################################USER INPUT NEEDED HERE#######################################################
    ################################BEWARE OF STORAGE OF CONFIDENTAIL DATA############################################

    #TODO I want to convert these options to command line arguments!

    ##------------ ------------ Program Options ------------  ------------ ## 
    #set your chosen option to true(only one can work at a time and each requires different input)
    use_excel_sheet = True
    use_database = False

    #do you want to check for staff mentions? (note it is very slow only do so if necessary)
    #DISCLAIMER: you do not have to do this step it is very slow as there is 56,000 staff to check against
    check_for_staff_mentions = False

    #would you like a clean version of your query/excel sheet. What would you like it to be named.
    clean = True
    clean_result_file_name = "CleanedTest"


    ##------------ ------------ LOCALLY STORED DATA------------  ------------ ## 

    #If you have set use_excel_sheet = True, fill in these details
    if(use_excel_sheet):
        #Choose the excel sheet, its column you would like analysed and where you would like the ouput spreadsheet stored
        excel_sheet_path = '/Users/emma/Desktop/USYD_Projects/sreq2018.xlsx'
        column_to_analyse = 'o2'
        output_directory = '/Users/emma/Desktop/USYD_Projects/Output'
        output_file_name = 'output_test_2'
        original_df = load_excel_sheet(excel_sheet_path,column_to_analyse)

        #a way of accessing locally stored staff_details(no db connection required)
        staff_excel_path = '/Users/emma/Desktop/USYD_Projects/staff_details.xls'

    ##------------  ------------ LIVE DATABASE CONNECTION------------  ------------ ##

    #If you have set use_database = True, fill in these details
    else:
        #provide the connection with your username,password and the database you wish to connect too(the one you wish to analyse)
        username = 'emma'
        password='v9q273h2pba9'
        database='ses'

        #provide your SQL query which will be the data from the chosen database you wish to analyse
        #eg. "select * from sfs.uss_results where year = 2018"

        sql_query = "SELECT * FROM `comments` LIMIT 10000"

        #provide the name of the comments column you wish to have analysed, the path for your output excel sheet and the name of the sheet
        column_to_analyse = 'niraw'
        output_directory = '/Users/emma/Desktop/USYD_Projects/Output'
        output_file_name = 'databse_ses_nibraw_test.xlsx'


    #####################################################################################################################

    #for locally stored data(no db connection required)
    if use_excel_sheet:

        #create the concerning student comments output excel
        student_final_df = produce_concerning_terms_excel(excel_sheet_path,column_to_analyse,output_directory,output_file_name)

        #create the abusive student comments towards staff output excel(this will create a seperate excel sheet as we are using the function seperately)
        produce_abusive_terms_excel(excel_sheet_path,column_to_analyse,output_directory,output_file_name)

        #this will add the abusive results onto the same spreadsheet as the concerning results
        combined_df = add_abusive_terms_to_excel(original_df,student_final_df,output_directory,column_to_analyse,output_file_name)

        if(check_for_staff_mentions):
            #this will add the staff who are mentioned onto the same spreadsheet in extra special columns
            final_df = add_staff_mentioned_column(combined_df,column_to_analyse,output_directory,output_file_name,staff_excel_path)

            #this will add an alert level column to the given dataframe
            add_severity_column(final_df,column_to_analyse,output_directory,output_file_name)

            if(clean):
                clean_my_result(final_df,clean_result_file_name,column_to_analyse)

        else:
             #this will add an alert level column to the given dataframe
            add_severity_column(combined_df,column_to_analyse,output_directory,output_file_name)

            if(clean):
                clean_my_result(combined_df,clean_result_file_name,column_to_analyse)

        

        
    #for a live database connection, correct database details with relevant access privileges required
    else:
        print("Connecting to Database. Please wait")
        #create the connection
        connection = connect_to_database(username,password,database)

        db_df = pd.read_sql(sql_query, connection) 
        
        print("Your query is " + sql_query)

        #perform the necessary/chosen computations
        #create the concerning student comments output excel
        student_final_df =  produce_concerning_terms_excel_db_access(connection,sql_query,column_to_analyse,output_directory,output_file_name)

        #create the abusive student comments towards staff output excel(this will create a seperate excel sheet as we are using the function seperately)
        produce_abusive_terms_excel_db_access(connection,sql_query,column_to_analyse,output_directory,output_file_name)

        #this will add the abusive results onto the same spreadsheet as the concerning results
        combined_df = add_abusive_terms_to_excel(db_df,student_final_df,output_directory,column_to_analyse,output_file_name)

        if(check_for_staff_mentions):
            #this will add the staff who are mentioned onto the same spreadsheet in extra special columns
            #DISCLAIMER: you do not have to do this step it is very slow there is 56,000 staff to check.

            #open a connection to the specified database
            connection2 = connect_to_database(username,password,'enrolments')

            db_df = pd.read_sql(sql_query, connection)

            final_df = add_staff_mentioned_column_db_access(combined_df,column_to_analyse,output_directory,output_file_name,connection2)

            #this will add an alert level column to the given dataframe
            add_severity_column(final_df,column_to_analyse,output_directory,output_file_name)

            #if the user wishes to have a new clean excel sheet
            if(clean):
                clean_my_result(final_df,clean_result_file_name,column_to_analyse)

        else:
             #this will add an alert level column to the given dataframe
            add_severity_column(combined_df,column_to_analyse,output_directory,output_file_name)

            #if the user wishes to have a new clean excel sheet
            if(clean):
                clean_my_result(combined_df,clean_result_file_name,column_to_analyse)


        #close the connection
        close_database(connection)



#TODO make command line inputs

#TODO: refactor some of the repeated code perhaps. also do the pure db functions and perhaps add options for which additional info a user wants
#TODO Error Checking/Failsafing
#TODO more comprehensive list of concerning terms(are false positives better than false negatives)
