#!/usr/bin/env python3
import json
import sys

import time

data = sys.stdin.read()
msg = json.loads(data)
with open("out.txt", "w") as f:
    print(msg, file=f)

# Stall
time.sleep(2)

if "my body" not in msg.get("body",""):# or True:
    # print("my title")
    # print("my body")
    resp = {}
    push = {"title":"my title", "body":"my body\nline 2"}
    resp["pushes"] = [push]
    print(json.dumps(resp), flush=True)

# time.sleep(5)
# print("Got it!")

# print("SLOW DOWN, PROFESSOR!", file=sys.stderr)
# sys.exit(1)
