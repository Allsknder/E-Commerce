from django.http import HttpRequest
import json
import datetime


from .models import *

# !NOTE: User is: 1) Customer, 2) Client (Supplier, Merchant)

def cart_data(request:HttpRequest) -> dict:
    #* Two Scenarios of Querying Data (Preparing the Cart) are going to be created for Customers:
    # 1) Authenticated Customer.
    if request.user.is_authenticated: # if the customer is registered with our website.
        customer        = request.user.customer # Grab the customer associated to that user. (so we can grab the customer's cart <order>)
        order, created  = Order.objects.get_or_create(customer=customer, isCompleted=False) # Grab the Customer's open cart (Not Compeleted Order) or create it.
        orderItems      = order.orderitem_set.all() 
        cartItemsNumber =  order.get_cart_items_number
        # 1) If the customer had the cart with items in it (The Cart isn't created), Grab it with its items. So the customer can continue shopping.
        # 2) If the cart was empty (or the cart got created) the `order.orderitem_set.all()` will return a blank List as a value to the 'orderItems' variable. (and that's okay)
        # 3) NOTE: The type of the `orderItems` var is: "django.db.models.query.QuerySet" which is 'List' (of objects) after all. (and here objects of type "OrderItem")
        # 4) Reference for `_set.all()` => https://tekshinobi.com/_set-meaning-in-django-many-to-many-relationship/

    # 2) Guest Customer.
    else: # If the cusotmer is not registered we don't want the cart page to break once the customer clicks his cart, Instead Return an empty list.
        cartData        = cart_cookie(request)
        orderItems      = cartData['items']
        order           = cartData['order']
        cartItemsNumber = cartData['cartItemsNumber']
    
    return {
        'items'           : orderItems,     # For the Body of 'cart.html' & 'checkout.html'
        'order'           : order,          # For (Total price, Total items in the order, status of shipping)
        'cartItemsNumber' : cartItemsNumber # For the Navbar Cart Icon.
    }



def cart_cookie(request:HttpRequest) -> dict:
    order = {
            'get_cart_items_number' : 0,      # For the total number of items in the upper part of the 'cart.html' & the lower right-sided part of the 'checkout.html' page.
            'get_cart_total_price'  : 0,      # For the total price in the upper part of the 'cart.html' & the lower right-sided part of the 'checkout.html' page.
            'needsShipping'         : False   # For Showing & Hiding the 'Shipping' HTML Form.
        }

    orderItems      = []                             # For the lower part (body) of the 'cart.html' page and the upper right-sided part of the 'checkout.html' page.
    cartItemsNumber = order['get_cart_items_number'] # For the Navbar Cart Icon.
    
    # Quering 'cart' Cookie value.
    # On the Guest User first visit to our website, He won't be having any 'cart' Cookie (Which we're querying here and <which got created in the 'main.html'>) => This will raise a "Key Error"
    # So we'll create a dummy "cart" value (empty dict) here for this view to avoid that exception.
    # REMEMBER: The WSGI Request firstly go to the view processor than the view returns the HTML templates that must be returned, This is the reason why the cart cookie can't be created on the first visit.
    try: 
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}
    
    
    for proIdAsKey in cart:
        try:
            cartItemsNumber += cart[proIdAsKey]['quantity'] 

            product = Product.objects.get(id=proIdAsKey)
            total   = (product.price * cart[proIdAsKey]['quantity']) # `total price` value for each orderItem.

            order['get_cart_total_price']  += total
            order['get_cart_items_number'] += cart[proIdAsKey]['quantity'] 

            item = {
                'product'             : {
                    'id'            : product.id,
                    'name'          : product.name,
                    'price'         : product.price,
                    'get_image_url' : product.get_image_url
                },
                'quantity'            : cart[proIdAsKey]['quantity'],
                'get_orderItem_total' : total
            }
            
            orderItems.append(item)

            if product.isDigital == False:
                order['needsShipping'] = True 
    
        # ? Why `try - except` Entity?
        # If the Guest Customer specified a product to buy and didn't complete the transaction, 
        # The product Id for the product for that customer is saved in the Cookies
        # and once that customer comes back in to the website to complete his transaction (before the cookie expiration date)
        # * Suppose that product got sold !!
        # then (When querying the product object here with the `id=proIdAsKey`) it'll throw "DoesNotExist" exception
        # And here where we handle it. (One of the potential scenarios)
        except: 
            pass 
            # ! BUG:
            # ? When the user add a product to the cart and get out of the site, When he comes back; If that product was sold,
            # ? The item (that got sold) quantity would still appear in the Navbar Cart Icon but not in any other place (not in the "oder['get_cart_items_numer']")
            # Potential Error:
            # The 'cartItemsNumber' variable here is defined out (above) of the 'try - except' block So its' Global line (16).
            # Potential Solutions:
            # 1) Move the defintion to inside the for loop.
            # 2) Query the cart orderItems and check if they exist in the Stock Each time the user with a filled open cart comes back again to 
            #    The site & update the cartItemsNumber basing on that.


    return {
        'items'           : orderItems,     # For the Body of 'cart.html' & 'checkout.html'
        'order'           : order,          # For (Total price, Total items in the order, status of shipping)
        'cartItemsNumber' : cartItemsNumber # For the Navbar Cart Icon.
    }



from .forms import CustomerForm

def guest_order_processor(request:HttpRequest, data):
    print("User is not Authenticated")
    print("PyCookies: ", request.COOKIES)

    # * Getting Guest Customer information.
    name  = data['userInfo']['name']
    
    form = CustomerForm(data['userInfo']) 
    if form.is_valid(): 
        phone = form.cleaned_data.get('phone') 
    elif form.is_valid() == False:
        print(form.errors)


    # Querying or Creating the Customer, => We'll Link the Guest Customer's orders with his Phone Number <Making kinda relation> (AlgoExp: LinkingGuestPhoneNumber.txt)
    customer, created = Customer.objects.get_or_create(phone=phone)
    # And for this Customer <once we find them or create them> we also want to set their name value.
    customer.name  = name # In case the same customer decided to change their name, (That's why it's outside the 'get_or_create()' method)
    if data['userInfo']['email']: # Because it's an Optional Field and can be (Blank (not required))
        customer.email = data['userInfo']['email']
    customer.save()

    # * Getting Guest Customer Cookie Cart items.
    cookieData = cart_cookie(request) 
    # Getting Guest Customer order items.
    items      = cookieData['items'] # List of Dicts, Each dict represents an orderItem.
    # Creating and saving the Customer's Order (each orderItem in the cart) in the Database, (Along with the shipping address), Then attaching all of them to the following 'order' object.
    order = Order.objects.create(customer = customer, isCompleted = False) # `isCompleted = False` until the payment processing has actually went through.

    # On each iteration we're gonna create an orderItem in the <Found or created> Customer's <order> in the Database.
    for item in items:
        product   = Product.objects.get(id=item['product']['id'])
        orderItem = OrderItem.objects.create(product=product, order=order, quantity=item['quantity'])

    return customer, order