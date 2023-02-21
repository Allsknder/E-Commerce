from django.shortcuts import render

# Create your views here.

def store_view(request):
    context = {}
    return render(request, 'shopping/store.html', context)


def cart_view(request):
    context = {}
    return render(request, 'shopping/cart.html', context)


def checkout_view(request):
    context = {}
    return render(request, 'shopping/checkout.html', context)

