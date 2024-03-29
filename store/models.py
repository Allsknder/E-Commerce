from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Customer(models.Model):
    user  = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True) # We want to delete the Customer instance if the associated User instance is deleted.
    name  = models.CharField(max_length=120, null=True, blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)

    def __str__(self):
        return self.name # The name of the customer will be returned in his record in the Customer's Table in the Database.




class Product(models.Model):
    name      = models.CharField(max_length=120)
    price     = models.DecimalField(max_digits=15, decimal_places=2)
    isDigital = models.BooleanField(default=False) # Defaults to "Needs to be shipped"
    image     = models.ImageField(blank=True)

    def __str__(self):
        return self.name

    @property
    def get_image_url(self):
        try:
            url = self.image.url
        except:
            url = 'https://img.icons8.com/external-outline-design-circle/10000/000000/external-E-commerce-seo-development-and-marketing-outline-design-circle.png' 
            # In case the above URL breaks => You can use the image you have: 'http://localhost:8000/static/images/LogoLikeImageAlter.png'
        return url
        



class Order(models.Model):
    customer      = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True) # If the Customer got deleted, We don't want to delete the order!!, We just want to set the Customer's value in in the currecnt record in the Table to Null.
    date_ordered  = models.DateTimeField(auto_now_add=True)
    isCompleted   = models.BooleanField(default=False) # The cart is still open (still getting filled with products)
    transactionId = models.CharField(max_length=100)

    def __str__(self):
        return str(self.id) # Because the 'id' value is 'int' and we can't return an 'int' for the 'str' value (the whole magic method is string <__str__>)
        # return f"{self.customer.name}{' Order is ready to Shipped' if self.isCompleted else ' is still shopping'}" # Each record in the "Order" Table will be addressed -named- by {the customer's name, concatenated with the status of the order <whether it's completed or not} So (I Think) we can by only One Look to the Table in the Admin Panel know if there any order is done and pending to be shipped.
    
    @property
    def get_cart_total_price(self):
        orderItems = self.orderitem_set.all() # So now 'orderItem' variable is a QuerySet (list like) of objects of Type "OrderItem" 
        total      = sum([item.get_orderItem_total for item in orderItems])
        return float(total)
    
    @property
    def get_cart_items_number(self):
        orderItems = self.orderitem_set.all() # So now 'orderItem' variable is a QuerySet (list like) of objects of Type "OrderItem" 
        total      = sum([item.quantity for item in orderItems])
        return total
    
    @property
    def needsShipping(self):
        shipping   = False # By default: There's no need to shipping; All items are digital.
        orderItems = self.orderitem_set.all()
        for item in orderItems: # If there any order item in our Order has 'isDigital' set to False (which  means it's physical product) make shipping True.
            if item.product.isDigital == False:
                shipping = True
        return shipping




class OrderItem(models.Model):
    order     = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True) # an Order (cart) can have multiple OrderItems (products)
    product   = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True) # one Product (e.g: book) can be the type of many order items depending on the quantity.
    quantity  = models.IntegerField(default=0) # Required number of items for the same product.
    dataAdded = models.DateTimeField(auto_now_add=True)

    def __str__(self): # (Optional)
        return f"{self.order.customer} | {self.order} | {self.product.name} | {self.quantity}" # Each record in the "OrderItem" Table will be addressed (named) by {the product name, concatenated with the quantity required of that product}
    

    @property # Instance property method (Getter)
    def get_orderItem_total(self):
        return (self.product.price * self.quantity )




class ShippingAddress(models.Model): # null=False => means if an Instance got created from this class, Any field that is set as non-nullable (null=False in it) (Default if not set manually) must be filled with data, Otherwise the instance isn't gonna be created.
    #? The reason of attaching this class to both Customer & Order classes (even though only Order can do the task) is ONLY because if the Order for the Cutomer got deleted, We would still want to have the his ShippingAddress.    
    customer      = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True) # Customer can have many Shipping Addresses. #! (If the Customer got deleted, Don't delete their shipping address; Just put the value for cell to Null <The same for order field>)
    order         = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True) # Order can be shipped to many Shipping Addresses ((I Think) Accepts the shippig of the same order To the same customer BUT in multiple locations)
    country       = models.CharField(max_length=200) # Syria, Irag, Egypt, ...
    city          = models.CharField(max_length=200) # Governorate Like: Latakia, Swuida, Damascus, ...
    address       = models.CharField(max_length=300) # Detailed Address which Describes the way for the location.
    zipcode       = models.CharField(max_length=200, blank=True) # House Number if existed.
    dateSubmitted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address 
        # return f"{self.customer.name} | {self.address}"