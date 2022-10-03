<!-- omit in toc -->
# Table of Contents
- [student2courses](#student2courses)
  - [Abstract](#abstract)
  - [Use case](#use-case)
- [Usage](#usage)
  - [Installation](#installation)
  - [Import](#import)
  - [Solve the Problem](#solve-the-problem)
  - [Verify Solution](#verify-solution)
- [Examples](#examples)
  - [Excel input data](#excel-input-data)
  - [csv input data](#csv-input-data)
- [Math behind the Solver](#math-behind-the-solver)
  
# student2courses

## Abstract 
Solves the problem of assigning $n$ students to $m$ courses taking into account the course preferences of each student. Each student chooses between 1 and $l$ courses. The complexity for time and space is both $O(lmn)$. Returns a dictionary (hashmap) with keys as student ids and values as course ids.
		
## Use case
Often universities offer courses with restricted capacities. The students are not randomly assigned, but assigned to a course of their preference whenever possible. For that, they are asked to vote for all courses of their preference. Now, is there a solution that respects all (or at least as many as possible) course preferences? The students are usually assigned manually by the administration. This tool was developed to avoid manual work and to provide an optimal solution. 

# Usage

## Installation
    pip install students2courses

## Import
    from students2courses import solver
	
## Solve the Problem
The method `solver.students_to_courses` takes two arguments:
* a dictionary of course capacities where the keys are the unique ids of the courses and the values are their capacities (integers).
* a dictionary with the votes of all students where the keys are unique student ids and the values are their votes (list of unique course ids).

Example:

    from collections import Counter
    from students2courses import solver

    course_capacities = {'1': 1, '2': 2, '3': 3}
    student_votes = {'A': ['1', '2'], 'B': ['1', '3'], 'C': ['2', '3'], 'D': ['1'], 'E': ['1', '2', '3'], 'F': ['3']}
    courses = solver.students_to_courses(course_capacities, student_votes)

    counter = Counter(courses.values())
    if counter[None] == 0:
        print('There is a solution.')
    else:
        print(f'There is no solution: {counter[None]} students cannot be assigned to their chosen courses.')

    for student, course in courses.items():
        if course is None:
            print(f'student {student} has yet to be assigned.')
        else:
            print(f'student {student} -> course {course}')

After execution our terminal tells us:

    There is a solution.
    student A -> course 2
    student B -> course 3
    student C -> course 2
    student D -> course 1
    student E -> course 3
    student F -> course 3

## Verify Solution
The solver-module has a method `verify_solution` that verifies a valid solution, but also verifies in case 
a solution does not exist that the number of students not assigned is minimal. The test-module uses it, so look there for examples.

# Examples

## Excel input data
In this example, we use *pandas* to transform Excel-data into the desired lists. An output file named *output.csv* is generated.

    import csv
    import os
    from  pathlib import Path
    import re

    import pandas

    from students2courses import solver

    DIR = Path(__file__).resolve().parent


    def main():
        df = pandas.read_excel(os.path.join(DIR, 'course_capacities.xlsx'))
        df = df.fillna('')
        courses = df.to_dict('records')
        C = {clean_name(course['ID']): course['Capacity'] for course in courses}

        df = pandas.read_excel(os.path.join(DIR, 'students_votes.xlsx'), usecols=['ID', 'Vote_1', 'Vote_2', 'Vote_3 (optional)'])
        df = df.fillna('')
        students = df.to_dict('records')
        S = { student['ID'] : [student['Vote_1'], student['Vote_2'], student['Vote_3 (optional)']] for student in students }
        S = { str(i): [clean_name(j) for j in vote if j] for i, vote in S.items() } 

        S2C = solver.students_to_courses(C, S)
        print(S2C)

        with open(os.path.join(DIR, 'output.csv'), 'w', encoding='utf-8') as f:
            fieldnames = ['Student_ID', 'Course_ID']
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')        
            writer.writeheader()
            writer.writerows([ {'Student_ID': i, 'Course_ID': j} for i, j in S2C.items()])

    def clean_name(name):
        name = name.replace('\xa0', ' ')   
        name = name.strip() 
        m = re.search('^[\s]*(.+[^\s])[\s]*$', name)
        return m.group(0)   


    if __name__ == '__main__': main()

## csv input data
Let's say we have 2 csv files:
*course_capacities.csv* contains:

    ID,Capacity
    a,4
    b,6
    c,3
    d,5
    e,6

and *student_votes.csv* contains:

    ID,Courses
    A,a
    B,e
    C,"a,b,d"
    D,"a,b,e"
    E,"a,e"
    F,"b,c"
    G,"c,d,e"
    H,e
    I,b
    J,"d,e"
    K,e
    L,"d,e"
    M,a
    N,e
    O,"b,d"
    P,d
    Q,"b,c,e"
    R,"c,d,e"
    S,d
    T,"a,c"

We can solve this problem with the following code:

    from pathlib import Path
    import csv
    import os

    from students2courses import solver

    DIR = Path(__file__).resolve().parent


    with open(os.path.join(DIR, 'course_capacities.csv'), 'r', encoding='UTF-8') as f:
        reader = csv.DictReader(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')        
        C = {row['ID']: int(row['Capacity']) for row in reader}

    with open(os.path.join(DIR, 'student_votes.csv'), 'r', encoding='UTF-8') as f:
        reader = csv.DictReader(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')        
        S = {row['ID']: row['Courses'].split(',') for row in reader}
    
    S2C = solver.students_to_courses(C, S)

    with open(os.path.join(DIR, 'output.csv'), 'w', encoding='utf-8') as f:
        fieldnames = ['Student_ID', 'Course_ID']
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')        
        writer.writeheader()
        writer.writerows([ {'Student_ID': i, 'Course_ID': j} for i, j in S2C.items()])

Now, the generated *output.csv* looks like this:

    Student_ID,Course_ID
    A,a
    B,e
    C,b
    D,a
    E,a
    F,b
    G,c
    H,e
    I,b
    J,d
    K,e
    L,d
    M,a
    N,e
    O,b
    P,d
    Q,b
    R,c
    S,d
    T,c

And we can verify that this solution is valid:

    >>> from collections import Counter
    >>> print(Counter(S2C.values()))
    Counter({'b': 5, 'a': 4, 'e': 4, 'd': 4, 'c': 3})

# Math behind the Solver
Given are $n$ students who have all chosen at least one course, but at most $l$ courses from a set of $m$ courses. Every course $j\in\{1,\dots,m\}$ has a capacity $c_j$. Can we allocate the students to the courses in such a way that each student gets a course of their choice?

Let $C = \{1,\dots, m\}$ be the set of all courses and $S = \{1,\dots, n\}$ be the set of all students.
Let $V=\{D : D\subseteq C, 1\leq |D|\leq l\}$ be the set of all possible course choices.
Further let $v: S\rightarrow V, i\mapsto v(i)=v_i$ be the course choice of student $i$ and
   $c: C\rightarrow \mathbb{N}, j\mapsto c(j)=c_j$ the capacity function where $c_j$ is the capacity of course $j$.
We call a tuple $(C, S, v, c)$ **course problem** and a function $f:S\rightarrow C\cup \{\emptyset\}, i\mapsto f(i)$ we call **mapping**.

We are now looking - if available - for a mapping $f$ of students to courses that does not overcrowd the courses and respects the course choices of the students. If that is true, we call $f$ **valid**. Written formally, $f$ is valid if the properties
1. $|\{i \in S : f(i)=j\}| \leq c_j$ for all courses $j\in C$ and
2. $f(i) \in v_i\cup\{\emptyset\}$ for all students $i\in S$

are fulfilled. We allow the empty set as a function value of $f$ so that we can also consider valid mappings if a course problem is not solvable in the sense of our problem.

What are the prerequisites for our course problem to be solvable at all? An obvious requirement is that there must be at least as many course places as students. This can be generalized, because for each subset of courses, all students whose course choice is in this subset must fit into these courses. Therefore we call a course problem $(C, S, v, c)$ **suitable** if for all $D\subseteq C\$ holds
$$
|\{ i\in S : v_i\subseteq D\}| \leq \sum\limits_{j\in D} c_j.
$$

Later on we would like to be able to assess the quality of various mappings. One mapping is better than another if it manages to assign more students to their chosen courses.
To quantify this, we define the **kernel** of $f$ by $\text{ker}(f)= \{i \in S:f(i)=\emptyset\}$. So the kernel of $f$ holds all students who did not get a course under $f$.
Let $f$ and $g$ be two valid mappings of a course problem. Then both **are equally good** if $|\text{ker}(f)|=|\text{ker}(g)|$. We say $f$ is **better** than $g$ if $|\text{ker}(f)|<|\text{ker}(g)|$.

Now one last definition: We call a course problem $(C,S,v,c)$ **solvable** if a valid mapping $f$ exists with $|\text{ker}(f)|=0$ . That makes sense, because then we would have taken care of all the students to their satisfaction.

We would like to work towards a nice theorem and so that the proof of the theorem is as elegant as possible, we outsource the technical part to the following lemma:

**Lemma**

Let $(C, S, v, c)$ be a suitable course problem and $f$ a valid mapping of the course problem under which courses from $D\subseteq C$ with $0<|D|<|C|$ are completely occupied .
If there is a student $i$ with $v_i\subseteq D$ in $\text{ker}(f)$, then there is an equally good mapping $g$ of the course problem with $\text{ker}(f) = \text{ker}(g)$, where there is a vacancy in one of the courses from $D$.

*proof*

Since there is a suitable course problem where Student $i\in S$ is not yet assigned to a course, there must still be a free place in a course $j\in C$. Let $k=|D|$ and we set $D_k=D$.

If there is a student in $D_k$ who chose $j$, we can reassign that to $j$ and we're done. Otherwise there must be a student $i_k$ from $D_k$ who chose a course from $C\setminus (D_k\cup\{j\})$ since the course problem is suitable but the courses from $D_k$ are full, although $i$ has only selected courses from $D_k$. Let $j_k$ be this course.
Now there are two cases:
1. There is still a free place in $j_k$. Then we can transfer this very student from $D_k$ to $j_k$ and we're done.
2. There is no free space in $j_k$. Then we consider $D_{k+1}=D_k\cup\{j_k\}$ and repeat the procedure for $k+1$.

 At the latest at $D_{m-1}$ the second case can no longer occur since there was a free slot. We now swap a few more students to create the free space in the original $D$. Suppose we have to go up to $k_{\max}$ .
 With
$$
   g: S \rightarrow C, i \mapsto g(i)=
  \begin{cases}
    j_k & \text{for } i\in \{i_k,i_{k+1},\dots,i_{k_{\max}-1}\},\\
    j & \text{for } i=i_{k_{\max}},\\
    f(i) & \text{otherwise}
  \end{cases}
$$
we have reached our goal, because there is now a place in the course $f(i_k)$.  $\square$

In summary, the lemma says: If we have a set of full courses given a suitable course problem, and we cannot assign a student because his course choice lies in these full courses, then switching students can free up a place in one of his chosen courses .
Ultimately, a suitable course problem can free up a place for each student in one of their chosen courses without forcing another student out of all chosen courses. And with that we have already reached our goal.

**Theorem**

A course problem is solvable if and only if it is suitable.

*proof*

If the course problem can be solved, it must also be suitable - we already knew that. For the inverse, we assume that a suitable course problem is unsolvable. Then there is a valid mapping $f$ where $|\text{ker}(f)|>0$ is minimal among all valid mappings. There is a student $i$ in the kernel of $f$. The courses from $v_i$ are full. Since the course problem is suitable, there must be a course with a vacancy.
With our lemma there is then an equally good function $g$ with an identical kernel, where there is a free space in $v_i$. But then we could modify $g$ and now assign student $i$ to a course in $v_i$, making $g$ better than $f$, a contradiction. So the course problem must be solvable.  $\square$

Now even the best theory is useless here if we can't put it into practice. To check whether a course problem is solvable, we can e.g. iterate through all subsets of $C$ and, following the definition, check the prerequisites for whether the course problem is suitable. We need $2^m$ steps for the loop alone. This means exponential complexity. In addition, we then only know whether the course problem can be solved or not, but we do not obtain any solution.

If we look at the lemma again, it provides a faster and constructive way: we can successively assign the students to courses. If all the chosen courses of a student are occupied, we can either create a free place in one of these courses by swapping students who have already been assigned to other courses, or the course problem is not suitable.
Every time a student $i$ is assigned to course $j$ via $f(i) := j$ we keep track of which other courses from $v_i$ we can swap $i$. We can find a solution with time complexity $\mathcal{O}(lmn)$ or, if there is no solution, at least a mapping with a minimal kernel. We can then allocate the students from the kernal to the remaining free course places as we wish.
