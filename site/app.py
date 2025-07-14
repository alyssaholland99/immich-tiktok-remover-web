from flask import Flask, render_template, request
import requests

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    response = None
    container_id = ""
    if request.method == 'POST':
        immich_url = request.form.get('immich_url')
        immich_api = request.form.get('immich_api')
        repeat = request.form.get('repeat')
        # Send a POST request to a placeholder API
        payload = {'immich_url': immich_url, 'immich_api_key': immich_api, 'repeat': repeat}
        response = requests.post('https://api.immich-tiktok-remover.co.uk//remove', json=payload)
        if "Container ID: " in response.text:
            container_id = str(response.text.split("Container ID: ")[1])
        return render_template('index.html', api_response=response.text, response_code=response.status_code, container_id=container_id)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True,  port=5001)
