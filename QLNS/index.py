from flask import render_template, request, redirect, session, jsonify
from QLNS import app, dao, admin, login, utils
from flask_login import login_user, logout_user
from QLNS.decorator import annonynous_user
import cloudinary.uploader


# trang chủ
@app.route("/")
def index():
    book = dao.load_book(category_id=request.args.get('category_id'),
                                 kw=request.args.get('keyword'))
    return render_template('home.html',book=book)


@app.route('/book/<int:book_id>')
def details(book_id):
    p = dao.get_book_by_id(book_id)
    return render_template('details.html', book=p)


# đăng nhập trang admin
@app.route('/login-admin', methods=['post'])
def login_admin():
    username = request.form['username']
    password = request.form['password']

    user = dao.auth_user(username=username, password=password)
    if user:
        login_user(user=user)

    return redirect('/admin')


# đăng nhập
@app.route('/login', methods=['get', 'post'])
@annonynous_user
def login_my_user():
    err_msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = dao.auth_user(username=username, password=password)
        if user:
            login_user(user=user)

            n = request.args.get('next')
            return redirect(n if n else '/')
        else:
            err_msg = 'Tên đăng nhập hoặc mật khẩu không đúng'

    return render_template('login.html', err_msg=err_msg)


# đăng xuất
@app.route('/logout')
def logout_my_user():
    logout_user()
    return redirect('/login')


# đăng kí người dùng
@app.route('/register', methods=['get', 'post'])
def register():
    err_msg = ''
    if request.method == 'POST':
        password = request.form['password']
        confirm = request.form['confirm']
        if password.__eq__(confirm):
            avatar = ''
            if request.files:
                res = cloudinary.uploader.upload(request.files['avatar'])
                print(res)
                avatar = res['secure_url']

            try:
                dao.register(name=request.form['name'],
                             password=password,
                             username=request.form['username'], avatar=avatar)

                return redirect('/login')
            except:
                err_msg = 'Đã có lỗi xảy ra! Vui lòng quay lại sau!'
        else:
            err_msg = 'Mật khẩu KHÔNG khớp!'

    return render_template('register.html', err_msg=err_msg)


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


@app.route('/cart')
def cart():
    return render_template('cart.html')


@app.route('/api/cart', methods=['post'])
def add_to_cart():
    data = request.json

    key = app.config['CART_KEY']
    cart = session[key] if key in session else {}

    id = str(data['id'])
    name = data['name']
    price = data['price']

    if id in cart:
        cart[id]['quantity'] += 1
    else:
        cart[id] = {
            "id": id,
            "name": name,
            "price": price,
            "quantity": 1
        }

    session[key] = cart

    return jsonify(utils.cart_stats(cart))

#UPDATE SL
@app.route('/api/cart/<book_id>', methods=['put'])
def update_cart(book_id):
    key = app.config['CART_KEY']

    cart = session.get(key)
    if cart and book_id in cart:
        cart[book_id]['quantity'] = int(request.json['quantity'])

    session[key] = cart

    return jsonify(utils.cart_stats(cart))

#XÓA SP
@app.route('/api/cart/<book_id>', methods=['delete'])
def delete_cart(book_id):
    key = app.config['CART_KEY']

    cart = session.get(key)
    if cart and book_id in cart:
        del cart[book_id]

    session[key] = cart

    return jsonify(utils.cart_stats(cart))


@app.route('/pay')
def pay():
    key = app.config['CART_KEY']
    cart = session.get(key)

    if dao.add_bill(cart=cart):
        del session[key]
    else:
        return jsonify({'status': 500})

    return jsonify({'status': 200})


@app.context_processor
def common_attribute():
    categories = dao.load_categories()
    return {'categories': categories,
            'cart': utils.cart_stats(session.get(app.config['CART_KEY']))
            }


if __name__ == '__main__':
    app.run(debug=True)
