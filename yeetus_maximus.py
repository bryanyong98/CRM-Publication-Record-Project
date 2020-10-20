import pandas as pd
import time
import tkinter
from tkinter import *
from tkinter import filedialog
from tkinter import Label
import os


#####################################
#       Variable Declaration        #
#####################################

# Global variables
file_path = None
file_path_str = None # Used in window label
dir_path = ""
df = None


#####################################
#       Function Definitions        #
##################################### 

# Function to select file path from file explorer
def select_file_path():        
    root = tkinter.Tk()
    root.withdraw() 
    # Select file to read
    file_types = [
        ('CSV files', '*.csv'),
        ('Excel files', '*.xlsx'),
        ('Text files', '*.txt'), 
        ('All files', '*'), 
    ]
    file_path = filedialog.askopenfile(filetypes=file_types)

    # reading csv file as input
    df = pd.read_csv(file_path.name)
    return df, file_path

def select_file():
    global df
    global file_path
    global file_path_str
    df, file_path = select_file_path()
    file_path_str.set(str(file_path.name))

def select_dest_dir():
    global dir_path
    root = tkinter.Tk()
    root.withdraw()
    # Select directory to export to
    dir_path = filedialog.askdirectory()

    return dir_path

def select_dir():
    global df
    global dir_path
    global dest_path_str
    dir_path = select_dest_dir()
    if len(dir_path) > 0:
        dest_path_str.set(dir_path)

def path_selection_window():
    # Specifying global variables to manipulate
    global file_path_str
    global dest_path_str
    global dir_path
    
    window = tkinter.Tk()
    file_path_str = StringVar() # Manipulating global variable
    dest_path_str = StringVar()  # Manipulating global variable (destination directory)
    # Label for selected files
    path_label = Label(window, textvariable=file_path_str)
    dest_label = Label(window, textvariable=dest_path_str)
    file_path_str.set("None")
    dest_path_str.set(os.getcwd())
    # Button to select file path
    file_button = tkinter.Button(window, text="Choose File", command=select_file)
    # Button to select file destination
    folder_destination_button = tkinter.Button(window, text="Select Destination Folder", command=select_dir)
    # Button to process the file
    merge_file_button = tkinter.Button(window, text="Process file", command=processFile)
    # Show window elements in window
    file_button.pack()
    path_label.pack()
    folder_destination_button.pack()
    dest_label.pack()
    merge_file_button.pack()
    
    window.mainloop()


def findAffiliation():
    # List of all the relevant university references to compare
    academicRef = ["University", "College", "Universiti", "Academy", "School", "Campus", "Kolej", "Institute", "institut"]

    # Getting the list of affiliations from data
    affi = df["Authors with affiliations"].values

    affiList = []
    # seperating all data into individual rows in an array
    for item in affi:
        item = str(item)
        affiList.append(item.split("; "))

    # Initializing global variable for checking if affiliation is an industry
    global industryBool

    if "IND.(Y/N)" in df.columns:
        df.drop("IND.(Y/N)")
        df.drop("INT.(Y/N)")
        df.drop("NAT.(Y/N)")

    # Initialise all row columns to N at beginning
    df.insert(df.columns.get_loc("Affiliations"), "IND.(Y/N)", "N")
    df.insert(df.columns.get_loc("Affiliations"), "INT.(Y/N)", "N")
    df.insert(df.columns.get_loc("Affiliations"), "NAT.(Y/N)", "N")

    # Looping through all the rows of affiliation column of the data given
    for i in range(len(affiList)):
        # Setting the checks before looping through each
        nationalBool = False
        internationalBool = False
        industryBool = False
        doubleCheck = False
        monashAuthors = []

        duplicateRow = affiList[i][:]
        # Looping through each row and all their affiliations
        for j in range(len(affiList[i])):

            # remove commas so that matching strings will be accurate (just in case) eachAffi is an array of one
            # company/uni i.e [Institute, for, Integrated, and, Intelligent, Systems, Griffith, University, Nathan,
            # Brisbane, QLD, '' ,4111, Australia]

            # Represents each line of affiliation
            if "," in affiList[i][j]:
                # affiList[i][j].split
                Nameindex = [i for i, n in enumerate(affiList[i][j]) if n == ','][1]
                AuthorName = affiList[i][j][0:Nameindex].replace(",", "")

                eachAffi = affiList[i][j][Nameindex+1:].replace(",", "")
            else:
                AuthorName = ""
                eachAffi = affiList[i][j]

            if "Malaysia" in eachAffi and "Monash" in eachAffi:
                monashAuthors.append(AuthorName)
                duplicateRow[j] = None

        for k in range(len(duplicateRow)):
            if duplicateRow[k] is not None:
                if "," in duplicateRow[k]:
                    # affiList[i][j].split
                    Nameindex = [i for i, n in enumerate(duplicateRow[k]) if n == ','][1]
                    AuthorName = duplicateRow[k][0:Nameindex].replace(",", "")

                    eachAffi = duplicateRow[k][Nameindex+1:].replace(",", "")
                else:
                    AuthorName = ""
                    eachAffi = duplicateRow[k]

            validAffi = []
            if AuthorName not in monashAuthors:
                validAffi.append(eachAffi)

        for n in range(len(validAffi)):
            # filter based on whether they are universities or not, then those that are
            # not will automatically be group under industry.
            if not any(keyWord in validAffi[n] for keyWord in academicRef):
                industryBool = True
            else:
                if "Malaysia" in validAffi[n]:
                    nationalBool = True
                else:
                    internationalBool = True

        # if it is an industry, change the cell to Y and make sure that it will not repeat again
        # print(monashAuthors)
        if industryBool is True and AuthorName not in monashAuthors:
            # Set the particular row column to YES since it is part of the industry.
            df.loc[i, 'IND.(Y/N)'] = "Y"
            # doubleCheck = True

        # if it is national, then change the cell to Y
        if nationalBool and AuthorName not in monashAuthors:
            df.loc[i, 'NAT.(Y/N)'] = "Y"

        # if it is international, then change the cell to Y
        if internationalBool and AuthorName not in monashAuthors:
            df.loc[i, 'INT.(Y/N)'] = "Y"


def findMonashAuthors():
    max_monash_authors = 0    # Maximum number of Monash Author column
    entry_index = 0    # Current index of publication entry
    authors_w_affiliations = df['Authors with affiliations'].values # All values in 'Authors w Affiliations' column
    
    # Drop already-typed Monash Author and respective School columns
    dropRows = []
    for columns in df.columns:
        if 'Monash Author' in columns or 'School' in columns:
            dropRows.append(columns)
    df.drop(dropRows, axis=1, inplace=True)

    # Insert "School" column
    school_col_index = df.columns.get_loc("DOI") + 1
    df.insert(school_col_index, "School", "")
    
    publication_index = 0
    # For all authors of each publication
    for authors in authors_w_affiliations:
        monash_authors = {}
        school_list = []
        school_list_str = ""
        authors_list = str(authors).split(';')
        # For each individual author of the publication
        for author in authors_list:
            # Search for Monash-affiliated authors by keyword 'Monash'
            if 'Monash' in author and 'Malaysia' in author:
                name_end_index = [i for i, n in enumerate(author) if n==","][1]
                author_name = author[:name_end_index].lstrip().rstrip()
                school_string_index = author.find('School of')
                dept_string_index = author.find('Department')
                # If affiliation is 'School of ..'
                if (school_string_index != -1):
                    school_string_start = author[school_string_index:]
                    school_string_end_index = school_string_start.index(',') + school_string_index
                    school = author[school_string_index:school_string_end_index].rstrip()
                    school_stripped = school.split('School of ')[1].lstrip().rstrip()
                    if 'Engineering' in school_stripped:
                        school_stripped = 'Engineering' # For certain special affilations, i.e. School of Engineering and Advanced Engineering Platform
                    monash_authors[author_name] = school_stripped
                    if school_stripped not in school_list:
                        school_list.append(school_stripped)
                # If affiliation is 'Department of ..' or '.. Department'
                elif (dept_string_index != -1):
                    if author[dept_string_index + 10] == ',':
                        author_split = author.split(",")
                        for data in author_split:
                            if 'Department' in data:
                                dept = data.rstrip().lstrip()
                                dept_stripped = dept.split('Department')[0].lstrip().rstrip()
                                if 'Engineering' in dept_stripped:
                                    dept_stripped = 'Engineering'
                    else:
                        dept_string_start = author[dept_string_index:]
                        dept_string_end_index = dept_string_start.index(',') + dept_string_index
                        dept = author[dept_string_index:dept_string_end_index].rstrip()
                        dept_stripped = dept.split('Department of')[1].lstrip().rstrip()
                        if 'Engineering' in dept_stripped:
                            dept_stripped = 'Engineering'
                    monash_authors[author_name] = dept_stripped
                    if dept_stripped not in school_list:
                        school_list.append(dept_stripped)
                else:
                    monash_authors[author_name] = "INDETERMINATE"

        # Insert all schools into School column
        for i in range(len(school_list)):
            if i == 0:
                school_list_str = school_list[i]
            else:
                school_list_str += " / " + school_list[i]
        df["School"][publication_index] = school_list_str
                    
        publication_index += 1
            
        # For all Monash-affiliated authors of the publication, insert into dataframe
        # Insert new columns for Monash Author and School if needed
        for i in range(max_monash_authors, len(monash_authors)):
            df.insert((i+1)*2-1, "Monash Author{}".format(" " + str(i+1)), "")
            df.insert((i+1)*2, "School {}".format(str(i+1)), "")
        # Update current max monash authors to new max if exceeded
        if len(monash_authors) > max_monash_authors:
            max_monash_authors = len(monash_authors)
        # Populate the Monash Author and School columns
        for authors in monash_authors:
            keyIndex = list(monash_authors.keys()).index(authors) + 1
            df["Monash Author {}".format(keyIndex)][entry_index] = authors
            df["School {}".format(keyIndex)][entry_index] = monash_authors[authors]
            
        entry_index += 1
        
    print("Done")


def processFile():

    global df
    global dir_path
    start = time.time()
    findAffiliation()
    findMonashAuthors()
    if dir_path == "":
        df.to_csv("exported.csv", index=False)
    else:
        df.to_csv(dir_path+"/exported.csv", index=False)
    end = time.time()
    print(str(end-start) +' seconds')

    

#############################
#       Implementation      #
#############################

path_selection_window()




#############################
#       Dev Notes           #
#############################

# findAffiliation()

# df.to_csv(r'C:\post-exam-project\hello.csv', index = None, header=True)

########### SID's laptop config ###############################################
df.to_csv(r'S:\chongpro\post-exam-project\hello.csv', index = None, header=True)
###############################################################################
