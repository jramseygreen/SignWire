# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 16:32:54 2021

@author: Josh
"""
import hashlib
import os


def file_exists(name):
    try:
        open(name, 'rb')
        return True
    except:
        return False


def read_data(name):
    try:
        f = open(name, "r")  # read file
        contents = f.read()
        f.close()
        return contents
    except:
        return None


def write_data(name, content):
    try:
        f = open(name, "w")  # open file for writing
    except:
        f = open(name, "x")  # create file
        f = open(name, "w")  # then open

    f.write(content)
    f.close()


# returns an array of bytes from a given file
def read_bytes(file):
    try:
        data = []
        f = open(file, "rb")
        data = f.read(1024)
        return data
    except:
        return None


def write_bytes(file_paths, data):
    for path in file_paths:
        f = open(path, 'wb')
        f.write(data)
        f.close()


def remove_file(file_paths):
    for path in file_paths:
        os.remove(path)


# returns an md5 hash of a given file
def to_md5(filepath):
    return hashlib.md5(read_bytes(filepath)).hexdigest()
