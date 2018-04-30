#!/usr/bin/python3
import logging, pydicom, hashlib, os, shutil, sys, filecmp
from glob import iglob

base = '/datasets'
heap = '/input'

def content_hash(filename):
    hash_sha1 = hashlib.sha1()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha1.update(chunk)
    return hash_sha1.hexdigest()

def move_file(path):
    file = pydicom.read_file(path)
    siid = file.SeriesInstanceUID
    hash = hashlib.sha1(siid.encode('utf-8')).hexdigest().lower()
    root = os.path.join(base, hash[0], hash[1], hash[2], hash[3], hash)
    data = os.path.join(root, 'data')
    meta = os.path.join(root, 'meta')
    soid = file.SOPInstanceUID
    name = '{}.dcm'.format(soid)
    full = os.path.join(data, name)
    if not os.path.exists(root):
        os.makedirs(root, exist_ok=True) # Multiple instances may run at the same time
    if os.path.isfile(full):
        if content_hash(full) != content_hash(path):
            logging.error("File with different contents already exists at {}".format(full))
        os.remove(path)
        logging.warning(f"{path} deleted")
    else:
        os.makedirs(meta, exist_ok=True)
        os.makedirs(data, exist_ok=True)
        shutil.move(path, full)
    return True
    
for filename in iglob(os.path.join(heap, "*")):
    print(filename)
#    path = os.path.join(heap, filename)
#    logging.debug("Handling file {}".format(path))
#    try:
#        move_file(path)
#    except:
#        logging.error("Could not handle file {}".format(path))
