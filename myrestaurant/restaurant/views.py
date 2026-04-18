from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView, CreateView, View
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Category, Dish, Cart, CartItem, Order, OrderItem, GlobalReview, Profile
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import RegisterForm, ProfileForm
from django.contrib import messages
from django.db.models import Avg
from .models import Review
from django.contrib.auth import logout


def logout_view(request):
    logout(request)
    return redirect('home')


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("home")

        return render(request, "login.html", {"error": "Неверный логин или пароль"})

    return render(request, "login.html")


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            Profile.objects.create(user=user)
            Cart.objects.create(user=user)

            login(request, user)
            return redirect("home")
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})




def get_user_cart(user):
    cart, created = Cart.objects.get_or_create(user=user)
    return cart


class HomeView(TemplateView):
    template_name = 'home.html'


class CategoryListView(ListView):
    model = Category
    template_name = 'category_list.html'
    context_object_name = 'categories'


class DishListView(ListView):
    model = Dish
    template_name = 'dish_list.html'
    context_object_name = 'dishes'

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return Dish.objects.filter(category_id=category_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(Category, id=self.kwargs['category_id'])
        return context


class DishDetailView(DetailView):
    model = Dish
    template_name = 'dish_detail.html'
    context_object_name = 'dish'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['reviews'] = self.object.review_set.all()

        context['avg_rating'] = self.object.review_set.aggregate(
            avg=Avg('rating')
        )['avg']

        return context


class CartView(LoginRequiredMixin, TemplateView):
    template_name = 'cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
#        context['cart'] = get_user_cart(self.request.user)


        cart = get_user_cart(self.request.user)

        context['cart'] = cart
        context['total_price'] = cart.get_total_price()

        return context


class AddToCartView(LoginRequiredMixin, View):
    def post(self, request, dish_id):
        cart = get_user_cart(request.user)
        dish = get_object_or_404(Dish, id=dish_id)

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            dish=dish
        )

        if not created:
            item.quantity += 1
            item.save()

        return redirect('cart')


class RemoveFromCartView(LoginRequiredMixin, View):
    def post(self, request, item_id):
        item = get_object_or_404(CartItem, id=item_id)
        item.delete()
        return redirect('cart')


class CreateOrderView(View):
    def post(self, request):

        if request.user.is_authenticated:
            cart = get_user_cart(request.user)

            if not cart.items.exists():
                messages.error(request, "Корзина пуста — нельзя оформить заказ")
                return redirect('cart')

            profile = Profile.objects.get(user=request.user)

            if not profile.address or not profile.phone:
                messages.error(request, "Заполни профиль")
                return redirect('profile')

            address = profile.address
            phone = profile.phone
            user = request.user

        else:

            address = request.POST.get("address")
            phone = request.POST.get("phone")
            payment_method = request.POST.get("payment_method")

            if not address or not phone:
                messages.error(request, "Заполни адрес и телефон")
                return redirect('create_order')

            user = None

        payment_method = request.POST.get("payment_method")

        order = Order.objects.create(
            user=user,
            address=address,
            phone=phone,
            payment_method=payment_method,
            total_price=0
        )

        total = 0


        if request.user.is_authenticated:
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    dish=item.dish,
                    quantity=item.quantity,
                    price=item.dish.price
                )
                total += item.dish.price * item.quantity

            cart.items.all().delete()

        order.total_price = total
        order.save()

        messages.success(request, "✅ Заказ успешно оформлен!")

        return redirect('order_detail', pk=order.id)

    def get(self, request):
        return render(request, 'create_order.html')


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'order_detail.html'
    context_object_name = 'order'


class MyOrdersView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'my_orders.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class AddReviewView(LoginRequiredMixin, View):
    def post(self, request, dish_id):
        dish = get_object_or_404(Dish, id=dish_id)

        Review.objects.create(
            user=request.user,
            dish=dish,
            rating=request.POST.get("rating"),
            comment=request.POST.get("comment")
        )

        return redirect('dish_detail', pk=dish.id)


class GlobalReviewsView(ListView):
    model = GlobalReview
    template_name = 'global_reviews.html'
    context_object_name = 'reviews'


class AddGlobalReviewView(LoginRequiredMixin, View):
    def post(self, request):
        GlobalReview.objects.create(
            user=request.user,
            rating=request.POST.get("rating"),
            comment=request.POST.get("comment")
        )
        return redirect('global_reviews')


class IncreaseQuantityView(LoginRequiredMixin, View):
    def post(self, request, item_id):
        item = get_object_or_404(CartItem, id=item_id)
        item.quantity += 1
        item.save()
        return redirect('cart')


class DecreaseQuantityView(LoginRequiredMixin, View):
    def post(self, request, item_id):
        item = get_object_or_404(CartItem, id=item_id)

        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()

        return redirect('cart')


class ReorderView(LoginRequiredMixin, View):
    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)

        cart, created = Cart.objects.get_or_create(user=request.user)

        for item in order.items.all():
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                dish=item.dish,
                defaults={'quantity': item.quantity}
            )

            if not created:
                cart_item.quantity += item.quantity
                cart_item.save()

        return redirect('cart')


class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        profile, created = Profile.objects.get_or_create(user=request.user)

        edit = request.GET.get("edit")

        form = ProfileForm(instance=profile)

        return render(request, 'profile.html', {
            'profile': profile,
            'form': form,
            'edit': edit
        })

    def post(self, request):
        profile, created = Profile.objects.get_or_create(user=request.user)
        form = ProfileForm(request.POST, instance=profile)

        if form.is_valid():
            form.save()

        return redirect('profile')


