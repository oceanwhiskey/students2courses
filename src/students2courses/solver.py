from __future__ import annotations
from collections import defaultdict, Counter


class StudentAllocationNotPossible(Exception): pass
courses_switched_to: dict[Course, Switch] = {}


def students_to_courses(C: dict[str, int], S: dict[str, list]) -> dict[str, str]:
    ''' Solves the problem of assigning n students to m courses, where each students 
        chooses a list of courses. Time/space complexity O(nm). Returns a list s2c with s2c[i] being the course to which
        student i was assigned to.
    
    >>> course_capacities = {'1': 1, '2': 2, '3': 3}
    >>> student_votes = {'1': ['1', '3'], '2': ['1', '3'], '3': ['2', '3'], '4': ['1'], '5': ['1', '2', '3'], '6': ['3']}
    >>> students_to_courses(course_capacities, student_votes)
    {'1': '3', '2': '3', '3': '2', '4': '1', '5': '2', '6': '3'}
    '''    
    courses = {id: Course(id=id, capacity=int(cap)) for id, cap in C.items()}
    students = [Student(id=id, voted_courses=[courses[j] for j in vote]) for id, vote in S.items()]

    for student in sorted(students, key=lambda student: len(student.voted_courses), reverse=True):
        # the sorting is a matter of taste: here, the more courses you have voted for, 
        # the better the chance to get at least one of your chosen courses.
        student.assign()

    return {student.id: student.assigned_course.id if student.assigned_course else None for student in students }


class Course:
    students: set[Student]
    _id: int = 0
    neighbours: defaultdict[Course, set[Student]]
    capacity: int

    def __init__(self, id: str, capacity: int) -> None:
        self.id = id
        self._id = Course._id
        Course._id = Course._id + 1
        self.students = set()
        self.neighbours = defaultdict(set)
        self.capacity = capacity
    
    def __hash__(self) -> int:
        return self._id

    def __repr__(self) -> str:
        return f'Course(id={self.id}, capacity={self.capacity}, students={len(self.students)})'

    def __eq__(self, __o) -> bool:
        return self.id == __o.id

    def add_student(self, student: Student):
        self.students.add(student)
        for course in student.voted_courses:
            if course != self:
                self.neighbours[course].add(student)
    
    def remove_student(self, student: Student):
        self.students.remove(student)
        for course in student.voted_courses:
            if course != self:
                self.neighbours[course].remove(student)
            if not self.neighbours[course]:
                del self.neighbours[course]

    def is_full(self) -> bool:
        return len(self.students) >= self.capacity


class Switch:
    __slots__ = ('student', 'target', 'source')
    student: Student
    target: Course
    source: Course

    def __init__(self, student: Student, source: Course, target: Course ) -> None:
        self.student = student
        self.source = source
        self.target = target
    
    def __repr__(self) -> str:
        return f'SWITCH {self.student.id}: {self.source.id}->{self.target.id}'


class Student:
    _id: int = 0
    voted_courses: list[Course]
    assigned_course: Course

    def __init__(self, id: str, voted_courses: list[Course]) -> None:
        self.id = id
        self._id = Student._id
        Student._id = Student._id + 1
        self.voted_courses = voted_courses
        self.assigned_course = None
    
    def __hash__(self) -> int:
        return self._id
    
    def __repr__(self) -> str:
        return f'Student(id={self.id}, voted_courses={list(map(lambda c: c.id, self.voted_courses))})'
    
    def __eq__(self, __o) -> bool:
        return self.id == __o.id

    def __lt__(self, other) -> bool:
        return self.id < other.id

    def assign(self):
        global courses_switched_to
        courses_switched_to = {}

        courses_to_check = {course: self for course in self.voted_courses}
        course = rassign(courses_to_check)
        if course:
            execute_switches(course, self)
        return course


def rassign(courses_to_check: dict[Course, Student]) -> Course:
    global courses_switched_to

    if not courses_to_check:
        return None

    for course, student in courses_to_check.items():
        if course.is_full():
            continue
        else:
            if course in courses_switched_to:
                return course
            if student.assigned_course:
                switch = Switch(student, student.assigned_course, course)
                courses_switched_to[course] = switch
            return course
    else:
        new_courses_to_check = {}
        for course in courses_to_check:
            for neighbour in course.neighbours.keys():
                if neighbour not in courses_switched_to and neighbour not in new_courses_to_check:
                    for s in course.neighbours[neighbour]:
                        student = s
                        break
                    new_courses_to_check[neighbour] = student
                    switch = Switch(student, course, neighbour)
                    courses_switched_to[neighbour] = switch
        return rassign(new_courses_to_check)


def execute_switches(course_to_switch_to: Course, student: Student) -> None:
    if course_to_switch_to in student.voted_courses:
        course_to_switch_to.add_student(student)
        student.assigned_course = course_to_switch_to
    else:
        switch = courses_switched_to[course_to_switch_to]
        switch.source.remove_student(switch.student)
        switch.target.add_student(switch.student)
        switch.student.assigned_course = switch.target
        execute_switches(switch.source, student)


def verify_solution(S2C: dict, S: dict, C: dict):
    counter = Counter(S2C.values())
    if counter[None] == 0:
        # solution found, verify conditions for a valid solution
        for i, j in S2C.items():
            assert j in S[i]
        for j, capacity in counter.items():
            assert capacity <= C[j]   
    else:
        def connected_courses(courses_to_process: set, courses_processed: set, S2C: dict, C2S: dict, S: dict) -> set:
            students = { s for c in courses_to_process for s in C2S[c] }
            courses = { c for s in students for c in S[s] if ( c not in courses_to_process and c not in courses_processed) }
            if not courses:
                return courses_to_process.union(courses_processed)
            else:
                return connected_courses(courses, courses_to_process.union(courses_processed), S2C, C2S, S)

        # no solution found, verify that 
        # * no solution exists and
        # * there is no better assignment that assigns more students to their voted courses
        C2S = {c : [] for c in C.keys()}
        for s, c in S2C.items():
            if c: C2S[c].append(s)
        students = { s for s, c in S2C.items() if c == None}      
        courses = { c for s in students for c in S[s] }
        courses = connected_courses(courses, set(), S2C, C2S, S) # these are the bottleneck-courses
        students = { s for s, cs in S.items() if set(cs) <= courses}
        assert len(students) == sum(C[c] for c in courses) + counter[None]    

if __name__ == '__main__':
    import doctest
    doctest.testmod()