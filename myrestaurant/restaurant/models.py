from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class MediaFile(models.Model):
    file = models.FileField(upload_to='mediafiles/')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name

    class Meta:
        verbose_name = "Медіафайл"
        verbose_name_plural = "Медіафайли"



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    media = GenericRelation(MediaFile, related_query_name='profile')

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'Профіль'


class Category(models.Model):
    name = models.CharField(max_length=100)
    media = GenericRelation(MediaFile, related_query_name='category')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії'
        ordering = ['name']


class Dish(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    ingredients = models.TextField()
    price = models.DecimalField(decimal_places=2, max_digits=8)
    media = GenericRelation(MediaFile, related_query_name='dish')
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Страва'
        verbose_name_plural = 'Страви'
        ordering = ['name']


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_total_price(self):
        return sum(item.dish.price * item.quantity for item in self.items.all())

    def __str__(self):
        return f"Cart {self.id}"

    class Meta:
        verbose_name = 'Кошик'


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.dish.name} ({self.quantity})"

    class Meta:
        unique_together = ('cart', 'dish')
        verbose_name = "Елемент кошика"
        verbose_name_plural = "Елемент кошика"


class Order(models.Model):

    PAYMENT_CHOICES = [
        ("online", "Online"),
        ("cash", "Cash"),
    ]

    STATUS_CHOICES = [
        ("new", "New"),
        ("processing", "Processing"),
        ("done", "Done"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")

    def calculate_total(self):
        return sum(item.price * item.quantity for item in self.items.all()) or 0

    def __str__(self):
        return f"Order {self.id}"

    class Meta:
        verbose_name = "Замовлення"
        verbose_name_plural = "Замовлення"
        ordering = ["-created_at"]



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name="order_items")
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.dish.name} ({self.quantity})"

    class Meta:
        verbose_name = "Елемент замовлення"
        verbose_name_plural = "Елемент замовлення"


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    media = GenericRelation(MediaFile, related_query_name='review')

    def __str__(self):
        return f"{self.user.username} - {self.dish.name}"

    class Meta:
        verbose_name = "Відгук"
        verbose_name_plural = "Відгуки"
        ordering = ["-created_at"]


class GlobalReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.rating})"

    class Meta:
        verbose_name = "Відгук про додаток"
        verbose_name_plural = "Відгуки про додаток"
        ordering = ["-created_at"]