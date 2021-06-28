#!/bin/bash

set -e
(>&2 echo "Begin of script")
source ./penv27.tar/bin/activate
(>&2 echo "Activated venv")
./penv27.tar/bin/python udaf.py
(>&2 echo "End of script")