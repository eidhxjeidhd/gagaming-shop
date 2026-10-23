from datetime import datetime
from flask import Flask, flash, jsonify, redirect, render_template_string, request, session, url_for
import hashlib
import json
import urllib.request
import urllib.parse

app = Flask(__name__)
app.secret_key = 'shop_blox_fruit_smart_v27'

# Cấu hình API ShopBanThe
PARTNER_ID = '71186911886'
PARTNER_KEY = 'f7377b035f5b5d2c4a5d04e487b39aaf'

# Cơ sở dữ liệu giả lập trong bộ nhớ (Bổ sung thêm kho coupon)
users = {
    'admin': {
        'password': '123',
        'role': 'admin',
        'balance': 500000,
        'total_deposited': 0,
    },
    'player1': {
        'password': '123',
        'role': 'user',
        'balance': 50000,
        'total_deposited': 100000,
    },
}

# Sản phẩm được phân loại: 'tuichon' (có ảnh chi tiết) hoặc 'random' (xé túi hên xui)
products = [
    {
        'id': 1276,
        'name': 'ACC BLOX FRUITS TỘC V4 FULL GEAR, KITSUNE',
        'category': 'tuichon',
        'desc': 'Acc max level, full trang bị xịn',
        'price': 30000,
        'image': 'https://i.ibb.co/DHCWq65g/file-00000000414c821198dbb4fd0f8ab53e.png',
        'game_accs': [
            'bloxfruit_1276_1@gmail.com | Pass123',
            'bloxfruit_1276_2@gmail.com | Pass456',
        ],
    },
    {
        'id': 5000,
        'name': 'TÚI MÙ BLOX FRUIT SIÊU RẺ (5K)',
        'category': 'random',
        'desc': 'Hên xui trúng acc khủng, giá cực rẻ câu khách!',
        'price': 5000,
        'image': 'https://i.ibb.co/0pvhCGz1/zlp-1792493518267.jpg',
        'game_accs': [
            'random_acc_1@gmail.com | Pass111',
            'random_acc_2@gmail.com | Pass222',
        ],
    },
]

# Quản lý mã giảm giá (Admin có thể chủ động thêm và bật/tắt hết hạn ngay lập tức)
coupons_db = [
    {'id': 1, 'code': 'GIAM5K', 'discount_amount': 5000, 'is_active': True}
]

cards_queue = []
purchase_history = []
messages_db = [
    {
        'user': 'player1',
        'sender': 'admin',
        'message': 'Chào bạn, shop hỗ trợ gì cho bạn?',
    }
]

BASE_HTML = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Shop Blox Fruits - Tự Động 100%</title>
    <style>
        body { background-color: #121212; color: #fff; font-family: Arial, sans-serif; margin: 0; padding: 0; }
        header { background: #1e1e1e; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #333; flex-wrap: wrap; gap: 10px; }
        .logo { font-size: 20px; font-weight: bold; color: #ff4757; text-decoration: none; }
        .nav-buttons a { background: #ff4757; color: white; padding: 8px 12px; border-radius: 5px; text-decoration: none; font-weight: bold; font-size: 13px; display: inline-block; }
        .container { padding: 20px; max-width: 900px; margin: auto; }
        .card { background: #1e1e1e; border: 1px solid #333; border-radius: 8px; padding: 15px; margin-bottom: 15px; }
        .product-title { color: #ff4757; font-weight: bold; font-size: 16px; }
        .price { color: #ff4757; font-size: 18px; font-weight: bold; }
        .btn { background: #ff4757; color: white; border: none; padding: 10px; width: 100%; border-radius: 5px; font-weight: bold; cursor: pointer; text-align: center; display: block; text-decoration: none; box-sizing: border-box; }
        input, select { width: 100%; padding: 10px; margin: 8px 0; background: #2c2c2c; border: 1px solid #444; color: white; border-radius: 5px; box-sizing: border-box; }
        .alert { background: #ff4757; padding: 10px; border-radius: 5px; margin-bottom: 15px; text-align: center; font-weight: bold; }
        .success-box { background: #1b2a1e; border: 1px solid #2ed573; padding: 15px; border-radius: 5px; margin-top: 10px; }
        .top-user-item { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #333; font-size: 14px; }
        .chat-box { background: #1e1e1e; border: 1px solid #444; border-radius: 8px; padding: 10px; max-height: 180px; overflow-y: auto; margin-bottom: 10px; }
        .chat-msg { margin-bottom: 8px; font-size: 13px; }
        .chat-msg.user { color: #70a1ff; text-align: right; }
        .chat-msg.admin { color: #2ed573; text-align: left; }
    </style>
</head>
<body>
    <header>
        <a href="/" class="logo">⚡ SHOP BLOX FRUIT PRO</a>
        <div class="nav-buttons">
            {% if 'username' in session %}
                <span>Số dư: <b style="color: #2ed573;">{{ "{:,.0f}".format(users[session['username']]['balance']) }}đ</b></span>
                <a href="/lich-su" style="background: #3742fa;">LỊCH SỬ</a>
                {% if session['role'] == 'admin' %}
                    <a href="/admin" style="background: #2ed573;">⚙️ QUẢN TRỊ</a>
                {% endif %}
                <a href="/logout" style="background: #747d8c;">ĐĂNG XUẤT</a>
            {% else %}
                <a href="/login">ĐĂNG NHẬP</a>
                <a href="/register" style="background: #3742fa;">ĐĂNG KÝ</a>
            {% endif %}
        </div>
    </header>
    <div class="container">
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            {% for message in messages %}
              <div class="alert">{{ message }}</div>
            {% endfor %}
          {% endif %}
        {% endwith %}

        {{ content | safe }}
    </div>
</body>
</html>
"""


@app.route('/')
def index():
  sorted_users = sorted(
      users.items(), key=lambda x: x[1].get('total_deposited', 0), reverse=True
  )
  top_html = ''
  rank = 1
  for uname, udata in sorted_users:
    if udata.get('total_deposited', 0) > 0:
      top_html += (
          '<div class="top-user-item"><span><b>#'
          + str(rank)
          + '</b>. '
          + uname
          + '</span><span style="color: #ffa502; font-weight: bold;">'
          + f"{udata.get('total_deposited', 0):,}"
          + 'đ</span></div>'
      )
      rank += 1
  if not top_html:
    top_html = (
        '<p style="color: #aaa; text-align: center;">Chưa có dữ liệu nạp'
        ' tiền.</p>'
    )

  chat_html = ''
  if 'username' in session and session['role'] != 'admin':
    curr_user = session['username']
    user_msgs = [m for m in messages_db if m['user'] == curr_user]
    msgs_render = ''
    if not user_msgs:
      msgs_render = (
          '<p style="color: #777; font-size: 12px; text-align: center;">Chưa'
          ' có tin nhắn, hãy chat với admin nếu cần hỗ trợ!</p>'
      )
    else:
      for m in user_msgs:
        sender_label = 'Bạn' if m['sender'] == curr_user else 'Admin'
        css_class = 'user' if m['sender'] == curr_user else 'admin'
        msgs_render += (
            '<div class="chat-msg '
            + css_class
            + '"><b>'
            + sender_label
            + ':</b> '
            + m['message']
            + '</div>'
        )

    chat_html = (
        '<div class="card" style="border: 2px solid #ff4757; margin-top:'
        ' 15px;"><h3 style="color: #ff4757; margin-top: 0;">💬 Hỗ Trợ Trực'
        ' Tuyến</h3><div class="chat-box">'
        + msgs_render
        + '</div><form action="/send-message" method="POST"><input type="text"'
        ' name="message" placeholder="Nhập tin nhắn cho Admin..." required'
        ' style="margin: 0 0 8px 0;"><button type="submit" class="btn"'
        ' style="padding: 6px; font-size: 13px;">GỬI TIN'
        ' NHẮN</button></form></div>'
    )

  products_html = ''
  for p in products:
    stock_count = len(p['game_accs'])
    # Phân biệt nút mua cho Tự Chọn (có ảnh) và Random (Xé túi)
    if p.get('category') == 'random':
      action_btn = (
          '<a href="/tui-mu/'
          + str(p['id'])
          + '" class="btn" style="background: #ffa502; margin-top:'
          ' 10px;">⚡ XÉ TÚI NGAY</a>'
      )
    else:
      action_btn = (
          '<a href="/buy/'
          + str(p['id'])
          + '" class="btn" style="margin-top: 10px;">🛒 MUA NGAY</a>'
      )

    img_tag = (
        '<img src="'
        + p['image']
        + '" style="width: 100%; height: 140px; object-fit: cover;'
        ' border-radius: 6px; margin-bottom: 8px;">'
        if p.get('image')
        else ''
    )

    products_html += (
        '<div class="card">'
        + img_tag
        + '<div class="product-title">MS: #'
        + str(p['id'])
        + '</div><p><b>'
        + p['name']
        + '</b></p><p style="color: #aaa; font-size: 13px;">'
        + p['desc']
        + '</p><p>Kho còn: <b>'
        + str(stock_count)
        + '</b> acc</p><div class="price">'
        + f"{p['price']:,}"
        + 'đ</div>'
        + action_btn
        + '</div>'
    )

  nap_html = ''
  if 'username' in session and session['role'] != 'admin':
    curr_username = session['username']
    suggest_note = f'NAP {curr_username.upper()}'
    nap_html = f"""
        <div class="card" style="border: 2px solid #2ed573;">
            <h3 style="color: #2ed573; margin-top:0;">⚡ NẠP TIỀN TỰ ĐỘNG 100%</h3>
            
            <div style="background: #111; padding: 12px; border-radius: 6px; margin-bottom: 15px;">
                <p style="margin: 0 0 5px 0; color: #ffa502; font-weight: bold;">📝 1. Chuyển khoản QR siêu tốc:</p>
                <p style="margin: 0; font-size: 13px; color: #ddd;">Nội dung: <b style="color: #2ed573; font-size: 15px;">{suggest_note}</b>. Tự động cộng tiền sau 3 giây!</p>
            </div>

            <div style="text-align: center; margin-bottom: 10px;">
                <img src="https://i.ibb.co/0pvhCGz1/zlp-1792493518267.jpg" alt="QR Code" style="max-width: 180px; border-radius: 8px; border: 2px solid #fff;">
                <p style="font-size: 12px; color: #aaa; margin: 5px 0;">Chủ TK: NGUYEN VAN DUONG</p>
            </div>

            <form action="/nap-the" method="POST" style="margin-top: 20px; border-top: 1px dashed #444; padding-top: 15px;">
                <h4 style="color: #ffa502; margin: 0 0 8px 0;">2. Nạp Thẻ Cào Tự Động</h4>
                <label>Nhà mạng:</label>
                <select name="telco">
                    <option value="VIETTEL">Viettel</option>
                    <option value="MOBIFONE">Mobifone</option>
                    <option value="VINAPHONE">Vinaphone</option>
                    <option value="VIETNAMOBILE">Vietnamobile</option>
                </select>
                <label>Mệnh giá:</label>
                <select name="amount">
                    <option value="10000">10.000 đ</option>
                    <option value="20000">20.000 đ</option>
                    <option value="50000">50.000 đ</option>
                    <option value="100000">100.000 đ</option>
                    <option value="200000">200.000 đ</option>
                    <option value="300000">300.000 đ</option>
                    <option value="500000">500.000 đ</option>
                    <option value="1000000">1.000.000 đ</option>
                </select>
                <input type="text" name="code" placeholder="Mã thẻ cào" required>
                <input type="text" name="serial" placeholder="Số Serial" required>
                <button type="submit" class="btn" style="background: #ffa502; margin-top: 10px;">NẠP THẺ TỰ ĐỘNG</button>
            </form>
        </div>
        """

  banner_html = """
        <div class="card" style="text-align: center; padding: 10px; border: 2px solid #ff4757;">
            <img src="https://i.ibb.co/DHCWq65g/file-00000000414c821198dbb4fd0f8ab53e.png" alt="Giao diện Shop" style="width: 100%; max-height: 400px; object-fit: contain; border-radius: 6px;">
        </div>
        """

  content = (
      banner_html
      + nap_html
      + '<div style="display: grid; grid-template-columns: 2fr 1fr; gap:'
      ' 15px;"><div><h2>DANH MỤC TÀI KHOẢN BLOX FRUIT & TÚI MÙ</h2><div'
      ' style="display: grid; grid-template-columns: 1fr 1fr; gap:'
      ' 15px;">'
      + products_html
      + '</div></div><div><div class="card" style="border: 2px solid #ffa502;'
      ' margin-bottom: 15px;"><h3 style="color: #ffa502; text-align:'
      ' center;">🏆 TOP NẠP TIỀN</h3>'
      + top_html
      + '</div>'
      + chat_html
      + '</div></div>'
  )
  return render_template_string(BASE_HTML, content=content, users=users)


# GIAO DIỆN XÉ TÚI MÙ (RANDOM) KÈM NHẬP MÃ GIẢM GIÁ
@app.route('/tui-mu/<int:product_id>')
def tui_mu(product_id):
  if 'username' not in session:
    flash('Vui lòng đăng nhập để mở túi mù!')
    return redirect(url_for('login'))
  product = next((p for p in products if p['id'] == product_id), None)
  if not product:
    flash('Không tìm thấy sản phẩm!')
    return redirect(url_for('index'))

  content = f"""
    <div class="card" style="max-width: 500px; margin: auto; text-align: center;">
        <h2 style="color: #ffa502;">⚡ MỞ TÚI MÙ: {product['name']}</h2>
        <p style="color: #aaa;">{product['desc']}</p>
        <p class="price">Giá túi: {product['price']:,}đ</p>
        <p>Kho còn: <b>{len(product['game_accs'])}</b> tài khoản</p>
        
        <div style="margin: 20px 0; text-align: left;">
            <label>Nhập mã giảm giá:</label>
            <input type="text" id="coupon_code" placeholder="Nhập mã (VD: GIAM5K)">
            <button type="click" onclick="applyCoupon({product['price']})" class="btn" style="background: #3742fa; margin-top: 5px;">Áp mã</button>
            <p id="coupon_msg" style="font-size: 13px; margin-top: 5px;"></p>
        </div>

        <h3 id="final_price_display">Tổng thanh toán: {product['price']:,}đ</h3>
        <button onclick="xeTui({product['id']})" class="btn" style="background: #ffa502; font-size: 16px; padding: 12px;">🔥 XÉ TÚI NGAY</button>
        <br>
        <a href="/" style="color: #aaa; text-decoration: none; font-size: 13px;">← Quay về trang chủ</a>
    </div>

    <script>
    let currentDiscount = 0;
    function applyCoupon(basePrice) {
        let code = document.getElementById('coupon_code').value;
        fetch('/api/check-coupon', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({code: code})
        })
        .then(res => res.json())
        .then(data => {
            let msg = document.getElementById('coupon_msg');
            if(data.success) {
                currentDiscount = data.discount;
                let final = Math.max(0, basePrice - currentDiscount);
                msg.style.color = '#2ed573';
                msg.innerText = "Áp mã thành công! Giảm " + data.discount + "đ";
                document.getElementById('final_price_display').innerText = "Tổng thanh toán: " + final.toLocaleString() + "đ";
            } else {
                currentDiscount = 0;
                msg.style.color = '#ff4757';
                msg.innerText = data.message;
                document.getElementById('final_price_display').innerText = "Tổng thanh toán: " + basePrice.toLocaleString() + "đ";
            }
        });
    }

    function xeTui(productId) {
        let code = document.getElementById('coupon_code').value;
        fetch('/api/buy-random/' + productId, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({coupon_code: code})
        })
        .then(res => res.json())
        .then(data => {
            if(data.success) {
                alert("🎉 Xé túi thành công! Tài khoản của bạn:\\n" + data.account_info);
                window.location.href = '/lich-su';
            } else {
                alert(data.message);
            }
        });
    }
    </script>
    """
  return render_template_string(BASE_HTML, content=content, users=users)


# API KIỂM TRA MÃ GIẢM GIÁ
@app.route('/api/check-coupon', methods=['POST'])
def check_coupon():
  data = request.json or {}
  code = data.get('code', '').strip().upper()
  coupon = next(
      (c for c in coupons_db if c['code'] == code and c['is_active']), None
  )
  if coupon:
    return jsonify(
        {'success': True, 'discount': coupon['discount_amount']}
    )
  return jsonify(
      {'success': False, 'message': 'Mã giảm giá không hợp lệ hoặc đã hết hạn!'}
  )


# API XỬ LÝ XÉ TÚI RANDOM VÀ TRỪ TIỀN
@app.route('/api/buy-random/<int:product_id>', methods=['POST'])
def api_buy_random(product_id):
  if 'username' not in session:
    return jsonify({'success': False, 'message': 'Vui lòng đăng nhập!'})
  username = session['username']
  product = next((p for p in products if p['id'] == product_id), None)

  if not product or len(product['game_accs']) <= 0:
    return jsonify(
        {
            'success': False,
            'message': (
                'Kho túi mù chưa có đủ tài khoản hợp lệ. Vui lòng liên hệ shop.'
            ),
        }
    )

  data = request.json or {}
  coupon_code = data.get('coupon_code', '').strip().upper()
  final_price = product['price']

  if coupon_code:
    coupon = next(
        (c for c in coupons_db if c['code'] == coupon_code and c['is_active']),
        None,
    )
    if coupon:
      final_price = max(0, product['price'] - coupon['discount_amount'])
    else:
      return jsonify(
          {'success': False, 'message': 'Mã giảm giá không hợp lệ hoặc đã hết hạn!'}
      )

  if users[username]['balance'] < final_price:
    return jsonify({'success': False, 'message': 'Số dư tài khoản không đủ!'})

  users[username]['balance'] -= final_price
  acc_info = product['game_accs'].pop(0)

  purchase_history.append({
      'user': username,
      'product_name': product['name'] + ' (Random)',
      'account_details': acc_info,
  })

  return jsonify({'success': True, 'account_info': acc_info})


@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    if username in users and users[username]['password'] == password:
      session['username'] = username
      session['role'] = users[username]['role']
      flash('Đăng nhập thành công!')
      return redirect(url_for('index'))
    flash('Sai tài khoản hoặc mật khẩu!')
  content = """
    <div class="card" style="max-width: 400px; margin: auto;">
        <h2 style="text-align: center; color: #ff4757;">ĐĂNG NHẬP</h2>
        <form method="POST">
            <input type="text" name="username" placeholder="Nhập tài khoản..." required>
            <input type="password" name="password" placeholder="Nhập mật khẩu..." required>
            <button type="submit" class="btn" style="margin-top: 15px;">ĐĂNG NHẬP</button>
        </form>
    </div>
    """
  return render_template_string(BASE_HTML, content=content, users=users)


@app.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    if username in users:
      flash('Tài khoản đã tồn tại!')
    else:
      users[username] = {
          'password': password,
          'role': 'user',
          'balance': 0,
          'total_deposited': 0,
      }
      flash('Đăng ký thành công! Hãy đăng nhập.')
      return redirect(url_for('login'))
  content = """
    <div class="card" style="max-width: 400px; margin: auto;">
        <h2 style="text-align: center; color: #ff4757;">ĐĂNG KÝ TÀI KHOẢN</h2>
        <form method="POST">
            <input type="text" name="username" placeholder="Nhập tài khoản..." required>
            <input type="password" name="password" placeholder="Nhập mật khẩu..." required>
            <button type="submit" class="btn" style="background: #3742fa; margin-top: 15px;">ĐĂNG KÝ</button>
        </form>
    </div>
    """
  return render_template_string(BASE_HTML, content=content, users=users)


@app.route('/logout')
def logout():
  session.clear()
  return redirect(url_for('index'))


# WEBHOOK NHẬN BIẾN ĐỘNG SỐ DƯ NGÂN HÀNG (QR)
@app.route('/webhook/bank', methods=['POST'])
def bank_webhook():
  data = request.json or request.form
  content = str(
      data.get('content', data.get('description', ''))
  ).upper()
  try:
    amount = int(float(data.get('transferAmount', data.get('amount', 0))))
  except:
    amount = 0

  if amount > 0:
    for uname in users:
      if uname.upper() in content:
        users[uname]['balance'] += amount
        users[uname]['total_deposited'] = (
            users[uname].get('total_deposited', 0) + amount
        )
        cards_queue.append({
            'id': len(cards_queue) + 1,
            'user': uname,
            'type': 'Tự động QR',
            'info': f'Nội dung: {content}',
            'amount': amount,
            'status': 'Thành công',
        })
        return jsonify({'success': True, 'message': f'Đã cộng {amount} cho {uname}'})

  return jsonify({'success': False, 'message': 'Không khớp tài khoản'})


# GỬI THẺ CÀO SANG API SHOPBANTHE
@app.route('/nap-the', methods=['POST'])
def nap_the():
  if 'username' not in session:
    return redirect(url_for('login'))

  telco = request.form['telco']
  code = request.form['code'].strip()
  serial = request.form['serial'].strip()
  amount = request.form['amount']
  request_id = str(len(cards_queue) + 1000)

  raw_sign = PARTNER_KEY + code + serial
  sign = hashlib.md5(raw_sign.encode('utf-8')).hexdigest()

  api_url = f"https://shopbanthe.com/api/card-charging?partner_id={PARTNER_ID}&telco={telco}&code={code}&serial={serial}&amount={amount}&request_id={request_id}&sign={sign}"

  try:
    req = urllib.request.Request(
        api_url,
        headers={
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/json',
        },
    )
    with urllib.request.urlopen(req, timeout=15) as response:
      res = json.loads(response.read().decode('utf-8'))
      message = res.get('message', 'Đã xử lý thẻ')
      cards_queue.append({
          'id': len(cards_queue) + 1,
          'user': session['username'],
          'type': f'Thẻ {telco}',
          'info': f'Seri: {serial} - Mã: {code}',
          'amount': int(amount),
          'status': 'Đang chờ xử lý',
      })
      flash(f'Phản hồi từ cổng thẻ: {message}')
  except Exception as e:
    cards_queue.append({
        'id': len(cards_queue) + 1,
        'user': session['username'],
        'type': f'Thẻ {telco}',
        'info': f'Seri: {serial} - Mã: {code}',
        'amount': int(amount),
        'status': 'Đang chờ xử lý (Hệ thống gạch thẻ đang bận)',
    })
    flash('Đã ghi nhận thẻ vào hệ thống, đang chờ xử lý!')

  return redirect(url_for('index'))


@app.route('/callback-the', methods=['GET', 'POST'])
def callback_the():
  data = request.args if request.method == 'GET' else (request.json or request.form)
  status = data.get('status')
  amount = int(data.get('amount', 0))

  if str(status) == '1' and amount > 0:
    for c in cards_queue:
      if c['status'] in ['Đang chờ xử lý', 'Đang chờ xử lý (Hệ thống gạch thẻ đang bận)']:
        c['status'] = 'Thành công'
        uname = c['user']
        if uname in users:
          users[uname]['balance'] += amount
          users[uname]['total_deposited'] = (
              users[uname].get('total_deposited', 0) + amount
          )
        break
  return jsonify({'success': True})


@app.route('/buy/<int:product_id>')
def buy(product_id):
  if 'username' not in session:
    flash('Vui lòng đăng nhập để mua tài khoản!')
    return redirect(url_for('login'))
  username = session['username']
  product = next((p for p in products if p['id'] == product_id), None)
  if not product or len(product['game_accs']) <= 0:
    flash('Sản phẩm đã hết hàng trong kho!')
    return redirect(url_for('index'))
  if users[username]['balance'] < product['price']:
    flash('Số dư của bạn không đủ, vui lòng nạp thêm tiền!')
    return redirect(url_for('index'))

  users[username]['balance'] -= product['price']
  acc_info = product['game_accs'].pop(0)
  purchase_history.append({
      'user': username,
      'product_name': product['name'],
      'account_details': acc_info,
  })

  content = f"""
    <div class="card" style="max-width: 600px; margin: auto; text-align: center;">
        <h2 style="color: #2ed573;">🎉 MUA TÀI KHOẢN THÀNH CÔNG!</h2>
        <p>Sản phẩm: <b>{product['name']}</b></p>
        <div class="success-box">
            <p>Thông tin tài khoản & mật khẩu:</p>
            <h3 style="color: #ffa502; background: #111; padding: 10px; border-radius: 5px;">{acc_info}</h3>
            <p style="font-size: 13px; color: #aaa;">(Hãy đổi mật khẩu ngay!)</p>
        </div>
        <a href="/" class="btn" style="margin-top: 20px;">VỀ TRANG CHỦ</a>
    </div>
    """
  return render_template_string(BASE_HTML, content=content, users=users)


@app.route('/lich-su')
def lich_su():
  if 'username' not in session:
    return redirect(url_for('login'))
  user_history = [
      h for h in purchase_history if h['user'] == session['username']
  ]
  history_html = '<h2>LỊCH SỬ MUA TÀI KHOẢN</h2>'
  if not user_history:
    history_html += '<p>Bạn chưa mua tài khoản nào.</p>'
  else:
    for h in user_history:
      history_html += (
          '<div class="card"><p><b>Sản phẩm:</b> '
          + h['product_name']
          + '</p><p><b>Thông tin Acc:</b> <span style="color: #2ed573;">'
          + h['account_details']
          + '</span></p></div>'
      )
  return render_template_string(BASE_HTML, content=history_html, users=users)


@app.route('/send-message', methods=['POST'])
def send_message():
  if 'username' not in session:
    return redirect(url_for('login'))
  msg = request.form['message'].strip()
  if msg:
    messages_db.append(
        {'user': session['username'], 'sender': session['username'], 'message': msg}
    )
    flash('Đã gửi tin nhắn cho Admin thành công!')
  return redirect(url_for('index'))


# ==================== KHU VỰC ADMIN (QUẢN TRỊ TOÀN DIỆN + QUẢN LÝ MÃ GIẢM GIÁ) ====================
@app.route('/admin', methods=['GET', 'POST'])
def admin():
  if 'username' not in session or session.get('role') != 'admin':
    flash('Bạn không có quyền truy cập trang quản trị!')
    return redirect(url_for('index'))

  # Xử lý thêm sản phẩm (Có chọn loại: Tự chọn hay Random)
  if request.method == 'POST' and 'add_product' in request.form:
    name = request.form['name']
    price = int(request.form['price'])
    category = request.form['category']
    desc = request.form['desc']
    image = request.form.get('image', '')
    game_acc = request.form['game_acc'].strip()

    existing_product = next((p for p in products if p['name'] == name), None)
    if existing_product:
      existing_product['game_accs'].append(game_acc)
      flash('Đã thêm tài khoản vào kho sản phẩm có sẵn!')
    else:
      new_id = products[-1]['id'] + 1 if products else 1000
      products.append({
          'id': new_id,
          'name': name,
          'category': category,
          'desc': desc,
          'price': price,
          'image': image,
          'game_accs': [game_acc],
      })
      flash('Đã tạo danh mục sản phẩm mới thành công!')
    return redirect(url_for('admin'))

  # Xử lý thêm mã giảm giá mới
  if request.method == 'POST' and 'add_coupon' in request.form:
    code = request.form['coupon_code'].strip().upper()
    discount = float(request.form['discount_amount'])
    if code:
      new_id = coupons_db[-1]['id'] + 1 if coupons_db else 1
      coupons_db.append({
          'id': new_id,
          'code': code,
          'discount_amount': discount,
          'is_active': True,
      })
      flash(f'Đã thêm mã giảm giá "{code}" thành công!')
    return redirect(url_for('admin'))

  # Xử lý cộng tiền user
  if request.method == 'POST' and 'bonus_user' in request.form:
    target_username = request.form['target_username'].strip()
    bonus_amount = int(request.form['bonus_amount'])
    if target_username in users:
      users[target_username]['balance'] += bonus_amount
      users[target_username]['total_deposited'] = (
          users[target_username].get('total_deposited', 0) + bonus_amount
      )
      flash(f'Đã cộng {bonus_amount:,}đ cho "{target_username}"!')
    else:
      flash(f'Không tìm thấy tài khoản "{target_username}"!')
    return redirect(url_for('admin'))

  # Xử lý trả lời tin nhắn
  if request.method == 'POST' and 'reply_msg' in request.form:
    target_user = request.form['target_user']
    reply_text = request.form['reply_text'].strip()
    if reply_text:
      messages_db.append(
          {'user': target_user, 'sender': 'admin', 'message': reply_text}
      )
      flash(f'Đã gửi phản hồi đến "{target_user}"!')
    return redirect(url_for('admin'))

  # Render danh sách mã giảm giá trong admin
  coupons_html = ''
  for c in coupons_db:
    status_text = (
        '<span style="color: #2ed573;">Đang hoạt động</span>'
        if c['is_active']
        else '<span style="color: #ff4757;">Đã tắt / Hết hạn</span>'
    )
    btn_text = 'Tắt / Vô hiệu hóa' if c['is_active'] else 'Bật lại'
    btn_color = '#ff4757' if c['is_active'] else '#2ed573'
    coupons_html += f"""
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #333; padding: 8px 0; font-size: 14px;">
            <span><b>{c['code']}</b> (-{c['discount_amount']:,.0f}đ) - {status_text}</span>
            <form action="/admin/coupon/toggle/{c['id']}" method="POST" style="margin: 0;">
                <button type="submit" style="background: {btn_color}; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer;">{btn_text}</button>
            </form>
        </div>
        """

  chat_users = sorted(list(set([m['user'] for m in messages_db])))
  chat_admin_html = ''
  for cu in chat_users:
    user_chat_history = [m for m in messages_db if m['user'] == cu]
    history_render = ''
    for m in user_chat_history:
      sender_label = 'Khách' if m['sender'] == cu else 'Admin'
      history_render += (
          '<div><b>' + sender_label + ':</b> ' + m['message'] + '</div>'
      )
    chat_admin_html += (
        '<div class="card" style="background: #252525; margin-bottom:'
        ' 10px;"><p><b>Khách hàng: <span style="color: #70a1ff;">'
        + cu
        + '</span></b></p><div style="background: #121212; padding: 8px;'
        ' border-radius: 5px; max-height: 100px; overflow-y: auto; font-size:'
        ' 13px; margin-bottom: 8px;">'
        + history_render
        + '</div><form method="POST"><input type="hidden" name="target_user"'
        ' value="'
        + cu
        + '"><input type="text" name="reply_text"'
        ' placeholder="Nhập nội dung trả lời..." required style="margin:'
        ' 0 0 5px 0;"><button type="submit" name="reply_msg" class="btn"'
        ' style="padding: 5px; font-size: 12px; background:'
        ' #2ed573;">GỬI PHẢN HỒI</button></form></div>'
    )

  cards_html = ''
  if not cards_queue:
    cards_html = '<p>Không có lịch sử nạp tiền nào.</p>'
  else:
    for c in cards_queue:
      cards_html += (
          '<div class="card"><p><b>User:</b> '
          + c['user']
          + ' | <b>Loại:</b> '
          + c['type']
          + ' | <b>Số tiền:</b> <span style="color: #ffa502;">'
          + f"{c['amount']:,}"
          + 'đ</span></p><p><b>Thông tin:</b> '
          + c['info']
          + '</p><p><b>Trạng thái:</b> <span style="color: #2ed573;">'
          + c['status']
          + '</span></p></div>'
      )

  admin_content = f"""
    <h2>⚙️ TRANG QUẢN TRỊ ADMIN (FULL TÍNH NĂNG)</h2>
    
    <div class="card">
        <h3 style="color: #ff4757;">📦 Thêm Sản Phẩm (Tự chọn hoặc Random)</h3>
        <form method="POST">
            <input type="text" name="name" placeholder="Tên sản phẩm..." required>
            <label>Phân loại:</label>
            <select name="category">
                <option value="tuichon">Acc Tự Chọn (Có ảnh chi tiết)</option>
                <option value="random">Acc Random / Túi Mù (Hên xui, 5k)</option>
            </select>
            <input type="number" name="price" placeholder="Giá tiền (VNĐ)..." required>
            <input type="text" name="image" placeholder="Link ảnh minh họa (URL)...">
            <input type="text" name="desc" placeholder="Mô tả ngắn..." required>
            <input type="text" name="game_acc" placeholder="Tài khoản | Mật khẩu game..." required>
            <button type="submit" name="add_product" class="btn" style="margin-top: 10px; background: #2ed573;">THÊM VÀO KHO</button>
        </form>
    </div>

    <div class="card">
        <h3 style="color: #ffa502;">🎟️ Quản Lý Mã Giảm Giá (Bật / Tắt Hết Hạn Ngay)</h3>
        <form method="POST" style="margin-bottom: 15px;">
            <input type="text" name="coupon_code" placeholder="Mã giảm giá (VD: GIAM5K)..." required>
            <input type="number" name="discount_amount" placeholder="Số tiền giảm (VNĐ)..." required>
            <button type="submit" name="add_coupon" class="btn" style="background: #ffa502; margin-top: 5px;">THÊM MÃ GIẢM GIÁ</button>
        </form>
        <div style="background: #111; padding: 10px; border-radius: 6px;">
            {coupons_html if coupons_html else '<p>Chưa có mã giảm giá nào.</p>'}
        </div>
    </div>

    <div class="card">
        <h3 style="color: #ffa502;">💰 Cộng tiền cho Thành viên</h3>
        <form method="POST">
            <input type="text" name="target_username" placeholder="Tên tài khoản khách..." required>
            <input type="number" name="bonus_amount" placeholder="Số tiền cộng (VNĐ)..." required>
            <button type="submit" name="bonus_user" class="btn" style="margin-top: 10px; background: #ffa502;">CỘNG TIỀN NGAY</button>
        </form>
    </div>

    <div class="card">
        <h3 style="color: #70a1ff;">💬 Quản lý Tin nhắn Hỗ trợ Khách hàng</h3>
        {chat_admin_html if chat_admin_html else '<p>Chưa có tin nhắn nào.</p>'}
    </div>

    <div class="card">
        <h3 style="color: #2ed573;">📋 Lịch sử Nạp thẻ & QR tự động</h3>
        {cards_html}
    </div>
    """
  return render_template_string(BASE_HTML, content=admin_content, users=users)


# Route Bật/Tắt (Hết hạn) nhanh mã giảm giá
@app.route('/admin/coupon/toggle/<int:coupon_id>', methods=['POST'])
def toggle_coupon(coupon_id):
  if 'username' not in session or session.get('role') != 'admin':
    return redirect(url_for('index'))
  for c in coupons_db:
    if c['id'] == coupon_id:
      c['is_active'] = not c['is_active']
      flash(f'Đã đổi trạng thái mã {c["code"]} thành công!')
      break
  return redirect(url_for('admin'))


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000)
