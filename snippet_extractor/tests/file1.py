import os
from math import sqrt
from file2 import _function

global_var = 10
x_ = 11

class ExampleClass:
    def method(self):
        print("Method called")

def helper_function():
    global global_var
    global_var += 6
    print("Helper function")

def main_function():
    global x_
    global global_var
    x = global_var
    _function(4)
    x = 5 * x_
    y = sqrt(x)
    helper_function()
    obj = ExampleClass()
    obj.method()
    