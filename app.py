from flask import Flask, request, jsonify
from sqlalchemy import text, create_engine
import mysql.connector

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask("__name__")


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@localhost/FlaskCrud'

db = SQLAlchemy(app)

my_db = mysql.connector.connect(
    host = "localhost",
    user = "root",
    passwd = "password",
    database = "FlaskCrud",
)

my_cursor = my_db.cursor()


engine = create_engine('mysql://root:password@localhost/FlaskCrud')

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50), unique = True)
    date_joined = db.Column(db.Date, default=datetime.utcnow)

    def __init__(self,id,name,email,date_joined):
        self.name = name
        self.email = email
        self.date_joined = date_joined
        self.id = id



with app.app_context():
    db.create_all()
    db.session.commit()


@app.route('/adduser', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        id = data.get('id')
        date_joined = data.get('date')

        query = text("INSERT INTO user (id,name, email,date_joined) VALUES (:id, :name, :email, :date_joined)")
        result = db.session.execute(query, {'id' : id, 'name' : name, 'email' : email, 'date_joined' : date_joined})

        # new_user = User(name=data['name'], email=data['email'], id=data['id'],date_joined=data['date'])
        # db.session.add(new_user)
        
        db.session.commit()
    
        return jsonify({"message": "user added Successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/users", methods=['GET'])
def user_list():
    try:
        
        # result = db.session.query(User.id, User.name, User.email, User.date_joined).all()
        # result = db.session.execute(db.select(User).order_by(User.id)).scalars()
        
        query = text("SELECT * FROM user")
        result = engine.connect().execute(query)
        
        users = [{"id": row.id, "name": row.name, "email": row.email, "date_joined": row.date_joined} for row in result]
        return jsonify(users), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error":str(e)}), 500

@app.route('/deleteUser/<int:id>', methods =['DELETE'])
def del_user(id):
    try:
        result = db.get_or_404(User, id)
        users = {"id": result.id, "name": result.name, "email": result.email, "date_joined": result.date_joined}

        query = text("DELETE FROM user WHERE id = :id")
        db.session.execute(query, {'id' : id})

        # db.session.delete(result)
        db.session.commit()
        return jsonify(users), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error":str(e)}), 500

@app.route("/userUpdate", methods =['PUT'])
def update_user():
    try:
        users = request.get_json()
        # existingUser = db.get_or_404(User,users.get('id'))

        # existingUser.email = users.get('email')
        # existingUser.name = users.get('name')
        # existingUser.date_joined = users.get('date')

        query = text("UPDATE user SET name = :name, date_joined = :date_joined WHERE id = :id")
        
        db.session.execute(query, {'name' : users.get('name') , 'date_joined' : users.get('date') , 'id' : users.get('id')})

        db.session.commit()

        return jsonify({"message" : "User Updated Successfully"})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error":str(e)}), 500


if __name__ == "__main__":
    app.run()
  