import hashlib
import filetype


def get_mime_type(file):
    kind = filetype.guess(file)
    return kind.mime if kind else 'application/octet-stream'


def get_md5_hash(file):
    hash_md5 = hashlib.md5()
    for chunk in iter(lambda: file.read(4096), b""):
        hash_md5.update(chunk)
    file.seek(0)
    return hash_md5.hexdigest()
