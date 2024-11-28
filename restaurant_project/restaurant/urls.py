from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('manager/', views.manager_dashboard, name='manager_dashboard'),
    path('customer/', views.customer_dashboard, name='customer_dashboard'),
    path('order-placed/', views.order_placed, name='order_placed'),
    path('logout/', views.logout_view, name='logout'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('update_cart_item/', views.update_cart_item, name='update_cart_item'),
    path('get_cart_data/', views.get_cart_data, name='get_cart_data'),
    path('add_product/', views.add_product_form, name='add_product_form'),
    path('view_user_orders/', views.view_user_orders, name='view_user_orders'),
    path('place_order/', views.place_order, name='place_order'),
    path('view_user_orders/', views.view_user_orders, name='view_user_orders'),
    path('add_product_form/', views.add_product_form, name='add_product_form'),

]
