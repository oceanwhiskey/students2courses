from collections import Counter
import csv
import os
from pathlib import Path
from typing import Tuple

from students2courses import solver

DIR = Path(__file__).resolve().parent


def main():
    small_example()
    

def small_example():
    course_capacities = {'course_1': 1, 'course_2': 2, 'course_3': 3}
    student_votes = {'student_1': ['course_1', 'course_2'], 'student_2': ['course_1', 'course_3'], 'student_3': ['course_2', 'course_3'], 'student_4': ['course_1'], 'student_5': ['course_1', 'course_2', 'course_3'], 'student_6': ['course_3']}
    courses = solver.students_to_courses(course_capacities, student_votes)

    counter = Counter(courses.values())
    if counter[None] == 0:
        print('There is a solution.')
    else:
        print(f'There is no solution: {counter[None]} students cannot be assigned to their chosen courses.')

    for student, course in courses.items():
        if course == None:
            print(f'{student} has yet to be assigned.')
        else:
            print(f'{student} -> {course}')
 
    solver.verify_solution(courses, student_votes, course_capacities)


def solve_problem_from_csv():  
    with open(os.path.join(DIR, 'course_capacities.csv'), 'r', encoding='UTF-8') as f:
        reader = csv.DictReader(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')        
        C = {row['ID']: int(row['Capacity']) for row in reader}

    with open(os.path.join(DIR, 'student_votes.csv'), 'r', encoding='UTF-8') as f:
        reader = csv.DictReader(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')        
        S = {row['ID']: row['Courses'].split(',') for row in reader}

    S2C = solver.students_to_courses(C, S)
    solver.verify_solution(S2C, S, C)
   

if __name__ == '__main__': main()