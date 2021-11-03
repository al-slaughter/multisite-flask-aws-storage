import os
from flask import Flask, render_template, request, redirect, send_file
from s3_functions import list_files, upload_file, show_image, create_folder
from werkzeug.utils import secure_filename
import jwt
import requests
import base64
import json


app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
BUCKET = "dev-finalproject-img-mgr20211101145336209100000001"
region = "us-west-2"

@app.route("/")
def home():
    contents = list_files(BUCKET)
    print(contents)
    return render_template('index.html')


@app.route("/pics")
def list():
    # Step 1: Get the key id from JWT headers (the kid field)
    encoded_jwt = request.headers.get('x-amzn-oidc-data')
    jwt_headers = encoded_jwt.split('.')[0]
    decoded_jwt_headers = base64.b64decode(jwt_headers)
    decoded_jwt_headers = decoded_jwt_headers.decode("utf-8")
    decoded_json = json.loads(decoded_jwt_headers)
    kid = decoded_json['kid']
    # Step 2: Get the public key from regional endpoint
    url = 'https://public-keys.auth.elb.' + region + '.amazonaws.com/' + kid
    req = requests.get(url)
    pub_key = req.text
    # Step 3: Get the payload
    payload = jwt.decode(encoded_jwt, pub_key, algorithms=['ES256'])
    user = payload['username']
    contents = show_image(BUCKET + "/" + user)
    return render_template('collection.html', contents=contents)


@app.route("/upload", methods=['POST'])
def upload():
    if request.method == "POST":
        f = request.files['file']
        # Step 1: Get the key id from JWT headers (the kid field)
        encoded_jwt = request.headers.get('x-amzn-oidc-data')
        jwt_headers = encoded_jwt.split('.')[0]
        decoded_jwt_headers = base64.b64decode(jwt_headers)
        decoded_jwt_headers = decoded_jwt_headers.decode("utf-8")
        decoded_json = json.loads(decoded_jwt_headers)
        kid = decoded_json['kid']
        # Step 2: Get the public key from regional endpoint
        url = 'https://public-keys.auth.elb.' + region + '.amazonaws.com/' + kid
        req = requests.get(url)
        pub_key = req.text
        # Step 3: Get the payload
        payload = jwt.decode(encoded_jwt, pub_key, algorithms=['ES256'])
        user = payload['username']
        upload = "uploads/" + f"{f.filename}"
        folder = BUCKET + "/" + user)
        create_folder(user, BUCKET)
        f.save(os.path.join(UPLOAD_FOLDER, secure_filename(f.filename)))
        upload_file(upload, folder)
        return redirect("/")


if __name__ == '__main__':
    app.run(debug=True)
