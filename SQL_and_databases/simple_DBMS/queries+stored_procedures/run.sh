#!/bin/bash

db2 -t -v < test_query.sql 2>&1 | tee logs/test_query.log
#This file helps run the scripts in DB2.
#Change the name of the file you want to run and use the command line to run this file

#IMPORTANT: Don't forget to create a logs directory