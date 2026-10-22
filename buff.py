from flask import Flask, flash, redirect, render_template_string, request, session, url_for

app = Flask(__name__)
app.secret_key = 'shop_blox_fruit_full_pro_v22'

# Cơ sở dữ liệu giả lập trong bộ nhớ
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

products = [
    {
        'id': 1276,
        'name': 'ACC BLOX FRUITS TỘC V4 FULL GEAR, KITSUNE',
        'desc': 'Acc max level, full trang bị xịn',
        'price': 30000,
        'game_accs': [
            'bloxfruit_1276_1@gmail.com | Pass123',
            'bloxfruit_1276_2@gmail.com | Pass456',
        ],
    }
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
    <title>Shop Blox Fruits - Tự Động & Uy Tín</title>
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
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { border: 1px solid #444; padding: 10px; text-align: center; font-size: 14px; }
        th { background: #222; }
        .top-user-item { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #333; font-size: 14px; }
        .chat-box { background: #1e1e1e; border: 1px solid #444; border-radius: 8px; padding: 10px; max-height: 180px; overflow-y: auto; margin-bottom: 10px; }
        .chat-msg { margin-bottom: 8px; font-size: 13px; }
        .chat-msg.user { color: #70a1ff; text-align: right; }
        .chat-msg.admin { color: #2ed573; text-align: left; }
    </style>
</head>
<body>
    <header>
        <a href="/" class="logo">🔥 SHOP BLOX FRUIT</a>
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
    products_html += (
        '<div class="card"><div class="product-title">MS: #'
        + str(p['id'])
        + '</div><p><b>'
        + p['name']
        + '</b></p><p style="color: #aaa; font-size: 13px;">'
        + p['desc']
        + '</p><p>Kho còn: <b>'
        + str(stock_count)
        + '</b> acc</p><div class="price">'
        + f"{p['price']:,}"
        + 'đ</div><a href="/buy/'
        + str(p['id'])
        + '" class="btn" style="margin-top: 10px;">🛒 MUA NGAY</a></div>'
    )

  nap_html = ''
  if 'username' in session and session['role'] != 'admin':
    nap_html = """
        <div class="card" style="border: 2px solid #ffa502;">
            <h3 style="color: #ffa502; margin-top:0;">💳 NẠP TIỀN TỰ ĐỘNG (THẺ CÀO & QR CHUYỂN KHOẢN)</h3>
            
            <form action="/nap-the" method="POST" style="margin-bottom: 20px; border-bottom: 1px dashed #444; padding-bottom: 15px;">
                <h4 style="color: #ffa502; margin: 0 0 8px 0;">1. Nạp Thẻ Cào Tự Động</h4>
                <label>Chọn nhà mạng:</label>
                <select name="telco">
                    <option value="Viettel">Viettel</option>
                    <option value="Mobifone">Mobifone</option>
                    <option value="Vinaphone">Vinaphone</option>
                    <option value="Vietnamobile">Vietnamobile</option>
                    <option value="ZaloPay">ZaloPay</option>
                    <option value="Gate">Gate</option>
                    <option value="Vcoin">Vcoin</option>
                </select>
                <label>Chọn mệnh giá:</label>
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
                <button type="submit" class="btn" style="background: #ffa502; margin-top: 10px;">NẠP THẺ NGAY</button>
            </form>

            <form action="/nap-qr" method="POST">
                <h4 style="color: #2ed573; margin: 0 0 8px 0;">2. Chuyển Khoản Ngân Hàng / Ví (Chủ TK: NGUYEN VAN DUONG)</h4>
                <div style="text-align: center; margin-bottom: 10px;">
                    <img src="https://i.ibb.co/0pvhCGz1/zlp-1792493518267.jpg" alt="QR Code" style="max-width: 180px; border-radius: 8px; border: 2px solid #fff;">
                    <p style="font-size: 12px; color: #aaa; margin: 5px 0;">Quét mã QR trên để chuyển khoản, sau đó điền thông tin bên dưới.</p>
                </div>
                <input type="number" name="amount" placeholder="Nhập số tiền đã chuyển (VNĐ)" required>
                <input type="text" name="note" placeholder="Nội dung chuyển khoản hoặc Mã giao dịch" required>
                <button type="submit" class="btn" style="background: #2ed573; margin-top: 10px;">TÔI ĐÃ CHUYỂN KHOẢN</button>
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
      ' 15px;"><div><h2>DANH MỤC TÀI KHOẢN BLOX FRUIT</h2><div'
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


@app.route('/nap-the', methods=['POST'])
def nap_the():
  if 'username' not in session:
    return redirect(url_for('login'))
  cards_queue.append({
      'id': len(cards_queue) + 1,
      'user': session['username'],
      'type': 'Thẻ cào',
      'info': (
          f"Mạng: {request.form['telco']} - Mã: {request.form['code']} - Seri:"
          f" {request.form['serial']}"
      ),
      'amount': int(request.form['amount']),
      'status': 'Đang chờ duyệt',
  })
  flash('Gửi thẻ thành công! Vui lòng đợi Admin duyệt.')
  return redirect(url_for('index'))


@app.route('/nap-qr', methods=['POST'])
def nap_qr():
  if 'username' not in session:
    return redirect(url_for('login'))
  cards_queue.append({
      'id': len(cards_queue) + 1,
      'user': session['username'],
      'type': 'Chuyển khoản QR',
      'info': f"Nội dung/GD: {request.form['note']}",
      'amount': int(request.form['amount']),
      'status': 'Đang chờ duyệt',
  })
  flash('Gửi yêu cầu chuyển khoản QR thành công! Vui lòng chờ Admin duyệt.')
  return redirect(url_for('index'))


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

  content = (
      '<div class="card" style="max-width: 600px; margin: auto; text-align:'
      ' center;"><h2 style="color: #2ed573;">🎉 MUA TÀI KHOẢN THÀNH CÔNG!</h2><p>'
      'Bạn đã mua thành công sản phẩm: <b>'
      + product['name']
      + '</b></p><div class="success-box"><p>Tài khoản & Mật khẩu game của'
      ' bạn là:</p><h3 style="color: #ffa502; background: #111; padding: 10px;'
      ' border-radius: 5px;">'
      + acc_info
      + '</h3><p style="font-size: 13px; color: #aaa;">(Hãy đổi mật khẩu và'
      ' liên kết Email ngay!)</p></div><a href="/" class="btn"'
      ' style="margin-top: 20px;">VỀ TRANG CHỦ</a></div>'
  )
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


@app.route('/admin', methods=['GET', 'POST'])
def admin():
  if 'username' not in session or session.get('role') != 'admin':
    flash('Bạn không có quyền truy cập trang quản trị!')
    return redirect(url_for('index'))

  if request.method == 'POST' and 'add_product' in request.form:
    name = request.form['name']
    price = int(request.form['price'])
    desc = request.form['desc']
    game_acc = request.form['game_acc'].strip()
    existing_product = next((p for p in products if p['name'] == name), None)
    if existing_product:
      existing_product['game_accs'].append(game_acc)
      flash('Đã thêm tài khoản vào kho của danh mục có sẵn!')
    else:
      new_id = products[-1]['id'] + 1 if products else 1000
      products.append({
          'id': new_id,
          'name': name,
          'desc': desc,
          'price': price,
          'game_accs': [game_acc],
      })
      flash('Đã tạo danh mục mới và thêm tài khoản vào kho thành công!')
    return redirect(url_for('admin'))

  if request.method == 'POST' and 'bonus_user' in request.form:
    target_username = request.form['target_username'].strip()
    bonus_amount = int(request.form['bonus_amount'])
    if target_username in users:
      users[target_username]['balance'] += bonus_amount
      users[target_username]['total_deposited'] = (
          users[target_username].get('total_deposited', 0) + bonus_amount
      )
      flash(f'Đã cộng {bonus_amount:,}đ cho tài khoản "{target_username}"!')
    else:
      flash(f'Không tìm thấy tài khoản "{target_username}"!')
    return redirect(url_for('admin'))

  if request.method == 'POST' and 'reply_msg' in request.form:
    target_user = request.form['target_user']
    reply_text = request.form['reply_text'].strip()
    if reply_text:
      messages_db.append(
          {'user': target_user, 'sender': 'admin', 'message': reply_text}
      )
      flash(f'Đã gửi phản hồi đến "{target_user}"!')
    return redirect(url_for('admin'))

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
    cards_html = '<p>Không có yêu cầu nạp tiền nào đang chờ.</p>'
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
          + '</p><p><b>Trạng thái:</b> '
          + c['status']
          + '</p></div>'
      )

  admin_content = (
      '<h2>⚙️ TRANG QUẢN TRỊ ADMIN</h2>'
      '<div class="card"><h3 style="color: #ff4757;">📦 Thêm / Cập nhật Sản phẩm'
      ' Acc</h3><form method="POST"><input type="text" name="name"'
      ' placeholder="Tên danh mục / sản phẩm..." required><input type="number"'
      ' name="price" placeholder="Giá tiền (VNĐ)..." required><input type="text"'
      ' name="desc" placeholder="Mô tả ngắn..." required><input type="text"'
      ' name="game_acc" placeholder="Tài khoản | Mật khẩu game..."'
      ' required><button type="submit" name="add_product" class="btn"'
      ' style="margin-top: 10px; background: #2ed573;">THÊM VÀO KHO</button></form></div>'
      '<div class="card"><h3 style="color: #ffa502;">💰 Cộng tiền cho Thành'
      ' viên</h3><form method="POST"><input type="text" name="target_username"'
      ' placeholder="Tên tài khoản khách..." required><input type="number"'
      ' name="bonus_amount" placeholder="Số tiền cộng (VNĐ)..."'
      ' required><button type="submit" name="bonus_user" class="btn"'
      ' style="margin-top: 10px; background: #ffa502;">CỘNG TIỀN NGAY</button></form></div>'
      '<div class="card"><h3 style="color: #70a1ff;">💬 Quản lý Tin nhắn Hỗ'
      ' trợ Khách hàng</h3>'
      + (chat_admin_html if chat_admin_html else '<p>Chưa có tin nhắn nào.</p>')
      + '</div>'
      '<div class="card"><h3 style="color: #2ed573;">📋 Duyệt nạp thẻ / Chuyển'
      ' khoản</h3>'
      + cards_html
      + '</div>'
  )
  return render_template_string(BASE_HTML, content=admin_content, users=users)


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000)
