from django.urls import path
from . import views

urlpatterns = [

    path('ECE-LexiconCollector', views.keyword_selector, name='keyword_selector'),
    path('ECE-LexiconCollector/', views.keyword_selector, name='keyword_selector'),
    path('ECE-LexiconCollector/update', views.keyword_selector_update, name='keyword_selector_update'),
    path('ECE-LexiconCollector/update_edit', views.keyword_selector_update_edit, name='keyword_selector_update_edit'),
    path('ECE-LexiconCollector/help', views.help, name='help'),
    path('ECE-LexiconCollector/help/', views.help, name='help'),
    path('ECE-LexiconCollector/pos_keyword_view', views.pos_keyword_view, name='pos_keyword_view'),
    path('ECE-LexiconCollector/pos_keyword_view/', views.pos_keyword_view, name='pos_keyword_view'),
    path('ECE-LexiconCollector/neg_keyword_view', views.neg_keyword_view, name='neg_keyword_view'),
    path('ECE-LexiconCollector/neg_keyword_view/', views.neg_keyword_view, name='neg_keyword_view'),


    # for login
    path('ECE-LexiconCollector/signup', views.signup, name='signup'),
    path('ECE-LexiconCollector/signup/', views.signup, name='signup'),
    path('ECE-LexiconCollector/signup/user_duplication_check', views.user_duplication_check, name='user_duplication_check'),
    path('ECE-LexiconCollector/signup/signup_after', views.signup_after, name='signup_after'),
    path('ECE-LexiconCollector/login', views.login, name='login'),
    path('ECE-LexiconCollector/login/', views.login, name='login'),
    path('ECE-LexiconCollector/logout/', views.logout, name='logout'),
    path('ECE-LexiconCollector/logout', views.logout, name='logout'),

    # 유저정보수정
    path('ECE-LexiconCollector/account', views.account, name='account'),
    path('ECE-LexiconCollector/forgot_password', views.forgot_password, name='forgot_password'),
    path('ECE-LexiconCollector/reset_password', views.reset_password, name='reset_password'),

    path('test', views.test, name='test'),

]