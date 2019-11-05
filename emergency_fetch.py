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
  logging.debug("%s#Trying v3 api", str(comicId))
  headers = {'user-agent': 'Mozilla/5.0'}
  v3url = "http://v3api.dmzj.com/comic/" + str(comicId) + ".json"
  tryloop = 5
  while tryloop > 0:
    try:
      r = requests.get(v3url, headers=headers, timeout=10)
      tryloop = 0
    except:
      logging.warning("%s#Exception Happened!", str(comicId))
      tryloop = tryloop - 1
      if tryloop == 0:
        logging.error("%s#Retries Exhausted!", str(comicId))
  if (validate(r) == -1 or validate(r) == 1):
    return r
  logging.debug("%s#Trying v2 api", str(comicId))
  v2url = "http://v2.api.dmzj.com/comic/" + str(comicId) + ".json"
  tryloop = True
  while tryloop > 0:
    try:
      r = requests.get(v2url, headers=headers, timeout=10)
      tryloop = 0
    except:
      logging.warning("%s#Exception Happened!", str(comicId))
      tryloop = tryloop - 1
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
  #print(json_format.MessageToJson(dmzj))
  with open("dmzj.bin", "wb") as f:
    f.write(dmzj.SerializeToString())

  # Release the file lock
  lck.release()
    
def thread_job(comicId):
  r = crawler(comicId)
  # Only record normal result
  if (validate(r) == 1):
    logging.info("%s#Found. Recording...", str(comicId))
    pb_parser(r)
  return

def main():
  logging.basicConfig(filename='dmzj.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')

  comic = range(2000, 5000)

  #thread_job(8)
  #return

  with concurrent.futures.ThreadPoolExecutor() as executor:
    executor.map(thread_job, comic)

if __name__ == "__main__":
    main()
