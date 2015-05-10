#! /usr/bin/env python
# coding=utf-8

from flask import Flask, render_template
import json
import base64
import requests


def login(client_id, client_secret, project_key):
    encoded = base64.b64encode("%s:%s" % (client_id, client_secret))
    headers = {'Authorization': "Basic %s" % encoded,
               'Content-Type' : 'application/x-www-form-urlencoded' }
    body = "grant_type=client_credentials&scope=manage_project:%s" % project_key
    url = "https://auth.sphere.io/oauth/token"
    r = requests.post(url, data=body, headers=headers)
    if r.status_code is 200:
        return r.json()
    else:
        raise Exception("Failed to get an access token. Are you sure you have added them to config.py?")

def get_address(street):
    data = requests.get('http://drinkbringer.de/?term='+street).text
    if data == 'NaN':
        return []
    json_data = []
    for line in data.split('\n'):
        json_data.append(line.split('\t'))
    return json_data[:-1]

def validate(auth, project_key):
    headers = { "Authorization" : "Bearer %s" % auth["access_token"] }
    url = "https://api.sphere.io/%s/customers" % project_key
    r = requests.get(url, headers=headers)
    custommers = r.json()
    res = []
    for custommer in custommers["results"]:
        for i, address in enumerate(custommer['addresses']):
            street = address['streetName'].lower()
            data = get_address(street)
            valid = False
            for line in data:
                if address['postalCode'] == line[1] and address['city'] == line[2]:
                    valid = True
            res.append({
                'name': '%s %s'%(custommer['firstName'], custommer['lastName']),
                'id': custommer['id'],
                'address_no': i + 1,
                'is_valid': valid,
                'color': 'green' if valid else 'red',
            })
    return res

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/<client_id>/<client_secret>/<project_key>/')
def api(client_id, client_secret, project_key):
    auth = login(str(client_id), str(client_secret), str(project_key))
    return json.dumps(validate(auth, str(project_key)))

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
