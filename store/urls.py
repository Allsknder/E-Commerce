from django.urls import path

from .views import *

# Create your path for this App specifically here.

urlpatterns = [
    path('', store_view, name="store"), 
    path('cart/', cart_view, name="cart"), 
    path('checkout/', checkout_view, name="checkout"), 
    path('update_item/', update_item_function, name="update-item"),
    path('process_order/', process_order_function, name="process-order")

]