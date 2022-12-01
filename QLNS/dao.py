from QLNS.models import User, Category, Book, User, Bill, BillDetails
from flask_login import current_user
from sqlalchemy import func
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


def count_book_by_cate():
    return db.session.query(Category.id, Category.name, func.count(Book.id))\
                     .join(Book, Book.category_id.__eq__(Category.id), isouter=True)\
                     .group_by(Category.id).all()


def stats_revenue(kw=None, from_date=None, to_date=None):
    query = db.session.query(Book.id, Book.name, func.sum(BillDetails.quantity*BillDetails.price))\
                      .join(BillDetails, BillDetails.book_id.__eq__(Book.id))\
                      .join(Bill, Bill.id.__eq__(BillDetails.bill_id))

    if kw:
        query = query.filter(Book.name.contains(kw))

    if from_date:
        query = query.filter(Bill.created_date.__ge__(from_date))

    if to_date:
        query = query.filter(Bill.created_date.__le__(to_date))

    return query.group_by(Book.id).order_by(Book.name).all()


if __name__ == '__main__':
    from QLNS import app
    with app.app_context():
        print(stats_revenue())