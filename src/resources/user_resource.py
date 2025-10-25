from flask import request
from flask_restx import Resource, Namespace, fields
from bson import ObjectId
import json
from ..models import collection as db
from ..serializers.user_serializer import serialize_single_user, serialize_users

user = Namespace("users", description="Namespace for the users")

user_json = user.model("User", 
    {
        "first_name": fields.String(required=True, description="User's first name"),
        "last_name": fields.String(required=True, description="User's last name"),
        "email": fields.String(required=True, description="User's email address"),
    }
)

@user.route("/")
class UserList(Resource):
    """Resource to get user data in the database that was saved"""
    def get(self):
        """Method to get the saved user data in the database to read and user""" 
        try:
            users = db.find({})
            serialized_users = serialize_users(users)
            return {
                "message": "Users fetched successfully", 
                "users": serialized_users
            }, 200
        except Exception as e:
            return {
                "message": f"Error fetching users: {str(e)}"
            }, 500
                
    @user.expect(user_json)                
    def post(self):
        """Method to create register of the user in the database with the provided data"""
        try:
            # Get JSON data from request
            data = request.get_json()
            
            if not data:
                return {"message": "No data provided"}, 400
            
            # Validate required fields
            required_fields = ['first_name', 'last_name', 'email']
            for field in required_fields:
                if field not in data or not data[field]:
                    return {"message": f"Missing required field: {field}"}, 400
            
            # Check if email already exists
            existing_user = db.find_one({"email": data['email']})
            if existing_user:
                return {"message": "User with this email already exists"}, 409
            
            # Insert new user
            result = db.insert_one(data)
            
            # Find the newly created user using the inserted ID
            new_user = db.find_one({"_id": result.inserted_id})
            
            if new_user:
                serialized_user = serialize_single_user(new_user)
                return {
                    "message": "User created successfully",
                    "user": serialized_user
                }, 201
            else:
                return {"message": "User created but could not be retrieved"}, 500
                
        except Exception as e:
            return {
                "message": f"Error creating user: {str(e)}"
            }, 500