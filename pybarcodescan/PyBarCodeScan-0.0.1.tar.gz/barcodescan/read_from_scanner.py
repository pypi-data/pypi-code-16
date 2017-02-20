import sys
import httplib2
import json


def read_from_scanner():
  while True:
    line = sys.stdin.readline().rstrip()
    yield line


if __name__ == "__main__":

  for line in read_from_scanner():
    j = json.dumps({'data': line})
    h = httplib2.Http()
    (resp_headers, _) = h.request("http://localhost:8000", body=j, method="PUT",
                                  headers={'Content-Type': 'application/json'})
    print(resp_headers.status)
