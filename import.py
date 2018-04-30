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
    if not "SeriesInstanceUID" in file:
        logging.warning(f"{path} has no SeriesInstanceUID. Skipping.")
        return False
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
        logging.debug(f"Created dataset {root}")
    if os.path.isfile(full):
        if content_hash(full) != content_hash(path):
            logging.error(f"File with different contents already exists at {full}")
        os.remove(path)
        logging.warning(f"{path} deleted")
        return False
    else:
        os.makedirs(meta, exist_ok=True)
        os.makedirs(data, exist_ok=True)
        shutil.move(path, full)
    return True
    
for path in iglob(os.path.join(heap, "*")):
    logging.debug(f"Handling file {path}")
    move_file(path)
