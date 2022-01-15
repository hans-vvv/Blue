from database.database import db


users_userroles = db.Table(
    'users_userroles', db.Model.metadata,
    db.Column('user_id', db.ForeignKey('users.id'), primary_key=True, index=True),
    db.Column('userrole_id', db.ForeignKey('userroles.id'), primary_key=True, index=True),
)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String, unique=True)
    userroles = db.relationship('UserRole', secondary=users_userroles, back_populates='users')
    password = db.Column(db.String)

    def __repr__(self):
        return "<User(id={})>".format(self.id)


class UserRole(db.Model):
    __tablename__ = 'userroles'

    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String)
    users = db.relationship('User', secondary=users_userroles, back_populates='userroles')


