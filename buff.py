from flask import Flask, flash, jsonify, redirect, render_template_string, request, session, url_for
import hashlib
import json
import urllib.request
import urllib.parse

app = Flask(__name__)
app.secret_key = 'shop_blox_fruit_smart_v27'

PARTNER_ID = '71186911886'
PARTNER_KEY = 'f7377b035f5b5d2c4a5d04e487b39aaf'

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
        'name': 'ACC BLOX FRUITS TỘC V4',
        'category': 'tuichon',
        'desc': 'Acc max level, full trang bị',
        'price': 30000,
        'image': 'https://i.ibb.co/DHCWq65g/file-00000000414c821198dbb4fd0f8ab53e.png',
        'game_accs': ['acc1@gmail.com | pass1'],
    },
    {
        'id': 5000,
        'name': 'TÚI MÙ BLOX FRUIT (5K)',
        'category': 'random',
        'desc': 'Hên xui trúng acc khủng',
        'price': 5000,
        'image': 'https://i.ibb.co/0pvhCGz1/zlp-1792493518267.jpg',
        'game_accs': ['random1@gmail.com | pass1'],
    },
]

coupons_db = [
    {'id': 1, 'code': 'GIAM5K', 'discount_amount': 5000, 'is_active': True}
]

cards_queue = []
purchase_history = []
messages_db = []

BASE_HTML = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Shop Blox Fruits</title>
    <style>
        body { background-color: #121212; color: #fff; font-family: Arial, sans-serif; margin: 0; padding: 15px; }
        .card { background: #1e1e1e; border: 1px solid #333; border-radius: 8px; padding: 15px; margin-bottom: 15px; }
        .btn { background: #ff4757; color: white; border: none; padding: 10px; width: 100%; border-radius: 5px; font-weight: bold; cursor: pointer; text-align: center; display: block; text-decoration: none; box-sizing: border-box; }
        input, select { width: 100%; padding: 10px; margin: 8px 0; background: #2c2c2c; border: 1px solid #444; color: white; border-radius: 5px; box-sizing: border-box; }
        .alert { background: #ff4757; padding: 10px; border-radius: 5px; margin-bottom: 15px; text-align: center; }
    </style>
</head>
<body>
    <div style="max-width: 800px; margin: auto;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <a href="/" style="color: #ff4757; font-weight: bold; text-decoration: none; font-size: 18px;">⚡ SHOP GAME</a>
            <div>
                {% if 'username' in session %}
                    <span>Số dư: <b style="color: #2ed573;">{{ users[session['username']]['balance'] }}đ</b></span>
                    <a href="/lich-su" style="color: #70a1ff; margin-left: 10px;">Lịch sử</a>
                    {% if session['role'] == 'admin' %}
                        <a href="/admin" style="color: #2ed573; margin-left: 10px;">Admin</a>
                    {% endif %}
                    <a href="/logout" style="color: #ff4757; margin-left: 10px;">Thoát</a>
                {% else %}
                    <a href="/login" style="color: #ff4757;">Đăng nhập</a>
                {% endif %}
            </div>
        </div>
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
  p_html = ''
  for p in products:
    btn = (
        f'<a href="/tui-mu/{p["id"]}" class="btn"'
        ' style="background:#ffa502;">⚡ XÉ TÚI NGAY</a>'
        if p.get('category') == 'random'
        else f'<a href="/buy/{p["id"]}" class="btn">🛒 MUA NGAY</a>'
    )
    p_html += (
        '<div class="card">'
        f"<h3>{p['name']}</h3>"
        f"<p>{p['desc']}</p>"
        f'<p>Giá: <b style="color:#ff4757;">{p["price"]:,}đ</b> | Kho:'
        f" {len(p['game_accs'])}</p>"
        f'{btn}'
        '</div>'
    )
  content = (
      '<h2>DANH MỤC SẢN PHẨM</h2>'
      + p_html
      + '<br><a href="/admin" style="color: #2ed573;">Trang Quản Trị Admin</a>'
  )
  return render_template_string(BASE_HTML, content=content, users=users)


@app.route('/tui-mu/<int:product_id>')
def tui_mu(product_id):
  if 'username' not in session:
    return redirect(url_for('login'))
  p = next((x for x in products if x['id'] == product_id), None)
  if not p:
    return redirect(url_for('index'))

  content = (
      '<div class="card" style="text-align: center;">'
      f"<h2>⚡ MỞ TÚI MÙ: {p['name']}</h2>"
      f"<p>Giá: {p['price']:,}đ</p>"
      '<input type="text" id="coupon" placeholder="Nhập mã giảm giá...">'
      f'<button onclick="xeTui({p[\'id\']})" class="btn"'
      ' style="background: #ffa502; margin-top: 10px;">XÉ TÚI NGAY</button>'
      '<br><a href="/" style="color: #aaa;">← Quay lại</a>'
      '</div>'
      '<script>'
      'function xeTui(id) {'
      "let code = document.getElementById('coupon').value;"
      "fetch('/api/buy-random/' + id, {"
      "method: 'POST',"
      "headers: {'Content-Type': 'application/json'},"
      "body: JSON.stringify({coupon_code: code})"
      '})'
      '.then(res => res.json())'
      '.then(data => {'
      'if(data.success) {'
      'alert("Thành công! Acc: " + data.account_info);'
      "window.location.href = '/lich-su';"
      '} else {'
      'alert(data.message);'
      '}'
      '});'
      '}'
      '</script>'
  )
  return render_template_string(BASE_HTML, content=content, users=users)


@app.route('/api/buy-random/<int:product_id>', methods=['POST'])
def api_buy_random(product_id):
  if 'username' not in session:
    return jsonify({'success': False, 'message': 'Chưa đăng nhập'})
  uname = session['username']
  p = next((x for x in products if x['id'] == product_id), None)
  if not p or not p['game_accs']:
    return jsonify({'success': False, 'message': 'Hết hàng'})

  data = request.json or {}
  code = data.get('coupon_code', '').strip().upper()
  price = p['price']

  if code:
    coupon = next(
        (c for c in coupons_db if c['code'] == code and c['is_active']), None
    )
    if coupon:
      price = max(0, price - coupon['discount_amount'])
    else:
      return jsonify({'success': False, 'message': 'Mã giảm giá không hợp lệ'})

  if users[uname]['balance'] < price:
    return jsonify({'success': False, 'message': 'Không đủ số dư'})

  users[uname]['balance'] -= price
  acc = p['game_accs'].pop(0)
  purchase_history.append(
      {'user': uname, 'product_name': p['name'], 'account_details': acc}
  )
  return jsonify({'success': True, 'account_info': acc})


@app.route('/buy/<int:product_id>')
def buy(product_id):
  if 'username' not in session:
    return redirect(url_for('login'))
  uname = session['username']
  p = next((x for x in products if x['id'] == product_id), None)
  if not p or not p['game_accs']:
    flash('Hết hàng!')
    return redirect(url_for('index'))
  if users[uname]['balance'] < p['price']:
    flash('Không đủ số dư!')
    return redirect(url_for('index'))

  users[uname]['balance'] -= p['price']
  acc = p['game_accs'].pop(0)
  purchase_history.append(
      {'user': uname, 'product_name': p['name'], 'account_details': acc}
  )
  content = (
      '<div class="card" style="text-align: center;">'
      '<h2 style="color: #2ed573;">MUA THÀNH CÔNG!</h2>'
      f'<p>Thông tin: <b>{acc}</b></p>'
      '<a href="/" class="btn">VỀ TRANG CHỦ</a>'
      '</div>'
  )
  return render_template_string(BASE_HTML, content=content, users=users)


@app.route('/lich-su')
def lich_su():
  if 'username' not in session:
    return redirect(url_for('login'))
  hist = [h for h in purchase_history if h['user'] == session['username']]
  h_html = '<h2>Lịch sử mua hàng</h2>'
  for h in hist:
    h_html += (
        '<div class="card">'
        f'<p>{h["product_name"]}</p><b'
        f' style="color:#2ed573;">{h["account_details"]}</b>'
        '</div>'
    )
  if not hist:
    h_html += '<p>Chưa có lịch sử.</p>'
  return render_template_string(BASE_HTML, content=h_html, users=users)


@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    u = request.form['username']
    p = request.form['password']
    if u in users and users[u]['password'] == p:
      session['username'] = u
      session['role'] = users[u]['role']
      return redirect(url_for('index'))
    flash('Sai tài khoản hoặc mật khẩu!')
  content = """
    <div class="card" style="max-width: 400px; margin: auto;">
        <h2>ĐĂNG NHẬP</h2>
        <form method="POST">
            <input type="text" name="username" placeholder="Tài khoản" required>
            <input type="password" name="password" placeholder="Mật khẩu" required>
            <button type="submit" class="btn" style="margin-top: 10px;">ĐĂNG NHẬP</button>
        </form>
    </div>
    """
  return render_template_string(BASE_HTML, content=content, users=users)


@app.route('/logout')
def logout():
  session.clear()
  return redirect(url_for('index'))


@app.route('/admin', methods=['GET', 'POST'])
def admin():
  if 'username' not in session or session.get('role') != 'admin':
    return redirect(url_for('index'))

  if request.method == 'POST':
    if 'add_product' in request.form:
      products.append({
          'id': len(products) + 100,
          'name': request.form['name'],
          'category': request.form['category'],
          'desc': request.form['desc'],
          'price': int(request.form['price']),
          'game_accs': [request.form['game_acc']],
      })
      flash('Đã thêm sản phẩm!')
    elif 'add_coupon' in request.form:
      coupons_db.append({
          'id': len(coupons_db) + 1,
          'code': request.form['code'].strip().upper(),
          'discount_amount': float(request.form['discount']),
          'is_active': True,
      })
      flash('Đã thêm mã giảm giá!')
    return redirect(url_for('admin'))

  c_html = ''.join([
      f'<div>{c["code"]} (-{c["discount_amount"]}đ) - {"Hoạt động" if c["is_active"] else "Tắt"}</div>'
      for c in coupons_db
  ])

  content = f"""
    <h2>TRANG QUẢN TRỊ ADMIN</h2>
    <div class="card">
        <h3>Thêm sản phẩm</h3>
        <form method="POST">
            <input type="text" name="name" placeholder="Tên sản phẩm" required>
            <select name="category"><option value="tuichon">Tự chọn</option><option value="random">Random</option></select>
            <input type="number" name="price" placeholder="Giá" required>
            <input type="text" name="desc" placeholder="Mô tả">
            <input type="text" name="game_acc" placeholder="Tài khoản | Mật khẩu" required>
            <button type="submit" name="add_product" class="btn" style="background:#2ed573;">Thêm sản phẩm</button>
        </form>
    </div>
    <div class="card">
        <h3>Thêm mã giảm giá</h3>
        <form method="POST">
            <input type="text" name="code" placeholder="Mã (VD: GIAM5K)" required>
            <input type="number" name="discount" placeholder="Số tiền giảm" required>
            <button type="submit" name="add_coupon" class="btn" style="background:#ffa502;">Thêm mã</button>
        </form>
        <div style="margin-top: 10px;">{c_html}</div>
    </div>
    <a href="/" style="color: #ff4757;">← Về trang chủ</a>
    """
  return render_template_string(BASE_HTML, content=content, users=users)


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000)
