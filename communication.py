import requests
from settings import bootstrap_ip, bootstrap_port
import jsonpickle as jp

def unicast_bootstrap(api, message):
    return unicast((bootstrap_ip, bootstrap_port), api, message)

def unicast(host, api, message):
    ip, port = host
    message = jp.encode(message)
    response = requests.post('http://{}:{}/{}'.format(ip, port, api), message)
    return response.json()


def broadcast(hosts, api, message):
    responses = []
    timeouts = []
    message = jp.encode(message, keys=True)

    for ip, port in hosts:
        try:
            response = requests.post('http://{}:{}/{}'.format(ip, port, api), message)
            responses.append(jp.decode(response.text, keys = True))
            # print(jp.decode(response.text, keys = True))

        except requests.exceptions.Timeout:
            timeouts.append((ip, port))
    
    return responses
