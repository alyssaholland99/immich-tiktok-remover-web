from flask import Flask, jsonify, request
import subprocess, os, validators, time, re, requests

from helpers import *

app = Flask(__name__)

@app.route('/status', methods=['GET'])
def get_status():
    return 'up', 200

@app.route('/remove', methods=['POST'])
def remove_tiktoks():

    payload = request.get_json()
    immich_url = payload['immich_url']
    immich_api_key = payload['immich_api_key']
    repeat = payload['repeat']

    if immich_url[-1] != "/":
        immich_url += "/"

    if not key_valid(immich_api_key):
        return 'Not a valid API key', 400

    filename = "{}_{}".format(immich_url, immich_api_key[:10])

    if too_many_requests(filename):
        return 'You can only use this service once every 3 hours', 429

    if not validators.url(immich_url):
        return 'Not a valid URL', 400
    
    if not server_connection(immich_url, immich_api_key):
        return 'Invalid server details, please check your input', 400
    
    if cache_file_exists(filename):
        os.system('helm uninstall {} -n immich-tiktok-remover-api'.format(("immich-tiktok-remover-" + get_hash(filename))[:53]))
    
    if repeat:
        os.system('helm upgrade --set IMMICH_URL={} --set IMMICH_API={} --set fullnameOverride={} --set SECRET_NAME={} --set image.tag=stable -n immich-tiktok-remover-api -i {} ../immich-tiktok-remover/'.format(immich_url, immich_api_key, "immich-tiktok-remover-" + get_hash(filename), "immich-tiktok-remover-" + get_hash(filename), ("immich-tiktok-remover-" + get_hash(filename))[:53]))
    else:
        os.system('helm upgrade --set IMMICH_URL={} --set IMMICH_API={} --set fullnameOverride={} --set SECRET_NAME={} -n immich-tiktok-remover-api -i {} ../immich-tiktok-remover/'.format(immich_url, immich_api_key, "immich-tiktok-remover-" + get_hash(filename), "immich-tiktok-remover-" + get_hash(filename), ("immich-tiktok-remover-" + get_hash(filename))[:53]))

    return 'Starting process...\nConnected to your Immich instance.\nContainer Started.\nKeep an eye on your Immich instance, the tool is currently running.', 200

@app.route('/stop', methods=['POST'])
def remove_deployment():

    payload = request.get_json()
    immich_url = payload['immich_url']
    immich_api_key = payload['immich_api_key']

    if immich_url[-1] != "/":
        immich_url += "/"

    if not key_valid(immich_api_key):
        return 'Not a valid API key', 400

    filename = "{}_{}".format(immich_url, immich_api_key[:10])

    if not validators.url(immich_url):
        return 'Not a valid URL', 400
    
    if cache_file_exists(filename):
        os.system('helm uninstall {} -n immich-tiktok-remover-api'.format(("immich-tiktok-remover-" + get_hash(filename))[:53]))
        return 'Stopping tool', 200
    else:
        return 'No job with these parameters exist', 404


if __name__ == '__main__':
    app.run()