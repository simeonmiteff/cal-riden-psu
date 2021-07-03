#!/bin/sh
# use this to get the latest commit for the rd6006 if upgrading the dependency
# on this package to a new release in requirements.txt
git ls-remote https://github.com/Baldanos/rd6006 HEAD | cut -f1
