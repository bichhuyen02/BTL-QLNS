from flask import render_template, request, redirect
from QLNS import app, dao, admin, login
from flask_login import login_user, logout_user
from QLNS.decorator import annonynous_user
import cloudinary.uploader

# trang chủ
@app.route("/")
def index():
    return render_template('home.html')

# đăng nhập
@app.route('/login',methods=['get', 'post'])
@annonynous_user
def login_my_user():
    err_msg=''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = dao.auth_user(username=username, password=password)
        if user:
            login_user(user=user)
            return redirect('/')
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


if __name__ == '__main__':
    app.run(debug=True)



