from django.urls import path, include
from . import views
from .views import *

urlpatterns = [
    path('', HomeView.as_view(), name='home'),

    path('categories/', CategoryListView.as_view(), name='categories'),
    path('category/<int:category_id>/', DishListView.as_view(), name='dishes'),
    path('dish/<int:pk>/', DishDetailView.as_view(), name='dish_detail'),

    path('cart/', CartView.as_view(), name='cart'),
    path('add-to-cart/<int:dish_id>/', AddToCartView.as_view(), name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', RemoveFromCartView.as_view(), name='remove_from_cart'),

    path('create-order/', CreateOrderView.as_view(), name='create_order'),
    path('order/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('my-orders/', MyOrdersView.as_view(), name='my_orders'),

    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),

    path('dish/<int:dish_id>/review/', AddReviewView.as_view(), name='add_review'),

    path('reviews/', GlobalReviewsView.as_view(), name='global_reviews'),
    path('reviews/add/', AddGlobalReviewView.as_view(), name='add_global_review'),

    path('cart/increase/<int:item_id>/', IncreaseQuantityView.as_view(), name='increase_quantity'),
    path('cart/decrease/<int:item_id>/', DecreaseQuantityView.as_view(), name='decrease_quantity'),

    path('reorder/<int:order_id>/', ReorderView.as_view(), name='reorder'),

    path("profile/", ProfileView.as_view(), name="profile"),

    path("logout/", views.logout_view, name="logout"),

]