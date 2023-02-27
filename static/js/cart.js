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
                console.log('User is NOT Authenticated!')
            }
            else 
            {
                update_user_order(productId, action)
            }
        }
    )
}

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