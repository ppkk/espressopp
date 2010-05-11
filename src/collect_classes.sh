#!/bin/bash

# collect all classfiles
FILES=`grep -rl --include "*.hpp" "ESPP_CLASS" *`

##################################################
# Generate SubMakefile.am

# Headers
echo "# This file was autogenerated by $0 on `date`" > SubMakefile.am
echo "# Please do not modify it!" >> SubMakefile.am
echo >> SubMakefile.am

echo -n "noinst_HEADERS +=" >> SubMakefile.am
for file in $FILES; do
    echo -n " $file" >> SubMakefile.am
done
echo >> SubMakefile.am

# Source files
echo -n "libespresso_common_la_SOURCES +=" >> SubMakefile.am
for file in $FILES; do
    file=${file/.hpp/.cpp}
    if test -e $file; then
	echo -n " $file" >> SubMakefile.am
    fi
done
echo >> SubMakefile.am

# Python files
echo -n "python_SCRIPTS +=" >> SubMakefile.am
for file in $FILES; do
    file=${file/.hpp/.py}
    if test -e $file; then
	echo -n " $file" >> SubMakefile.am
    fi
done
echo >> SubMakefile.am

# * check macro definition at the beggining of the .hpp file?
# * check namespace in the file?
# * add class to bindings.cpp
# * add class to __init__.py?
