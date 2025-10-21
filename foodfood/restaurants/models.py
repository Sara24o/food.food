from django.db import models
from django.utils.text import slugify
from django.db.models import TextChoices
from accounts.models import Vendor
from PIL import Image
from pathlib import Path


TARGET_IMAGE_SIZE = (800, 600)  # width, height for uniform presentation


def _compress_and_fit_image(image_path: str, target_size=TARGET_IMAGE_SIZE) -> None:
    """Open an image at image_path, convert to RGB, center-crop to cover target_size,
    and save compressed back to the same path.
    """
    try:
        with Image.open(image_path) as img:
            # Convert to RGB to avoid issues with PNG/alpha when saving JPEG
            if img.mode in ("RGBA", "P"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3] if img.mode == "RGBA" else None)
                img = background
            else:
                img = img.convert("RGB")

            target_w, target_h = target_size
            src_w, src_h = img.size

            # Compute scale to cover the target area
            scale = max(target_w / src_w, target_h / src_h)
            new_size = (int(src_w * scale), int(src_h * scale))
            img = img.resize(new_size, Image.LANCZOS)

            # Center crop
            left = (img.width - target_w) // 2
            top = (img.height - target_h) // 2
            right = left + target_w
            bottom = top + target_h
            img = img.crop((left, top, right, bottom))

            # Save compressed using original extension to avoid format mismatch
            ext = Path(image_path).suffix.lower()
            save_kwargs = {"optimize": True}
            if ext in (".jpg", ".jpeg"):
                save_kwargs.update({"quality": 85, "progressive": True})
            elif ext == ".png":
                save_kwargs.update({"compress_level": 6})
            img.save(image_path, **save_kwargs)
    except Exception:
        # If anything goes wrong, skip silently to avoid breaking save()
        # Logging can be added later if needed.
        pass


class Restaurant(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="restaurants")
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="restaurants/", blank=True, null=True)
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
            base = slugify(self.name) or "restaurant"
            slug_candidate = base
            index = 1
            while Restaurant.objects.filter(slug=slug_candidate).exclude(pk=self.pk).exists():
                index += 1
                slug_candidate = f"{base}-{index}"
            self.slug = slug_candidate
        super().save(*args, **kwargs)
        # Process image after initial save, when file path exists
        if self.image and getattr(self.image, 'path', None):
            _compress_and_fit_image(self.image.path, TARGET_IMAGE_SIZE)


class MenuItem(models.Model):
    class Category(TextChoices):
        # Catégories principales de plats
        STARTER = "starter", "Starter"
        MAIN = "main", "Main Course"
        SIDE = "side", "Side Dish"
        DESSERT = "dessert", "Dessert"
        DRINK = "drink", "Beverage"
        # Types de plats spécifiques
        PIZZA = "pizza", "Pizza"
        BURGER = "burger", "Burger"
        SUSHI = "sushi", "Sushi"
        PASTA = "pasta", "Pasta"
        SALAD = "salad", "Salad"
        SOUP = "soup", "Soup"
        GRILL = "grill", "Grilled"
        NOODLES = "noodles", "Noodles"
        SANDWICH = "sandwich", "Sandwich"
        WRAP = "wrap", "Wrap"
        TACO = "taco", "Taco"
        BOWL = "bowl", "Bowl"
        # Catégories spéciales
        COMBO = "combo", "Combo Meal"
        BREAKFAST = "breakfast", "Breakfast"
        KIDS = "kids", "Kids Menu"
        APPETIZER = "appetizer", "Appetizer"
        SNACK = "snack", "Snack"
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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image and getattr(self.image, 'path', None):
            _compress_and_fit_image(self.image.path, TARGET_IMAGE_SIZE)

# Create your models here.
