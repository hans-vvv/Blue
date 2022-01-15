from views import db
from models import UserRole, User


db.drop_all()
db.create_all()

userrole = UserRole(name='admin')
user = User(name='Hans', password='Hans')
userrole.users.append(user)
db.session.add(userrole)
db.session.add(user)
userrole = UserRole(name='lcm_user')
user = User(name='Erik', password='Erik')
userrole.users.append(user)
userrole = UserRole(name='lcm_superuser')
db.session.add(userrole)
db.session.add(user)

db.session.commit()
