from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_celery import Celery

app = Flask(__name__)
CORS(app)


@app.route('/submit', methods=['POST'])
def submit_data():
    data = request.get_json()  # Retrieve the JSON data from the request
    # test.insert("practice", "flight", list(data.keys()), list(data.values()))
    return jsonify(data), 201

if __name__ == '__main__':
    app.run(port=5002)



