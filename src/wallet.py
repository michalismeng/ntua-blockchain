import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4


# def generate_wallet():
# 	private_key = RSA.generate(2048)
# 	public_key = private_key.publickey()
# 	return (private_key, public_key)


class wallet:

	def __init__(self):
		self.private_key = RSA.generate(2048)
		self.address = self.private_key.publickey()

		#self.transactions