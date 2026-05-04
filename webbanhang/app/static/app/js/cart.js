var updateBtns = document.getElementsByClassName('update-cart')
for (var i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function() {
        var productId = this.dataset.product
        var action = this.dataset.action
        console.log('productId:', productId, 'action:', action)
        if (user === 'AnonymousUser') {
            addCookieItem(productId, action)
        }else{
            updateUserOrder(productId, action)
        }
    })
}

function updateUserOrder(productId, action){
    console.log('User is authenticated, sending request...')
    var url = '/update_item/'
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
             'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
            'productId': productId,
            'action': action,
        })
    })
    .then((response) => {
        return response.json()
    })
    .then((data) => {
        console.log('Data:', data)
        location.reload()
    })
}

function addCookieItem(productId, action){
    console.log('User is not authenticated, adding to cookie...');
    
    if (action == 'add') {
        if (cart[productId] == undefined) {
            cart[productId] = {'quantity': 1};
        } else {
            cart[productId]['quantity'] += 1;
        }
    }

    if (action == 'remove') {
        cart[productId]['quantity'] -= 1;
        if (cart[productId]['quantity'] <= 0) {
            console.log('Item should be deleted');
            delete cart[productId];
        }
    }

    if (action == 'delete') {
        console.log('Item deleted completely');
        delete cart[productId];
    }

    console.log('CART:', cart);
    
    // Tự cài đặt thời gian sống của cookie (ví dụ: 30 ngày)
    var expDays = 30; // Bạn có thể thay đổi số ngày lưu cookie tại đây
    var date = new Date();
    date.setTime(date.getTime() + (3600 * 1000));
    var expires = "expires=" + date.toUTCString();
    
    // Lưu lại cookie với thời hạn 
    document.cookie = 'cart=' + JSON.stringify(cart) + ";" + expires + ";domain=;path=/";
    
    // Reload lại trang sau khi cập nhật dữ liệu giỏ hàng vào cookie
    location.reload();
}