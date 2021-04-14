#! /usr/bin/python3
import api
import timeit

api.apiAccess()
print(timeit.timeit(api.apiAccess))