from datetime import datetime
from flask import Flask, flash, jsonify, redirect, render_template_string, request, session, url_for
import hashlib
import json
import urllib.request
import urllib.parse

app = Flask(__name__)
app.secret_key = 'shop_blox_fruit_smart_v30'

PARTNER_ID = '71186911886'
PARTNER_KEY = 'f7377b035f5b5d2c4a5d04e487b39aaf'

TELEGRAM_BOT_TOKEN = '8818555905:AAGFfnQhNpSQ0jC20X5IsZ0WVAVQImJVkM4'
TELEGRAM_CHAT_ID = '8976860826'

def send_telegram_notification(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message, 'parse_mode': 'HTML'}
        data = urllib.parse.urlencode(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, method='POST')
        with urllib.request.urlopen(req, timeout=5) as response:
            pass
    except Exception as e:
        print(f"Lỗi gửi Telegram: {e}")

users = {
    'admin': {'password': '123', 'role': 'admin', 'balance': 500000, 'total_deposited': 0},
    'player1': {'password': '123', 'role': 'user', 'balance': 50000, 'total_deposited': 100000},
}

products = [
    {
        'id': 1276,
        'name': 'ACC BLOX FRUITS TỘC V4 FULL GEAR, KITSUNE',
        'category': 'tuichon',
        'desc': 'Acc max level, full trang bị xịn, haki cực mạnh',
        'price': 30000,
        'image': 'https://i.ibb.co/DHCWq65g/file-00000000414c821198dbb4fd0f8ab53e.png',
        'game_accs': ['bloxfruit_1276_1@gmail.com | Pass123', 'bloxfruit_1276_2@gmail.com | Pass456'],
    },
    {
        'id': 5000,
        'name': 'TÚI MÙ BLOX FRUIT SIÊU RẺ (5K)',
        'category': 'random',
        'desc': 'Hên xui trúng acc khủng, tỷ lệ trúng tộc v4 cực cao!',
        'price': 5000,
        'image': '',
        'game_accs': ['random_acc_1@gmail.com | Pass111', 'random_acc_2@gmail.com | Pass222'],
    },
]

private_cai_cuoc_db = [
    {
        'id': 1,
        'account': 'adminnekk999 | ggggggggg',
        'note': 'Đang cày dở level 2400, giữ lại trái phật tổ trong rương'
    }
]

cay_thue_services = [
    {'id': 1, 'name': 'Cày Max Level (Level 1 -> Max)', 'price': 50000, 'desc': 'Cày nhanh gọn, an toàn.'}
]

cay_thue_status = {'is_ready': True, 'current_task': 'Đang trống, sẵn sàng nhận đơn mới!'}

coupons_db = [
    {
        'id': 1, 'code': 'GIAM5K', 'discount_amount': 5000, 
        'expiry_date': datetime.now().timestamp() + (7 * 86400),
        'max_uses': 10, 'used_count': 0, 'is_active': True
    }
]

cards_queue = []
purchase_history = []
visitors_history = []
messages_db = [{'user': 'player1', 'sender': 'admin', 'message': 'Chào bạn, shop hỗ trợ gì cho bạn?'}]

BASE_HTML = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Shop Blox Fruits - Uy Tín & Tự Động</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0f1016; --card-bg: #181a25; --border-color: #2a2d3d;
            --primary: #ff4757; --primary-hover: #ff6b81; --accent: #ffa502;
            --success: #2ed573; --text-main: #ffffff; --text-secondary: #a4b0be;
        }
        @keyframes rgb-rainbow { 0% { filter: hue-rotate(0deg); } 100% { filter: hue-rotate(360deg); } }
        @keyframes rgb-border {
            0% { border-color: #ff0000; box-shadow: 0 0 10px rgba(255,0,0,0.4); }
            50% { border-color: #00ff00; box-shadow: 0 0 10px rgba(0,255,0,0.4); }
            100% { border-color: #ff00ff; box-shadow: 0 0 10px rgba(255,0,255,0.4); }
        }
        @keyframes rgb-anim { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
        .rgb-box { border: 2px solid #ff0000 !important; animation: rgb-border 6s infinite; }
        .rgb-btn {
            background: linear-gradient(45deg, #ff0000, #ff7300, #fffb00, #48ff00, #00ffd5, #002bff, #7a00ff, #ff00c8, #ff0000) !important;
            background-size: 400% !important; animation: rgb-anim 8s linear infinite !important; color: white !important; transition: 0.3s;
        }
        .rgb-btn:hover { transform: translateY(-2px); box-shadow: 0 0 20px rgba(255, 255, 255, 0.6) !important; }
        .rgb-text {
            background: linear-gradient(to right, #ff4757, #ffa502, #2ed573, #1e90ff, #70a1ff, #ff6b81);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: rgb-rainbow 6s linear infinite; font-weight: 700;
        }
        body { background-color: var(--bg-color); color: var(--text-main); font-family: 'Poppins', sans-serif; margin: 0; padding: 0; }
        header { background: rgba(24, 26, 37, 0.95); backdrop-filter: blur(10px); padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); position: sticky; top: 0; z-index: 1000; flex-wrap: wrap; gap: 15px; }
        .logo { font-size: 22px; font-weight: 700; color: var(--primary); text-decoration: none; display: flex; align-items: center; gap: 8px; }
        .nav-buttons { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
        .container { padding: 30px 20px; max-width: 1100px; margin: auto; }
        .card { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 14px; padding: 20px; margin-bottom: 20px; box-shadow: 0 8px 25px rgba(0,0,0,0.3); position: relative; }
        .product-title { color: var(--text-main); font-weight: 600; font-size: 16px; margin-bottom: 5px; }
        .price { color: var(--primary); font-size: 20px; font-weight: 700; margin: 10px 0; }
        .btn { background: linear-gradient(135deg, #ff4757, #ff6b81); color: white; border: none; padding: 12px; width: 100%; border-radius: 8px; font-weight: 600; cursor: pointer; text-align: center; display: block; text-decoration: none; box-sizing: border-box; transition: 0.3s; }
        .btn-delete { background: rgba(255,71,87,0.2); border: 1px solid var(--primary); color: var(--primary-hover); padding: 5px 12px; border-radius: 6px; font-size: 12px; font-weight: 600; text-decoration: none; display: inline-flex; align-items: center; gap: 5px; }
        input, select, textarea { width: 100%; padding: 12px 15px; margin: 10px 0; background: #12131c; border: 1px solid var(--border-color); color: white; border-radius: 8px; box-sizing: border-box; font-family: 'Poppins', sans-serif; font-size: 14px; }
        input:focus, select:focus, textarea:focus { outline: none; border-color: var(--primary); }
        .alert { background: rgba(255,71,87,0.15); border: 1px solid var(--primary); color: #ff6b81; padding: 12px 20px; border-radius: 10px; margin-bottom: 20px; text-align: center; font-weight: 500; }
        .success-box { background: rgba(46,213,115,0.1); border: 1px solid var(--success); padding: 20px; border-radius: 10px; margin-top: 15px; text-align: center; }
        .top-user-item { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid var(--border-color); font-size: 14px; align-items: center; }
        .chat-box { background: #12131c; border: 1px solid var(--border-color); border-radius: 10px; padding: 12px; max-height: 220px; overflow-y: auto; margin-bottom: 12px; }
        .chat-msg { margin-bottom: 10px; font-size: 13px; line-height: 1.4; }
        .chat-msg.user { color: #70a1ff; text-align: right; }
        .chat-msg.admin { color: var(--success); text-align: left; }
    </style>
</head>
<body>
    <header>
        <a href="/" class="logo rgb-text">⚡ BLOX FRUIT STORE</a>
        <div class="nav-buttons">
            {% if 'username' in session %}
                <span style="background: rgba(46,213,115,0.15); border: 1px solid var(--success); color: var(--success); padding: 8px 14px; border-radius: 8px; font-weight: 600; font-size: 13px;">Số dư: {{ "{:,.0f}".format(users[session['username']]['balance']) }}đ</span>
                <a href="/lich-su" class="rgb-btn" style="padding: 9px 18px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 13px;">📜 Lịch sử</a>
                <a href="/doi-mat-khau" class="rgb-btn" style="padding: 9px 18px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 13px;">🔒 Đổi MK</a>
                {% if session.get('role') == 'admin' %}
                    <a href="/admin" class="rgb-btn" style="padding: 9px 18px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 13px;">⚙️ Quản trị</a>
                {% endif %}
                <a href="/logout" style="background: #747d8c; padding: 9px 18px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 13px; color: white;">Thoát</a>
            {% else %}
                <a href="/login" class="rgb-btn">Đăng nhập</a>
                <a href="/register" class="rgb-btn">Đăng ký</a>
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
    visitor_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    current_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    visitors_history.insert(0, {'ip': visitor_ip, 'time': current_time})
    if len(visitors_history) > 50: visitors_history.pop()

    sorted_users = sorted(users.items(), key=lambda x: x[1].get('total_deposited', 0), reverse=True)
    top_html = ''
    rank = 1
    for uname, udata in sorted_users:
        if udata.get('total_deposited', 0) > 0:
            medal = '🥇' if rank == 1 else ('🥈' if rank == 2 else ('🥉' if rank == 3 else f'#{rank}'))
            top_html += f'<div class="top-user-item"><span><b>{medal}</b> {uname}</span><span style="color: var(--accent); font-weight: 600;">{udata.get("total_deposited", 0):,}đ</span></div>'
            rank += 1
    if not top_html: top_html = '<p style="color: var(--text-secondary); text-align: center; font-size: 13px;">Chưa có dữ liệu nạp tiền.</p>'

    chat_html = ''
    if 'username' in session and session.get('role') != 'admin':
        curr_user = session['username']
        user_msgs = [m for m in messages_db if m['user'] == curr_user]
        msgs_render = ''
        if not user_msgs:
            msgs_render = '<p style="color: #777; font-size: 12px; text-align: center;">Chưa có tin nhắn!</p>'
        else:
            for m in user_msgs:
                sender_label = 'Bạn' if m['sender'] == curr_user else 'Admin'
                css_class = 'user' if m['sender'] == curr_user else 'admin'
                msgs_render += f'<div class="chat-msg {css_class}"><b>{sender_label}:</b> {m["message"]}</div>'

        chat_html = f'<div class="card rgb-box" style="border: 1px solid var(--primary);"><h3 style="color: var(--primary); margin-top: 0;">💬 Hỗ Trợ Trực Tuyến</h3><div class="chat-box">{msgs_render}</div><form action="/send-message" method="POST"><input type="text" name="message" placeholder="Nhập tin nhắn..." required style="margin: 0 0 10px 0;"><button type="submit" class="btn rgb-btn" style="padding: 8px; font-size: 13px;">GỬI TIN NHẮN</button></form></div>'

    products_html = ''
    for p in products:
        stock_count = len(p['game_accs'])
        action_btn = f'<a href="/tui-mu/{p["id"]}" class="btn rgb-btn" style="margin-top: 15px;">⚡ XÉ TÚI NGAY</a>' if p.get('category') == 'random' else f'<a href="/buy/{p["id"]}" class="btn rgb-btn" style="margin-top: 15px;">🛒 MUA NGAY</a>'
        img_tag = f'<img src="{p["image"]}" style="width: 100%; height: 160px; object-fit: cover; border-radius: 10px; margin-bottom: 12px; border: 1px solid var(--border-color);">' if p.get('image') else ''
        delete_btn = f'<div style="position: absolute; top: 15px; right: 15px;"><a href="/admin/delete/{p["id"]}" class="btn-delete" onclick="return confirm(\'Xóa sản phẩm?\');">🗑️ XÓA</a></div>' if session.get('role') == 'admin' else ''

        products_html += f'<div class="card rgb-box" style="display: flex; flex-direction: column; justify-content: space-between;">{delete_btn}<div>{img_tag}<div style="color: var(--text-secondary); font-size: 12px; font-weight: 600;">MÃ SÓ: #{p["id"]}</div><div class="product-title">{p["name"]}</div><p style="color: var(--text-secondary); font-size: 13px; line-height: 1.4;">{p["desc"]}</p></div><div><div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px;"><span style="font-size: 13px; color: var(--text-secondary);">Kho: <b style="color: white;">{stock_count}</b></span><span class="price">{p["price"]:,}đ</span></div>{action_btn}</div></div>'

    status_badge = '<span style="color: var(--success); font-weight: bold;">🟢 Sẵn sàng nhận đơn</span>' if cay_thue_status['is_ready'] else '<span style="color: var(--primary); font-weight: bold;">🔴 Đang bận</span>'
    status_note_box = f'<div style="background: #12131c; padding: 10px; border-radius: 6px; margin-bottom: 15px; font-size: 13px; border: 1px solid var(--border-color);">Trạng thái: {status_badge}<br><span style="color: var(--text-secondary);">Thông báo: <b>{cay_thue_status["current_task"]}</b></span></div>'

    cay_thue_html = ''
    for ct in cay_thue_services:
        btn_cay = f'<a href="/dat-cay-thue/{ct["id"]}" class="btn rgb-btn" style="margin-top: 12px;">⚡ ĐẶT DỊCH VỤ</a>' if cay_thue_status['is_ready'] else '<button class="btn" style="background: #475569; cursor: not-allowed; margin-top: 12px;" disabled>Đang bận!</button>'
        delete_ct_btn = f'<div style="position: absolute; top: 15px; right: 15px;"><a href="/admin/delete-cay-thue/{ct["id"]}" class="btn-delete" onclick="return confirm(\'Xóa?\');">🗑️ XÓA</a></div>' if session.get('role') == 'admin' else ''
        cay_thue_html += f'<div class="card rgb-box" style="position: relative;">{delete_ct_btn}<div class="product-title">{ct["name"]}</div><p style="color: var(--text-secondary); font-size: 13px;">{ct["desc"]}</p><div class="price">{ct["price"]:,}đ</div>{btn_cay}</div>'

    nap_html = ''
    if 'username' in session and session.get('role') != 'admin':
        curr_username = session['username']
        suggest_note = f'NAP {curr_username.upper()}'
        nap_html = f'<div class="card rgb-box" style="border: 1px solid var(--success);"><h3 class="rgb-text" style="margin-top:0;">⚡ NẠP TIỀN TỰ ĐỘNG</h3><div style="background: #12131c; padding: 15px; border-radius: 10px; margin-bottom: 20px; border: 1px solid var(--border-color);"><p style="margin: 0 0 8px 0; color: var(--accent); font-weight: 600;">📝 1. Chuyển khoản QR:</p><p style="margin: 0; font-size: 13px; color: var(--text-secondary);">Nội dung: <b style="color: var(--success); font-size: 15px;">{suggest_note}</b></p></div><div style="text-align: center; margin-bottom: 15px;"><img src="https://i.ibb.co/0pvhCGz1/zlp-1792493518267.jpg" alt="QR" style="max-width: 190px; border-radius: 10px; border: 3px solid white;"></div><form action="/nap-the" method="POST" style="border-top: 1px dashed var(--border-color); padding-top: 15px;"><h4 style="color: var(--accent); margin: 0 0 10px 0; font-size: 15px;">2. Nạp Thẻ Cào</h4><select name="telco"><option value="VIETTEL">Viettel</option><option value="MOBIFONE">Mobifone</option><option value="VINAPHONE">Vinaphone</option></select><select name="amount"><option value="10000">10.000đ</option><option value="20000">20.000đ</option><option value="50000">50.000đ</option><option value="100000">100.000đ</option></select><input type="text" name="code" placeholder="Mã thẻ" required><input type="text" name="serial" placeholder="Số Serial" required><button type="submit" class="btn rgb-btn" style="margin-top: 10px;">NẠP THẺ</button></form></div>'

    banner_html = '<div class="card rgb-box" style="text-align: center; padding: 15px; border: 1px solid var(--primary);"><img src="https://i.ibb.co/DHCWq65g/file-00000000414c821198dbb4fd0f8ab53e.png" alt="Banner" style="width: 100%; max-height: 380px; object-fit: cover; border-radius: 10px;"></div>'

    content = f'{banner_html}{nap_html}<div style="display: grid; grid-template-columns: 2fr 1fr; gap: 20px;"><div><h2 class="rgb-text">🔥 TÀI KHOẢN & TÚI MÙ</h2><div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">{products_html}</div><h2 class="rgb-text" style="margin-top: 30px;">⚔️ CÀY THUÊ</h2>{status_note_box}<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">{cay_thue_html}</div></div><div><div class="card rgb-box" style="border: 1px solid var(--accent); margin-bottom: 20px;"><h3 class="rgb-text" style="text-align: center; margin-top: 0;">🏆 TOP NẠP</h3>{top_html}</div>{chat_html}</div></div>'
    return render_template_string(BASE_HTML, content=content, users=users)

@app.route('/dat-cay-thue/<int:ct_id>', methods=['GET', 'POST'])
def dat_cay_thue(ct_id):
    if 'username' not in session: return redirect(url_for('login'))
    service = next((s for s in cay_thue_services if s['id'] == ct_id), None)
    if not service: return redirect(url_for('index'))
    if request.method == 'POST':
        username_game = request.form.get('username_game', '').strip()
        password_game = request.form.get('password_game', '').strip()
        users[session['username']]['balance'] -= service['price']
        purchase_history.append({'user': session['username'], 'product_name': f"Cày: {service['name']}", 'account_details': f"TK: {username_game} | Pass: {password_game}"})
        flash('Đặt cày thuê thành công!')
        return redirect(url_for('lich_su'))
    content = f'<div class="card rgb-box" style="max-width: 500px; margin: auto;"><h2 class="rgb-text" style="text-align: center;">ĐẶT CÀY THUÊ</h2><form method="POST"><input type="text" name="username_game" placeholder="Tài khoản game" required><input type="password" name="password_game" placeholder="Mật khẩu game" required><button type="submit" class="btn rgb-btn" style="margin-top: 15px;">THANH TOÁN</button></form></div>'
    return render_template_string(BASE_HTML, content=content, users=users)

@app.route('/doi-mat-khau', methods=['GET', 'POST'])
def doi_mat_khau():
    if 'username' not in session: return redirect(url_for('login'))
    if request.method == 'POST':
        users[session['username']]['password'] = request.form.get('new_password')
        flash('Đổi mật khẩu thành công!')
        return redirect(url_for('index'))
    content = '<div class="card rgb-box" style="max-width: 420px; margin: auto;"><h2 class="rgb-text" style="text-align: center;">ĐỔI MK</h2><form method="POST"><input type="password" name="old_password" placeholder="MK cũ" required><input type="password" name="new_password" placeholder="MK mới" required><button type="submit" class="btn rgb-btn" style="margin-top: 15px;">ĐỔI</button></form></div>'
    return render_template_string(BASE_HTML, content=content, users=users)

@app.route('/tui-mu/<int:product_id>')
def tui_mu(product_id):
    if 'username' not in session: return redirect(url_for('login'))
    product = next((p for p in products if p['id'] == product_id), None)
    content = f'<div class="card rgb-box" style="max-width: 500px; margin: auto; text-align: center;"><h2 class="rgb-text">⚡ MỞ TÚI MÙ</h2><p class="price">{product["price"]:,}đ</p><button onclick="xeTui({product[\"id\"]})" class="btn rgb-btn">🔥 XÉ TÚI</button></div><script>function xeTui(id){fetch("/api/buy-random/"+id, {method:"POST"}).then(res=>res.json()).then(d=>{if(d.success){alert("Thành công: "+d.account_info);location.href="/lich-su"}else{alert(d.message)}})}</script>'
    return render_template_string(BASE_HTML, content=content, users=users)

@app.route('/api/buy-random/<int:product_id>', methods=['POST'])
def api_buy_random(product_id):
    if 'username' not in session: return jsonify({'success': False, 'message': 'Đăng nhập đi!'})
    product = next((p for p in products if p['id'] == product_id), None)
    if not product or not product['game_accs']: return jsonify({'success': False, 'message': 'Hết hàng!'})
    acc_info = product['game_accs'].pop(0)
    users[session['username']]['balance'] -= product['price']
    purchase_history.append({'user': session['username'], 'product_name': product['name'], 'account_details': acc_info})
    return jsonify({'success': True, 'account_info': acc_info})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u, p = request.form['username'], request.form['password']
        if u in users and users[u]['password'] == p:
            session['username'] = u
            session['role'] = users[u]['role']
            return redirect(url_for('index'))
    content = '<div class="card rgb-box" style="max-width: 420px; margin: auto;"><h2 class="rgb-text" style="text-align: center;">ĐĂNG NHẬP</h2><form method="POST"><input type="text" name="username" placeholder="Tài khoản" required><input type="password" name="password" placeholder="Mật khẩu" required><button type="submit" class="btn rgb-btn" style="margin-top: 15px;">ĐĂNG NHẬP</button></form></div>'
    return render_template_string(BASE_HTML, content=content, users=users)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        u, p = request.form['username'].strip(), request.form['password'].strip()
        if u and p and u not in users:
            users[u] = {'password': p, 'role': 'user', 'balance': 0, 'total_deposited': 0}
            return redirect(url_for('login'))
    content = '<div class="card rgb-box" style="max-width: 420px; margin: auto;"><h2 class="rgb-text" style="text-align: center;">ĐĂNG KÝ</h2><form method="POST"><input type="text" name="username" placeholder="Tài khoản" required><input type="password" name="password" placeholder="Mật khẩu" required><button type="submit" class="btn rgb-btn" style="margin-top: 15px;">ĐĂNG KÝ</button></form></div>'
    return render_template_string(BASE_HTML, content=content, users=users)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/admin/delete/<int:product_id>')
def delete_product(product_id):
    global products
    products = [p for p in products if p['id'] != product_id]
    return redirect(url_for('index'))

@app.route('/admin/delete-private-acc/<int:acc_id>')
def delete_private_acc(acc_id):
    global private_cai_cuoc_db
    private_cai_cuoc_db = [acc for acc in private_cai_cuoc_db if acc['id'] != acc_id]
    return redirect(url_for('admin'))

@app.route('/admin/delete-cay-thue/<int:ct_id>')
def delete_cay_thue(ct_id):
    global cay_thue_services
    cay_thue_services = [s for s in cay_thue_services if s['id'] != ct_id]
    return redirect(url_for('admin'))

@app.route('/buy/<int:product_id>')
def buy(product_id):
    if 'username' not in session: return redirect(url_for('login'))
    product = next((p for p in products if p['id'] == product_id), None)
    if not product or not product['game_accs']: return redirect(url_for('index'))
    acc_info = product['game_accs'].pop(0)
    users[session['username']]['balance'] -= product['price']
    purchase_history.append({'user': session['username'], 'product_name': product['name'], 'account_details': acc_info})
    content = f'<div class="card rgb-box" style="max-width: 600px; margin: auto; text-align: center;"><h2 class="rgb-text">🎉 MUA THÀNH CÔNG</h2><div class="success-box"><h3>{acc_info}</h3></div><a href="/" class="btn rgb-btn" style="margin-top: 25px;">VỀ TRANG CHỦ</a></div>'
    return render_template_string(BASE_HTML, content=content, users=users)

@app.route('/lich-su')
def lich_su():
    if 'username' not in session: return redirect(url_for('login'))
    user_history = [h for h in purchase_history if h['user'] == session['username']]
    history_html = '<h2 class="rgb-text">📜 LỊCH SỬ GIAO DỊCH</h2>'
    for h in user_history:
        history_html += f'<div class="card rgb-box"><p><b>Sản phẩm:</b> {h["product_name"]}</p><p><b>Chi tiết:</b> <span style="color: var(--success);">{h["account_details"]}</span></p></div>'
    return render_template_string(BASE_HTML, content=history_html, users=users)

@app.route('/send-message', methods=['POST'])
def send_message():
    if 'username' not in session: return redirect(url_for('login'))
    msg = request.form['message'].strip()
    if msg: messages_db.append({'user': session['username'], 'sender': session['username'], 'message': msg})
    return redirect(url_for('index'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'username' not in session or session.get('role') != 'admin': return redirect(url_for('index'))

    if request.method == 'POST':
        if 'add_product' in request.form:
            name, price, cat = request.form['name'], int(request.form['price']), request.form['category']
            products.append({'id': len(products)+1000, 'name': name, 'category': cat, 'desc': request.form['desc'], 'price': price, 'image': request.form.get('image', ''), 'game_accs': [request.form['game_acc'].strip()]})
        elif 'add_private_acc' in request.form:
            private_cai_cuoc_db.append({'id': len(private_cai_cuoc_db)+1, 'account': request.form['private_account'].strip(), 'note': request.form['private_note'].strip()})
        elif 'add_cay_thue' in request.form:
            cay_thue_services.append({'id': len(cay_thue_services)+1, 'name': request.form['ct_name'].strip(), 'price': int(request.form['ct_price']), 'desc': request.form['ct_desc'].strip()})
        elif 'update_cay_thue_status' in request.form:
            cay_thue_status['is_ready'] = True if request.form.get('is_ready') == 'on' else False
            cay_thue_status['current_task'] = request.form.get('current_task', '').strip()
        return redirect(url_for('admin'))

    private_accs_html = ''.join([f'<div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); padding: 10px 0; font-size: 13px;"><div><b style="color: var(--success);">🎮 {acc["account"]}</b><br><span style="color: var(--accent);">📝 {acc["note"]}</span></div><a href="/admin/delete-private-acc/{acc["id"]}" class="btn-delete">🗑️ XÓA</a></div>' for acc in private_cai_cuoc_db]) or '<p>Trống.</p>'
    checked_attr = 'checked' if cay_thue_status['is_ready'] else ''

    admin_content = f"""
    <h2 class="rgb-text">⚙️ TRANG QUẢN TRỊ ADMIN</h2>
    
    <div class="card rgb-box" style="border: 1px solid var(--accent);">
        <h3 class="rgb-text" style="margin-top: 0;">📒 Sổ Tay Cày Cuốc Nick (Riêng tư)</h3>
        <form method="POST">
            <input type="text" name="private_account" placeholder="username | password" required>
            <textarea name="private_note" placeholder="Ghi chú tiến độ cày..." rows="2" style="width:100%; padding:12px; background:#12131c; border:1px solid var(--border-color); color:white; border-radius:8px;" required></textarea>
            <button type="submit" name="add_private_acc" class="btn rgb-btn" style="margin-top: 10px;">LƯU VÀO SỔ TAY</button>
        </form>
        <div style="background: #12131c; padding: 12px; border-radius: 8px; margin-top: 15px; max-height: 250px; overflow-y: auto;">{private_accs_html}</div>
    </div>

    <div class="card rgb-box" style="border: 1px solid var(--primary);">
        <h3 class="rgb-text" style="margin-top: 0;">🛒 Đăng Sản Phẩm Lên Shop</h3>
        <form method="POST">
            <input type="text" name="name" placeholder="Tên sản phẩm..." required>
            <select name="category"><option value="tuichon">Tự chọn (Có ảnh)</option><option value="random">Random / Túi mù</option></select>
            <input type="number" name="price" placeholder="Giá tiền (VNĐ)..." required>
            <input type="text" name="image" placeholder="Link ảnh minh họa...">
            <input type="text" name="desc" placeholder="Mô tả ngắn..." required>
            <input type="text" name="game_acc" placeholder="username | password" required>
            <button type="submit" name="add_product" class="btn rgb-btn" style="margin-top: 15px;">ĐĂNG BÁN</button>
        </form>
    </div>

    <div class="card rgb-box" style="border: 1px solid var(--success);">
        <h3 class="rgb-text" style="margin-top: 0;">⚡ Trạng Thái Cày Thuê</h3>
        <form method="POST">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
                <input type="checkbox" name="is_ready" {checked_attr} style="width: 20px; height: 20px; accent-color: var(--success);">
                <label style="font-size: 14px; font-weight: 600;">Sẵn sàng nhận đơn</label>
            </div>
            <input type="text" name="current_task" value="{cay_thue_status["current_task"]}" placeholder="Thông báo...">
            <button type="submit" name="update_cay_thue_status" class="btn rgb-btn" style="margin-top: 10px;">CẬP NHẬT</button>
        </form>
    </div>
    """
    return render_template_string(BASE_HTML, content=admin_content, users=users)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
