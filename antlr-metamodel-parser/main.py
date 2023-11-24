from flask import Flask, jsonify, request
import os
from base.base import inspect_with_llama, inspect_with_langchain
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()
import os

app = Flask(__name__)

openai_key = "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"



CORS(app)


# CORS Headers
@app.after_request
def after_request(response):
    response.headers.add(
        "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
    )
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
    return response




@app.route('/')
def index():
    return jsonify({"Choo Choo": "Welcome to your Flask app 🚅"})


@app.route("/about")
def about():
     return jsonify({"Choo Choo": "Welcome to About 🚅"})


@app.route("/post_json", methods=["POST", "GET"])
async def post_json():
    content_type = request.headers.get("Content-Type")
    if content_type == "application/json":
        json = request.json
        prompt = json["prompt"]
        answer = await inspect_with_langchain(prompt, openai_key)
        return jsonify({"text": answer})
    else:
        return "Content-Type not supported!"



if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
