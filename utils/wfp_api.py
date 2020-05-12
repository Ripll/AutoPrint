#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import time
from utils.wfp_config import M_LOGIN, M_KEY, SIGNATURE_FIELDS, TransactionType
from config import ip, WEBHOOK_PORT, bot
from random import choice
import string
import json
import hashlib
import hmac
from functools import reduce


async def get_invoice(chat_id, task_id, amount):
    url = 'https://api.wayforpay.com/api'
    random = ''.join([choice(string.ascii_letters
                      + string.digits) for n in range(10)])
    headers = {"Content-Type": "multipart/form-data;"}
    if int(amount) == float(amount):
        amount = int(amount)
    else:
        amount = float(amount)
    params = {
        "transactionType": "CREATE_INVOICE",
        "merchantAccount": M_LOGIN,
        "merchantAuthType": "SimpleSignature",
        "merchantDomainName": "https://t.me/{}".format((await bot.get_me()).username),
        "apiVersion": 1,
        "serviceUrl": "https://{}:{}/wfp".format(ip, WEBHOOK_PORT),
        "language": "ua",
        "orderReference": "{}_{}_{}".format(chat_id, task_id, random),
        "orderDate": int(time.time()),
        "amount": amount,
        "currency": "UAH",
        "productName": [f"Оплата рахунку {task_id}"],
        "productPrice": [1],
        "productCount": [1],
    }

    params["merchantSignature"] = generate_signature(M_KEY,
                                                     [params[i] for i in params if i in SIGNATURE_FIELDS[TransactionType.CREATE_INVOICE]])

    x = requests.post(url, json=params, headers=headers, verify=False)
    print(x.json())
    return x.json()['invoiceUrl']


def gen_answer(data):
    params = {
         "orderReference": data["orderReference"],
         "status": "accept",
         "time": int(time.time()),
    }
    params["signature"] = generate_signature(M_KEY,
                                            [params[i] for i in params if i in SIGNATURE_FIELDS[TransactionType.WEBHOOK]])
    return json.dumps(params)


def generate_signature(merchant_key, fields):
    # flatten fields
    fields = reduce(lambda x, y: x + (list(y) if isinstance(y, (list, tuple)) else [y]), fields, [])
    signature_str = ';'.join(map(str, fields))
    return hmac.new(merchant_key.encode(), signature_str.encode(), hashlib.md5).hexdigest()