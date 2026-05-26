// Toast Notification System helper
if (!document.getElementById('toast-styles')) {
    var style = document.createElement('style');
    style.id = 'toast-styles';
    style.innerHTML = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes fadeOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
        .toast-slide-in {
            animation: slideIn 0.3s forwards ease-out;
        }
        .toast-fade-out {
            animation: fadeOut 0.4s forwards ease-in;
        }
        .custom-toast {
            display: flex !important;
            opacity: 1 !important;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15) !important;
            background: rgba(255, 255, 255, 0.98) !important;
            backdrop-filter: blur(10px);
            border-radius: 12px;
            margin-bottom: 10px;
            width: 350px;
            border-left: 4px solid #e65540 !important;
            transition: all 0.3s ease;
        }
    `;
    document.head.appendChild(style);
}

function showToast(title, message, imageUrl = null) {
    var toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'position-fixed bottom-0 end-0 p-3';
        toastContainer.style.zIndex = '2000';
        document.body.appendChild(toastContainer);
    }
    
    var toastId = 'toast-' + Date.now();
    var imgHtml = imageUrl ? `<img src="${imageUrl}" class="rounded me-2" alt="product" style="width: 45px; height: 45px; object-fit: cover; border: 1px solid #eaeaea;">` : '';
    
    var toastHtml = `
        <div id="${toastId}" class="custom-toast align-items-center border-0 toast-slide-in" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="w-100">
                <div class="toast-header bg-transparent border-0 pt-3 px-3 pb-2 d-flex align-items-center">
                    <span class="rounded-circle me-2 bg-success d-flex align-items-center justify-content-center text-white" style="width: 20px; height: 20px;">
                        <i class="fas fa-check" style="font-size: 10px;"></i>
                    </span>
                    <strong class="me-auto text-dark" style="font-family: 'Montserrat', sans-serif; font-size: 14px;">${title}</strong>
                    <button type="button" class="btn-close ms-2" aria-label="Close" style="font-size: 10px;"></button>
                </div>
                <div class="toast-body px-3 pb-3 pt-0 d-flex align-items-center">
                    ${imgHtml}
                    <div style="font-size: 13px; color: #4a4a4a; font-family: 'Montserrat', sans-serif; line-height: 1.4;">
                        ${message}
                    </div>
                </div>
            </div>
        </div>
    `;
    
    var tempDiv = document.createElement('div');
    tempDiv.innerHTML = toastHtml;
    var toastEl = tempDiv.firstElementChild;
    toastContainer.appendChild(toastEl);
    
    // Auto-remove toast after 4 seconds
    setTimeout(function() {
        toastEl.classList.remove('toast-slide-in');
        toastEl.classList.add('toast-fade-out');
        setTimeout(function() {
            toastEl.remove();
        }, 500);
    }, 4000);

    // Manual close handler
    var closeBtn = toastEl.querySelector('.btn-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            toastEl.classList.remove('toast-slide-in');
            toastEl.classList.add('toast-fade-out');
            setTimeout(function() {
                toastEl.remove();
            }, 500);
        });
    }
}

// Redraw Mini-Cart elements dynamically
function updateMiniCartUI(data) {
    // 1. Update Badge
    var badge = document.getElementById('cart-badge');
    if (badge) {
        badge.innerText = data.cart_items_count;
        badge.style.display = data.cart_items_count > 0 ? 'inline-block' : 'none';
    }
    
    // 2. Update Total Amount
    var totalAmount = document.getElementById('cart-total-amount');
    if (totalAmount) {
        totalAmount.innerText = data.cart_total;
    }
    
    // 3. Update Dropdown Items list
    var itemsContainer = document.querySelector('.cart-items');
    if (itemsContainer) {
        itemsContainer.innerHTML = '';
        if (data.items.length === 0) {
            itemsContainer.innerHTML = '<div class="text-center py-4 text-muted empty-cart-msg">Giỏ hàng của bạn đang trống.</div>';
            return;
        }
        
        data.items.forEach(function(item) {
            var oldPriceHtml = item.product_old_price ? `<span class="text-muted text-decoration-line-through" style="font-size: 11px;">${item.product_old_price}</span>` : '';
            var variantHtml = item.variant_title ? `<div class="text-uppercase text-danger fw-bold" style="font-size: 10px; margin-top: 2px;">${item.variant_title}</div>` : '';
            
            var itemHtml = `
                <div class="cart-item-mini d-flex align-items-start py-3 border-bottom">
                  <img src="${item.product_image}" class="border" style="width: 80px; height: 80px; object-fit: cover;">
                  <div class="flex-grow-1 ms-3">
                    <div class="fw-bold text-uppercase" style="font-size: 12px; color: #4a4a4a; line-height: 1.4;">${item.product_name}</div>
                    ${variantHtml}
                    <div class="text-uppercase text-muted" style="font-size: 11px; margin-top: 4px;"></div>
                    
                    <div class="d-flex justify-content-between align-items-center mt-2">
                      <div class="d-flex align-items-center">
                        <div class="bg-light text-center me-2 text-secondary" style="width: 25px; height: 25px; line-height: 25px; font-size: 12px;">${item.quantity}</div>
                        <span class="fw-bold me-2" style="font-size: 13px; color: #333;">${item.product_price}</span>
                        ${oldPriceHtml}
                      </div>
                      <button class="btn btn-sm btn-light p-0 border d-flex align-items-center justify-content-center fw-bold update-cart" 
                              data-product="${item.product_id}" 
                              data-action="delete" 
                              data-variant="${item.variant_id || ''}"
                              style="width: 20px; height: 20px; background: #eee; font-size: 12px; line-height: 12px;">
                        &times;
                      </button>
                    </div>
                  </div>
                </div>
            `;
            itemsContainer.insertAdjacentHTML('beforeend', itemHtml);
        });
    }
}

// Event Delegation for all Cart Actions
document.addEventListener('click', function(e) {
    var button = e.target.closest('.update-cart');
    if (button) {
        e.preventDefault();
        var productId = button.dataset.product;
        var action = button.dataset.action;
        var variantId = button.dataset.variant || null;
        var quantity = parseInt(button.dataset.quantity || 1);
        console.log('productId:', productId, 'action:', action, 'variantId:', variantId, 'quantity:', quantity);
        
        if (user === 'AnonymousUser') {
            addCookieItem(productId, action, variantId, quantity);
        } else {
            updateUserOrder(productId, action, variantId, quantity);
        }
    }
});

function updateUserOrder(productId, action, variantId, quantity = 1){
    console.log('User is authenticated, sending request...');
    var url = '/update_item/';
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
            'productId': productId,
            'action': action,
            'variantId': variantId,
            'quantity': quantity
        })
    })
    .then((response) => response.json())
    .then((data) => {
        console.log('Data:', data);
        var path = window.location.pathname;
        if (path === '/cart/' || path === '/checkout/' || path.indexOf('/profile/') !== -1) {
            location.reload();
        } else {
            updateMiniCartUI(data);
            
            if (action == 'add') {
                var addedItem = data.items.find(item => item.product_id == productId && (!variantId || item.variant_id == variantId));
                if (addedItem) {
                    showToast(
                        "Đã thêm vào giỏ hàng",
                        `Bạn đã thêm <strong>${addedItem.product_name}</strong> vào giỏ hàng thành công.`,
                        addedItem.product_image
                    );
                } else {
                    showToast("Đã thêm vào giỏ hàng", "Đã cập nhật giỏ hàng thành công.");
                }
            } else if (action == 'delete') {
                showToast("Đã xóa sản phẩm", "Đã xóa sản phẩm khỏi giỏ hàng thành công.");
            }
        }
    })
    .catch((error) => {
        console.error('Error updating order:', error);
    });
}

function addCookieItem(productId, action, variantId, quantity = 1){
    console.log('User is not authenticated, adding to cookie...');
    var key = variantId ? productId + '_' + variantId : productId;
    
    if (action == 'add') {
        if (cart[key] == undefined) {
            cart[key] = {'quantity': quantity};
        } else {
            cart[key]['quantity'] += quantity;
        }
    }

    if (action == 'remove') {
        if (cart[key] != undefined) {
            cart[key]['quantity'] -= quantity;
            if (cart[key]['quantity'] <= 0) {
                delete cart[key];
            }
        }
    }

    if (action == 'delete') {
        delete cart[key];
    }

    console.log('CART:', cart);
    
    var expDays = 30; 
    var date = new Date();
    date.setTime(date.getTime() + (expDays * 24 * 60 * 60 * 1000));
    var expires = "expires=" + date.toUTCString();
    
    document.cookie = 'cart=' + JSON.stringify(cart) + ";" + expires + ";domain=;path=/";
    
    var path = window.location.pathname;
    if (path === '/cart/' || path === '/checkout/' || path.indexOf('/profile/') !== -1) {
        location.reload();
    } else {
        // Fetch get_cart_data to update UI dynamically
        fetch('/get_cart_data/')
        .then(response => response.json())
        .then(data => {
            updateMiniCartUI(data);
            
            if (action == 'add') {
                var addedItem = data.items.find(item => item.product_id == productId && (!variantId || item.variant_id == variantId));
                if (addedItem) {
                    showToast(
                        "Đã thêm vào giỏ hàng",
                        `Bạn đã thêm <strong>${addedItem.product_name}</strong> vào giỏ hàng thành công.`,
                        addedItem.product_image
                    );
                } else {
                    showToast("Đã thêm vào giỏ hàng", "Đã cập nhật giỏ hàng thành công.");
                }
            } else if (action == 'delete') {
                showToast("Đã xóa sản phẩm", "Đã xóa sản phẩm khỏi giỏ hàng thành công.");
            }
        })
        .catch((error) => {
            console.error('Error fetching cart data:', error);
        });
    }
}