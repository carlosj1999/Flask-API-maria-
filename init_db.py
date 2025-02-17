from api_auto_payment import app, db

# Use the app context to initialize the database
with app.app_context():
    db.create_all()
    print("Database tables created successfully.")
