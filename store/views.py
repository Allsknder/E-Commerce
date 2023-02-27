from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
import json
import datetime

from .models import *

# Create your views here.
# !NOTE: User is: 1) Customer, 2) Client (Supplier, Merchant)

def store_view(request:HttpRequest):

    if request.user.is_authenticated:
        customer       = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, isCompleted=False)
        orderItems     = order.orderitem_set.all()
        cartItemsNumber =  order.get_cart_items_number
    
    else:
        orderItems     = []
        order          = {
            'get_cart_items_number' : True,
            'get_cart_total_price'  : "3000",
        }
        cartItemsNumber =  order['get_cart_items_number']


    products = Product.objects.all()
    context = {
        'products' :  products,
        'cartItemsNumber' : cartItemsNumber
    }
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
        cartItemsNumber =  order.get_cart_items_number
    # 2) Guest Customer.
    else: # If the cusotmer is not registered we don't want the cart page to break once the customer clicks his cart, Instead Return an empty list.
        order = { # Temporary
            'get_cart_items_number' : True,
            'get_cart_total_price'  : "3000",
        }

        orderItems      = []
        cartItemsNumber = order['get_cart_items_number']

    context = {
        'items'           : orderItems, 
        'order'           : order, 
        'cartItemsNumber' : cartItemsNumber
    }
    return render(request, 'shopping/cart.html', context)



def checkout_view(request:HttpRequest):
    #* The same two scenarios are of Querying Data (Customer Cart Items) from 'cart_view()' are gonna be created:
    # 1) Authenticated Customer.
    if request.user.is_authenticated:
        customer        = request.user.customer
        order, created  = Order.objects.get_or_create(customer=customer, isCompleted=False)
        orderItems      = order.orderitem_set.all()
        cartItemsNumber =  order.get_cart_items_number
        shipping        = order.needsShipping

    # 2) Guest Customer.
    else:
        order      = {
            'get_cart_items_number' : True,
            'get_cart_total_price'  : "3000",
            'shipping'              : False

        }
        orderItems       = []
        cartItemsNumber  = order['get_cart_items_number']
        shipping         = order['shipping']


    context = {
        'items'           : orderItems, 
        'order'           : order, 
        'cartItemsNumber' : cartItemsNumber,
        'shipping'        : shipping
    }
    return render(request, 'shopping/checkout.html', context)


# This function will trigger once the Authenticated (Only) Customer clicks any 'Add to Cart' button in 'store.html' or playing with the quantity in 'cart.html'
def update_item_function(request:HttpRequest):
    # Parsing POST Data.
    data = json.loads(request.body) # json.loads() function: Accepts only byte string (stringified version of JSON which must be done in the JS file)
    productID  = data['productID']
    action     = data['action'] 


    print(f"productID: {productID} \naction: {action}")

    # Now we have the 'product ID' and what do we want to do with it [(Put in (OR Remove from) the Cart for the Authenticated Customer]
    # Here lays the logic of the Adding, Creating (store.html), Subtracting And Removing Operations.
    
    #! Authenticated Customer Entering the Store.
    # After the Customer clicked his first 'Add to Cart' button => And it appears that he's registered with our website (Becuase this function got triggered)
    customer            = request.user.customer  # Take his ID Card ('Customer' associated instance) => (In order to be able to grab his order)
    product             = Product.objects.get(id=productID) # Take this with you you'll need it.
    order, createdOrder = Order.objects.get_or_create(customer=customer, isCompleted=False)
    # Search for an open Cart (Order) for this Customer left from previous sesssion => Get it, IF he doesn't have any => Open one (Cart) for the Customer (associated with his name). (It's not affect the 'orderItem' logic whether it's created or not)
    orderItem, created  = OrderItem.objects.get_or_create(order=order, product=product) 
    # New OrderItem #? => 'Create' an "OrderItem" instance of "Product": productID that he's clicked And handle it below & return resutls to be in the "Order": (New or Existed) Cart for the Customer. 
    # existed Oitem #? =>  'Get' the "OrderItem" instance of "Product": productID that he's clicked And handle it below & return resutls to be in the "Order": (New or Existed) Cart for this Customer. 

    if action == 'add':      # If the orderItem object got created => This is not gonna be affecting the quantity; Because once it's created the default quantity is going to be zero.
        orderItem.quantity += 1
    elif action == 'remove': # Available in the 'cart.html' page.
        orderItem.quantity -= 1
    
    orderItem.save()

    if orderItem.quantity <= 0: # For the 'cart.html' page.
        orderItem.delete()

    return JsonResponse("Item Was Added", safe=False) # Promise of Success (For confimation Purposes and other things)



def process_order_function(request:HttpRequest):
    data = json.loads(request.body)
    transactionID = datetime.datetime.now().timestamp()

    if request.user.is_authenticated:
        customer            = request.user.customer
        order, created      = Order.objects.get_or_create(customer=customer, isCompleted=False)
        FrontCartTotal      = float(data['userInfo']['total']) # Because we want to do some arithmetic Comparisons.
        order.transactionId = transactionID

        # Now we want to check if the Total price that is being passed in from the Front-End is valid and not Manipulated by Javascripter
        # By comparing the Front-End `total` value with the Back-End `total` value.
        if FrontCartTotal == order.get_cart_total_price:
            order.isCompleted = True
        order.save() 
        #! NOTE: You can put the 'order.save()' statement within the block of the `if statement` if you're not going to be the Merchant.
        #! Only for make things more clear for your Clients.
        # We want to save the order, whether the user has manipulated the data or not (For Advanced Purposes (Generating Reports))


        if order.needsShipping == True:
            ShippingAddress.objects.create(
                customer = customer, 
                order    = order, 
                country  = data['shippingInfo']['country'], 
                city     = data['shippingInfo']['city'], 
                address  = data['shippingInfo']['address'], 
                zipcode  = data['shippingInfo']['zipcode'], 
            )
    else:
        print("User is not Authenticated.")

    return JsonResponse("Payment Submitted", safe=False)