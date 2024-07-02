import logging
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo, ObjectId
from bson.json_util import dumps
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.DEBUG)  # Set logging level to DEBUG

# Authentication setup
auth = HTTPBasicAuth()
users = {
    "admin": generate_password_hash("password123")
}

# MongoDB configuration
app.config["MONGO_URI"] = os.environ.get('MONGO_URI', 'mongodb://mongo:27017/robo')
mongo = PyMongo(app)

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username

# Route for adding a lead
@app.route('/leads', methods=['POST'])
@auth.login_required
def add_lead():
    try:
        data = request.get_json(force=True)
        name = data['name']
        email = data['email']
        phone = data['phone']
        lead_id = mongo.db.leads.insert_one({'name': name, 'email': email, 'phone': phone})
        return jsonify({'message': 'Lead added successfully', 'lead_id': str(lead_id)})
    except Exception as e:
        logging.error(f"Error adding lead: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/leads/<lead_id>', methods=['PUT'])
@auth.login_required
def update_lead(lead_id):
    data = request.get_json(force=True)
    name = data['name']
    email = data['email']
    phone = data['phone']
    result = mongo.db.leads.update_one({'_id': ObjectId(lead_id)}, {'$set': {'name': name, 'email': email, 'phone': phone}})
    return jsonify({'message': 'Lead updated successfully'} if result.modified_count > 0 else {'message': 'Lead not found'})

@app.route('/leads/<lead_id>', methods=['DELETE'])
@auth.login_required
def delete_lead(lead_id):
    result = mongo.db.leads.delete_one({'_id': ObjectId(lead_id)})
    return jsonify({'message': 'Lead deleted successfully'} if result.deleted_count > 0 else {'message': 'Lead not found'})

@app.route('/leads', methods=['GET'])
@auth.login_required
def get_leads():
    leads = mongo.db.leads.find()
    return dumps(leads)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

