from collections import OrderedDict
import utils
import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import json
import requests
from flask import Flask, jsonify, request, render_template


class Transaction:

    def __init__(self, sender_address, recipient_address, amount, total):
        self.sender_address = sender_address
        self.receiver_address = recipient_address
        self.amount = amount
        self.transaction_inputs = None
        self.transaction_id = self.__myHash__()
        output_to_recipient = {"id": self.transaction_id, "recipient": recipient_address, "amount": amount}
        output_to_self = {"id": self.transaction_id, "recipient": sender_address, "amount": total - amount}

        self.transaction_outputs = [output_to_recipient, output_to_self]


    def __myHash__(self):
        hashString = "%s%s%s" % (self.sender_address, self.receiver_address, self.amount)
        return SHA.new(hashString.encode())

    # def to_dict(self):
        

    def sign_transaction(self, private_key):
        """
        Sign transaction with private key
        """
        self.signature = PKCS1_v1_5.new(private_key).sign(self.transaction_id)
    
    def verify_transaction(self):
        h = self.__myHash__()
        return PKCS1_v1_5.new(self.sender_address).verify(h, self.signature)

    # def tojson(self):
    #     return json.dumps({
    #         'sender_address':self.sender_address,
    #         'receiver_address':self.receiver_address,
    #         'amount':self.amount,
    #         'transaction_inputs':self.transaction_inputs,
    #         'transaction_outputs':self.transaction_outputs,
    #         'signature':self.signature            
    #         })


       