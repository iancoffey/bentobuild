# Copyright 2020 VMware, Inc.
# SPDX-License-Identifier: Apache-2

from bentobuild import job
import threading
import sys

b = job.BentoJobBuilder()
j = b.safe_build(sys.argv[1], sys.argv[2], sys.argv[3])
print(type(j))
b.status(j)


def printit():
    threading.Timer(5.0, printit).start()
    b.status(j)


printit()
