from app.database import SessionLocal
from app.models import User

db = SessionLocal()

users = db.query(User).all()
print(f'Found {len(users)} users')
for user in users:
    print(f'ID: {user.id}')
    print(f'Username: {user.username}')
    print(f'Email: {user.email}')
    print(f'-'*30)

db.close()
