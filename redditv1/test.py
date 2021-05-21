import libnum
import random
import sys
import hexdump


from Cryptodome.Cipher import AES
from Cryptodome.Util.number import getPrime
from Cryptodome.Random import get_random_bytes


def chunkstring(string, length):
    return (string[0 + i:length + i] for i in range(0, len(string), length))


def generate_keys(prime):
    while True:
        e = random.randint(0, prime - 2)
        if libnum.gcd(e, prime - 1) == 1 and e > 2:
            break
    d = libnum.invmod(e, prime - 1)

    return e, d


def crypt(chunk, key, prime):
    num = 0
    for c in chunk:
        num *= 256
        num += ord(c)
    res = pow(num, key, prime)
    vect = []
    for i in range(0, len(chunk)):
        vect.append(chr(res % 256))
        res = res // 256

    return "".join(reversed(vect))


primebits = 64
msg = "Hello"

if (len(sys.argv) > 1):
    primebits = int(sys.argv[1])
if (len(sys.argv) > 2):
    msg = (sys.argv[2])

FRAGMENT_SIZE = primebits // 8

msg = msg + " " * ((FRAGMENT_SIZE -
                    (len(msg) % FRAGMENT_SIZE)) % FRAGMENT_SIZE)

res = chunkstring(msg, FRAGMENT_SIZE)

PRIME = getPrime(primebits, randfunc=get_random_bytes)

e, d = generate_keys(PRIME)

vect = []
for elem in res:
    enc = str(crypt(elem, e, PRIME))
    vect.append(enc)

enc = "".join(vect)

dec = []
for elem in chunkstring(enc, FRAGMENT_SIZE):
    dec.append(crypt(elem, d, PRIME))

print(f"Msg={msg}")
print(f"PRIME={PRIME}")
print(f"e={e}, d={d}")
print("Encrpyted: " + hexdump.dump(enc.encode()))

print("\nDecrypted: " + "".join(dec))
