import os
import hashlib


def chunk_reader(fobj, chunk_size=1024):
    """Generator that reads a file in chunks of bytes"""
    while True:
        chunk = fobj.read(chunk_size)
        if not chunk:
            return
        yield chunk


def get_hash(filename, first_chunk_only=False, hash_method=hashlib.sha1):
    hash_obj = hash_method()
    file_object = open(filename, 'rb')
    if first_chunk_only:
        hash_obj.update(file_object.read(1024))
    else:
        for chunk in chunk_reader(file_object):
            hash_obj.update(chunk)
    hashed = hash_obj.digest()
    file_object.close()
    return hashed


def check_for_duplicates(directory, sending_file_path, sending_file_name):
    hashes_by_size = {}
    hashes_on_1k = {}
    hashes_full = {}
    sending_file_size = os.path.getsize(sending_file_path)
    hashes_by_size.update({sending_file_size: [sending_file_path]})

    for filename in os.listdir(directory):
        if filename == sending_file_name:
            print(f"Duplicate found:\n"
                  f"{filename}  ==  {sending_file_name}")
            print(f"\"{sending_file_name}\" not copied!\n"
                  f"ERROR: File with the same name already exists! Please rename the file and try again.")
            break
        full_path = os.path.join(directory, filename)
        # if the target is a symlink (soft one), this will dereference it -
        # change the value to the actual target file
        full_path = os.path.realpath(full_path)
        try:
            file_size = os.path.getsize(full_path)
        except (OSError,):
            # not accessible (permissions, etc) - pass on
            continue

        duplicate = hashes_by_size.get(file_size)
        if duplicate:
            hashes_by_size[file_size].append(full_path)
        else:
            hashes_by_size[file_size] = []  # create the list for this file size
            hashes_by_size[file_size].append(full_path)

    # For all files with the same file size, get their hash on the 1st 1024 bytes
    for __, files in hashes_by_size.items():
        if len(files) < 2:
            continue  # this file size is unique, no need to spend cpy cycles on it

        for filename in files:
            try:
                small_hash = get_hash(filename, first_chunk_only=True)
            except (OSError,):
                # the file access might've changed till the exec point got here
                continue

            duplicate = hashes_on_1k.get(small_hash)
            if duplicate:
                hashes_on_1k[small_hash].append(filename)
            else:
                hashes_on_1k[small_hash] = []  # create the list for this 1k hash
                hashes_on_1k[small_hash].append(filename)

    # For all files with the hash on the 1st 1024 bytes, get their hash on the full file - collisions will be duplicates
    for __, files in hashes_on_1k.items():
        if len(files) < 2:
            continue  # this hash of fist 1k file bytes is unique, no need to spend cpy cycles on it

        for filename in files:
            try:
                full_hash = get_hash(filename, first_chunk_only=False)
            except (OSError,):
                # the file access might've changed till the exec point got here
                continue

            duplicate = hashes_full.get(full_hash)
            if duplicate:
                print(f"Duplicate found:\n"
                      f"{filename}  ==  {duplicate[2:]}")
                print(f"\"{duplicate[2:]}\" not copied!\n"
                      f"ERROR: File already exists!")
            else:
                hashes_full[full_hash] = filename


if __name__ == '__main__':
    __location__ = "ENTER PATH TO TARGET DIRECTORY HERE"
    __test_file_location__ = "ENTER THE LOCATION OF THE TEST FILE HERE"
    sending_file_name = "ENTER THE NAME OF THE FILE YOU WANT TO SEND HERE"
    sending_file_path = os.path.join(__test_file_location__, sending_file_name)

    check_for_duplicates(__location__, sending_file_path, sending_file_name)
