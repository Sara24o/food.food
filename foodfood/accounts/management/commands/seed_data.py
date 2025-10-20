from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from accounts.models import Customer, Vendor
from restaurants.models import Restaurant, MenuItem
from orders.models import Order, OrderItem
from decimal import Decimal
import random
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Seed the database with realistic test data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            self.clear_data()

        self.stdout.write('Creating test data...')
        
        with transaction.atomic():
            # Create users
            customers = self.create_customers()
            vendors = self.create_vendors()
            
            # Create restaurants
            restaurants = self.create_restaurants(vendors)
            
            # Create menu items
            self.create_menu_items(restaurants)
            
            # Create orders
            self.create_orders(customers, restaurants)
            
        self.stdout.write(
            self.style.SUCCESS('Successfully created test data!')
        )

    def clear_data(self):
        """Clear existing test data"""
        Order.objects.all().delete()
        MenuItem.objects.all().delete()
        Restaurant.objects.all().delete()
        Customer.objects.all().delete()
        Vendor.objects.all().delete()
        User.objects.filter(username__startswith='test_').delete()

    def create_customers(self):
        """Create test customers"""
        customers_data = [
            {
                'username': 'test_customer1',
                'email': 'john.doe@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'phone': '+33123456789',
                'address': '123 Rue de la Paix, 75001 Paris',
                'preferences': 'Pas de gluten, végétarien'
            },
            {
                'username': 'test_customer2',
                'email': 'marie.martin@example.com',
                'first_name': 'Marie',
                'last_name': 'Martin',
                'phone': '+33987654321',
                'address': '45 Avenue des Champs-Élysées, 75008 Paris',
                'preferences': 'Épicé, halal'
            },
            {
                'username': 'test_customer3',
                'email': 'pierre.durand@example.com',
                'first_name': 'Pierre',
                'last_name': 'Durand',
                'phone': '+33555666777',
                'address': '78 Boulevard Saint-Germain, 75005 Paris',
                'preferences': 'Bio, local'
            },
            {
                'username': 'test_customer4',
                'email': 'sophie.bernard@example.com',
                'first_name': 'Sophie',
                'last_name': 'Bernard',
                'phone': '+33444555666',
                'address': '12 Place de la République, 75011 Paris',
                'preferences': 'Vegan, sans lactose'
            },
            {
                'username': 'test_customer5',
                'email': 'alex.moreau@example.com',
                'first_name': 'Alex',
                'last_name': 'Moreau',
                'phone': '+33333444555',
                'address': '56 Rue de Rivoli, 75004 Paris',
                'preferences': 'Cuisine asiatique, sushi'
            }
        ]
        
        customers = []
        for data in customers_data:
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password='testpass123',
                first_name=data['first_name'],
                last_name=data['last_name']
            )
            customer = Customer.objects.create(
                user=user,
                phone=data['phone'],
                address=data['address'],
                preferences=data['preferences']
            )
            customers.append(customer)
            
        self.stdout.write(f'Created {len(customers)} customers')
        return customers

    def create_vendors(self):
        """Create test vendors"""
        vendors_data = [
            {
                'username': 'test_vendor1',
                'email': 'chef@bistrot-paris.fr',
                'first_name': 'Chef',
                'last_name': 'Dubois',
                'restaurant_name': 'Le Bistrot Parisien',
                'description': 'Cuisine française traditionnelle dans un cadre chaleureux',
                'phone': '+33111111111',
                'address': '15 Rue de la Paix, 75002 Paris'
            },
            {
                'username': 'test_vendor2',
                'email': 'manager@pizza-roma.fr',
                'first_name': 'Marco',
                'last_name': 'Rossi',
                'restaurant_name': 'Pizza Roma',
                'description': 'Pizzas authentiques italiennes cuites au feu de bois',
                'phone': '+33222222222',
                'address': '28 Avenue de l\'Opéra, 75001 Paris'
            },
            {
                'username': 'test_vendor3',
                'email': 'owner@sushi-tokyo.fr',
                'first_name': 'Yuki',
                'last_name': 'Tanaka',
                'restaurant_name': 'Sushi Tokyo',
                'description': 'Sushi et sashimi frais préparés par des maîtres sushi',
                'phone': '+33333333333',
                'address': '42 Rue de Rivoli, 75004 Paris'
            },
            {
                'username': 'test_vendor4',
                'email': 'chef@burger-gourmet.fr',
                'first_name': 'Tom',
                'last_name': 'Wilson',
                'restaurant_name': 'Burger Gourmet',
                'description': 'Burgers artisanaux avec des ingrédients premium',
                'phone': '+33444444444',
                'address': '67 Boulevard Saint-Germain, 75005 Paris'
            },
            {
                'username': 'test_vendor5',
                'email': 'manager@indian-spice.fr',
                'first_name': 'Raj',
                'last_name': 'Patel',
                'restaurant_name': 'Indian Spice',
                'description': 'Cuisine indienne authentique avec épices importées',
                'phone': '+33555555555',
                'address': '89 Rue de la Roquette, 75011 Paris'
            }
        ]
        
        vendors = []
        for data in vendors_data:
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password='testpass123',
                first_name=data['first_name'],
                last_name=data['last_name']
            )
            vendor = Vendor.objects.create(
                user=user,
                restaurant_name=data['restaurant_name'],
                description=data['description'],
                phone=data['phone'],
                address=data['address']
            )
            vendors.append(vendor)
            
        self.stdout.write(f'Created {len(vendors)} vendors')
        return vendors

    def create_restaurants(self, vendors):
        """Create test restaurants"""
        restaurants_data = [
            {
                'name': 'Le Bistrot Parisien',
                'slug': 'bistrot-parisien',
                'description': 'Cuisine française traditionnelle dans un cadre chaleureux. Nos plats sont préparés avec des ingrédients frais et locaux.',
                'cuisine_type': 'french',
                'delivery_fee': Decimal('3.50'),
                'delivery_time': 35,
                'rating': Decimal('4.5'),
                'is_open': True
            },
            {
                'name': 'Pizza Roma',
                'slug': 'pizza-roma',
                'description': 'Pizzas authentiques italiennes cuites au feu de bois. Pâte fraîche préparée quotidiennement.',
                'cuisine_type': 'italian',
                'delivery_fee': Decimal('2.90'),
                'delivery_time': 25,
                'rating': Decimal('4.3'),
                'is_open': True
            },
            {
                'name': 'Sushi Tokyo',
                'slug': 'sushi-tokyo',
                'description': 'Sushi et sashimi frais préparés par des maîtres sushi. Poissons importés quotidiennement du Japon.',
                'cuisine_type': 'japanese',
                'delivery_fee': Decimal('4.50'),
                'delivery_time': 40,
                'rating': Decimal('4.7'),
                'is_open': True
            },
            {
                'name': 'Burger Gourmet',
                'slug': 'burger-gourmet',
                'description': 'Burgers artisanaux avec des ingrédients premium. Viande française, pains briochés faits maison.',
                'cuisine_type': 'burger',
                'delivery_fee': Decimal('3.00'),
                'delivery_time': 30,
                'rating': Decimal('4.2'),
                'is_open': True
            },
            {
                'name': 'Indian Spice',
                'slug': 'indian-spice',
                'description': 'Cuisine indienne authentique avec épices importées. Plats végétariens et non-végétariens disponibles.',
                'cuisine_type': 'indian',
                'delivery_fee': Decimal('3.20'),
                'delivery_time': 35,
                'rating': Decimal('4.4'),
                'is_open': True
            }
        ]
        
        restaurants = []
        for i, data in enumerate(restaurants_data):
            restaurant = Restaurant.objects.create(
                vendor=vendors[i],
                name=data['name'],
                slug=data['slug'],
                description=data['description'],
                cuisine_type=data['cuisine_type'],
                delivery_fee=data['delivery_fee'],
                delivery_time=data['delivery_time'],
                rating=data['rating'],
                is_open=data['is_open']
            )
            restaurants.append(restaurant)
            
        self.stdout.write(f'Created {len(restaurants)} restaurants')
        return restaurants

    def create_menu_items(self, restaurants):
        """Create menu items for each restaurant"""
        menu_data = {
            'Le Bistrot Parisien': [
                {'name': 'Coq au Vin', 'description': 'Poulet mijoté dans le vin rouge avec champignons et lardons', 'price': Decimal('18.50'), 'category': 'main'},
                {'name': 'Bœuf Bourguignon', 'description': 'Bœuf braisé au vin rouge avec carottes et oignons', 'price': Decimal('19.90'), 'category': 'main'},
                {'name': 'Escargots de Bourgogne', 'description': 'Escargots au beurre persillé, 6 pièces', 'price': Decimal('12.50'), 'category': 'starter'},
                {'name': 'Tarte Tatin', 'description': 'Tarte aux pommes caramélisées, crème chantilly', 'price': Decimal('8.50'), 'category': 'dessert'},
                {'name': 'Soupe à l\'Oignon', 'description': 'Soupe traditionnelle aux oignons caramélisés, gratinée', 'price': Decimal('9.90'), 'category': 'soup'},
                {'name': 'Salade de Chèvre Chaud', 'description': 'Salade verte, chèvre chaud sur toast, noix', 'price': Decimal('14.50'), 'category': 'salad'},
                {'name': 'Vin Rouge de Bordeaux', 'description': 'Verre de vin rouge de la région bordelaise', 'price': Decimal('6.50'), 'category': 'drink'},
                {'name': 'Café Expresso', 'description': 'Café expresso italien', 'price': Decimal('2.50'), 'category': 'drink'}
            ],
            'Pizza Roma': [
                {'name': 'Margherita', 'description': 'Tomate, mozzarella, basilic frais', 'price': Decimal('12.90'), 'category': 'pizza'},
                {'name': 'Quattro Stagioni', 'description': 'Tomate, mozzarella, jambon, champignons, artichauts, olives', 'price': Decimal('16.50'), 'category': 'pizza'},
                {'name': 'Diavola', 'description': 'Tomate, mozzarella, salami piquant, piments', 'price': Decimal('15.90'), 'category': 'pizza'},
                {'name': 'Prosciutto e Funghi', 'description': 'Tomate, mozzarella, jambon de Parme, champignons', 'price': Decimal('17.50'), 'category': 'pizza'},
                {'name': 'Calzone', 'description': 'Pizza pliée fourrée à la ricotta, jambon et mozzarella', 'price': Decimal('14.90'), 'category': 'pizza'},
                {'name': 'Bruschetta', 'description': 'Pain grillé, tomates fraîches, basilic, huile d\'olive', 'price': Decimal('8.50'), 'category': 'starter'},
                {'name': 'Tiramisu', 'description': 'Dessert italien au café et mascarpone', 'price': Decimal('6.90'), 'category': 'dessert'},
                {'name': 'Coca-Cola', 'description': 'Boisson gazeuse 33cl', 'price': Decimal('3.50'), 'category': 'drink'}
            ],
            'Sushi Tokyo': [
                {'name': 'Sashimi Mix', 'description': 'Assortiment de 12 pièces de sashimi frais', 'price': Decimal('28.90'), 'category': 'sushi'},
                {'name': 'Maki California', 'description': 'Rouleau de riz avec crabe, avocat et concombre', 'price': Decimal('12.50'), 'category': 'sushi'},
                {'name': 'Maki Saumon', 'description': 'Rouleau de riz avec saumon frais et concombre', 'price': Decimal('11.90'), 'category': 'sushi'},
                {'name': 'Nigiri Thon', 'description': '6 pièces de nigiri au thon frais', 'price': Decimal('16.50'), 'category': 'sushi'},
                {'name': 'Chirashi Bowl', 'description': 'Bol de riz vinaigré avec sashimi et légumes', 'price': Decimal('22.90'), 'category': 'main'},
                {'name': 'Miso Soup', 'description': 'Soupe traditionnelle japonaise aux algues', 'price': Decimal('4.50'), 'category': 'soup'},
                {'name': 'Edamame', 'description': 'Fèves de soja salées, 100g', 'price': Decimal('5.90'), 'category': 'starter'},
                {'name': 'Thé Vert', 'description': 'Thé vert japonais traditionnel', 'price': Decimal('3.50'), 'category': 'drink'}
            ],
            'Burger Gourmet': [
                {'name': 'Classic Burger', 'description': 'Steak de bœuf, cheddar, salade, tomate, oignons', 'price': Decimal('14.90'), 'category': 'burger'},
                {'name': 'Bacon Deluxe', 'description': 'Double steak, bacon croustillant, cheddar, sauce BBQ', 'price': Decimal('18.50'), 'category': 'burger'},
                {'name': 'Chicken Supreme', 'description': 'Filet de poulet pané, avocat, tomate, sauce ranch', 'price': Decimal('16.90'), 'category': 'burger'},
                {'name': 'Veggie Burger', 'description': 'Steak végétal, avocat, tomate, salade, sauce tahini', 'price': Decimal('15.50'), 'category': 'burger'},
                {'name': 'Frites Maison', 'description': 'Frites coupées à la main, sel de mer', 'price': Decimal('4.90'), 'category': 'side'},
                {'name': 'Onion Rings', 'description': 'Anneaux d\'oignon panés et frits', 'price': Decimal('5.50'), 'category': 'side'},
                {'name': 'Milkshake Vanille', 'description': 'Milkshake à la vanille avec chantilly', 'price': Decimal('6.90'), 'category': 'drink'},
                {'name': 'Coca-Cola', 'description': 'Boisson gazeuse 50cl', 'price': Decimal('4.50'), 'category': 'drink'}
            ],
            'Indian Spice': [
                {'name': 'Chicken Tikka Masala', 'description': 'Poulet mariné dans une sauce tomate épicée', 'price': Decimal('16.90'), 'category': 'main'},
                {'name': 'Lamb Biryani', 'description': 'Riz parfumé au safran avec agneau et épices', 'price': Decimal('18.50'), 'category': 'main'},
                {'name': 'Palak Paneer', 'description': 'Fromage frais dans une sauce aux épinards', 'price': Decimal('14.50'), 'category': 'main'},
                {'name': 'Chicken Curry', 'description': 'Poulet mijoté dans une sauce curry douce', 'price': Decimal('15.90'), 'category': 'main'},
                {'name': 'Samosas', 'description': 'Beignets fourrés aux légumes épicés, 3 pièces', 'price': Decimal('6.90'), 'category': 'starter'},
                {'name': 'Naan Pain', 'description': 'Pain indien cuit au tandoor', 'price': Decimal('3.50'), 'category': 'side'},
                {'name': 'Riz Basmati', 'description': 'Riz parfumé cuit à la vapeur', 'price': Decimal('4.50'), 'category': 'side'},
                {'name': 'Lassi Mangue', 'description': 'Boisson au yaourt et mangue', 'price': Decimal('4.90'), 'category': 'drink'}
            ]
        }
        
        total_items = 0
        for restaurant in restaurants:
            items = menu_data.get(restaurant.name, [])
            for item_data in items:
                MenuItem.objects.create(
                    restaurant=restaurant,
                    name=item_data['name'],
                    description=item_data['description'],
                    price=item_data['price'],
                    category=item_data['category'],
                    is_available=True
                )
                total_items += 1
                
        self.stdout.write(f'Created {total_items} menu items')

    def create_orders(self, customers, restaurants):
        """Create test orders"""
        orders_data = [
            {
                'customer': customers[0],
                'restaurant': restaurants[0],
                'status': Order.STATUS_DELIVERED,
                'days_ago': 5,
                'items': [
                    {'name': 'Coq au Vin', 'quantity': 1, 'price': Decimal('18.50')},
                    {'name': 'Tarte Tatin', 'quantity': 1, 'price': Decimal('8.50')}
                ]
            },
            {
                'customer': customers[1],
                'restaurant': restaurants[1],
                'status': Order.STATUS_DELIVERED,
                'days_ago': 3,
                'items': [
                    {'name': 'Margherita', 'quantity': 2, 'price': Decimal('12.90')},
                    {'name': 'Bruschetta', 'quantity': 1, 'price': Decimal('8.50')}
                ]
            },
            {
                'customer': customers[2],
                'restaurant': restaurants[2],
                'status': Order.STATUS_ON_THE_WAY,
                'days_ago': 1,
                'items': [
                    {'name': 'Sashimi Mix', 'quantity': 1, 'price': Decimal('28.90')},
                    {'name': 'Maki California', 'quantity': 2, 'price': Decimal('12.50')}
                ]
            },
            {
                'customer': customers[3],
                'restaurant': restaurants[3],
                'status': Order.STATUS_PREPARING,
                'days_ago': 0,
                'items': [
                    {'name': 'Bacon Deluxe', 'quantity': 1, 'price': Decimal('18.50')},
                    {'name': 'Frites Maison', 'quantity': 1, 'price': Decimal('4.90')}
                ]
            },
            {
                'customer': customers[4],
                'restaurant': restaurants[4],
                'status': Order.STATUS_PENDING,
                'days_ago': 0,
                'items': [
                    {'name': 'Chicken Tikka Masala', 'quantity': 1, 'price': Decimal('16.90')},
                    {'name': 'Naan Pain', 'quantity': 2, 'price': Decimal('3.50')}
                ]
            }
        ]
        
        total_orders = 0
        for order_data in orders_data:
            # Calculate order date
            order_date = datetime.now() - timedelta(days=order_data['days_ago'])
            
            # Get actual menu items
            restaurant = order_data['restaurant']
            menu_items = {item.name: item for item in restaurant.menu_items.all()}
            
            # Create order
            order = Order.objects.create(
                customer=order_data['customer'],
                restaurant=restaurant,
                delivery_address=order_data['customer'].address,
                status=order_data['status'],
                created_at=order_date
            )
            
            # Create order items
            for item_data in order_data['items']:
                menu_item = menu_items.get(item_data['name'])
                if menu_item:
                    OrderItem.objects.create(
                        order=order,
                        menu_item=menu_item,
                        quantity=item_data['quantity'],
                        price=menu_item.price
                    )
            
            # Recalculate total
            order.recalculate_total()
            total_orders += 1
            
        self.stdout.write(f'Created {total_orders} orders')