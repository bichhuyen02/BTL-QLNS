from QLNS.models import User, Category, Book, User, Bill, BillDetails, Comment
from flask_login import current_user
from sqlalchemy import func
from QLNS import db
import hashlib
from sqlalchemy import extract, and_


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


def checkup_username(user_name):
    query = User.query.filter(User.active.__eq__(True))

    if query.filter(User.username.__eq__(user_name)):
        return False
    else:
        return True



def register(name, phone, username, password, avatar):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u = User(name=name, phone=phone, username=username.strip(), password=password, avatar=avatar)
    db.session.add(u)
    db.session.commit()


def get_user_by_id(user_id):
    return User.query.get(user_id)


def checkup_inventory(book_id, quantity):
    query = Book.query.get(book_id)
    if query.inventory.__ge__(quantity):
        return True
    else:
        return False


def add_bill(cart):
    if cart:
        b = Bill(user=current_user)
        db.session.add(b)
        for c in cart.values():
            d = BillDetails(quantity=c['quantity'],
                               price=c['price'],
                               bill=b,
                               book_id=int(c['id']))
            p = Book.query.get(d.book_id)
            p.inventory = p.inventory - d.quantity
            db.session.add(d)
        try:
            db.session.commit()
        except:
            return False
        else:
            return True


def get_bill_id():
    bill = Bill.query.all()
    max = bill[0].id
    for c in bill:
        if max.__lt__(c.id):
            max = c.id
    return Bill.query.get(max)


def count_book_by_cate():
    return db.session.query(Category.id, Category.name, func.count(Book.id))\
            .join(Book, Book.category_id.__eq__(Category.id), isouter=True)\
            .group_by(Category.id).order_by(-Category.name).all()


def stats_revenue_book():
    data = db.session.query(Book.id, Book.name, func.month(Bill.created_date),
                            func.sum(BillDetails.quantity)) \
        .join(Bill) \
        .filter(Bill.id == BillDetails.bill_id) \
        .join(Book) \
        .filter(Book.id == BillDetails.book_id) \
        .group_by(func.month(Bill.created_date), Book.name) \
        .order_by(func.month(Bill.created_date), Book.id)

    return data.all()


def stats_revenue_category():
    data = db.session.query(Category.id, Category.name, func.month(Bill.created_date),
                            func.sum(BillDetails.quantity*BillDetails.price)) \
            .join(Bill).filter(Bill.id == BillDetails.bill_id) \
            .join(Book).filter(Book.id == BillDetails.book_id) \
            .join(Category).filter(Category.id == Book.category_id)\
            .group_by(func.month(Bill.created_date), Category.name) \
            .order_by(func.month(Bill.created_date), Category.id)
    return data.all()


def load_comments(book_id):
    return Comment.query.filter(Comment.book_id.__eq__(book_id)).order_by(-Comment.id).all()


def save_comment(book_id, content):
    c = Comment(content=content, book_id=book_id, user=current_user)
    db.session.add(c)
    db.session.commit()

    return c


# def add_GoodsReceived(book_id, goodsReceived_quantity):
#     b = Book.query.get(book_id)
#     b.inventory = b.inventory + goodsReceived_quantity
#     db.session.commit()


# if __name__ == '__main__':
#     from QLNS import app
#     with app.app_context():
#         print()

