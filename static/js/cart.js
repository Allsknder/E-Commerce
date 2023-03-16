var updateBtns = document.getElementsByClassName("update-cart")

for (var i = 0; i < updateBtns.length; i++)
{
    updateBtns[i].addEventListener('click', function()
        {
            // This function will execute on each iteration (each click for a button)
            var productId = this.dataset.product
            var action    = this.dataset.action

            // Little are the information that we know about the user till this point, But once the user clicks any 'add to cart' button =>
            // We're gonna be querying their status.
            console.log('USER:', user)
            if (user == 'AnonymousUser')
            {
                addCookieItem(productId, action)
            }
            else 
            {
                update_user_order(productId, action)
            }
        }
    )
}

// Function for Guest User.
function addCookieItem(product, action)
{
    console.log("User is not Authenticated Creating the Cart Cookie...")
    
    // The structure of the cart JS object.
    // cart = {
    //     1 : {'quantity' : 4},
    //     2 : {'quantity' : 3},
    //     4 : {'quantity' : 1}
    // }
    // cart[1]['quantity']

    if (action == 'add')
    {
        if (cart[product] == undefined )
        {
            cart[product] = {'quantity' : 1}
        }
        else 
        {
            cart[product]['quantity'] += 1
        }
    }

    if (action == 'remove') 
    {
        cart[product]['quantity'] -= 1
        // We know it does exist becuase the action of 'remove' is only got sent when the down arrow in the 'cart.html' page got clicked, So that we directly decreased the quantity.
        if (cart[product]['quantity'] <= 0)
        {
            console.log("Removing Item...")
            delete cart[product]
        }
    }

    console.log('Updated Cart:', cart)
    // Here we want to send the updated cart content to the browser so the page can reload safely without losing user's cart data.
    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"

    // We're gonna be reloading the website whenever 'add' or 'remove' actions are happenning so we can update the "Cart Total" in each page.
    location.reload()
}


// Function for Authenticated User.
function update_user_order(product, action)
{
    console.log('User is Authenticated, Sending Data...')

    // We want to use the name of the view instead of its URL, And we're gonna be doing that using the 'main.html' tempalte.
    var url = viewName

    fetch(url, {
        method  : 'POST', 
        headers : {
            'Content-Type' : 'application/json', 
            'X-CSRFToken'  : csrftoken
        },
        body    : JSON.stringify ({ // Got Sent to the Back-End As a type that can be Loaded to Python data type 'dict'. (without the need to serialization)
            'productID'    : product,
            'action'       : action 
        })
    })
    // The return object (respone) from the function-based view that processed this POST Request.
    .then(response => {
        return response.json();
    })
    .then(data => {
        console.log('Data:', data)
        location.reload()
    })


}