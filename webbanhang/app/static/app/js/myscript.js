$('#slider1, #slider2, #slider3').owlCarousel({
    loop: true,
    margin: 20,
    responsiveClass: true,
    responsive: {
        0: {
            items: 2,
            nav: false,
            autoplay: true,
        },
        600: {
            items: 4,
            nav: true,
            autoplay: true,
        },
        1000: {
            items: 6,
            nav: true,
            loop: true,
            autoplay: true,
        }
    }
})

$('.plus-cart').click(function(){
    var id=$(this).attr("pid").toString();
    var eml=this.parentNode.children[2] 
    $.ajax({
        type:"GET",
        url:"/pluscart",
        data:{
            prod_id:id
        },
        success:function(data){
            eml.innerText=data.quantity 
            document.getElementById("amount").innerText=data.amount 
            document.getElementById("totalamount").innerText=data.totalamount
        }
    })
})

$('.minus-cart').click(function(){
    var id=$(this).attr("pid").toString();
    var eml=this.parentNode.children[2] 
    $.ajax({
        type:"GET",
        url:"/minuscart",
        data:{
            prod_id:id
        },
        success:function(data){
            eml.innerText=data.quantity 
            document.getElementById("amount").innerText=data.amount 
            document.getElementById("totalamount").innerText=data.totalamount
        }
    })
})


$('.remove-cart').click(function(){
    var id=$(this).attr("pid").toString();
    var eml=this
    $.ajax({
        type:"GET",
        url:"/removecart",
        data:{
            prod_id:id
        },
        success:function(data){
            document.getElementById("amount").innerText=data.amount 
            document.getElementById("totalamount").innerText=data.totalamount
            eml.parentNode.parentNode.parentNode.parentNode.remove() 
        }
    })
})


$('.plus-wishlist').click(function(){
    var id=$(this).attr("pid").toString();
    $.ajax({
        type:"GET",
        url:"/pluswishlist",
        data:{
            prod_id:id
        },
        success:function(data){
            //alert(data.message)
            window.location.href = `http://localhost:8000/product-detail/${id}`
        }
    })
})


$('.minus-wishlist').click(function(){
    var id=$(this).attr("pid").toString();
    $.ajax({
        type:"GET",
        url:"/minuswishlist",
        data:{
            prod_id:id
        },
        success:function(data){
            window.location.href = `http://localhost:8000/product-detail/${id}`
        }
    })
})

// cart
function formatVND(number) {
  return number.toLocaleString('vi-VN') + 'đ';
}

function updateTotal() {
  let total = 0;

  document.querySelectorAll('.cart-item').forEach(item => {
    const price = parseInt(item.dataset.price);
    const qty = parseInt(item.querySelector('.quantity').value) || 0;
    total += price * qty;
  });

  const totalEl = document.getElementById('totalPrice');
  if (!totalEl) return;

  totalEl.innerText = formatVND(total);
}

// document.querySelectorAll('.btn-plus').forEach(btn => {
//   btn.addEventListener('click', () => {
//     const input = btn.parentElement.querySelector('.quantity');
//     input.value = parseInt(input.value) + 1;
//     updateTotal();
//   });
// });

// document.querySelectorAll('.btn-minus').forEach(btn => {
//   btn.addEventListener('click', () => {
//     const input = btn.parentElement.querySelector('.quantity');
//     let value = parseInt(input.value) - 1;
//     if (value < 1) value = 1;
//     input.value = value;
//     updateTotal();
//   });
// });

document.querySelectorAll('.quantity').forEach(input => {
  input.addEventListener('input', updateTotal);
});

updateTotal();


// checkout

let quantity = 1;
let discount = 0;



document.querySelectorAll('.btn-plus').forEach(btn=>{
  btn.addEventListener('click', ()=>{
    const input = btn.parentElement.querySelector('.quantity');
    quantity = parseInt(input.value) + 1;
    input.value = quantity;
    render();
    updateTotal();
  });
});

document.querySelectorAll('.btn-minus').forEach(btn=>{
  btn.addEventListener('click', ()=>{
    const input = btn.parentElement.querySelector('.quantity');
    quantity = Math.max(1, parseInt(input.value) - 1);
    input.value = quantity;
    render();
    updateTotal();
  });
});

document.querySelectorAll('.quantity').forEach(input=>{
  input.addEventListener('input', ()=>{
    quantity = parseInt(input.value) || 1;
    render();
  });
});

function formatVND(n){return n.toLocaleString('vi-VN')+'đ'}

function render(){
  const subtotal_text = document.getElementById('subtotal')
  if (!subtotal_text) return;
  
  const subtotal = parseInt(subtotal_text.getAttribute('data-value')) || 0;
  subtotal_text.innerText = formatVND(subtotal);
  
  const discount_text = document.getElementById('discount')
  if (discount_text) discount_text.innerText = formatVND(discount);
  
  const final_text = document.getElementById('final')
  if (final_text) final_text.innerText = formatVND(subtotal - discount);
}

function applyCoupon(){
  const code = document.getElementById('coupon').value.trim();
  const subtotal_text = document.getElementById('subtotal');
  const subtotal = subtotal_text ? (parseInt(subtotal_text.getAttribute('data-value')) || 0) : 0;
  
  if(code==='SALE10') discount = subtotal * 0.1;
  else if(code==='SALE20') discount = subtotal * 0.2;
  else discount = 0;
  render();
}

render();

// const cartBtn = document.getElementById("cartBtn");
// const cartDropdown = document.getElementById('cartDropdown');
 
// if (cartBtn && cartDropdown) {
//   cartBtn.addEventListener('click', (e) => {
//     // console.log('cartBtn clicked');
//     // e.preventDefault();
//     // cartDropdown.classList.toggle('active');
//   });

//   // click outside to close
//   window.addEventListener('click', (e) => {
//     if (!cartDropdown.contains(e.target) && !cartBtn.contains(e.target)) {
//       cartDropdown.classList.remove('active');
//     }
//   });
// }