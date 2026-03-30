import os
import re
import sys

def safe_print(msg):
    try:
        print(msg)
    except UnicodeEncodeError:
        # Try to encode and replace unsupported characters
        try:
            encoded = msg.encode('cp1252', errors='replace')
            print(encoded.decode('cp1252'))
        except:
            print("[Message contains unsupported characters]")

def get_new_footer():
    return '''<footer class="vs2t-footer">
    <div class="footer-services">
        <a class="service-box pink" href="#">
            <i class="fas fa-hotel"></i>
            <div>
                <span class="title">KHÁCH SẠN</span>
                <p>Khách sạn tốt nhất tại các địa điểm du lịch nổi tiếng.</p>
            </div>
        </a>
        <a class="service-box blue" href="Mua sắm.html">
            <i class="fas fa-shopping-cart"></i>
            <div>
                <span class="title">MUA SẮM</span>
                <p>Đa dạng sản phẩm, quà tặng du lịch chất lượng cao.</p>
            </div>
        </a>
        <a class="service-box orange" href="GIỎ HÀNG.html">
            <i class="fas fa-shopping-bag"></i>
            <div>
                <span class="title">GIỎ HÀNG</span>
                <p>Xem lại và thanh toán đơn hàng của bạn.</p>
            </div>
        </a>
        <a class="service-box teal" href="Vé máy bay.html">
            <i class="fas fa-plane"></i>
            <div>
                <span class="title">VÉ MÁY BAY</span>
                <p>Vé máy bay giá rẻ nhất, nhiều khuyến mãi hấp dẫn.</p>
            </div>
        </a>
    </div>

    <div class="footer-navigation">
        <div class="nav-column">
            <h4>Du lịch miền Bắc</h4>
            <ul>
                <li><a href="Hà Nội.html">Du lịch Hà Nội</a></li>
                <li><a href="Hạ Long.html">Du lịch Hạ Long</a></li>
                <li><a href="Hà Giang.html">Du lịch Hà Giang</a></li>
            </ul>
        </div>
        <div class="nav-column">
            <h4>Du lịch miền Trung</h4>
            <ul>
                <li><a href="Đà Nẵng.html">Du lịch Đà Nẵng</a></li>
                <li><a href="Huế.html">Du lịch Huế</a></li>
                <li><a href="Phan Thiết.html">Du lịch Phan Thiết</a></li>
            </ul>
        </div>
        <div class="nav-column">
            <h4>Du lịch miền Nam</h4>
            <ul>
                <li><a href="Sài Gòn.html">Du lịch Sài Gòn</a></li>
                <li><a href="Vũng Tàu.html">Du lịch Vũng Tàu</a></li>
                <li><a href="Tây Ninh.html">Du lịch Tây Ninh</a></li>
            </ul>
        </div>
    </div>

    <hr class="footer-divider">

    <div class="footer-main">
        <div class="company-info">
            <h3>CÔNG TY CỔ PHẦN TRUYỀN THÔNG DU LỊCH VS2T</h3>
            <p><strong>Địa chỉ :</strong> 235 Nguyễn Văn Cừ, phường Chợ Quán, TPHCM.</p>
            <p><strong>Văn phòng :</strong> D202</p>
            <p><strong>Điện thoại :</strong> 0936 676767 | <strong>Hotline :</strong> 1900 3667</p>
            <p><strong>Website :</strong> vs2t .com.vn | <strong>Email :</strong> info@vs2tcom.vn</p>
        </div>

        <div class="customer-corner">
            <h4>Góc khách hàng</h4>
            <ul>
                <li>Chính sách đặt tour</li>
                <li>Chính sách bảo mật</li>
                <li>Ý kiến khách hàng</li>
                <li>Phiếu góp ý</li>
            </ul>
        </div>

        <div class="newsletter">
            <h4>Đăng ký nhận thông tin khuyến mãi</h4>
            <div class="email-box">
                <input type="email" placeholder="Email của bạn">
                <button><i class="fas fa-envelope"></i></button>
            </div>
        </div>
    </div>

    <div class="footer-bottom">
        <div class="license">
            <p>GIẤY PHÉP KINH DOANH DỊCH VỤ LỮ HÀNH QUỐC TẾ</p>
            <p>Số GP/ No: 79-042/2026/ TCDL - GP LHQT</p>
        </div>
        <div class="social-links">
            <i class="fab fa-facebook"></i>
            <i class="fab fa-youtube"></i>
            <i class="fab fa-instagram"></i>
        </div>
        <div class="payment-methods">
            <i class="fab fa-cc-visa"></i>
            <i class="fab fa-cc-mastercard"></i>
        </div>
    </div>
    <div class="copyright">
        Copyright © 2026 <strong>VS2T</strong>. Ghi rõ nguồn "vs2t.com.vn" khi sử dụng thông tin từ website này.
    </div>
</footer>'''

def fix_footer(file_path, new_footer):
    # Read the file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        # Try with different encoding if UTF-8 fails
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
    
    # Check if file already has a proper footer tag
    footer_start = content.find('<footer>')
    if footer_start == -1:
        # Try with attributes
        footer_start = content.find('<footer ')
    
    if footer_start != -1:
        # File has a footer tag, replace it properly
        footer_end = content.find('</footer>', footer_start)
        if footer_end == -1:
            safe_print(f"No closing footer tag found in {os.path.basename(file_path)}")
            return False
        
        # Add the length of the closing tag
        footer_end += len('</footer>')
        
        # Replace the footer
        new_content = content[:footer_start] + new_footer + content[footer_end:]
        safe_print(f"Replaced existing footer in {os.path.basename(file_path)}")
    else:
        # File doesn't have a footer tag
        # First, remove any incorrectly inserted footer content from body
        # Look for patterns that might indicate our footer was incorrectly inserted
        
        # Remove any occurrence of our footer content that might be in the body
        footer_content_start = new_footer.find('<div class="footer-services">')
        if footer_content_start != -1:
            footer_marker = new_footer[footer_content_start:footer_content_start+100]  # First 100 chars of footer content
            if footer_marker in content:
                # Remove the incorrectly inserted footer content
                content = content.replace(footer_marker, '')
        
        # Also remove any standalone footer div classes that might have been inserted
        patterns_to_remove = [
            '<div class="footer-services">',
            '<div class="footer-navigation">',
            '<hr class="footer-divider">',
            '<div class="footer-main">',
            '<div class="footer-bottom">',
            '<div class="copyright">'
        ]
        
        for pattern in patterns_to_remove:
            content = content.replace(pattern, '')
        
        # Now add the proper footer tag before </body>
        body_end = content.find('</body>')
        if body_end != -1:
            # Insert footer before </body>
            new_content = content[:body_end] + new_footer + content[body_end:]
            safe_print(f"Inserted proper footer tag before </body> in {os.path.basename(file_path)}")
        else:
            # No </body> found, append to end
            new_content = content + new_footer
            safe_print(f"Appended proper footer tag to end of {os.path.basename(file_path)}")
    
    # Write back to file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
    except UnicodeEncodeError:
        # Try with UTF-8 with BOM if needed
        with open(file_path, 'w', encoding='utf-8-sig') as f:
            f.write(new_content)
    
    return True

def main():
    new_footer = get_new_footer()
    
    # Get all HTML files
    html_files = []
    for root, dirs, files in os.walk('F:\\Study\\Project SItes'):
        for file in files:
            if file.lower().endswith('.html'):
                html_files.append(os.path.join(root, file))
    
    # Process each file except index.html
    processed = 0
    skipped = 0
    failed = 0
    failed_files = []
    for file_path in html_files:
        filename = os.path.basename(file_path)
        if filename.lower() == 'index.html':
            safe_print(f"Skipping {filename}")
            skipped += 1
            continue
        
        safe_print(f"Processing {filename}")
        if fix_footer(file_path, new_footer):
            processed += 1
        else:
            failed += 1
            failed_files.append(filename)
            safe_print(f"Failed to process {filename}")
    
    safe_print(f"\nProcessed: {processed} files")
    safe_print(f"Skipped: {skipped} files")
    safe_print(f"Failed: {failed} files")
    if failed > 0:
        safe_print("Failed files:")
        for f in failed_files:
            safe_print(f"  {f}")

if __name__ == "__main__":
    main()