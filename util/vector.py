"""Utility functions for 2d vectors."""

import math


def subtract(a, b):
    """Subtract 2d vectors [a] - [b]."""
    def subtract(a, b):
        return a - b
    return map(subtract, a, b)


def multiply_scalar(a, v):
    """Multiply 2d vector by a scalar."""
    def multiply(v):
        return a * v
    return map(multiply, v)


def divide_scalar(a, v):
    """Divide 2d vector by a scalar."""
    def divide(v):
        return v / float(a)
    return map(divide, v)


def normalize(v):
    """Normalize 2d vector [v]."""
    x, y = v
    magnitude = math.sqrt(x*x + y*y)
    return divide_scalar(magnitude, v)
