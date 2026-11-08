from __future__ import annotations
from collections import defaultdict, Counter, deque
from typing import Optional


class StudentAllocationNotPossible(Exception):
    pass


def students_to_courses(
    C: dict[str, int],
    S: dict[str, list]
) -> dict[str, Optional[str]]:
    ''' Solves the problem of assigning n students to m courses, where
        each student chooses a list of at most l courses.
        Returns a dict s2c with s2c[i] being the course to which
        student i was assigned to, or None if no assignment was possible.
        The number of unassigned students is minimal.

        Time complexity (worst case): O(n * (l*m + min(m^2, l*n))).
        Students who cannot be assigned are cheap on average: every course
        visited by an unsuccessful search is never searched again.
        Space complexity: O(l*n + m).

        Raises ValueError if a student votes for an unknown course or if
        a capacity is negative. Duplicate votes are ignored.

    >>> course_capacities = {'1': 1, '2': 2, '3': 3}
    >>> student_votes = {
    ...     '1': ['1', '3'], '2': ['1', '3'], '3': ['2', '3'],
    ...     '4': ['1'], '5': ['1', '2', '3'], '6': ['3']
    ... }
    >>> students_to_courses(course_capacities, student_votes)
    {'1': '3', '2': '3', '3': '2', '4': '1', '5': '2', '6': '3'}
    '''
    courses = {}
    for id, cap in C.items():
        capacity = int(cap)
        if capacity < 0:
            raise ValueError(f'course {id!r} has negative capacity {cap!r}')
        courses[id] = Course(id=id, capacity=capacity)

    students = []
    for id, vote in S.items():
        unknown = [j for j in vote if j not in courses]
        if unknown:
            raise ValueError(
                f'student {id!r} voted for unknown course(s) {unknown!r}'
            )
        students.append(
            Student(id=id, voted_courses=[courses[j] for j in vote])
        )

    for student in sorted(
            students,
            key=lambda student: len(student.voted_courses),
            reverse=True
    ):
        # the sorting is a matter of taste: here, the more courses
        # you have voted for, the better the chance to get
        # at least one of your chosen courses.
        student.assign()

    return {
        student.id: student.assigned_course.id
        if student.assigned_course else None
        for student in students
    }


class Course:
    students: set[Student]
    _id: int = 0
    neighbours: defaultdict[Course, set[Student]]
    capacity: int
    dead: bool

    def __init__(self, id: str, capacity: int) -> None:
        self.id = id
        self._id = Course._id
        Course._id = Course._id + 1
        self.students = set()
        # neighbours[other] = students in this course who also voted other
        self.neighbours = defaultdict(set)
        self.capacity = capacity
        # a dead course is full and every student in it voted only for
        # dead courses: no switching chain through it can ever succeed
        self.dead = False

    def __hash__(self) -> int:
        return self._id

    def __repr__(self) -> str:
        return f'Course( \
            id={self.id}, \
            capacity={self.capacity}, \
            students={len(self.students)} \
        )'

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

    def __init__(
        self,
        student: Student,
        source: Course,
        target: Course
    ) -> None:
        self.student = student
        self.source = source
        self.target = target

    def __repr__(self) -> str:
        return f'SWITCH {self.student.id}: {self.source.id}->{self.target.id}'


class Student:
    _id: int = 0
    voted_courses: list[Course]
    assigned_course: Optional[Course]

    def __init__(self, id: str, voted_courses: list[Course]) -> None:
        self.id = id
        self._id = Student._id
        Student._id = Student._id + 1
        # remove duplicate votes, keep the order
        self.voted_courses = list(dict.fromkeys(voted_courses))
        self.assigned_course = None

    def __hash__(self) -> int:
        return self._id

    def __repr__(self) -> str:
        return f'Student( \
            id={self.id}, \
            voted_courses={list(map(lambda c: c.id, self.voted_courses))} \
        )'

    def __eq__(self, __o) -> bool:
        return self.id == __o.id

    def __lt__(self, other) -> bool:
        return self.id < other.id

    def assign(self) -> Optional[Course]:
        course, switches = find_free_course(self)
        if course:
            execute_switches(course, self, switches)
        return course


def find_free_course(
    student: Student
) -> tuple[Optional[Course], dict[Course, Switch]]:
    ''' Breadth-first search for a course with a free place that can be
        reached from the voted courses of student by a chain of switches
        (an augmenting path). Returns the free course and the switches
        needed to get there, or None if there is no such course. In the
        latter case all visited courses are marked dead.
    '''
    switches: dict[Course, Switch] = {}
    visited: set[Course] = set()
    frontier: list[Course] = []

    for course in student.voted_courses:
        if course.dead or course in visited:
            continue
        if not course.is_full():
            return course, switches
        visited.add(course)
        frontier.append(course)

    while frontier:
        next_frontier = []
        for course in frontier:
            for neighbour, movers in course.neighbours.items():
                if neighbour in visited or neighbour.dead:
                    continue
                mover = next(iter(movers))
                switches[neighbour] = Switch(mover, course, neighbour)
                if not neighbour.is_full():
                    return neighbour, switches
                visited.add(neighbour)
                next_frontier.append(neighbour)
        frontier = next_frontier

    # every visited course is full and all its students voted only for
    # visited (or already dead) courses, so this stays true forever
    for course in visited:
        course.dead = True
    return None, switches


def execute_switches(
    course_to_switch_to: Course,
    student: Student,
    switches: dict[Course, Switch]
) -> None:
    ''' Walks back along the chain of switches, starting at the free course,
        and finally assigns student to the course that became free. '''
    voted = set(student.voted_courses)
    course = course_to_switch_to
    while course not in voted:
        switch = switches[course]
        switch.source.remove_student(switch.student)
        switch.target.add_student(switch.student)
        switch.student.assigned_course = switch.target
        course = switch.source
    course.add_student(student)
    student.assigned_course = course


def verify_solution(S2C: dict, S: dict, C: dict):
    ''' Asserts that S2C is a valid assignment and that the number of
        unassigned students is minimal. '''
    assert set(S2C) == set(S)
    counter = Counter(S2C.values())
    for i, j in S2C.items():
        assert j is None or j in S[i]
    for j, capacity in counter.items():
        assert j is None or capacity <= C[j]

    if counter[None] == 0:
        return

    # no solution found, verify that there is no better assignment:
    # R = courses reachable from unassigned students by switching chains.
    # All of them are full and all students who voted only for courses
    # in R exceed the capacity of R by exactly the number of unassigned
    # students, so no assignment can do better (Koenig-Ore).
    C2S: dict[str, list[str]] = {c: [] for c in C.keys()}
    for s, c in S2C.items():
        if c is not None:
            C2S[c].append(s)
    courses = {c for s in S2C if S2C[s] is None for c in S[s]}
    queue = deque(courses)
    while queue:
        c = queue.popleft()
        for s in C2S[c]:
            for d in S[s]:
                if d not in courses:
                    courses.add(d)
                    queue.append(d)
    students = {s for s, cs in S.items() if set(cs) <= courses}
    assert len(students) == sum(C[c] for c in courses) + counter[None]


if __name__ == '__main__':
    import doctest
    doctest.testmod()
