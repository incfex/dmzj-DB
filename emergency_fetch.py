#!/usr/local/bin/python3
import os
import json
import requests
import concurrent.futures
import multiprocessing
import logging
from google.protobuf import json_format

import dmzj_pb2

lck = multiprocessing.Lock()

def validate(r):
  #print(r.text)
  if (r.text == "[]" or r.text == '"Locked!"'):
    return -1
  elif (r.text == "漫画不存在!!!"):
    return 0
  else:
    return 1

def crawler(comicId):
  logging.info("%s#Trying v3 api", str(comicId))
  v3url = "http://v3api.dmzj.com/comic/" + str(comicId) + ".json"
  r = requests.get(v3url)
  if (validate(r) == -1 or validate(r) == 1):
    return r
  logging.info("%s#Trying v2 api", str(comicId))
  v2url = "http://v2.api.dmzj.com/comic/" + str(comicId) + ".json"
  r = requests.get(v2url)
  return r

def pb_parser(r):
  # Acquire the file lock
  lck.acquire()
  # Read from protobuf
  dmzj = dmzj_pb2.Dmzj()
  try:
    with open("dmzj.bin", "rb") as f:
      dmzj.ParseFromString(f.read())
  except IOError:
    logging.error("dmzj.bin: File not Found. Creating a new file.")

  # Create new manga message
  dmzjD = json_format.MessageToDict(dmzj)
  mangas = dmzjD.get("mangas", None)
  if (mangas == None):
    dmzjD["mangas"] = []
    mangas = dmzjD.get("mangas", None)

  mangas.append(r.json())
  json_format.Parse(json.dumps(dmzjD), dmzj)
  print(json_format.MessageToJson(dmzj))
  with open("dmzj.bin", "wb") as f:
    f.write(dmzj.SerializeToString())

  # Release the file lock
  lck.release()
    
def thread_job(comicId):
  r = crawler(comicId)
  # Only record normal result
  if (validate(r) == 1):
    pb_parser(r)
  return

def main():
  logging.basicConfig(level=logging.INFO)

  comic = range(1, 10)

  #thread_job(8)
  #return

  with concurrent.futures.ThreadPoolExecutor() as executor:
    executor.map(thread_job, comic)

if __name__ == "__main__":
    main()