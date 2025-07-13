from flask import Flask, render_template, request
import requests

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    response = None
    if request.method == 'POST':
        immich_url = request.form.get('immich_url')
        immich_api = request.form.get('immich_api')
        repeat = request.form.get('repeat')
        # Send a POST request to a placeholder API
        payload = {'immich_url': immich_url, 'immich_api_key': immich_api, 'repeat': repeat}
        response = requests.post('http://localhost:5000/remove', json=payload)
        return render_template('index.html', api_response=response.text, response_code=response.status_code)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
