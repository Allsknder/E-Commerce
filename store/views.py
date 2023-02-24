from django.shortcuts import render

from django.http import HttpRequest
from .models import *

# Create your views here.
# !NOTE: User is: 1) Customer, 2) Client (Supplier, Merchant)

def store_view(request):
    products = Product.objects.all()
    context = {'products' :  products}
    return render(request, 'shopping/store.html', context)


def cart_view(request:HttpRequest):
    #* Two Scenarios of Querying Data (Preparing the Cart) are going to be created for Customers:
    # 1) Authenticated Customer.
    if request.user.is_authenticated: # if the customer is registered with our website.
        customer        = request.user.customer # Grab the customer associated to that user. (so we can grab the customer's cart <order>)
        order, created  = Order.objects.get_or_create(customer=customer, isCompleted=False) # Grab the Customer's open cart (Not Compeleted Order) or create it.
        orderItems      = order.orderitem_set.all() 
        # 1) If the customer had the cart with items in it (The Cart isn't created), Grab it with its items. So the customer can continue shopping.
        # 2) If the cart was empty (or the cart got created) the `order.orderitem_set.all()` will return a blank List as a value to the 'orderItems' variable. (and that's okay)
        # 3) NOTE: The type of the `orderItems` var is: "django.db.models.query.QuerySet" which is 'List' (of objects) after all. (and here objects of type "OrderItem")
        # 4) Reference for `_set.all()` => https://tekshinobi.com/_set-meaning-in-django-many-to-many-relationship/

    # 2) Guest Customer.
    else: # If the cusotmer is not registered we don't want the cart page to break once the customer clicks his cart, Instead Return an empty list.
        order = { # Temporary
            'get_cart_items_number' : True,
            'get_cart_total_price'  : "3000",
        }

        orderItems = []

    context = {'items' : orderItems, 'order' : order}
    return render(request, 'shopping/cart.html', context)


def checkout_view(request:HttpRequest):
    #* The same two scenarios are of Querying Data (Customer Cart Items) from 'cart_view()' are gonna be created:
    # 1) Authenticated Customer.
    if request.user.is_authenticated:
        customer       = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, isCompleted=False)
        orderItems     = order.orderitem_set.all()

    # 2) Guest Customer.
    else:
        order      = {
            'get_cart_items_number' : True,
            'get_cart_total_price' : "3000"
        }
        orderItems = []


    context = {'items' : orderItems, 'order' : order}
    return render(request, 'shopping/checkout.html', context)

