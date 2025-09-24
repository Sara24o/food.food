from django.db import models
from django.utils.text import slugify
from django.db.models import TextChoices
from accounts.models import Vendor


class Restaurant(models.Model):
    class CuisineType(TextChoices):
        AFRICAN = "african", "African"
        AMERICAN = "american", "American"
        ASIAN = "asian", "Asian"
        BBQ = "bbq", "BBQ"
        BURGER = "burger", "Burger"
        CHINESE = "chinese", "Chinese"
        COFFEE = "coffee", "Coffee"
        DESSERT = "dessert", "Dessert"
        FRENCH = "french", "French"
        GREEK = "greek", "Greek"
        INDIAN = "indian", "Indian"
        ITALIAN = "italian", "Italian"
        JAPANESE = "japanese", "Japanese"
        LEBANESE = "lebanese", "Lebanese"
        MEXICAN = "mexican", "Mexican"
        PIZZA = "pizza", "Pizza"
        SEAFOOD = "seafood", "Seafood"
        SUSHI = "sushi", "Sushi"
        THAI = "thai", "Thai"
        VEGAN = "vegan", "Vegan"
        VEGETARIAN = "vegetarian", "Vegetarian"
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="restaurants")
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="restaurants/", blank=True, null=True)
    cuisine_type = models.CharField(max_length=32, choices=CuisineType.choices, default=CuisineType.ASIAN)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    delivery_time = models.PositiveIntegerField(help_text="Estimated delivery time in minutes", default=30)
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    is_open = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Restaurant"
        verbose_name_plural = "Restaurants"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class MenuItem(models.Model):
    class Category(TextChoices):
        STARTER = "starter", "Starter"
        MAIN = "main", "Main"
        SIDE = "side", "Side"
        DESSERT = "dessert", "Dessert"
        DRINK = "drink", "Drink"
        COMBO = "combo", "Combo"
        BREAKFAST = "breakfast", "Breakfast"
        KIDS = "kids", "Kids"
        SALAD = "salad", "Salad"
        SOUP = "soup", "Soup"
        PASTA = "pasta", "Pasta"
        PIZZA = "pizza", "Pizza"
        BURGER = "burger", "Burger"
        GRILL = "grill", "Grill"
        SUSHI = "sushi", "Sushi"
        NOODLES = "noodles", "Noodles"
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="menu_items")
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.CharField(max_length=24, choices=Category.choices, default=Category.MAIN)
    image = models.ImageField(upload_to="menu_items/", blank=True, null=True)
    is_available = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Menu Item"
        verbose_name_plural = "Menu Items"

    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"

# Create your models here.
