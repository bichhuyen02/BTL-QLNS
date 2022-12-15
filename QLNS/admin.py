from QLNS import db, app, dao
from QLNS.models import Category, Book, UserRole, Tag
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask import redirect, request
from flask_login import logout_user, current_user
from wtforms import TextAreaField
from wtforms.widgets import TextArea




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


class BookView(AuthenticatedModelView):
    column_searchable_list = ['name', 'author']
    column_filters = ['name', 'author']
    form_excluded_columns = ['bill_details','received_details', 'received', 'tags', 'comments', 'goods_details']
    can_view_details = True
    column_exclude_list = ['image', 'description']
    can_export = True
    column_export_list = ['id', 'name', 'description', 'price']
    column_labels = {
        'name': 'Tên sách',
        'author': 'Tác giả',
        'description': 'Nội dung',
        'price': 'Giá'
    }
    page_size = 7
    extra_js = ['//cdn.ckeditor.com/4.6.0/standard/ckeditor.js']
    form_overrides = {
        'description': CKTextAreaField
    }


class StatsView(AuthenticatedView):
    @expose('/')
    def index(self):
        stats = dao.stats_revenue_book()
        stats1 = dao.stats_revenue_category()
        return self.render('admin/stats.html', stats=stats, stats1=stats1)



class LogoutView(AuthenticatedView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')


class MyAdminView(AdminIndexView):
    @expose('/')
    def index(self):
        stats = dao.count_book_by_cate()
        return self.render('admin/index.html', stats=stats)



admin = Admin(app=app, name='Quản trị nhà sách', template_mode='bootstrap4', index_view=MyAdminView(), )
admin.add_view(AuthenticatedModelView(Category, db.session, name='Thể Loại'))
admin.add_view(BookView(Book, db.session, name='Sách'))
admin.add_view(AuthenticatedModelView(Tag, db.session))
admin.add_view(StatsView(name='Thống kê - báo cáo'))
admin.add_view(LogoutView(name='Đăng xuất'))