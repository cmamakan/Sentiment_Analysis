from flask import Flask, render_template, url_for
from pymongo import MongoClient

# Instance de l'application Flask
app = Flask(__name__)

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
MONGODB_DATABASE = 'twitter_analysis'
MONGODB_COLLECTION = 'data'

# Connexion à MongoDB
client = MongoClient('mongodb://localhost:27017')
db = client["twitter_analysis"]
collection = db["data"]

@app.route('/')
def index():
    cursor = collection.find({}, {'_id': 0, 'sentiment_class': 1})
    data = list(cursor)

    return render_template('index.html', data=data)

if __name__ == "__main__":
    app.run(debug=True) 

