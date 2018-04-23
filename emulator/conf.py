
import math
from fte.encrypter import Encrypter

def inv_char_calc(output):
    return int(output*math.log(divisions)/math.log(size_of_char)) -1

size_of_char = 0x100
divisions = 15
URI_length = 500

wrapped_length = URI_length + 18

frag_ciphertext_length = inv_char_calc(URI_length)
frag_plaintext_padded_length = frag_ciphertext_length - Encrypter._CTXT_EXPANSION
frag_plaintext_length = frag_plaintext_padded_length - 1 # leave at least one byte to pad
