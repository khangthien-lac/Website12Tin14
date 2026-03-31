// ===== Cart with localStorage (no server needed, GitHub Pages ready) =====

function getCart() {
  try {
    return JSON.parse(localStorage.getItem("tour_cart")) || {};
  } catch {
    return {};
  }
}

function saveCart(cart) {
  localStorage.setItem("tour_cart", JSON.stringify(cart));
}

function getCartItems() {
  const cart = getCart();
  const items = [];
  for (const id in cart) {
    const d = cart[id];
    items.push({
      id,
      name: d.name,
      price: d.price,
      qty: d.qty,
      total: d.price * d.qty,
    });
  }
  return items;
}

function getCartTotal() {
  return getCartItems().reduce((sum, i) => sum + i.total, 0);
}

function formatPrice(price) {
  return Number(price).toLocaleString("vi-VN") + " VND";
}

function showNotification(msg) {
  let box = document.getElementById("cart-notification");
  if (!box) {
    box = document.createElement("div");
    box.id = "cart-notification";
    box.style.cssText =
      "position:fixed;top:20px;right:20px;background:#4CAF50;color:#fff;padding:14px 24px;border-radius:8px;z-index:9999;font-size:15px;box-shadow:0 4px 12px rgba(0,0,0,.2);transition:opacity .4s";
    document.body.appendChild(box);
  }
  box.textContent = msg;
  box.style.opacity = "1";
  clearTimeout(box._timer);
  box._timer = setTimeout(() => (box.style.opacity = "0"), 2500);
}

function getTotalCartCount() {
  let total = 0;
  try {
    const tourCart = JSON.parse(localStorage.getItem("tour_cart") || '{}');
    for (const id in tourCart) {
      total += Number(tourCart[id].qty) || 0;
    }
  } catch(e) {}
  try {
    const hotelCart = JSON.parse(localStorage.getItem("hotel_cart") || '[]');
    hotelCart.forEach(it => { total += Number(it.qty) || 0; });
  } catch(e) {}
  try {
    const shopCart = JSON.parse(localStorage.getItem("vs2t_cart") || '[]');
    shopCart.forEach(it => { total += Number(it.qty) || 0; });
  } catch(e) {}
  try {
    const flightCart = JSON.parse(localStorage.getItem("flightCart") || '[]');
    flightCart.forEach(it => { 
      total += (Number(it.adults) || 0) + (Number(it.children) || 0) + (Number(it.infants) || 0); 
    });
  } catch(e) {}
  return total;
}

function updateCartBadge() {
  const total = getTotalCartCount();
  document.querySelectorAll('.nav-cart').forEach(navCart => {
    let badge = navCart.querySelector('.cart-badge');
    if (!badge) {
      badge = document.createElement('span');
      badge.className = 'cart-badge';
      badge.style.cssText = 'display:inline-block;background-color:var(--primary-color,#e74c3c);color:#fff;border-radius:50%;padding:2px 6px;font-size:12px;margin-left:6px;';
      navCart.appendChild(badge);
    }
    badge.textContent = total;
    badge.style.display = total > 0 ? 'inline-block' : 'none';
  });
}

document.addEventListener('DOMContentLoaded', updateCartBadge);
window.addEventListener('storage', updateCartBadge);

// ---- Add to cart (from tour detail pages) ----
function addToCart(id, name, price) {
  const cart = getCart();
  if (cart[id]) {
    cart[id].qty += 1;
  } else {
    cart[id] = { name, price, qty: 1 };
  }
  saveCart(cart);
  showNotification('Đã thêm "' + name + '" vào giỏ hàng!');
}

// ---- Load cart page (GIỎ HÀNG.html) ----
function loadCart() {
  const container = document.getElementById("cart-items");
  if (!container) return;
  const items = getCartItems();
  renderCart(items, getCartTotal());
}

function renderCart(items, total) {
  const container = document.getElementById("cart-items");
  const totalDiv = document.getElementById("cart-total");
  const checkoutDiv = document.getElementById("checkout-section");

  if (!items || items.length === 0) {
    container.innerHTML =
      '<p style="text-align:center;padding:40px;font-size:18px">🛒 Giỏ hàng trống</p>' +
      '<p style="text-align:center"><a href="index.html" style="color:#3498db">← Tiếp tục xem tour</a></p>';
    if (totalDiv) totalDiv.textContent = "";
    if (checkoutDiv) checkoutDiv.style.display = "none";
    return;
  }

  let html = '<table style="width:100%;border-collapse:collapse;margin:20px 0">';
  html += '<tr style="background:#f5f5f5">';
  html += '<th style="padding:10px;text-align:left;border-bottom:2px solid #ddd">Sản phẩm</th>';
  html += '<th style="padding:10px;text-align:right;border-bottom:2px solid #ddd">Đơn giá</th>';
  html += '<th style="padding:10px;text-align:center;border-bottom:2px solid #ddd">Số lượng</th>';
  html += '<th style="padding:10px;text-align:right;border-bottom:2px solid #ddd">Thành tiền</th>';
  html += '<th style="padding:10px;text-align:center;border-bottom:2px solid #ddd">Xóa</th>';
  html += "</tr>";

  for (const item of items) {
    html += '<tr style="border-bottom:1px solid #eee">';
    html += '<td style="padding:10px">' + item.name + "</td>";
    html += '<td style="padding:10px;text-align:right">' + formatPrice(item.price) + "</td>";
    html += '<td style="padding:10px;text-align:center">';
    html += '<button onclick="updateQty(\'' + item.id + "'," + (item.qty - 1) + ')" style="width:28px;cursor:pointer;border:1px solid #ccc;background:#fff;border-radius:4px">-</button>';
    html += '<span style="margin:0 8px;font-weight:bold">' + item.qty + "</span>";
    html += '<button onclick="updateQty(\'' + item.id + "'," + (item.qty + 1) + ')" style="width:28px;cursor:pointer;border:1px solid #ccc;background:#fff;border-radius:4px">+</button>';
    html += "</td>";
    html += '<td style="padding:10px;text-align:right;font-weight:bold">' + formatPrice(item.total) + "</td>";
    html += '<td style="padding:10px;text-align:center">';
    html += '<button onclick="removeItem(\'' + item.id + '\')" style="color:red;cursor:pointer;background:none;border:none;font-size:18px">✕</button>';
    html += "</td></tr>";
  }

  html += "</table>";
  container.innerHTML = html;
  if (totalDiv)
    totalDiv.innerHTML =
      '<strong style="font-size:20px">Tổng cộng: ' + formatPrice(total) + " VND</strong>";
  if (checkoutDiv) checkoutDiv.style.display = "block";
}

function updateQty(id, qty) {
  const cart = getCart();
  if (qty <= 0) {
    delete cart[id];
  } else {
    cart[id].qty = qty;
  }
  saveCart(cart);
  loadCart();
}

function removeItem(id) {
  const cart = getCart();
  delete cart[id];
  saveCart(cart);
  loadCart();
}

function checkout() {
  const nameEl = document.getElementById("customer-name");
  const emailEl = document.getElementById("customer-email");
  const phoneEl = document.getElementById("customer-phone");

  const name = nameEl ? nameEl.value.trim() : "";
  const email = emailEl ? emailEl.value.trim() : "";
  const phone = phoneEl ? phoneEl.value.trim() : "";

  if (!name || !email) {
    alert("Vui lòng nhập tên và email!");
    return;
  }

  const items = getCartItems();
  const total = getCartTotal();
  const orderId = "DH" + Date.now();
  const dateStr = new Date().toLocaleString("vi-VN");

  // Save order to localStorage
  const orders = JSON.parse(localStorage.getItem("tour_orders") || "[]");
  orders.push({ orderId, name, email, phone, items, total, date: dateStr });
  localStorage.setItem("tour_orders", JSON.stringify(orders));

  // Clear cart
  localStorage.removeItem("tour_cart");

  // Show invoice
  const container = document.getElementById("cart-items");
  const totalDiv = document.getElementById("cart-total");
  const checkoutDiv = document.getElementById("checkout-section");

  let html = '<div style="text-align:center;padding:20px">';
  html += '<h2 style="color:#27ae60">✅ Đặt hàng thành công!</h2>';
  html += '<p style="color:#666">Mã đơn hàng: <strong>' + orderId + '</strong></p>';
  html += '</div>';

  html += '<table style="width:100%;border-collapse:collapse;margin:20px 0">';
  html += '<tr style="background:#f5f5f5">';
  html += '<th style="padding:10px;text-align:left;border:1px solid #ddd">Sản phẩm</th>';
  html += '<th style="padding:10px;text-align:center;border:1px solid #ddd">SL</th>';
  html += '<th style="padding:10px;text-align:right;border:1px solid #ddd">Đơn giá</th>';
  html += '<th style="padding:10px;text-align:right;border:1px solid #ddd">Thành tiền</th>';
  html += '</tr>';

  for (let i = 0; i < items.length; i++) {
    const it = items[i];
    html += '<tr>';
    html += '<td style="padding:8px;border:1px solid #ddd">' + it.name + '</td>';
    html += '<td style="padding:8px;text-align:center;border:1px solid #ddd">' + it.qty + '</td>';
    html += '<td style="padding:8px;text-align:right;border:1px solid #ddd">' + formatPrice(it.price) + '</td>';
    html += '<td style="padding:8px;text-align:right;border:1px solid #ddd">' + formatPrice(it.total) + '</td>';
    html += '</tr>';
  }

  html += '</table>';
  html += '<p style="text-align:right;font-size:18px;font-weight:bold;margin:20px 0">Tổng cộng: ' + formatPrice(total) + ' VND</p>';
  html += '<div style="background:#f8f9fa;padding:15px;border-radius:8px;margin:20px 0">';
  html += '<p><strong>Khách hàng:</strong> ' + name + '</p>';
  html += '<p><strong>Email:</strong> ' + email + '</p>';
  if (phone) html += '<p><strong>SĐT:</strong> ' + phone + '</p>';
  html += '<p><strong>Ngày:</strong> ' + dateStr + '</p>';
  html += '</div>';
  html += '<div style="text-align:center;margin:20px 0">';
  html += '<a href="index.html" style="display:inline-block;background:#3498db;color:#fff;padding:12px 30px;border-radius:6px;text-decoration:none;font-weight:bold">← Tiếp tục mua tour</a>';
  html += '</div>';

  container.innerHTML = html;
  if (totalDiv) totalDiv.innerHTML = "";
  if (checkoutDiv) checkoutDiv.style.display = "none";
}
