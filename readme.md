1. Buildup a hash table of the files, where the filesize is the key.
2. For files with the same size, create a hash table with the hash of their first 1024 bytes; non-colliding elements are unique
3. For files with the same hash on the first 1k bytes, calculate the hash on the full contents - files with matching ones are NOT unique.