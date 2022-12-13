from QLNS.models import User, Category, Book, User, Bill, BillDetails, Comment
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


def checkup_username(user_name):
    query = User.query.filter(User.active.__eq__(True))

    if query.filter(User.username.__eq__(user_name)):
        return False
    else:
        return True



def register(name, username, password, avatar):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u = User(name=name, username=username.strip(), password=password, avatar=avatar)
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
        r = Bill(user=current_user)
        db.session.add(r)
        for c in cart.values():
            d = BillDetails(quantity=c['quantity'],
                               price=c['price'],
                               bill=r,
                               book_id=int(c['id']))
            p = Book.query.get(d.book_id)
            p.inventory=p.inventory - d.quantity
            db.session.add(d)
        try:
            db.session.commit()
        except:
            return False
        else:
            return True


def get_bill():
    b = db.session.query(func.max(Bill.id)).first()
    for c in BillDetails.query.filter(BillDetails.bill_id.__eq__(b)).all():
        book = Book.query.get(c.book_id)
        # return book.name
    return b

# def test():
#     data = []
#     for c in BillDetails.query.filter(BillDetails.bill_id.__eq__(2)).all():
#         data = [c.id]
#     return data


def count_book_by_cate():
    return db.session.query(Category.id, Category.name, func.count(Book.id))\
            .join(Book, Book.category_id.__eq__(Category.id), isouter=True)\
            .group_by(Category.id).order_by(-Category.name).all()


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


def get_comments_by_book(book_id):
    return Comment.query.filter(Comment.product_id.__eq__(book_id)).order_by(-Comment.id).all()



def add_comment(book_id, content):
    c = Comment(content=content, book_id=book_id, user=current_user)
    db.session.add(c)
    db.session.commit()

    return c


# def add_GoodsReceived(book_id, goodsReceived_quantity):
#     b = Book.query.get(book_id)
#     b.inventory = b.inventory + goodsReceived_quantity
#     db.session.commit()


if __name__ == '__main__':
    from QLNS import app
    with app.app_context():
        print(get_bill())