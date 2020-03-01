import os
from tqdm import tqdm


def split_file(input_file_path: str, max_size: int = 1e+7):
    """
    Splits file into multiple chunks of specified size.
    """
    max_size = int(max_size)
    in_f = open(input_file_path, 'rb')
    chunk = in_f.read(max_size)
    input_file_path = input_file_path.replace('/', '_')

    try:
        os.mkdir('Chunks_for_{og_file}/'.format(og_file=input_file_path))
    except:
        pass

    i = 0
    while chunk:  # while chunk is not empty
        with open('Chunks_for_{og_file}/{i}.chunk'.format(i=i, og_file=input_file_path), 'wb') as out_f:
            out_f.write(chunk)
        chunk = in_f.read(max_size)
        i += 1

    in_f.close()


def stitch_file(folder_path: str, out_path: str):
    """
    Stitches the chunks found in the specified folder together and writes them as the file specified in out_path.
    Assumes that chunks are named {i}.chunk sequentially, just like output from split_file().
    """
    with open(out_path, 'wb') as out_f:
        list_of_chunk_files = []
        i = 0
        while os.path.exists(folder_path + '{}.chunk'.format(i)):
            list_of_chunk_files.append(folder_path + '{}.chunk'.format(i))
            i += 1
        print("Found {} chunk files.".format(len(list_of_chunk_files)))

        for chunk_file_name in tqdm(list_of_chunk_files):
            with open(chunk_file_name, 'rb') as in_f:
                chunk = in_f.read()
                out_f.write(chunk)
