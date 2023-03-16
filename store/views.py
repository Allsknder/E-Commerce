from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
import json
import datetime

from .models import *
from .OrderProcessors import cart_cookie, cart_data, guest_order_processor

# Create your views here.

def store_view(request:HttpRequest):
    data            = cart_data(request)
    cartItemsNumber = data['cartItemsNumber']

    products = Product.objects.all()
    context = {
        'products'        :  products,
        'cartItemsNumber' : cartItemsNumber
    }
    return render(request, 'shopping/store.html', context)



def cart_view(request:HttpRequest):
    cartData        = cart_data(request)
    orderItems      = cartData['items']
    order           = cartData['order']
    cartItemsNumber = cartData['cartItemsNumber']

    context = {
        'items'           : orderItems,
        'order'           : order, 
        'cartItemsNumber' : cartItemsNumber
    }
    return render(request, 'shopping/cart.html', context)



def checkout_view(request:HttpRequest):
    data            = cart_data(request)
    orderItems      = data['items']
    order           = data['order']
    cartItemsNumber = data['cartItemsNumber']


    context = {
        'items'           : orderItems, 
        'order'           : order, 
        'cartItemsNumber' : cartItemsNumber,
    }
    return render(request, 'shopping/checkout.html', context)



#! Functions.
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

# When open the site in `incognito mode` the 'csrf_token' is not getting generated in the 'main.html' template, So it's not being passed to the Backend 
# With the headers in the "fetch call" that is created in the 'checkout.html' page for some reason.
# So the commented ``import and decorator`` are a quick fix for such problem => (Since the data that are being sent are not too valuable)
# from django.views.decorators.csrf import csrf_exempt

# @csrf_exempt
def process_order_function(request:HttpRequest):
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer        = request.user.customer
        order, created  = Order.objects.get_or_create(customer=customer, isCompleted=False)   
    else:
        customer, order = guest_order_processor(request, data)
    
     #? Regardless of who is checking out, We still need to Confirm total price & creating transactionID & saving the order <And the ShippingAddress if needed> in the Database.
    
    # * Confirming Total Price.
    # Now we want to check if the Total price that is being passed in from the Front-End is valid and not Manipulated by Javascripter. HOW? By comparing the Front-End `total` value with the Back-End `total` value.
    FrontCartTotal      = float(data['userInfo']['total']) # Because we want to do some arithmetic Comparisons.
    if FrontCartTotal == order.get_cart_total_price:
        order.isCompleted = True

    # * Creating an ID number for each Transaction.
    transactionID = datetime.datetime.now().timestamp()
    order.transactionId = transactionID

    # * Saving the order in the Database.
    order.save() 
    # NOTE: You can put the 'order.save()' statement within the block of the `if statement` if you're not going to be the Merchant.
    # Only for make things more clear for your Clients.
    # We want to save the order, whether the user has manipulated the data or not (For Advanced Purposes (Generating Reports))
        
    
    # * Saving the Shipping Address for the customer in Database if needed.
    if order.needsShipping == True:
        ShippingAddress.objects.create(
            customer = customer, 
            order    = order, 
            country  = data['shippingInfo']['country'], 
            city     = data['shippingInfo']['city'], 
            address  = data['shippingInfo']['address'], 
            zipcode  = data['shippingInfo']['zipcode'], 
        )
    
    return JsonResponse("Payment Submitted", safe=False)
