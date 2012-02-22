import collections

# http://gsoc.cat-v.org/people/mjl/blog/2007/08/06/1_Rabin_fingerprints/

def blocklist(stream, limit, prime=269, window_size=31, block_size=4096):
    blocks = []
    window = collections.deque([0 for i in range(window_size)], maxlen=window_size)
    csum = 1
    unique = 0 # TODO
    prime_pow = prime**window_size
    csum_mod = 2**32

    for i in range(limit):
        c = stream.read(1)[0]

        csum *= prime
        csum %= csum_mod
        csum += c
        csum %= csum_mod

        pc = window.popleft()
        window.append(c)

        csum -= pc * prime_pow
        csum %= csum_mod
        if abs(csum) % block_size == unique:
            blocks.append(i)
        if i % (1024*1024) == 0:
            print("{} MB processed".format(i/(1024*1024)))

    return blocks
