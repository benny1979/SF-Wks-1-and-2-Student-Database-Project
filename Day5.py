
import dataset
import sys
import json
import logging
import csv


logging.basicConfig(filename='logfile.log',level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info('****NEW SESSION****.')

db = dataset.connect('sqlite:///mydatabase.db')
logging.info('Connecting to database.')
table = db['students']
table.delete()
logging.info('Clearing database.')


def get_user_function():
    '''Gets user input
    Expects
    1/ ADD + NAME + OCCUPATION + SKILL LEVEL
    2/ DELETE + NAME
    3/ PRINT
    4/ AVERAGE
    '''
    while True:
        user_input = raw_input("Enter your instructions: ")
        if user_input.lower() == "exit":
            logging.info('****END SESSION****.')
            sys.exit()
        else:
            dispatcher(user_input)

def parse_instruction(user_input):
    parsed_instruction = user_input.split(' ')
    return parsed_instruction

def dispatcher(instruction):
    '''Send to add, delete, print or average'''
    parsed_instruction = parse_instruction(instruction)
    if parsed_instruction[0].lower() == 'add':
        add_student(parsed_instruction[1].title(),parsed_instruction[2].title(),int(parsed_instruction[3]))
    elif parsed_instruction[0].lower() == 'delete':
        delete_student(parsed_instruction[1].title())
    elif parsed_instruction[0].lower() == 'print':
        print_students()
    elif parsed_instruction[0].lower() == 'average':
        avg()
    elif parsed_instruction[0].lower() == 'save':
        if '.csv' in parsed_instruction[1].lower() or '.json' in parsed_instruction[1].lower():
            save(parsed_instruction[1].lower())
        else:
            print "----------"
            print "Invalid file format"
            print "----------"
            logging.warning('File save failed. Invalid file format.')
    elif parsed_instruction[0].lower() == 'load':
        if '.json' in parsed_instruction[1].lower():
            load(parsed_instruction[1].lower())
        elif '.csv' in parsed_instruction[1].lower():
            loadcsv(parsed_instruction[1].lower())
        else:
            print "----------"
            print "File load failed. Invalid file format"
            print "----------"
            logging.warning('File load failed. Invalid file format.')
    else:
        print "----------"
        print  "Try again using one of these formats:\n1 / ADD + NAME + OCCUPATION + SKILL LEVEL\n2 / DELETE + NAME\n3 / PRINT\n4 / AVERAGE"
        print "----------"
        logging.warning('Unknown instruction attempted: %s', instruction)

def add_student(student_name, student_occupation, student_skill):
    '''Adds student to database'''
    logging.info('Add attempted.')
    if table.find_one(Student=student_name) is not None:
        print "----------"
        print student_name + " is already on system and has not been added."
        print "----------"
        logging.warning('Failed. Student already on system.')
    else:
        table.insert(dict(Student=student_name,Occupation=student_occupation,Skill=int(student_skill)))
        print "----------"
        print student_name + " added to database."
        print "----------"
        logging.info('%s added.', student_name)


def delete_student(student_name):
    '''Deletes student from database'''
    #test if student name in database
    logging.info('Delete attempted.')
    if table.find_one(Student=student_name) is None:
        print "----------"
        print "Student not in database."
        print "----------"
        logging.warning('Failed. Student not in database.')
    else:
        table.delete(Student=student_name)
        print "----------"
        print student_name + " deleted."
        print "----------"
        logging.info('%s deleted.', student_name)

def print_students():
    '''Prints how many, lowest and highest levels, then lists'''
    if len(table) == 0:
        print "----------"
        print "Student database empty. "
        print "----------"
    else:
        print "-----------"
        print "Number of students: " + str(len(table))
        print "Highest skill level: " + str(find_skill_level()[1])
        print "Lowest skill level: " + str(find_skill_level()[0])
        parse_students()

def avg():
    '''Average the scores'''
    if len(table) == 0:
        print "----------"
        print "No students in database!"
    else:
        running_total = 0
        for row in table.all():
            running_total += row['Skill']
        print "----------"
        print "The average Python level is " + str(running_total/len(table))
        print "----------"

def find_skill_level():
    min_skill = 10
    max_skill = 0
    for row in table['Skill']:
        if row['Skill'] < min_skill:
            min_skill = row['Skill']
        if row['Skill'] > max_skill:
            max_skill = row['Skill']
    return (min_skill,max_skill)

def parse_students():
    print "----------"
    for row in table:
        print "Student Name: " + row['Student']
        print "Occupation: " + row['Occupation']
        print "Skill level: " + str(row['Skill'])
        print "----------"

def save(savefilename):
    result = table.all()
    if '.csv' in savefilename:
        savefileformat = 'csv'
    else:
        savefileformat = 'json'
    dataset.freeze(result, format=savefileformat, filename=savefilename)
    print "----------"
    print "Database saved."
    print "----------"
    logging.info('Data exported as %s.', savefilename)

def load(jsonfilename):
    try:
        with open(jsonfilename,'r') as f:
            data = json.load(f)
            for student in data['results']:
                if table.find_one(Student=student['Student']) is not None:
                    print "----------"
                    print student['Student'] + " is already on system and has not been added."
                    print "----------"
                    logging.warning('Student %s already on system. Not added.', student['Student'])
                else:
                    table.insert(dict(Student=student['Student'], Occupation=student['Occupation'], Skill=int(student['Skill'])))
        print "--------"
        print "Database loaded."
        logging.info('Data imported.')
        print_students()
    except:
        print "----------"
        print "Error loading file. "
        print "----------"
        logging.warning('Error loading file.')

def loadcsv(csvfilename):
    try:
        with open(csvfilename,'r') as f:
            reader = csv.reader(f)
            count = 0
            headers = []
            for row in reader:
                if count == 0:
                    headers.extend(row)
                    count += 1
                else:
                    if table.find_one(Student=row[headers.index('Student')]) is not None:
                        print "----------"
                        print row[headers.index('Student')] + " is already on system and has not been added."
                        print "----------"
                        logging.warning('Student %s already on system. Not added.', row[0])
                    else:
                        table.insert(dict(Student=row[headers.index('Student')], Occupation=row[headers.index('Occupation')], Skill=int(row[headers.index('Skill')])))
                    count += 1
        print "--------"
        print "Database loaded."
        logging.info('Data imported.')
        print_students()
    except:
        print "----------"
        print "Error loading file. "
        print "----------"
        logging.warning('Error loading file.')



get_user_function()