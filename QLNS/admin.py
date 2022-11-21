from QLNS import db, app
from QLNS.models import UserRole
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask import redirect
from flask_login import logout_user, current_user
from wtforms import TextAreaField
from wtforms.widgets import TextArea

admin = Admin(app=app, name='Quản trị nhà sách', template_mode='bootstrap4')


class AuthenticatedModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


class AuthenticatedView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class CKTextAreaWidget(TextArea):
    def __call__(self, field, **kwargs):
        if kwargs.get('class'):
            kwargs['class'] += ' ckeditor'
        else:
            kwargs.setdefault('class', 'ckeditor')

        return super().__call__(field, **kwargs)


class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget()





class StatsView(AuthenticatedView):
    @expose('/')
    def index(self):
        return self.render('admin/stats.html')



class LogoutView(AuthenticatedView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')


# admin.add_view(AuthenticatedModelView(Category, db.session, name='Danh mục'))
# admin.add_view(ProductView(Product, db.session, name='Sản phẩm'))
admin.add_view(StatsView(name='Thống kê - báo cáo'))
admin.add_view(LogoutView(name='Đăng xuất'))