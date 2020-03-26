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
import jsonpickle as jp

class Transaction:

    def __init__(self, sender_address, recipient_address, amount, total, transaction_inputs):
        self.sender_address = sender_address
        self.receiver_address = recipient_address
        self.amount = amount
        self.transaction_inputs = transaction_inputs
        self.transaction_id = str(self.__myHash__().hexdigest())
        output_to_recipient = {"id": self.transaction_id, "recipient": recipient_address, "amount": amount}
        output_to_self = {"id": self.transaction_id, "recipient": sender_address, "amount": total - amount}

        self.transaction_outputs = [output_to_recipient, output_to_self]


    def __myHash__(self):
        hashString = jp.encode((self.sender_address, self.receiver_address, self.amount, self.transaction_inputs))
        return SHA.new(hashString.encode())

    def sign_transaction(self, private_key):
        """
        Sign transaction with private key
        """
        self.signature = PKCS1_v1_5.new(private_key).sign(self.__myHash__())
    
    def verify_transaction(self):
        h = self.__myHash__()
        return PKCS1_v1_5.new(self.sender_address).verify(h, self.signature)

    def stringify(self, node):
	    return '({}, {}, {})'.format(node.address_to_host(self.sender_address), node.address_to_host(self.receiver_address), self.amount)

    def __hash__(self):
        return self.transaction_id

