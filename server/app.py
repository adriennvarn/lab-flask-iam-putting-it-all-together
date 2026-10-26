#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe, UserSchema, RecipeSchema


class Signup(Resource):
    def post(self):
        json = request.get_json()

        username = json.get("username")
        password = json.get("password")
        bio = json.get("bio")
        image_url = json.get("image_url")

        if username and password:
            user = User(username=username, bio=bio, image_url=image_url)
            user.password_hash = password

        try:
            db.session.add(user)
            db.session.commit()
            session["user_id"] = user.id
            return UserSchema().dump(user), 201
        except:
            return {"error": "422 Unprocessable Entity"}, 422


class CheckSession(Resource):
    def get(self):
        if session.get("user_id"):
            user = User.query.filter(User.id == session["user_id"]).first()
            return UserSchema().dump(user), 200
        else:
            return {"error": "401 Unauthorized"}, 401


class Login(Resource):
    def post(self):
        json = request.get_json()
        
        username = json.get("username")
        password = json.get("password")
        
        user = User.query.filter(User.username == username).first()
        if user and user.authenticate(password):
            session["user_id"] = user.id
            return UserSchema().dump(user), 200
        else:
            return {"error": "Invalid login"}, 401


class Logout(Resource):
    def delete(self):
        if session.get("user_id"):
            session["user_id"] = None
            return {}, 204
        else:
            return {"error": "Not logged in"}, 401


class RecipeIndex(Resource):
    def get(self):
        if session.get("user_id"):
            return [RecipeSchema().dump(recipe) for recipe in Recipe.query.all()], 200
        else:
            return {"error": "You must be logged in to view this page."}, 401
    
    def post(self):
        if session.get("user_id"):
            json = request.get_json()
            
            user = User.query.filter(User.id == session["user_id"]).first()
            
            try:
                recipe = Recipe(title=json["title"], instructions=json["instructions"], minutes_to_complete=json["minutes_to_complete"], user=user)
                db.session.add(recipe)
                db.session.commit()
                return RecipeSchema().dump(recipe), 201
            except Exception:
                return {"error": "422 Unprocessable Entity"}, 422
            
        else:
            return {"error": "You must be logged in to add recipes."}, 401


api.add_resource(Signup, "/signup", endpoint="signup")
api.add_resource(CheckSession, "/check_session", endpoint="check_session")
api.add_resource(Login, "/login", endpoint="login")
api.add_resource(Logout, "/logout", endpoint="logout")
api.add_resource(RecipeIndex, "/recipes", endpoint="recipes")


if __name__ == "__main__":
    app.run(port=5555, debug=True)
