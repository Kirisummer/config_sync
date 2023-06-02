#!/bin/bash -e

rm *.py || true
classes=( )
for ui_file in *.ui; do
    py_module="${ui_file%.*}"
    pyside6-uic "$ui_file" > "${py_module}.py"
    class=$(grep -E '^class ' "${py_module}.py" | awk -F '[ (]' '{ print $2 }')
    printf 'from .%s import %s\n' "$py_module" "$class" >> __init__.py
    classes+=( "$class" )
done

printf '__all__ = [' >> __init__.py
for class in "${classes[@]}"; do
    printf '%s, ' "$class" >> __init__.py
done
printf ']' >> __init__.py
