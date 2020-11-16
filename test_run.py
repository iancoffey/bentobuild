from bentobuild.job import BentoJobBuilder
# from pprint import pprint
import threading
import sys

b = BentoJobBuilder()
job = b.safe_build(sys.argv[1], sys.argv[2], sys.argv[3])
print(type(job))
b.status(job)


def printit():
    threading.Timer(5.0, printit).start()
    b.status(job)


printit()
