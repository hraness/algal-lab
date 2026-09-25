#!/usr/bin/env python3
"""Flatten a hypergraph JSON into the text format read by bruteforce_check.c."""
import json, sys
doc = json.load(open(sys.argv[1]))
with open(sys.argv[2], "w") as f:
    for s in doc["at_most_4"]:
        f.write("4 %d %s\n" % (len(s), " ".join(map(str, s))))
    for s in doc["at_most_3"]:
        f.write("3 %d %s\n" % (len(s), " ".join(map(str, s))))
print("wrote", sys.argv[2], len(doc["at_most_4"]), len(doc["at_most_3"]))
