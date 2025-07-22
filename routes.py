from flask import render_template, redirect, request, session
from forms import ProductForm, RegisterForm, LoginForm
from os import path
from flask_login import login_user, logout_user, current_user, login_required
from uuid import uuid4
from ext import app, db
from models import Product, Users


@app.route("/")
def homepage():
    products = Product.query.limit(8).all()
    return render_template("homepage.html", products=products)


@app.route("/search")
def search():
    name = request.args.get("n", "").strip()
    products = Product.query.filter(Product.name.ilike(f"%{name}%")).all()
    return render_template("homepage.html", products=products, search_term=name)


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    form = ProductForm()
    if form.validate_on_submit():
        file = form.img.data
        filename, filetype = path.splitext(file.filename)
        filename = str(uuid4())
        filepath = path.join(app.root_path, "static", f"{filename}{filetype}")
        file.save(filepath)

        new_product = Product(
            name=form.name.data,
            title=form.title.data,
            price=form.price.data,
            date=form.date.data,
            category=form.category.data,
            img=f"/static/{filename}{filetype}",
        )

        db.session.add(new_product)
        db.session.commit()

        return redirect("/")
    return render_template("upload.html", form=form)


from datetime import datetime


@app.route("/edit_product/<int:product_id>", methods=["GET", "POST"])
@login_required
def edit_product(product_id):
    if current_user.role != "Admin":
        return redirect("/")

    product = Product.query.get_or_404(product_id)
    if isinstance(product.date, str):
        product.date = datetime.strptime(product.date, "%Y-%m-%d").date()

    form = ProductForm(
        name=product.name,
        title=product.title,
        price=product.price,
        date=product.date,
        category=product.category
    )

    if form.validate_on_submit():
        product.name = form.name.data
        product.title = form.title.data
        product.price = form.price.data
        product.date = form.date.data
        product.category = form.category.data

        if form.img.data:
            file = form.img.data
            filename, filetype = path.splitext(file.filename)
            filename = str(uuid4())
            filepath = path.join(app.root_path, "static", f"{filename}{filetype}")
            file.save(filepath)
            product.img = f"/static/{filename}{filetype}"

        db.session.commit()
        return redirect("/")

    return render_template("upload.html", form=form)


@app.route("/delete_product/<int:product_id>")
@login_required
def delete_product(product_id):
    if current_user.role != "Admin":
        return redirect("/")
    product = Product.query.get(product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect("/")


@app.route("/card/<prod_name>")
def card(prod_name):
    found_product = Product.query.filter_by(name=prod_name).first()

    if found_product:
        return render_template("card.html", found_product=found_product)
    return redirect("/")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/gallery")
def gallery():
    products = Product.query.all()
    return render_template("gallery.html", products=products)


@app.route("/search_gallery", methods=["GET"])
def search_gallery():
    category_filter = request.args.get("category", "").strip()
    price_filter = request.args.get("price", "").strip()

    products_query = Product.query

    if category_filter:
        products_query = products_query.filter(Product.category == category_filter)

    if price_filter:
        if price_filter == "low":
            products_query = products_query.filter(Product.price < 200)
        elif price_filter == "medium":
            products_query = products_query.filter(Product.price.between(200, 1000))
        elif price_filter == "high":
            products_query = products_query.filter(Product.price > 1000)

    products = products_query.all()

    return render_template("gallery.html", products=products)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        existing_user = Users.query.filter_by(username=form.username.data).first()
        if existing_user:
            return render_template("register.html", form=form, error="Username already exists")


        if form.username.data.lower() == "admin":
            if form.password.data == "admin123!":
                role = "Admin"
            else:
                return render_template("register.html", form=form, error="Invalid password for Admin")

        else:
            role = "Guest"

        new_user = Users(
            username=form.username.data,
            password=form.password.data,
            role=role
        )
        db.session.add(new_user)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html", form=form)



@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        users = Users.query.filter(Users.username == form.username.data).first()
        if users != None and users.check_password(form.password.data):
            login_user(users, remember=form.remember_me)
            return redirect("/")
      

    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")


@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    if "cart" not in session:
        session["cart"] = []

    item_id = request.form.get("item_id")
    product = Product.query.get(item_id)

    if product:
        item = {
            "id": product.id,
            "name": product.name,
            "price": product.price
        }
        session["cart"].append(item)
        session.modified = True

    return redirect("/cart")


@app.route("/remove_item/<int:item_id>", methods=["POST"])
def remove_item(item_id):
    cart = session.get("cart", [])

    session["cart"] = [item for item in cart if item["id"] != item_id]
    session.modified = True

    return redirect("/cart")


@app.route("/cart")
def cart_page():
    cart = session.get("cart", [])
    total_price = sum(item['price'] for item in cart)
    return render_template("cart.html", cart=cart, total_price=total_price)


@app.route("/clear_cart", methods=["POST"])
def clear_cart():
    session["cart"] = []
    session.modified = True
    return redirect("/cart")