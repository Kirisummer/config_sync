#!/bin/bash

rm *.py
for f in *.ui; do
    pyside6-uic "$f" > "${f%.*}.py"
done
