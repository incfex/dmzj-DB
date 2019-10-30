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
  if (r.text == "漫画不存在!!!" or r.text == "[]" or r.text == '"Locked!"'):
    return 0
  else:
    return 1

def crawler(comicId):
  v3url = "http://v3api.dmzj.com/comic/" + str(comicId) + ".json"
  r = requests.get(v3url)
  if (validate(r)):
    return r.text
  logging.info(" %s#Trying v2 api", str(comicId))
  v2url = "http://v2.api.dmzj.com/comic/" + str(comicId) + ".json"
  r = requests.get(v2url)
  return r.text

def pb_parser(data):
  dmzj = dmzj_pb2.Dmzj()
  lck.acquire()
  try:
    with open("dmzj.bin", "rb") as f:
      dmzj.ParseFromString(f.read())
  except IOError:
    logging.error("dmzj.bin: File not Found")

  _manga = dmzj.mangas.add()
  _manga.id = data.get("id", -1)
  print(json_format.MessageToJson(dmzj))
  lck.release()
    
def thread_job(comicId):
  r = crawler(comicId)
  if (validate(r)):
    pb_parser(json.loads(r))
  #script_dir = os.path.dirname(__file__)
  #rel_path = "offline_data/" + str(comicId) + ".txt"
  #abs_path = os.path.join(script_dir, rel_path)
  #with open(abs_path, 'w') as f:
  #  f.write(r)
  return

def main():
  logging.basicConfig(level=logging.INFO)

  comic = range(1, 3)
  
  with concurrent.futures.ThreadPoolExecutor() as executor:
    executor.map(thread_job, comic)

if __name__ == "__main__":
    main()