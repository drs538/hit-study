#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 28 10:14:34 2018

@author: danielleshala
"""

 # -*- coding: utf-8 -*-
 # NoteRedundancy -- Calculate a similarity score for nursing progress notes
 # using the Damerau Levenshtein Distance algorithm
 # Load libraries
import pyodbc
import pandas
 
'''
pyodbc --> Python library/module to access database/perform SQL Query

pandas --> Data analysis library for python
 
Would pandas be in the same category as numpy?
 
Highlights in https://pandas.pydata.org say use of DataFrames, I haven't come across it in Python (yet)
I'm assuming it's suitable for larger datasets,but I wonder what the difference between a data frame and array
is in terms of operations/functions?
 
"Intelligent data alignment", "Time-series function"
are these also reasons for choosing pandas? 
Would be interested to see how these apply to our data
'''
 
 
# Create a connection to the SQL server database
con = pyodbc.connect('DRIVER={ODBCd Driver 13 for SQL Server};'
                     'SERVER=CCIS-REPORT01;DATABASE=Notes;'
                     'Uid=NotesUser;Pwd=notes')
 
 
# Set the connection to autocommit
con.autocommit = True

curPatient = con.cursor()
 

# truncate the match table
curMatch = con.cursor()
curMatch.execute("truncate table match")
con.commit()

# Fetch the records for PICU admissions
qryPatient = ("select * from visit_unit where unit='PICU' "
              "and DatePart(yy, admit_time)=2017")
curPatient.execute(qryPatient)


# Iterate over the patient table and score those records
for row in curPatient.fetchall():
    patientID = row.emtek_id
    score = score_notes(patientID)
print('Finished......')


'''
looked up meaning of Truncating in SQL but don't quite understand why it (emptying) needs to be done? 
"Truncate is the database equivalent of zero-ing out a file. After TRUNCATE’ing a table, it will have no records in it.
The table’s columns, indexes, constraints, views, etc are all still there - it’s just “empty”." ()

please explain this part:
    curPatient = con.cursor() 
    curPatient.execute(qryPatient)
 '''
 
 



########################################################################

# Score the notes for each patient
def score_notes(emtekID):
    qryNote = ("select * from c_note where emtek_id = '"
                  + str(emtekID) + "' and note_obj = 'C_NONURSPRO'"
    noteData = pandas.read_sql(qryNote, con)
  
'''
is "scoring" the same as indexing nursing notes for each admission?
c_note and note_obj --> labels/variables within the database?
'C_NONURSPRO --> nursing progress notes?
if we are to specify the length of each note to be reviewed (ex. x lines/characters long), is this where that needs to be specified?

'''
  
# Process each note
for index, row in noteData.iterrows():
    # Check that we are at least at the second record
    if (index > 0):
        proportion = match_proportion(noteData.loc[index-1, :].note_text, 
                                      noteData.loc[index, :].note_text) 
        timestamp = noteData.loc[index-1, :].time_for
 
'''
why the need to specify both "index, row" for the for loop?
doesn't iterrows() presume operating on rows? (haven't used iterrows before)
 
noteData.loc[index-1, :] and [index, :]... 
     what is the ",:" for? 
     these are s1 and s2 respectively?
 
what does the timestamp variable do?
 '''
 
 
     # Insert the results back into the database server for future analysis
     qryMatch = "insert into match(emtek_id, time_for, score) values (?,?,?)"
     curMatch.execute(qryMatch, emtekID, timestamp, proportion)
     con.commit()
     
return

# Calculate the matching proportion using the damerau levenshtein distance
def match_proportion(s1, s2):
    distance = damerau_levenshtein_distance(s1, s2)
    proportion = 1 - distance / max (len(s1), len(s2))
    return proportion


# Calculate the Damerau Levenshtein Distance for two strings

def damerau_levenshtein_distance(s1, s2):
    d = {} 
    lenstr1 = len(s1)
    lenstr2 = len(s2)
    
    for i in range(-1,lenstr1+1):
        d[(i,-1)] = i+1 
        
    for j in range(-1,lenstr2+1):
        d[(-1,j)] = j+1

    for i in range(lenstr1):
        for j in range(lenstr2):
            if s1[i] == s2[j]:
                cost = 0
            else
                cost = 1
                
            d[(i,j)] = min(
                            d[(i-1,j)] + 1, # deletion
                            d[(i,j-1)] +1, # insertion
                            d[(i-1,j-1)] + cost, # substitution
                            )
                
            if i and j and s1[i]==s2[j-1] and s1[i-1] == s2[j]:
                d[(i,j)] = min (d[(i,j)], d[i-2,j-2] + cost) # transposition
    
    return d[lenstr1-1,lenstr2-1]
    
'''
 d = {} --> initialising an empty list?
 
 lenstr1 = len(s1)
 lenstr2 = len(s2)
     if s1 and s2 are the notes, this will count the number of characters in each note? 
     does it count by character or by word?
'''