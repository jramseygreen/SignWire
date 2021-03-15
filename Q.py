# -*- coding: utf-8 -*-
"""
Created on Thu Mar 11 03:36:49 2021

@author: Josh
"""


class MsgQueue:

    def __init__(self):
        self.q = []

    def push(self, obj):
        self.q += obj

    def pop(self):
        return self.q.pop(0)

    def peak(self):
        return self.q[0]

    def length(self):
        return len(self.q)

    def to_string(self):
        string = ''
        for item in self.q:
            string += str(item) + ','
        return string

    def clear(self):
        self.q = []

    def has_items(self):
        return len(self.q) > 0