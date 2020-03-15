from collections import OrderedDict

import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA

import requests
from flask import Flask, jsonify, request, render_template


class Transaction:

    def __init__(self, sender_address, sender_private_key, recipient_address, value, total):
        self.sender_address = sender_address
        self.receiver_address = recipient_address
        self.amount = value
        self.transaction_inputs = None

        output_to_recipient = {"id": self.transaction_id, "recipient": recipient_address, "amount": value}
        output_to_self = {"id": self.transaction_id, "recipient": sender_address, "amount": total - value}

        self.transaction_outputs = [output_to_recipient, output_to_self]

        self.transaction_id = __myHash__()

    def __myHash__(self):
        hashString = "%s%s%s" % (self.sender_address, self.receiver_address, self.amount) 
        return SHA.new(hashString.encode())

    # def to_dict(self):
        

    def sign_transaction(self, private_key):
        """
        Sign transaction with private key
        """
        key = RSA.importKey(private_key)
        signer = PKCS1_v1_5.new(key)
        signature = signer.sign(self.transaction_id)
        return signature


       