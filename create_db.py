from datetime import datetime
from ext import app, db
from models import Product, Users

products = []




for product in products:
    try:
        product["date"] = datetime.strptime(product["date"], "%d.%m.%y").date()
    except ValueError:
        # If it fails, try another format
        product["date"] = datetime.strptime(product["date"], "%m.%d.%y").date()



admin_user = {
    "username": "admin",
    "password": "admin123!",
    "role": "Admin",
}

with app.app_context():

    db.create_all()

    for product in products:

        existing_product = Product.query.filter_by(name=product["name"]).first()
        if not existing_product:
            new_product = Product(
                name=product["name"],
                title=product["title"],
                platform=product["platform"],
                condition=product["condition"],
                price=product["price"],
                date=product["date"],
                img=product["image"],
                category=product["category"]
            )
            db.session.add(new_product)


    existing_admin = Users.query.filter_by(username=admin_user["username"]).first()
    if not existing_admin:
        new_admin = Users(
            username=admin_user["username"],
            password=admin_user["password"],
            role=admin_user["role"]
        )
        db.session.add(new_admin)
        print("Admin user created successfully.")
    else:
        print("Admin user already exists.")


    db.session.commit()
    print("Database initialized successfully.")


