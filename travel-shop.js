(function(){
  const products = [
    // Category: Vali và các thể loại túi xách
    {name:'Balo du lịch 40L', desc:'Balo chống thấm, ngăn nếp gọn', price:'890,000 đ', img:'https://picsum.photos/seed/balo40l/300/200', code:'balo-40l', category:'vali-bags'},
    {name:'Balo du lịch 60L', desc:'Dung tích lớn cho chuyến dài', price:'1,190,000 đ', img:'https://picsum.photos/seed/balo60l/300/200', code:'balo-60l', category:'vali-bags'},
    {name:'Túi xách du lịch 25L', desc:'Nhỏ gọn, tiện dụng cho daily', price:'690,000 đ', img:'https://picsum.photos/seed/tui25l/300/200', code:'tui-25l', category:'vali-bags'},
    {name:'Túi đựng hộ chiếu', desc:'Bảo quản hộ chiếu và giấy tờ', price:'290,000 đ', img:'https://picsum.photos/seed/passportbag/300/200', code:'passport-bag', category:'vali-bags'},
    {name:'Balo laptop 15.6"', desc:'Ngăn đệm laptop an toàn', price:'990,000 đ', img:'https://picsum.photos/seed/laptopbalo/300/200', code:'balo-laptop', category:'vali-bags'},
    {name:'Vali cứng 20"', desc:'Khóa TSA, vỏ ABS cứng', price:'1,290,000 đ', img:'https://picsum.photos/seed/vali20cung/300/200', code:'vali-20', category:'vali-bags'},
    {name:'Vali mềm 24"', desc:'Dễ di chuyển, phụ kiện đầy đủ', price:'1,690,000 đ', img:'https://picsum.photos/seed/vali24mem/300/200', code:'vali-24', category:'vali-bags'},
    {name:'Vali kéo 28"', desc:'Khóa TSA, bánh xe êm', price:'1,990,000 đ', img:'https://picsum.photos/seed/vali28keo/300/200', code:'vali-28', category:'vali-bags'},
    {name:'Hộp đựng đồ du lịch (set)', desc:'Hộp chia ngăn tiện dụng', price:'410,000 đ', img:'https://picsum.photos/seed/packingcube/300/200', code:'packing-cube', category:'vali-bags'},
    {name:'Dây đeo vali chống thất lạc', desc:'Dây đeo giúp nhận diện nhanh', price:'120,000 đ', img:'https://picsum.photos/seed/lugiaotag/300/200', code:'luggage-tag', category:'vali-bags'},
    {name:'Khóa vali TSA', desc:'Khóa an toàn, kiểm tra qua TSA', price:'480,000 đ', img:'https://picsum.photos/seed/tsalock/300/200', code:'tsa-lock', category:'vali-bags'},
    {name:'Túi đựng nước 1L', desc:'Chống nước, dễ mang theo', price:'180,000 đ', img:'https://picsum.photos/seed/waterbag1l/300/200', code:'water-bag', category:'vali-bags'},
    {name:'Túi đựng quần áo du lịch', desc:'Phù hợp cho xách tay', price:'520,000 đ', img:'https://picsum.photos/seed/clothesbag/300/200', code:'clothes-bag', category:'vali-bags'},
    // Category: Các loại nón và ly lưu niệm
    {name:'Nón chịu nắng du lịch', desc:'Nón rộng vành, chống UV', price:'180,000 đ', img:'https://picsum.photos/seed/sunhat/300/200', code:'sun-hat', category:'hats-bottles'},
    {name:'Nón len du lịch inverno', desc:'Nón len ấm áp cho thời tiết lạnh', price:'220,000 đ', img:'https://picsum.photos/seed/winterhat/300/200', code:'winter-hat', category:'hats-bottles'},
    {name:'Ly lưu niệm sứ inlogo', desc:'Ly sứ gập gọn, in logo địa điểm', price:'150,000 đ', img:'https://picsum.photos/seed/souvenirmug/300/200', code:'souvenir-mug', category:'hats-bottles'},
    {name:'Ly nhôm bảo nhiệt 500ml', desc:'Ly nhôm giữ nhiệt lạnh/nóng', price:'320,000 đ', img:'https://picsum.photos/seed/thermalbottle500/300/200', code:'thermal-bottle', category:'hats-bottles'},
    {name:'Nón mũ luchar đỉnh phải', desc:'Nón mũ vai trò thể thao, thoáng mát', price:'200,000 đ', img:'https://picsum.photos/seed/sportcap/300/200', code:'sport-cap', category:'hats-bottles'},
    // Category: Các món ăn vặt như snack
    {name:'Bánh quy mérite du lịch', desc:'Bánh quy gói nhỏ, energía', price:'80,000 đ', img:'https://picsum.photos/seed/travelbiscuit/300/200', code:'travel-biscuit', category:'snacks'},
    {name:'Trái cây khô điều', desc:'Điều khô không đường aggi', price:'120,000 đ', img:'https://picsum.photos/seed/driedcashew/300/200', code:'dried-cashew', category:'snacks'},
    {name:'Bánh mì kẹp thanh long', desc:'Bánh mì kẹp giòn với начинка', price:'100,000 đ', img:'https://picsum.photos/seed/bananabread/300/200', code:'banana-bread', category:'snacks'},
    {name:'Kẹo dừa dẻo', desc:'Kẹo dừa dẻo không đường', price:'90,000 đ', img:'https://picsum.photos/seed/coconutcandy/300/200', code:'coconut-candy', category:'snacks'},
    {name:'Túi hỗn hợp trail mix', desc:'Hỗn hợp hạt, fruits khô', price:'150,000 đ', img:'https://picsum.photos/seed/trailmix/300/200', code:'trail-mix', category:'snacks'}
  ];

  const grid = document.getElementById('travelGrid');
  const searchInput = document.getElementById('travelSearch');

  // Cart functions
  const CART_KEY = 'vs2t_cart';
  function loadCart() {
    const cart = localStorage.getItem(CART_KEY);
    return cart ? JSON.parse(cart) : [];
  }
  function saveCart(cart) {
    localStorage.setItem(CART_KEY, JSON.stringify(cart));
  }
  function addToCart(product) {
    const cart = loadCart();
    const existing = cart.find(item => item.code === product.code);
    if (existing) {
      existing.qty += 1;
    } else {
      cart.push({ ...product, qty: 1 });
    }
    saveCart(cart);
    updateCartCount();
  }
  function updateCartCount() {
    const cart = loadCart();
    const totalQty = cart.reduce((sum, item) => sum + item.qty, 0);
    const navCart = document.querySelector('.nav-cart');
    if (navCart) {
      // Update or create badge
      let badge = navCart.querySelector('.cart-badge');
      if (!badge) {
        badge = document.createElement('span');
        badge.className = 'cart-badge';
        badge.style.display = 'inline-block';
        badge.style.backgroundColor = 'var(--primary-color)';
        badge.style.color = '#fff';
        badge.style.borderRadius = '50%';
        badge.style.padding = '2px 6px';
        badge.style.fontSize = '12px';
        badge.style.marginLeft = '6px';
        navCart.appendChild(badge);
      }
      badge.textContent = totalQty;
      if (totalQty === 0) {
        badge.style.display = 'none';
      } else {
        badge.style.display = 'inline-block';
      }
    }
  }

  // Initial cart count update
  updateCartCount();

  function renderCard(p){
    return '<div class="grid-column grid-stretch" style="min-width:240px;">'+
             '<div class="column-inner"><div class="content-inner">'+
               '<div class="grid-cell product-card" data-name="' + p.name + '" data-desc="' + p.desc + '" data-category="' + p.category + '" style="display:flex;flex-direction:column;align-items:center;padding:12px;border:1px solid #eee;border-radius:12px;background:#fff;min-height:420px;">' +
                 '<img class="content-image" src="' + p.img + '" alt="' + p.name + '" style="width:100%;max-width:300px;height:auto;border-radius:8px;"/>' +
                 '<h3 class="text-heading" style="text-align:center;margin:8px 0 4px;">' + p.name + '</h3>' +
                 '<p class="text-paragraph" style="text-align:center;margin:0 0 6px;">' + p.desc + '</p>' +
                 '<p class="text-paragraph" style="text-align:center;margin:0 0 8px;font-weight:700;">Giá: ' + p.price + '</p>' +
                 '<button class="btn-primary" style="width:100%;margin-top:6px;" data-product=\'' + JSON.stringify(p) + '\'>Đặt mua</button>' +
               '</div>' +
             '</div></div>' +
           '</div>';
  }
  function renderAll(){
    grid.innerHTML = products.map(renderCard).join('');
    // Attach event listeners to buttons
    document.querySelectorAll('.product-card button').forEach(btn => {
      btn.addEventListener('click', function() {
        const product = JSON.parse(this.getAttribute('data-product'));
        addToCart(product);
        // Optional: show feedback
        alert('Đã thêm "' + product.name + '" vào giỏ hàng!');
      });
    });
  }
  function filterSearch(query){
    const q = (query || '').toLowerCase();
    const cards = grid.querySelectorAll('.product-card');
    cards.forEach(card => {
      const name = (card.dataset.name || '').toLowerCase();
      const desc = (card.dataset.desc || '').toLowerCase();
      const show = !q || name.includes(q) || desc.includes(q);
      card.style.display = show ? 'flex' : 'none';
    });
  }
  if(searchInput){
    searchInput.addEventListener('input', function(e){
      filterSearch(e.target.value);
    });
  }
  renderAll();
})();