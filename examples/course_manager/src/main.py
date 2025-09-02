import argparse
import asyncio
import json
from typing import Optional

from .course_manager import CourseManager


async def demo_syllabus() -> dict:
    manager = CourseManager()
    course = await manager.create_course(
        course_id="CS101",
        name="Intro to AI Agents with Cursor",
        instructor="Dr. Ada Lovelace",
        tags=["ai", "agents", "cursor"],
    )

    await manager.add_lecture(
        course_id=course.course_id,
        title="Course Kickoff & Repo Tour",
        description="Orientation to Cursor project structure and agent templates.",
        duration_minutes=45,
        resources=[
            "README.md",
            "docs/implementation_guide.md",
            "examples/content_creator.prompt",
        ],
    )

    await manager.add_lecture(
        course_id=course.course_id,
        title="Building Your First Agent",
        description="Create and run a minimal agent using templates.",
        duration_minutes=60,
        resources=[
            "templates/agent_base.template",
            "scripts/setup_agent.py",
        ],
    )

    return course.to_dict()


async def run_cli(list_only: bool = False) -> None:
    if list_only:
        # For demo, list the demo syllabus
        syllabus = await demo_syllabus()
        print(json.dumps({"courses": [syllabus]}, indent=2))
        return

    syllabus = await demo_syllabus()
    print("\n=== Course Created ===")
    print(f"Course: {syllabus['name']} ({syllabus['course_id']})")
    print(f"Instructor: {syllabus['instructor']}")
    print(f"Lectures: {len(syllabus['lectures'])}")


def main(argv: Optional[list] = None) -> None:
    parser = argparse.ArgumentParser(
        description="Course/Lecture Manager - Cursor Example",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a demo course and print summary
  python -m examples.course_manager.src.main

  # Print a JSON syllabus
  python -m examples.course_manager.src.main --list
        """,
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List demo syllabus as JSON",
    )

    args = parser.parse_args(argv)

    asyncio.run(run_cli(list_only=args.list))


if __name__ == "__main__":
    main()


