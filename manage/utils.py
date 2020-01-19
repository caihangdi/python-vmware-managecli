#!/usr/bin/python
# -*- coding: utf-8 -*-
import csv
import re
import sys
import time

def csv2dict(csv_dir):
    with open(csv_dir, 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        column = [row for row in reader]
        return column


def sizeof_fmt(num):
    """
    Returns the human readable version of a file size

    :param num:
    :return:
    """
    for item in ['bytes', 'KB', 'MB', 'GB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, item)
        num /= 1024.0
    return "%3.1f%s" % (num, 'TB')


def return_none(message):
    if message is None:
        message = "None"
    return message


def pt2csv(tb):
    reload(sys)
    sys.setdefaultencoding('utf-8')
    lines = str(tb).split("\n")
    num_columns = len(re.findall("\+", lines[0])) - 1
    line_regex = r"\|" + (r" +(.*?) +\|" * num_columns)
    s = []
    path = 'csv_output.csv'
    for line in lines:
        m = re.match(line_regex, line.strip())
        if m:
            s.append(m.groups())
    with open(path, 'w') as csv_file:
        writer = csv.writer(csv_file, dialect='excel')
        for row in s:
            writer.writerow(row)
        print("Write a CSV file to path %s Successful." % path)


def progress(percent=0, jb="vcenter_job"):
    width = 30
    _output = sys.stdout
    left = width * percent // 100
    right = width - left
    _output.write('\r[{} {}] percent: {} working:{}'.format('#' * left, ' ' * right, percent, jb))
    _output.flush()