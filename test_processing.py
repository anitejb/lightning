"""Tests to determine fastest way to identify if an index is in openSections API response

Format of original input: List of course indexes as strings (sorted)

Rationales:
    - set lookup is technically O(1), whereas list lookup is O(n)
        - For small datasets, setup costs may exceed the benefit of faster lookup
    - int comparison in Python is much faster than str comparison
        - Conversion costs from str to int may exceed the benefit of faster comparisons
    - binary search is O(log(n)), whereas list lookup is O(n)

Conclusion: Binary search on the original input without modification (a sorted list of strs)
will be the fastest method, by far.
"""

import json
import time
from functools import wraps
import numpy as np

# Index of a known open course (14:440:191, Honors Intro to Engineering)
OPEN_INDEX_STR = "10836"
OPEN_INDEX_INT = 10836

# Index of a known closed course (course doesn't exist)
CLOSED_INDEX_STR = "99999"
CLOSED_INDEX_INT = 99999

# Seconds to repeatedly execute function in timeit decorator
TIMEOUT = 2.5

# Load API_RESPONSE of open sections from file
with open("sample_api_responses/openSections.gzip", "r") as f:
    API_RESPONSE = json.load(f)

##### UTIL FUNCTIONS #####


def timeit(func):
    """Wrapper to calculate mean and standard deviation of time taken for a function to finish."""

    @wraps(func)
    def wrapper_timeit(*args, **kwargs):
        timeit_start = time.time()
        function_times = []
        while time.time() - timeit_start < TIMEOUT:
            start = time.time()
            func(*args, **kwargs)
            function_times.append(time.time() - start)
        print(func.__name__)
        print("Number of runs:", len(function_times))
        print("Mean:", np.mean(function_times))
        print("Std Dev:", np.std(function_times))
        print()

    return wrapper_timeit


def binary_search(course, open_sections):
    """Determine if course is in open_sections using binary search."""
    lo = 0
    hi = len(open_sections) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if open_sections[mid] == course:
            return True
        if open_sections[mid] > course:
            hi = mid - 1
        else:
            lo = mid + 1
    return False


##### TESTING FUNCTIONS #####


@timeit
def test_list_str():
    """Measure the time taken to search for a course index in a list of strs.
    No modification to original API response.
    """
    open_sections = API_RESPONSE
    OPEN_INDEX_STR in open_sections
    CLOSED_INDEX_STR in open_sections


@timeit
def test_list_int():
    """Measure the time taken to search for a course index in a list of ints.
    Including setup time for str -> int conversion.
    """
    open_sections = [int(course_index) for course_index in API_RESPONSE]
    OPEN_INDEX_INT in open_sections
    CLOSED_INDEX_INT in open_sections


@timeit
def test_set_str():
    """Measure the time taken to search for a course index in a set of strs.
    Including setup time for list -> set conversion.
    """
    open_sections = set(API_RESPONSE)
    OPEN_INDEX_STR in open_sections
    CLOSED_INDEX_STR in open_sections


@timeit
def test_set_int():
    """Measure the time taken to search for a course index in a set of ints.
    Including setup time for list -> set and set -> int conversion.
    """
    open_sections = set(int(course_index) for course_index in API_RESPONSE)
    OPEN_INDEX_INT in open_sections
    CLOSED_INDEX_INT in open_sections


@timeit
def test_list_str_binary_search():
    """Measure the time taken to search for a course index in a list of strs using binary search.
    No modification to original API response.
    """
    open_sections = API_RESPONSE
    binary_search(OPEN_INDEX_STR, open_sections)
    binary_search(CLOSED_INDEX_STR, open_sections)


@timeit
def test_list_int_binary_search():
    """Measure the time taken to search for a course index in a list of ints using binary search.
    Including setup time for str -> int conversion.
    """
    open_sections = [int(course_index) for course_index in API_RESPONSE]
    binary_search(OPEN_INDEX_INT, open_sections)
    binary_search(CLOSED_INDEX_INT, open_sections)


if __name__ == "__main__":
    test_list_str()
    test_list_int()
    test_set_str()
    test_set_int()
    test_list_str_binary_search()
    test_list_int_binary_search()
