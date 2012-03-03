import collections

# http://gsoc.cat-v.org/people/mjl/blog/2007/08/06/1_Rabin_fingerprints/

def blocklist(stream, limit,
        prime=269,
        window_size=31,
        block_size=16*1024,
        min_block_size=2*1024,
        max_block_size=64*1024
        ):
    blocks = []
    window = collections.deque([0 for i in range(window_size)], maxlen=window_size)
    csum = 1
    unique = 0 # TODO
    prime_pow = prime**window_size
    csum_mod = 2**32

    curr_block_size = 0

    for i in range(limit):
        c = stream.read(1)[0]
        pc = window.popleft()
        window.append(c)
        curr_block_size += 1

        csum = (block_size + prime*csum + c - pc * prime_pow)
        csum = abs(csum) % block_size

        if curr_block_size >= max_block_size or csum == block_size - 1:
            if curr_block_size >= min_block_size:
                blocks.append(i)
                curr_block_size = 0

        if i % (1024*1024) == 0:
            print("{} MB processed".format(i/(1024*1024)))

    if blocks[len(blocks)-1] != limit:
        blocks.append(limit)

    return blocks
