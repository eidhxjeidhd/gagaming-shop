from datetime import datetime
import os
from flask import Flask, flash, jsonify, redirect, render_template_string, request, session, url_for
import urllib.request
import urllib.parse
import random

app = Flask(__name__)
app.secret_key = 'ga_gaming_roblox_full_option_2026'

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

PARTNER_ID = '71186911886'
PARTNER_KEY = 'f7377b035f5b5d2c4a5d04e487b39aaf'

TELEGRAM_BOT_TOKEN = '8818555905:AAGFfnQhNpSQ0jC20X5IsZ0WVAVQImJVkM4'
TELEGRAM_CHAT_ID = '8976860826'

def send_telegram_notification(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }
        data = urllib.parse.urlencode(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, method='POST')
        with urllib.request.urlopen(req, timeout=5) as response:
            pass
    except Exception as e:
        print(f"Lỗi gửi Telegram: {e}")

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
        'balance': 50050,
        'total_deposited': 100000,
    },
}

products = [
    {
        'id': 1276,
        'name': 'ACC BLOX FRUITS TỘC V4 FULL GEAR, KITSUNE',
        'category': 'tuichon',
        'desc': 'Acc max level, full trang bị xịn, haki cực mạnh',
        'price': 30000,
        'images': [
            'https://i.ibb.co/Z1Yck7SH/7475196962448704520-avatar-png.png'
        ],
        'game_accs': [
            'bloxfruit_1276_1@gmail.com | Pass123',
            'bloxfruit_1276_2@gmail.com | Pass456',
        ],
    },
]

cay_thue_services = [
    {
        'id': 1,
        'name': 'Cày Max Level (Level 1 -> Max)',
        'price': 50000,
        'desc': 'Cày nhanh gọn, an toàn, không dùng tool bẩn nguy hiểm.'
    }
]

cay_thue_status = {
    'is_ready': True,
    'current_task': 'Đang trống, sẵn sàng nhận đơn mới!'
}

private_cai_cuoc_db = []
coupons_db = [
    {
        'id': 1, 
        'code': 'GIAM5K', 
        'discount_amount': 5000, 
        'expiry_date': datetime.now().timestamp() + (7 * 86400),
        'max_uses': 10,
        'used_count': 0,
        'is_active': True
    }
]

cards_queue = []
purchase_history = []
visitors_history = []
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
    <title>GA GAMING ROBLOX - Shop Uy Tín & Tự Động</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0b0c10;
            --card-bg: #151823;
            --border-color: #232738;
            --primary: #ff4757;
            --primary-hover: #ff6b81;
            --accent: #ffa502;
            --success: #2ed573;
            --text-main: #ffffff;
            --text-secondary: #8f9bb3;
        }
        body { background-color: var(--bg-color); color: var(--text-main); font-family: 'Poppins', sans-serif; margin: 0; padding-bottom: 70px; }
        header { background: #12151f; border-bottom: 1px solid var(--border-color); padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 1000; }
        .logo-area { display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 16px; color: var(--primary); text-decoration: none; }
        .logo-area img { width: 36px; height: 36px; border-radius: 50%; border: 2px solid var(--primary); object-fit: cover; }
        .menu-btn { background: none; border: none; color: white; font-size: 22px; cursor: pointer; }
        .drawer { position: fixed; top: 0; right: -280px; width: 280px; height: 100%; background: #151823; border-left: 1px solid var(--border-color); z-index: 2000; transition: 0.3s ease; padding: 20px; box-sizing: border-box; }
        .drawer.open { right: 0; }
        .drawer-close { background: none; border: none; color: white; font-size: 20px; float: right; cursor: pointer; margin-bottom: 20px; }
        .drawer a { display: block; padding: 12px 15px; color: white; text-decoration: none; font-weight: 500; border-radius: 8px; margin-bottom: 8px; background: #1f2437; font-size: 14px; }
        .drawer a:hover { background: var(--primary); }
        .notice-banner { background: linear-gradient(90deg, #1f2437, #151823); border: 1px solid var(--border-color); padding: 12px 15px; border-radius: 10px; margin: 15px 15px 5px 15px; font-size: 13px; line-height: 1.5; color: #d1d5db; }
        .notice-banner b { color: var(--accent); }
        .social-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; padding: 15px; }
        .social-item { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 12px; padding: 12px; text-align: center; text-decoration: none; color: white; font-size: 12px; font-weight: 500; display: flex; flex-direction: column; align-items: center; gap: 6px; transition: 0.2s; }
        .social-item:hover { border-color: var(--primary); }
        .social-item img { width: 32px; height: 32px; border-radius: 8px; object-fit: cover; }
        .container { padding: 10px 15px; max-width: 1100px; margin: auto; }
        .card { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 14px; padding: 20px; margin-bottom: 20px; box-shadow: 0 8px 25px rgba(0,0,0,0.3); position: relative; }
        .product-title { color: var(--text-main); font-weight: 600; font-size: 15px; margin-bottom: 5px; }
        .price { color: var(--primary); font-size: 18px; font-weight: 700; margin: 10px 0; }
        .btn { background: linear-gradient(135deg, #ff4757, #ff6b81); color: white; border: none; padding: 10px; width: 100%; border-radius: 8px; font-weight: 600; cursor: pointer; text-align: center; display: block; text-decoration: none; box-sizing: border-box; transition: all 0.3s ease; }
        .btn-delete { background: rgba(255,71,87,0.2); border: 1px solid var(--primary); color: var(--primary-hover); padding: 5px 12px; border-radius: 6px; font-size: 12px; font-weight: 600; text-decoration: none; display: inline-flex; align-items: center; gap: 5px; }
        input, select, textarea { width: 100%; padding: 12px 15px; margin: 10px 0; background: #12131c; border: 1px solid var(--border-color); color: white; border-radius: 8px; box-sizing: border-box; font-family: 'Poppins', sans-serif; font-size: 14px; }
        .alert { background: rgba(255,71,87,0.15); border: 1px solid var(--primary); color: #ff6b81; padding: 12px 20px; border-radius: 10px; margin-bottom: 20px; text-align: center; font-weight: 500; }
        .top-user-item { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid var(--border-color); font-size: 14px; align-items: center; }
        .chat-box { background: #12131c; border: 1px solid var(--border-color); border-radius: 10px; padding: 12px; max-height: 220px; overflow-y: auto; margin-bottom: 12px; }
        .chat-msg { margin-bottom: 10px; font-size: 13px; line-height: 1.4; }
        .chat-msg.user { color: #70a1ff; text-align: right; }
        .chat-msg.admin { color: var(--success); text-align: left; }
        .slider-container { position: relative; width: 100%; border-radius: 10px; overflow: hidden; background: #12131c; border: 1px solid var(--border-color); margin-bottom: 15px; }
        .slider-track { display: flex; transition: transform 0.4s ease-in-out; width: 100%; }
        .slider-slide { min-width: 100%; box-sizing: border-box; display: flex; justify-content: center; align-items: center; }
        .slider-slide img { width: 100%; height: 240px; object-fit: cover; }
        .slider-btn { position: absolute; top: 50%; transform: translateY(-50%); background: rgba(0,0,0,0.6); color: white; border: none; padding: 10px 14px; cursor: pointer; font-size: 16px; border-radius: 50%; z-index: 10; transition: 0.2s; }
        .slider-btn:hover { background: var(--primary); }
        .slider-prev { left: 10px; }
        .slider-next { right: 10px; }
        .slider-dots { display: flex; justify-content: center; gap: 6px; margin-top: 8px; }
        .dot { width: 8px; height: 8px; background: #475569; border-radius: 50%; cursor: pointer; transition: 0.3s; }
        .dot.active { background: var(--primary); width: 20px; border-radius: 4px; }
        .bottom-nav { position: fixed; bottom: 0; left: 0; width: 100%; background: #12151f; border-top: 1px solid var(--border-color); display: flex; justify-content: space-around; padding: 10px 0; z-index: 1000; }
        .bottom-item { color: var(--text-secondary); text-decoration: none; font-size: 11px; display: flex; flex-direction: column; align-items: center; gap: 3px; font-weight: 500; }
        .bottom-item.active, .bottom-item:hover { color: var(--primary); }
        .bottom-item .avatar-circle { width: 32px; height: 32px; background: var(--accent); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: black; font-weight: bold; margin-top: -15px; border: 2px solid #12151f; }
    </style>
</head>
<body>
    <header>
        <a href="/" class="logo-area">
            <img src="https://i.ibb.co/Z1Yck7SH/7475196962448704520-avatar-png.png" alt="Logo">
            <span>GA GAMING ROBLOX</span>
        </a>
        <button class="menu-btn" onclick="toggleDrawer()">☰</button>
    </header>

    <div class="drawer" id="mobileDrawer">
        <button class="drawer-close" onclick="toggleDrawer()">✕</button>
        {% if 'username' in session %}
            <a href="#" style="background: rgba(46,213,115,0.2); color: var(--success);">Số dư: {{ "{:,.0f}".format(users[session['username']]['balance']) }}đ</a>
            <a href="/lich-su">📜 Lịch sử giao dịch</a>
            <a href="/doi-mat-khau">🔒 Đổi mật khẩu</a>
            {% if session.get('role') == 'admin' %}
                <a href="/admin">⚙️ Trang Quản Trị Admin</a>
            {% endif %}
            <a href="/logout" style="background: #e74c3c;">Đăng xuất</a>
        {% else %}
            <a href="/login">🔑 Đăng nhập hệ thống</a>
            <a href="/register">📝 Đăng ký tài khoản</a>
        {% endif %}
    </div>

    <div class="notice-banner">
        <b>100% ACC BÊN MÌNH ĐỀU LÀ ROBLOX QUỐC TẾ NHÉ.</b><br>
        Khi đăng nhập tài khoản Roblox, hệ thống sẽ yêu cầu xác minh 2 bước (2FA). Hãy tạo mã Backup Code theo video hướng dẫn để vào shop nhận acc tự động siêu tốc!
    </div>

    <div class="social-grid">
        <a href="https://www.youtube.com/@e_hahe" target="_blank" class="social-item">
            <img src="https://upload.wikimedia.org/wikipedia/commons/0/09/YouTube_full-color_icon_%282017%29.svg" alt="YT">
            Youtube mình
        </a>
        <a href="https://www.tiktok.com/@idollatao" target="_blank" class="social-item">
            <img src="https://sf16-scmcdn-va.ibytedtos.com/obj/eden-va/uv_ln7wvj/ljhwZthlaukjlkulzlp/tiktok-icon-2.png" alt="TikTok">
            TikTok Minh
        </a>
    </div>

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

    <div class="bottom-nav">
        <a href="/" class="bottom-item active" style="width: 100%;">
            <div class="avatar-circle">👤</div>
            <span>Trang chủ</span>
        </a>
    </div>

    <script>
        function toggleDrawer() {
            document.getElementById('mobileDrawer').classList.toggle('open');
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
  visitor_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
  current_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
  visitors_history.insert(0, {'ip': visitor_ip, 'time': current_time})
  if len(visitors_history) > 50:
    visitors_history.pop()

  sorted_users = sorted(users.items(), key=lambda x: x[1].get('total_deposited', 0), reverse=True)
  top_html = ''
  rank = 1
  for uname, udata in sorted_users:
    if udata.get('total_deposited', 0) > 0:
      medal = '🥇' if rank == 1 else ('🥈' if rank == 2 else ('🥉' if rank == 3 else f'#{rank}'))
      top_html += f'<div class="top-user-item"><span><b>{medal}</b> {uname}</span><span style="color: var(--accent); font-weight: 600;">{udata.get("total_deposited", 0):,}đ</span></div>'
      rank += 1
  if not top_html:
    top_html = '<p style="color: var(--text-secondary); text-align: center; font-size: 13px;">Chưa có dữ liệu nạp tiền.</p>'

  chat_html = ''
  if 'username' in session and session.get('role') != 'admin':
    curr_user = session['username']
    user_msgs = [m for m in messages_db if m['user'] == curr_user]
    msgs_render = ''
    if not user_msgs:
      msgs_render = '<p style="color: #777; font-size: 12px; text-align: center;">Chưa có tin nhắn, hãy chat với admin nếu cần hỗ trợ!</p>'
    else:
      for m in user_msgs:
        sender_label = 'Bạn' if m['sender'] == curr_user else 'Admin'
        css_class = 'user' if m['sender'] == curr_user else 'admin'
        msgs_render += f'<div class="chat-msg {css_class}"><b>{sender_label}:</b> {m["message"]}</div>'
    chat_html = f'<div class="card" style="border: 1px solid var(--primary);"><h3 style="color: var(--primary); margin-top: 0;">💬 Hỗ Trợ Trực Tuyến</h3><div class="chat-box">{msgs_render}</div><form action="/send-message" method="POST"><input type="text" name="message" placeholder="Nhập tin nhắn cho Admin..." required style="margin: 0 0 10px 0;"><button type="submit" class="btn rgb-btn" style="padding: 8px; font-size: 13px;">GỬI TIN NHẮN</button></form></div>'

  products_html = ''
  for p in products:
    stock_count = len(p.get('game_accs', []))
    if p.get('category') == 'random':
      action_btn = f'<a href="/tui-mu/{p["id"]}" class="btn rgb-btn" style="margin-top: 15px;">⚡ XÉ TÚI NGAY</a>'
    else:
      action_btn = f'<a href="/buy/{p["id"]}" class="btn rgb-btn" style="margin-top: 15px;">🛒 MUA NGAY</a>'

    images_list = p.get('images', [])
    if not isinstance(images_list, list) or len(images_list) == 0 or not images_list[0]:
      images_list = ['https://i.ibb.co/Z1Yck7SH/7475196962448704520-avatar-png.png']
    thumb_img = images_list[0]
    
    img_tag = f'<img src="{thumb_img}" style="width: 100%; height: 130px; object-fit: cover; border-radius: 10px; margin-bottom: 10px; border: 1px solid var(--border-color);">' if thumb_img else ''
    delete_btn = f'<div style="position: absolute; top: 15px; right: 15px;"><a href="/admin/delete/{p["id"]}" class="btn-delete" onclick="return confirm(\'Xóa sản phẩm này?\');">🗑️ XÓA</a></div>' if session.get('role') == 'admin' else ''

    products_html += f'<div class="card" style="display: flex; flex-direction: column; justify-content: space-between;">{delete_btn}<div>{img_tag}<div style="color: var(--text-secondary); font-size: 11px; font-weight: 600;">MÃ SÓ: #{p["id"]}</div><div class="product-title">{p.get("name", "")}</div><p style="color: var(--text-secondary); font-size: 12px; line-height: 1.4;">{p.get("desc", "")}</p></div><div><div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px;"><span style="font-size: 12px; color: var(--text-secondary);">Kho: <b style="color: white;">{stock_count}</b></span><span class="price">{p.get("price", 0):,}đ</span></div>{action_btn}</div></div>'

  status_badge = '<span style="color: var(--success); font-weight: bold;">🟢 Đang sẵn sàng nhận đơn</span>' if cay_thue_status['is_ready'] else '<span style="color: var(--primary); font-weight: bold;">🔴 Đang bận (Vui lòng đợi)</span>'
  status_note_box = f'<div style="background: #12131c; padding: 10px; border-radius: 6px; margin-bottom: 15px; font-size: 13px; border: 1px solid var(--border-color);">Trạng thái hiện tại: {status_badge}<br><span style="color: var(--text-secondary);">Thông báo: <b>{cay_thue_status["current_task"]}</b></span></div>'

  cay_thue_html = ''
  for ct in cay_thue_services:
    if cay_thue_status['is_ready']:
      btn_cay = f'<a href="/dat-cay-thue/{ct["id"]}" class="btn rgb-btn" style="margin-top: 12px;">⚡ ĐẶT DỊCH VỤ</a>'
    else:
      btn_cay = '<button class="btn" style="background: #475569; cursor: not-allowed; margin-top: 12px;" disabled>Đang bận cày cho khách, vui lòng đợi!</button>'
    delete_ct_btn = f'<div style="position: absolute; top: 15px; right: 15px;"><a href="/admin/delete-cay-thue/{ct["id"]}" class="btn-delete" onclick="return confirm(\'Xóa dịch vụ này?\');">🗑️ XÓA</a></div>' if session.get('role') == 'admin' else ''
    cay_thue_html += f'<div class="card" style="position: relative;">{delete_ct_btn}<div class="product-title">{ct["name"]}</div><p style="color: var(--text-secondary); font-size: 12px;">{ct["desc"]}</p><div class="price">{ct["price"]:,}đ</div>{btn_cay}</div>'
  if not cay_thue_html:
    cay_thue_html = '<p style="color: var(--text-secondary); font-size: 13px;">Chưa có gói cày thuê nào.</p>'

  nap_html = ''
  if 'username' in session and session.get('role') != 'admin':
    curr_username = session['username']
    suggest_note = f'NAP {curr_username.upper()}'
    nap_html = f'<div class="card" style="border: 1px solid var(--success);"><h3 class="rgb-text" style="margin-top:0;">⚡ NẠP TIỀN</h3><div style="background: #12131c; padding: 15px; border-radius: 10px; margin-bottom: 20px; border: 1px solid var(--border-color);"><p style="margin: 0 0 8px 0; color: var(--accent); font-weight: 600;">📝 1. Chuyển khoản QR siêu tốc:</p><p style="margin: 0; font-size: 13px; color: var(--text-secondary);">Nội dung: <b style="color: var(--success); font-size: 15px;">{suggest_note}</b>. Tự động cộng tiền sau 3 giây!</p></div><div style="text-align: center; margin-bottom: 15px;"><img src="https://i.ibb.co/0pvhCGz1/zlp-1792493518267.jpg" alt="QR" style="max-width: 190px; border-radius: 10px; border: 3px solid white;"><p style="font-size: 12px; color: var(--text-secondary); margin: 8px 0 0 0;">Chủ TK: NGUYEN VAN DUONG</p></div><form action="/nap-the" method="POST" style="margin-top: 20px; border-top: 1px dashed var(--border-color); padding-top: 20px;"><h4 style="color: var(--accent); margin: 0 0 12px 0; font-size: 15px;">2. Gửi Thẻ Cào (Duyệt Tay)</h4><label style="font-size: 13px; color: var(--text-secondary);">Nhà mạng:</label><select name="telco"><option value="VIETTEL">Viettel</option><option value="MOBIFONE">Mobifone</option><option value="VINAPHONE">Vinaphone</option></select><label style="font-size: 13px; color: var(--text-secondary);">Mệnh giá:</label><select name="amount"><option value="10000">10.000 đ</option><option value="20000">20.000 đ</option><option value="50000">50.000 đ</option><option value="100000">100.000 đ</option><option value="200000">200.000 đ</option><option value="500000">500.000 đ</option></select><input type="text" name="code" placeholder="Mã thẻ cào" required><input type="text" name="serial" placeholder="Số Serial" required><button type="submit" class="btn rgb-btn" style="margin-top: 12px;">GỬI THẺ CÀO DUYỆT</button></form></div>'

  banner_html = '<div class="card" style="text-align: center; padding: 10px; border: 1px solid var(--primary); background: linear-gradient(180deg, rgba(255,71,87,0.05), var(--card-bg));"><img src="https://i.ibb.co/Z1Yck7SH/7475196962448704520-avatar-png.png" alt="Banner" style="width: 100%; max-height: 250px; object-fit: cover; border-radius: 10px;"></div>'

  content = banner_html + nap_html + f'<div style="display: grid; grid-template-columns: 1fr; gap: 20px;"><div><h2 class="rgb-text">🔥 DANH MỤC TÀI KHOẢN & TÚI MÙ</h2><div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">{products_html}</div><h2 class="rgb-text" style="margin-top: 30px;">⚔️ DỊCH VỤ CÀY THUÊ UY TÍN</h2>{status_note_box}<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">{cay_thue_html}</div></div><div><div class="card" style="border: 1px solid var(--accent); margin-bottom: 20px;"><h3 class="rgb-text" style="text-align: center; margin-top: 0;">🏆 TOP NẠP TIỀN</h3>{top_html}</div>{chat_html}</div></div>'
  return render_template_string(BASE_HTML, content=content, users=users)

@app.route('/dat-cay-thue/<int:ct_id>', methods=['GET', 'POST'])
def dat_cay_thue(ct_id):
  if 'username' not in session:
    flash('Vui lòng đăng nhập để đặt dịch vụ!')
    return redirect(url_for('login'))
  if not cay_thue_status['is_ready']:
    flash('Shop đang bận, vui lòng đợi!')
    return redirect(url_for('index'))
  service = next((s for s in cay_thue_services if s['id'] == ct_id), None)
  if not service:
    flash('Không tìm thấy gói cày!')
    return redirect(url_for('index'))
  username = session['username']
  if request.method == 'POST':
    username_game = request.form.get('username_game', '').strip()
    password_game = request.form.get('password_game', '').strip()
    note_game = request.form.get('note_game', '').strip()
    if not username_game or not password_game:
      flash('Nhập đủ tài khoản và mật khẩu game!')
    elif users[username]['balance'] < service['price']:
      flash('Số dư không đủ!')
    else:
      users[username]['balance'] -= service['price']
      purchase_history.append({'user': username, 'product_name': f"Cày thuê: {service['name']}", 'account_details': f"TK: {username_game} | Pass: {password_game}"})
      send_telegram_notification(f"⚔️ <b>Có đơn cày thuê!</b>\nUser: {username}\nGói: {service['name']}\nTK: {username_game} | Pass: {password_game}")
      flash('Đặt đơn thành công!')
      return redirect(url_for('lich_su'))
  content = f"""
    <div class="card" style="max-width: 500px; margin: auto; border: 1px solid var(--accent);">
        <h2 class="rgb-text" style="text-align: center;">ĐẶT CÀY THUÊ</h2>
        <p style="color: var(--text-secondary); text-align: center;"><b>{service['name']}</b></p>
        <p class="price" style="text-align: center;">Giá: {service['price']:,}đ</p>
        <form method="POST">
            <label style="font-size: 13px; color: var(--text-secondary);">Tài khoản game:</label>
            <input type="text" name="username_game" placeholder="Nhập TK game..." required>
            <label style="font-size: 13px; color: var(--text-secondary);">Mật khẩu game:</label>
            <input type="password" name="password_game" placeholder="Nhập MK game..." required>
            <label style="font-size: 13px; color: var(--text-secondary);">Ghi chú thêm:</label>
            <textarea name="note_game" placeholder="Ghi chú..." rows="3"></textarea>
            <button type="submit" class="btn rgb-btn" style="margin-top: 15px;">XÁC NHẬN ĐẶT ĐƠN</button>
        </form>
        <div style="text-align: center; margin-top: 15px;"><a href="/" style="color: var(--text-secondary); font-size: 13px;">← Quay lại</a></div>
    </div>
    """
  return render_template_string(BASE_HTML, content=content, users=users)

@app.route('/doi-mat-khau', methods=['GET', 'POST'])
def doi_mat_khau():
  if 'username' not in session:
    return redirect(url_for('login'))
  if request.method == 'POST':
    username = session['username']
    old_pass = request.form.get('old_password', '').strip()
    new_pass = request.form.get('new_password', '').strip()
    if users[username]['password'] != old_pass:
      flash('Mật khẩu cũ không đúng!')
    elif len(new_pass) < 3:
      flash('Mật khẩu mới quá ngắn!')
    else:
      users[username]['password'] = new_pass
      flash('Đổi mật khẩu thành công!')
      return redirect(url_for('index'))
  content = """
    <div class="card" style="max-width: 420px; margin: auto;">
        <h2 class="rgb-text" style="text-align: center;">ĐỔI MẬT KHẨU</h2>
        <form method="POST">
            <label style="font-size: 13px; color: var(--text-secondary);">Mật khẩu cũ:</label>
            <input type="password" name="old_password" required>
            <label style="font-size: 13px; color: var(--text-secondary);">Mật khẩu mới:</label>
            <input type="password" name="new_password" required>
            <button type="submit" class="btn rgb-btn" style="margin-top: 15px;">ĐỔI MẬT KHẨU</button>
        </form>
    </div>
    """
  return render_template_string(BASE_HTML, content=content, users=users)

@app.route('/tui-mu/<int:product_id>')
def tui_mu(product_id):
  if 'username' not in session:
    flash('Đăng nhập để mở túi mù!')
    return redirect(url_for('login'))
  
  try:
    product = next((p for p in products if p['id'] == product_id), None)
    if not product:
      flash('Không tìm thấy sản phẩm!')
      return redirect(url_for('index'))

    images = product.get('images', [])
    if not isinstance(images, list) or len(images) == 0 or not images[0]:
      images = ['https://i.ibb.co/Z1Yck7SH/7475196962448704520-avatar-png.png']

    slider_slides = ''
    slider_dots = ''
    for i, img in enumerate(images):
      slider_slides += f'<div class="slider-slide"><img src="{img}" alt="Img"></div>'
      active_cls = ' active' if i == 0 else ''
      slider_dots += f'<span class="dot{active_cls}" onclick="currentSlide({i})"></span>'

    slider_html = f'<div class="slider-container"><div class="slider-track" id="sliderTrack">{slider_slides}</div>{"<button class=\"slider-btn slider-prev\" onclick=\"prevSlide()\">❮</button><button class=\"slider-btn slider-next\" onclick=\"nextSlide()\">❯</button>" if len(images) > 1 else ""}</div>{"<div class=\"slider-dots\">" + slider_dots + "</div>" if len(images) > 1 else ""}'

    content = f"""
      <div class="card" style="max-width: 500px; margin: auto; border: 1px solid var(--accent);">
          <h2 class="rgb-text" style="text-align: center;">⚡ MỞ TÚI MÙ: {product.get('name', '')}</h2>
          {slider_html}
          <p style="color: var(--text-secondary); text-align: center; margin-top: 10px;">{product.get('desc', '')}</p>
          <p class="price" style="text-align: center;">Giá: {product.get('price', 0):,}đ</p>
          <p style="color: var(--text-secondary); text-align: center;">Kho còn: <b style="color: white;">{len(product.get('game_accs', []))}</b> tài khoản</p>
          <div style="margin: 20px 0;"><label style="font-size: 13px; color: var(--text-secondary);">Mã giảm giá:</label><input type="text" id="coupon_code" placeholder="Mã (nếu có)"><button type="button" onclick="applyCoupon({product.get('price', 0)})" class="btn rgb-btn" style="margin-top: 8px;">Áp dụng mã</button><p id="coupon_msg" style="font-size: 13px; margin-top: 8px; text-align: center;"></p></div>
          <h3 id="final_price_display" style="margin: 15px 0; text-align: center; color: var(--success);">Tổng thanh toán: {product.get('price', 0):,}đ</h3>
          <button onclick="xeTui({product['id']})" class="btn rgb-btn" style="font-size: 16px; padding: 14px;">🔥 XÉ TÚI NGAY</button>
          <div style="text-align: center; margin-top: 15px;"><a href="/" style="color: var(--text-secondary); font-size: 13px;">← Trang chủ</a></div>
      </div>
      <script>
      let slideIndex = 0;
      function showSlide(index) {{ const track = document.getElementById("sliderTrack"); const slides = document.querySelectorAll(".slider-slide"); const dots = document.querySelectorAll(".dot"); if (slides.length === 0) return; if (index >= slides.length) slideIndex = 0; if (index < 0) slideIndex = slides.length - 1; track.style.transform = `translateX(-${slideIndex * 100}%)`; dots.forEach((dot, i) => {{ dot.classList.toggle("active", i === slideIndex); }}); }}
      function nextSlide() {{ slideIndex++; showSlide(slideIndex); }}
      function prevSlide() {{ slideIndex--; showSlide(slideIndex); }}
      function currentSlide(n) {{ slideIndex = n; showSlide(slideIndex); }}
      function applyCoupon(basePrice) {{ let code = document.getElementById("coupon_code").value; fetch("/api/check-coupon", {{method: "POST", headers: {{"Content-Type": "application/json"}}, body: JSON.stringify({{code: code}})}}).then(res => res.json()).then(data => {{ let msg = document.getElementById("coupon_msg"); if(data.success) {{ let final = Math.max(0, basePrice - data.discount); msg.style.color = "var(--success)"; msg.innerText = "Giảm " + data.discount.toLocaleString() + "đ"; document.getElementById("final_price_display").innerText = "Tổng thanh toán: " + final.toLocaleString() + "đ"; }} else {{ msg.style.color = "var(--primary)"; msg.innerText = data.message; }} }}); }}
      function xeTui(productId) {{ let code = document.getElementById("coupon_code").value; fetch("/api/buy-random/" + productId, {{method: "POST", headers: {{"Content-Type": "application/json"}}, body: JSON.stringify({{coupon_code: code}})}}).then(res => res.json()).then(data => {{ if(data.success) {{ alert("🎉 Thành công! Acc:\\n" + data.account_info); window.location.href = "/lich-su"; }} else {{ alert(data.message); }} }}); }}
      </script>
    """
    return render_template_string(BASE_HTML, content=content, users=users)
  except Exception as e:
    print(f"Lỗi tui-mu: {e}")
    flash("Đã xảy ra lỗi khi tải trang sản phẩm!")
    return redirect(url_for('index'))

@app.route('/buy/<int:product_id>')
def buy(product_id):
  if 'username' not in session:
    flash('Vui lòng đăng nhập!')
    return redirect(url_for('login'))
  
  try:
    product = next((p for p in products if p['id'] == product_id), None)
    if not product:
      flash('Không tìm thấy sản phẩm!')
      return redirect(url_for('index'))

    images = product.get('images', [])
    if not isinstance(images, list) or len(images) == 0 or not images[0]:
      images = ['https://i.ibb.co/Z1Yck7SH/7475196962448704520-avatar-png.png']

    slider_slides = ''
    slider_dots = ''
    for i, img in enumerate(images):
      slider_slides += f'<div class="slider-slide"><img src="{img}" alt="Img"></div>'
      active_cls = ' active' if i == 0 else ''
      slider_dots += f'<span class="dot{active_cls}" onclick="currentSlide({i})"></span>'

    slider_html = f'<div class="slider-container"><div class="slider-track" id="sliderTrack">{slider_slides}</div>{"<button class=\"slider-btn slider-prev\" onclick=\"prevSlide()\">❮</button><button class=\"slider-btn slider-next\" onclick=\"nextSlide()\">❯</button>" if len(images) > 1 else ""}</div>{"<div class=\"slider-dots\">" + slider_dots + "</div>" if len(images) > 1 else ""}'

    content = f"""
      <div class="card" style="max-width: 500px; margin: auto; border: 1px solid var(--primary);">
          <h2 class="rgb-text" style="text-align: center;">CHI TIẾT SẢN PHẨM</h2>
          {slider_html}
          <div class="product-title" style="font-size: 16px; margin-top: 10px;">{product.get('name', '')}</div>
          <p style="color: var(--text-secondary); font-size: 13px;">{product.get('desc', '')}</p>
          <p class="price">Giá: {product.get('price', 0):,}đ</p>
          <p style="color: var(--text-secondary); font-size: 13px;">Kho còn: <b style="color: white;">{len(product.get('game_accs', []))}</b> tài khoản</p>
          
          <div style="margin: 15px 0;">
              <label style="font-size: 13px; color: var(--text-secondary);">Mã giảm giá:</label>
              <input type="text" id="coupon_code" placeholder="Mã (nếu có)">
              <button type="button" onclick="applyCoupon({product.get('price', 0)})" class="btn rgb-btn" style="margin-top: 8px;">Áp dụng mã</button>
              <p id="coupon_msg" style="font-size: 13px; margin-top: 8px; text-align: center;"></p>
          </div>
          
          <h3 id="final_price_display" style="margin: 15px 0; text-align: center; color: var(--success);">Tổng thanh toán: {product.get('price', 0):,}đ</h3>
          
          <button onclick="confirmBuy({product['id']})" class="btn rgb-btn" style="font-size: 16px; padding: 14px;">🛒 MUA NGAY</button>
          <div style="text-align: center; margin-top: 15px;"><a href="/" style="color: var(--text-secondary); font-size: 13px;">← Trang chủ</a></div>
      </div>
      <script>
      let slideIndex = 0;
      function showSlide(index) {{ const track = document.getElementById("sliderTrack"); const slides = document.querySelectorAll(".slider-slide"); const dots = document.querySelectorAll(".dot"); if (slides.length === 0) return; if (index >= slides.length) slideIndex = 0; if (index < 0) slideIndex = slides.length - 1; track.style.transform = `translateX(-${slideIndex * 100}%)`; dots.forEach((dot, i) => {{ dot.classList.toggle("active", i === slideIndex); }}); }}
      function nextSlide() {{ slideIndex++; showSlide(slideIndex); }}
      function prevSlide() {{ slideIndex--; showSlide(slideIndex); }}
      function currentSlide(n) {{ slideIndex = n; showSlide(slideIndex); }}
      function applyCoupon(basePrice) {{ let code = document.getElementById('coupon_code').value; fetch('/api/check-coupon', {{method: 'POST', headers: {{'Content-Type': 'application/json'}}, body: JSON.stringify({{code: code}})}}).then(res => res.json()).then(data => {{ let msg = document.getElementById('coupon_msg'); if(data.success) {{ let final = Math.max(0, basePrice - data.discount); msg.style.color = 'var(--success)'; msg.innerText = "Giảm " + data.discount.toLocaleString() + "đ"; document.getElementById('final_price_display').innerText = "Tổng thanh toán: " + final.toLocaleString() + "đ"; }} else {{ msg.style.color = 'var(--primary)'; msg.innerText = data.message; }} }}); }}
      function confirmBuy(productId) {{ let code = document.getElementById('coupon_code').value; fetch('/api/buy-product/' + productId, {{method: 'POST', headers: {{'Content-Type': 'application/json'}}, body: JSON.stringify({{coupon_code: code}})}}).then(res => res.json()).then(data => {{ if(data.success) {{ alert("🎉 Mua thành công! Thông tin:\\n" + data.account_info); window.location.href = '/lich-su'; }} else {{ alert(data.message); }} }}); }}
      </script>
    """
    return render_template_string(BASE_HTML, content=content, users=users)
  except Exception as e:
    print(f"Lỗi buy: {e}")
    flash("Đã xảy ra lỗi khi tải trang mua hàng!")
    return redirect(url_for('index'))

@app.route('/api/buy-product/<int:product_id>', methods=['POST'])
def api_buy_product(product_id):
  if 'username' not in session:
    return jsonify({'success': False, 'message': 'Vui lòng đăng nhập!'})
  username = session['username']
  product = next((p for p in products if p['id'] == product_id), None)
  if not product or len(product.get('game_accs', [])) <= 0:
    return jsonify({'success': False, 'message': 'Hết hàng!'})

  data = request.json or {}
  coupon_code = data.get('coupon_code', '').strip().upper()
  final_price = product['price']
  now_ts = datetime.now().timestamp()

  if coupon_code:
    coupon = next((c for c in coupons_db if c['code'] == coupon_code), None)
    if not coupon or not coupon['is_active'] or now_ts > coupon.get('expiry_date', 0):
      return jsonify({'success': False, 'message': 'Mã giảm giá không hợp lệ!'})
    final_price = max(0, product['price'] - coupon['discount_amount'])
    coupon['used_count'] = coupon.get('used_count', 0) + 1

  if users[username]['balance'] < final_price:
    return jsonify({'success': False, 'message': 'Số dư không đủ!'})

  users[username]['balance'] -= final_price
  acc_info = product['game_accs'].pop(0)
  purchase_history.append({'user': username, 'product_name': product['name'], 'account_details': acc_info})
  send_telegram_notification(f"🛒 <b>Mua acc!</b>\nUser: {username}\nSP: {product['name']}\nAcc: {acc_info}")
  return jsonify({'success': True, 'account_info': acc_info})

@app.route('/api/check-coupon', methods=['POST'])
def check_coupon():
  data = request.json or {}
  code = data.get('code', '').strip().upper()
  coupon = next((c for c in coupons_db if c['code'] == code), None)
  if not coupon or not coupon['is_active']:
    return jsonify({'success': False, 'message': 'Mã không tồn tại!'})
  return jsonify({'success': True, 'discount': coupon['discount_amount']})

@app.route('/api/buy-random/<int:product_id>', methods=['POST'])
def api_buy_random(product_id):
  if 'username' not in session:
    return jsonify({'success': False, 'message': 'Vui lòng đăng nhập!'})
  username = session['username']
  product = next((p for p in products if p['id'] == product_id), None)
  if not product or len(product.get('game_accs', [])) <= 0:
    return jsonify({'success': False, 'message': 'Hết hàng túi mù!'})

  data = request.json or {}
  coupon_code = data.get('coupon_code', '').strip().upper()
  final_price = product['price']
  now_ts = datetime.now().timestamp()

  if coupon_code:
    coupon = next((c for c in coupons_db if c['code'] == coupon_code), None)
    if not coupon or not coupon['is_active']:
      return jsonify({'success': False, 'message': 'Mã không hợp lệ!'})
    final_price = max(0, product['price'] - coupon['discount_amount'])

  if users[username]['balance'] < final_price:
    return jsonify({'success': False, 'message': 'Số dư không đủ!'})

  users[username]['balance'] -= final_price
  acc_info = product['game_accs'].pop(0)
  purchase_history.append({'user': username, 'product_name': product['name'] + ' (Random)', 'account_details': acc_info})
  send_telegram_notification(f"🔥 <b>Mua túi mù!</b>\nUser: {username}\nSP: {product['name']}")
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
  content = '<div class="card" style="max-width: 420px; margin: auto; border: 1px solid var(--primary);"><h2 class="rgb-text" style="text-align: center;">ĐĂNG NHẬP</h2><form method="POST"><label style="font-size: 13px; color: var(--text-secondary);">Tài khoản:</label><input type="text" name="username" required><label style="font-size: 13px; color: var(--text-secondary);">Mật khẩu:</label><input type="password" name="password" required><button type="submit" class="btn rgb-btn" style="margin-top: 15px;">ĐĂNG NHẬP</button></form></div>'
  return render_template_string(BASE_HTML, content=content, users=users)

@app.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'POST':
    username = request.form['username'].strip()
    password = request.form['password'].strip()
    if not username or not password:
      flash('Nhập đủ thông tin!')
    elif username in users:
      flash('Tài khoản đã tồn tại!')
    else:
      users[username] = {'password': password, 'role': 'user', 'balance': 0, 'total_deposited': 0}
      flash('Đăng ký thành công!')
      return redirect(url_for('login'))
  content = '<div class="card" style="max-width: 420px; margin: auto;"><h2 class="rgb-text" style="text-align: center;">ĐĂNG KÝ</h2><form method="POST"><label style="font-size: 13px; color: var(--text-secondary);">Tài khoản:</label><input type="text" name="username" required><label style="font-size: 13px; color: var(--text-secondary);">Mật khẩu:</label><input type="password" name="password" required><button type="submit" class="btn rgb-btn" style="margin-top: 15px;">ĐĂNG KÝ</button></form></div>'
  return render_template_string(BASE_HTML, content=content, users=users)

@app.route('/logout')
def logout():
  session.clear()
  return redirect(url_for('index'))

@app.route('/admin/delete/<int:product_id>')
def delete_product(product_id):
  if 'username' not in session or session.get('role') != 'admin':
    return redirect(url_for('index'))
  global products
  products = [p for p in products if p['id'] != product_id]
  flash('Đã xóa sản phẩm!')
  return redirect(url_for('index'))

@app.route('/admin/delete-cay-thue/<int:ct_id>')
def delete_cay_thue(ct_id):
  if 'username' not in session or session.get('role') != 'admin':
    return redirect(url_for('index'))
  global cay_thue_services
  cay_thue_services = [s for s in cay_thue_services if s['id'] != ct_id]
  flash('Đã xóa gói cày!')
  return redirect(url_for('admin'))

@app.route('/admin/delete-private-acc/<int:acc_id>')
def delete_private_acc(acc_id):
  if 'username' not in session or session.get('role') != 'admin':
    return redirect(url_for('index'))
  global private_cai_cuoc_db
  private_cai_cuoc_db = [acc for acc in private_cai_cuoc_db if acc['id'] != acc_id]
  flash('Đã xóa ghi chú!')
  return redirect(url_for('admin'))

@app.route('/nap-the', methods=['POST'])
def nap_the():
  if 'username' not in session:
    return redirect(url_for('login'))
  cards_queue.append({'id': len(cards_queue)+1, 'user': session['username'], 'type': request.form['telco'], 'info': f"Seri: {request.form['serial']}", 'amount': int(request.form['amount']), 'status': 'Đang chờ Admin duyệt'})
  send_telegram_notification(f"💳 <b>Thẻ cào mới!</b>\nUser: {session['username']}\nTrị giá: {int(request.form['amount']):,}đ")
  flash('Đã gửi thẻ chờ duyệt!')
  return redirect(url_for('index'))

@app.route('/admin/duyet-the/<int:card_id>', methods=['POST'])
def duyet_the(card_id):
  if 'username' not in session or session.get('role') != 'admin':
    return redirect(url_for('index'))
  for c in cards_queue:
    if c['id'] == card_id and c['status'] == 'Đang chờ Admin duyệt':
      c['status'] = 'Thành công'
      users[c['user']]['balance'] += c['amount']
      users[c['user']]['total_deposited'] = users[c['user']].get('total_deposited', 0) + c['amount']
      flash('Đã duyệt thẻ!')
      break
  return redirect(url_for('admin'))

@app.route('/admin/huy-the/<int:card_id>', methods=['POST'])
def huy_the(card_id):
  if 'username' not in session or session.get('role') != 'admin':
    return redirect(url_for('index'))
  for c in cards_queue:
    if c['id'] == card_id:
      c['status'] = 'Đã hủy'
      flash('Đã hủy thẻ!')
      break
  return redirect(url_for('admin'))

@app.route('/lich-su')
def lich_su():
  if 'username' not in session:
    return redirect(url_for('login'))
  user_history = [h for h in purchase_history if h['user'] == session['username']]
  history_html = '<h2 class="rgb-text">📜 LỊCH SỬ GIAO DỊCH</h2>'
  if not user_history:
    history_html += '<div class="card" style="text-align: center; color: var(--text-secondary);"><p>Chưa có lịch sử.</p></div>'
  else:
    for h in user_history:
      history_html += f'<div class="card"><p style="margin: 0 0 5px 0; color: var(--text-secondary);"><b>Sản phẩm:</b> {h["product_name"]}</p><p style="margin: 0;"><b>Chi tiết:</b> <span style="color: var(--success); font-weight: 600;">{h["account_details"]}</span></p></div>'
  return render_template_string(BASE_HTML, content=history_html, users=users)

@app.route('/send-message', methods=['POST'])
def send_message():
  if 'username' not in session:
    return redirect(url_for('login'))
  msg = request.form['message'].strip()
  if msg:
    messages_db.append({'user': session['username'], 'sender': session['username'], 'message': msg})
    flash('Đã gửi tin nhắn!')
  return redirect(url_for('index'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
  if 'username' not in session or session.get('role') != 'admin':
    flash('Không có quyền!')
    return redirect(url_for('index'))

  if request.method == 'POST' and 'add_product' in request.form:
    name = request.form['name']
    price = int(request.form['price'])
    category = request.form['category']
    desc = request.form['desc']
    game_acc = request.form['game_acc'].strip()

    images_list = []
    uploaded_files = request.files.getlist('image_files')
    for file in uploaded_files:
      if file and file.filename:
        filename = datetime.now().strftime('%Y%m%d%H%M%S_') + ''.join(random.choices('0123456789abcdef', k=6)) + '_' + file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        images_list.append(f'/{filepath}')

    if not images_list:
      images_list = ['https://i.ibb.co/Z1Yck7SH/7475196962448704520-avatar-png.png']

    existing = next((p for p in products if p['name'] == name), None)
    if existing:
      if game_acc:
        existing['game_accs'].append(game_acc)
      flash('Đã thêm acc vào sản phẩm có sẵn!')
    else:
      new_id = products[-1]['id'] + 1 if products else 1000
      products.append({
          'id': new_id,
          'name': name,
          'category': category,
          'desc': desc,
          'price': price,
          'images': images_list,
          'game_accs': [game_acc] if game_acc else [],
      })
      flash('Đã thêm sản phẩm mới thành công!')
    return redirect(url_for('admin'))

  if request.method == 'POST' and 'add_cay_thue' in request.form:
    name = request.form['ct_name'].strip()
    price = int(request.form['ct_price'])
    desc = request.form['ct_desc'].strip()
    if name:
      new_id = cay_thue_services[-1]['id'] + 1 if cay_thue_services else 1
      cay_thue_services.append({'id': new_id, 'name': name, 'price': price, 'desc': desc})
      flash('Đã thêm gói cày thuê!')
    return redirect(url_for('admin'))

  if request.method == 'POST' and 'add_private_acc' in request.form:
    account = request.form.get('private_account', '').strip()
    note = request.form.get('private_note', '').strip()
    if account:
      new_id = private_cai_cuoc_db[-1]['id'] + 1 if private_cai_cuoc_db else 1
      private_cai_cuoc_db.append({'id': new_id, 'account': account, 'note': note})
      flash('Đã lưu sổ tay!')
    return redirect(url_for('admin'))

  if request.method == 'POST' and 'update_cay_thue_status' in request.form:
    ready_val = request.form.get('is_ready')
    cay_thue_status['is_ready'] = True if ready_val == 'on' else False
    cay_thue_status['current_task'] = request.form.get('current_task', '').strip()
    flash('Đã cập nhật trạng thái!')
    return redirect(url_for('admin'))

  if request.method == 'POST' and 'add_coupon' in request.form:
    code = request.form['coupon_code'].strip().upper()
    discount = float(request.form['discount_amount'])
    days = int(request.form.get('expires_in_days', 3))
    max_uses = int(request.form.get('max_uses', 10))
    if code:
      coupons_db.append({
          'id': len(coupons_db) + 1,
          'code': code,
          'discount_amount': discount,
          'expiry_date': datetime.now().timestamp() + (days * 86400),
          'max_uses': max_uses,
          'used_count': 0,
          'is_active': True,
      })
      flash('Đã tạo mã giảm giá!')
    return redirect(url_for('admin'))

  if request.method == 'POST' and 'bonus_user' in request.form:
    target = request.form['target_username'].strip()
    amount = int(request.form['bonus_amount'])
    if target in users:
      users[target]['balance'] += amount
      flash(f'Đã cộng {amount:,}đ cho {target}!')
    return redirect(url_for('admin'))

  if request.method == 'POST' and 'reply_msg' in request.form:
    target_user = request.form['target_user']
    reply_text = request.form['reply_text'].strip()
    if reply_text:
      messages_db.append({'user': target_user, 'sender': 'admin', 'message': reply_text})
      flash('Đã phản hồi khách!')
    return redirect(url_for('admin'))

  visitors_html = ''.join([f'<div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid var(--border-color); font-size: 13px;"><span>🌐 IP: <b style="color: #70a1ff;">{v["ip"]}</b></span><span style="color: var(--accent);">{v["time"]}</span></div>' for v in visitors_history]) if visitors_history else '<p style="color: var(--text-secondary); font-size: 13px;">Chưa có lượt truy cập.</p>'
  private_accs_html = ''.join([f'<div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); padding: 10px 0; font-size: 13px;"><div><b style="color: var(--success);">🎮 {acc["account"]}</b><br><span style="color: var(--accent);">📝 {acc["note"]}</span></div><a href="/admin/delete-private-acc/{acc["id"]}" class="btn-delete" onclick="return confirm(\'Xóa?\');">🗑️ XÓA</a></div>' for acc in private_cai_cuoc_db]) if private_cai_cuoc_db else '<p style="color: var(--text-secondary); font-size: 13px;">Sổ tay trống.</p>'
  
  coupons_html = ''
  for c in coupons_db:
    coupons_html += f'<div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); padding: 10px 0; font-size: 13px;"><span><b>{c["code"]}</b> (-{c["discount_amount"]:,.0f}đ)</span><form action="/admin/coupon/toggle/{c["id"]}" method="POST" style="margin:0;"><button type="submit" class="rgb-btn" style="padding: 4px 10px; border-radius: 4px; border:none; cursor:pointer;">{"Tắt" if c["is_active"] else "Bật"}</button></form></div>'

  chat_users = sorted(list(set([m['user'] for m in messages_db])))
  chat_admin_html = ''.join([f'<div class="card" style="background: #12131c; margin-bottom: 12px;"><p><b>Khách: <span style="color: #70a1ff;">{cu}</span></b></p><div style="background: #181a25; padding: 10px; border-radius: 8px; max-height: 100px; overflow-y: auto; font-size: 13px; margin-bottom: 10px;">' + ''.join([f"<div><b>{m['sender']}:</b> {m['message']}</div>" for m in messages_db if m['user'] == cu]) + f'</div><form method="POST"><input type="hidden" name="target_user" value="{cu}"><input type="text" name="reply_text" placeholder="Trả lời..." required style="margin: 0 0 8px 0;"><button type="submit" name="reply_msg" class="btn rgb-btn" style="padding: 6px; font-size: 12px;">GỬI</button></form></div>' for cu in chat_users])

  cards_html = ''.join([f'<div class="card"><p><b>User:</b> {c["user"]} | <b>{c["type"]}</b> | <span style="color
