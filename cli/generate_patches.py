#!/usr/bin/env python
# coding=utf-8
# PYTHON_ARGCOMPLETE_OK

import sys
from argparse import ArgumentParser

# Allow this script to be used from the parent directory
sys.path.append(".")

from app.models import Project, File
from app.utils.SourceFile import SourceFile


def main():
    # Parse arguments
    argument_parser = ArgumentParser(description="Generate patches.")
    argument_parser.add_argument(
        "--project", type=str, required=True,
        help="The name of the project. If not provided, all projects will be processed."
    )
    argument_parser.add_argument(
        "--files", type=str,
        help='File list in format: "file1@start:end;file2@start:end". If not provided, all files in project will be used.'
    )
    argument_parser.add_argument(
        "--mutators", type=str,
        help="Comma-separated list of mutators to use. If not provided, all mutators will be used."
    )
    arguments = argument_parser.parse_args()

    # Verify that the project exists
    project_query = Project.query.filter(Project.name == arguments.project)
    if project_query.count() == 0:
        print(f"Project '{arguments.project}' doesn't exist.", file=sys.stderr)
        exit(1)

    # Retrieve all files
    files = File.query.filter(File.project_id == project_query.first().id).all()

    if len(files) == 0:
        print("No files found to process.")
        exit(2)

    # Parse mutators if specified
    mutator_ids = arguments.mutators.split(',') if arguments.mutators else None

    # Parse file filters if specified
    file_filters = {}
    if arguments.files:
        for file_spec in arguments.files.split(';'):
            filename, line_range = file_spec.split('@')
            first_line, last_line = map(int, line_range.split(':'))
            file_filters[filename] = (first_line, last_line)

    # Process files
    for file in files:
        if file_filters and file.filename not in file_filters:
            continue

        print(f"Generating patches for '{file.filename}'...")
        
        # If file_filters is empty use all lines of every file
        first_line, last_line = file_filters.get(file.filename, (1, -1))
        source_file = SourceFile(file, first_line, last_line)
        source_file.generate_patches(mutator_ids)

    print("Done")
    exit(0)


if __name__ == "__main__":
    main()
