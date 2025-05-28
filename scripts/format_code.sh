#!/bin/bash
# Format Python code using isort and black

isort kicad_lib_validator tests
black kicad_lib_validator tests

echo "Formatting complete!" 