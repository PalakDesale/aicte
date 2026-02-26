from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('explore/', views.explore, name='explore'),
    path('cook/<int:pk>/', views.cook_detail, name='cook_detail'),
    path('add-to-cart/<int:dish_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/update/<int:dish_id>/<str:action>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:dish_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-history/', views.order_history, name='order_history'),
    path('cancel-order/<int:pk>/', views.cancel_order, name='cancel_order'),
    path('login/', auth_views.LoginView.as_view(template_name='marketplace/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('signup/', views.signup, name='signup'),
]
