from QLNS.models import User, Category, Book, User, Bill, BillDetails
from flask_login import current_user
from QLNS import db
import hashlib


def load_categories():
    return Category.query.all()


def load_book(category_id=None, kw=None):
    query = Book.query.filter(Book.active.__eq__(True))

    if category_id:
        query = query.filter(Book.category_id.__eq__(category_id))

    if kw:
        query = query.filter(Book.name.contains(kw))

    return query.all()


def get_book_by_id(book_id):
    return Book.query.get(book_id)


def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    return User.query.filter(User.username.__eq__(username.strip()),
                             User.password.__eq__(password)).first()


def register(name, username, password, avatar):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u = User(name=name, username=username.strip(), password=password, avatar=avatar)
    db.session.add(u)
    db.session.commit()


def get_user_by_id(user_id):
    return User.query.get(user_id)


def add_bill(cart):
    if cart:
        r = Bill(user=current_user)
        db.session.add(r)

        for c in cart.values():
            d = BillDetails(quantity=c['quantity'], price=c['price'],
                               bill=r, book_id=c['id'])
            db.session.add(d)

        try:
            db.session.commit()
        except:
            return False
        else:
            return True