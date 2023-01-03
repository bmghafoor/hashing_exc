from app import app
from models import db, User

with app.app_context():
    db.drop_all()
    db.create_all()

    User.query.delete()

    u = User.register('bmghafoor','password123','bmghafoor@gmail.com','Binyameen','Ghafoor')


    db.session.add(u)
    db.session.commit()

