from collections import Counter
import csv
import os
from typing import Tuple
from pathlib import Path

DIR = Path(__file__).resolve().parent
# import sys
# sys.path.append(os.path.join(DIR.parent, 'src'))
from students2courses import solver


def test_solve_problem_from_csv():  
    with open(os.path.join(DIR, 'course_capacities.csv'), 'r', encoding='UTF-8') as f:
        reader = csv.DictReader(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')        
        C = {row['ID']: int(row['Capacity']) for row in reader}

    with open(os.path.join(DIR, 'student_votes.csv'), 'r', encoding='UTF-8') as f:
        reader = csv.DictReader(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')        
        S = {row['ID']: row['Courses'].split(',') for row in reader}

    S2C = solver.students_to_courses(C, S)
    solver.verify_solution(S2C, S, C)
   

def test_example():
    course_capacities = {'1': 1, '2': 2, '3': 3}
    student_votes = {'A': ['1', '2'], 'B': ['1', '3'], 'C': ['2', '3'], 'D': ['1'], 'E': ['1', '2', '3'], 'F': ['3']}
    courses = solver.students_to_courses(course_capacities, student_votes)

    counter = Counter(courses.values())
    if counter[None] == 0:
        print('There is a solution.')
    else:
        print(f'There is no solution: {counter[None]} students cannot be assigned to their chosen courses.')

    for student, course in courses.items():
        if course == None:
            print(f'student {student} has yet to be assigned.')
        else:
            print(f'student {student} -> course {course}')
 
    solver.verify_solution(courses, student_votes, course_capacities)  


def test_random_examples():
    for i in range(10):
        m = i * 100
        C, S = generate_example(m=m, c_min=15, c_max=30, l=3)
        S2C = solver.students_to_courses(C, S)
        solver.verify_solution(S2C, S, C)
    

def generate_example(m: int=20, n=None, l: int=3, c_min: int=20, c_max: int=30) -> Tuple[dict, dict]:
    import random
    if not n: n = round((c_max + c_min) / 2 * m)
    C = {str(j): random.randint(c_min, c_max) for j in range(m)}
    S = {str(i): list(map(str, set(random.choices(range(len(C)), k=random.randint(1, l))))) for i in range(n)}
    return C, S
