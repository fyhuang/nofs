import collections

# http://gsoc.cat-v.org/people/mjl/blog/2007/08/06/1_Rabin_fingerprints/

def blocklist(data, prime=139, window_size=31, block_size=4096):
    blocks = []
    window = collections.deque([0 for i in range(window_size)], maxlen=window_size)
    csum = 1
    unique = 0 # TODO
    prime_pow = prime**window_size
    csum_mod = 2**16

    for i,c in enumerate(data):
        csum *= prime
        csum %= csum_mod
        csum += c
        csum %= csum_mod

        pc = window.popleft()
        window.append(c)

        csum -= pc * prime_pow
        csum %= csum_mod
        if csum % block_size == unique:
            blocks.append(i)
        if i % (1024*1024) == 0:
            print("{} MB processed".format(i/(1024*1024)))

    return blocks

with open('test.iso', 'rb') as f:
    data = f.read(32 * 1024 * 1024)
    blocks = blocklist(data)
    print(blocks)
    print(len(blocks))
