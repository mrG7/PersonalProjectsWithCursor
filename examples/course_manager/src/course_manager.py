import asyncio
from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class Lecture:
    title: str
    description: str
    duration_minutes: int
    resources: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        return {
            'title': self.title,
            'description': self.description,
            'duration_minutes': self.duration_minutes,
            'resources': list(self.resources),
        }


@dataclass
class Course:
    course_id: str
    name: str
    instructor: str
    lectures: List[Lecture] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    def add_lecture(self, lecture: Lecture) -> None:
        self.lectures.append(lecture)

    def to_dict(self) -> Dict[str, object]:
        return {
            'course_id': self.course_id,
            'name': self.name,
            'instructor': self.instructor,
            'tags': list(self.tags),
            'lectures': [l.to_dict() for l in self.lectures],
        }


class CourseManager:
    def __init__(self) -> None:
        self._courses: Dict[str, Course] = {}

    async def create_course(self, course_id: str, name: str, instructor: str, tags: Optional[List[str]] = None) -> Course:
        await asyncio.sleep(0)
        course = Course(course_id=course_id, name=name, instructor=instructor, tags=tags or [])
        self._courses[course_id] = course
        return course

    async def add_lecture(self, course_id: str, title: str, description: str, duration_minutes: int, resources: Optional[List[str]] = None) -> Lecture:
        await asyncio.sleep(0)
        course = self._courses[course_id]
        lecture = Lecture(title=title, description=description, duration_minutes=duration_minutes, resources=resources or [])
        course.add_lecture(lecture)
        return lecture

    async def list_courses(self) -> List[Course]:
        await asyncio.sleep(0)
        return list(self._courses.values())

    async def get_course(self, course_id: str) -> Optional[Course]:
        await asyncio.sleep(0)
        return self._courses.get(course_id)


