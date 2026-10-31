from datetime import datetime
from flask import Flask, flash, jsonify, redirect, render_template_string, request, session, url_for
import hashlib
import json
import urllib.request
import urllib.parse
import random

app = Flask(__name__)
app.secret_key = 'ga_gaming_roblox_full_option_2026'

PARTNER_ID = '71186911886'
PARTNER_KEY = 'f7377b035f5b5d2c4a5d04e487b39aaf'

# --- CẤU HÌNH TELEGRAM BOT CHÍNH CHỦ ---
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
            'https://i.ibb.co/Z1Yck7SH/7475196962448704520-avatar-png.png',
            'https://i.ibb.co/0pvhCGz1/zlp-1792493518267.jpg'
        ],
        'game_accs': [
            'bloxfruit_1276_1@gmail.com | Pass123',
            'bloxfruit_1276_2@gmail.com | Pass456',
        ],
    },
    {
        'id': 5000,
        'name': 'TÚI MÙ BLOX FRUIT SIÊU RẺ (5K)',
        'category': 'random',
        'desc': 'Hên xui trúng acc khủng, tỷ lệ trúng tộc v4 cực cao!',
        'price': 5000,
        'images': [
            'https://i.ibb.co/Z1Yck7SH/7475196962448704520-avatar-png.png'
        ],
        'game_accs': [
            'random_acc_1@gmail.com | Pass111',
            'random_acc_2@gmail.com | Pass222',
        ],
    },
]

# --- QUẢN LÝ DỊCH VỤ CÀY THUÊ ---
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
        .success-box { background: rgba(46,213,115,0.1); border: 1px solid var(--success); padding: 20px; border-radius: 10px; margin-top: 15px; text-align: center; }
        .top-user-item { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid var(--border-color); font-size: 14px; align-items: center; }
        .chat-box { background: #12131c; border: 1px solid var(--border-color); border-radius: 10px; padding: 12px; max-height: 220px; overflow-y: auto; margin-bottom: 12px; }
        .chat-msg { margin-bottom: 10px; font-size: 13px; line-height: 1.4; }
        .chat-msg.user { color: #70a1ff; text-align: right; }
        .chat-msg.admin { color: var(--success); text-align: left; }
        
        /* CSS cho Slider Ảnh Chi Tiết Sản Phẩm */
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

    <!-- YouTube và TikTok chính chủ -->
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

  sorted_users = sorted(
      users.items(), key=lambda x: x[1].get('total_deposited', 0), reverse=True
  )
  top_html = ''
  rank = 1
  for uname, udata in sorted_users:
    if udata.get('total_deposited', 0) > 0:
      medal = (
          '🥇'
          if rank == 1
          else ('🥈' if rank == 2 else ('🥉' if rank == 3 else f'#{rank}'))
      )
      top_html += (
          '<div class="top-user-item"><span><b>'
          + medal
          + '</b> '
          + uname
          + '</span><span style="color: var(--accent); font-weight: 600;">'
          + f"{udata.get('total_deposited', 0):,}"
          + 'đ</span></div>'
      )
      rank += 1
  if not top_html:
    top_html = (
        '<p style="color: var(--text-secondary); text-align: center; font-size:'
        ' 13px;">Chưa có dữ liệu nạp tiền.</p>'
    )

  chat_html = ''
  if 'username' in session and session.get('role') != 'admin':
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
        '<div class="card" style="border: 1px solid var(--primary);"><h3'
        ' style="color: var(--primary); margin-top: 0;">💬 Hỗ Trợ Trực'
        ' Tuyến</h3><div class="chat-box">'
        + msgs_render
        + '</div><form action="/send-message" method="POST"><input type="text"'
        ' name="message" placeholder="Nhập tin nhắn cho Admin..." required'
        ' style="margin: 0 0 10px 0;"><button type="submit" class="btn rgb-btn"'
        ' style="padding: 8px; font-size: 13px;">GỬI TIN NHẮN</button></form></div>'
    )

  products_html = ''
  for p in products:
    stock_count = len(p['game_accs'])
    if p.get('category') == 'random':
      action_btn = (
          '<a href="/tui-mu/'
          + str(p['id'])
          + '" class="btn rgb-btn" style="margin-top: 15px;">⚡ XÉ TÚI NGAY</a>'
      )
    else:
      action_btn = (
          '<a href="/buy/'
          + str(p['id'])
          + '" class="btn rgb-btn" style="margin-top: 15px;">🛒 MUA NGAY</a>'
      )

    images_list = p.get('images', [])
    thumb_img = images_list[0] if (images_list and len(images_list) > 0) else ''
    img_tag = (
        '<img src="'
        + thumb_img
        + '" style="width: 100%; height: 130px; object-fit: cover;'
        ' border-radius: 10px; margin-bottom: 10px; border: 1px solid'
        ' var(--border-color);">'
        if thumb_img
        else ''
    )

    delete_btn = ''
    if session.get('role') == 'admin':
      delete_btn = f'<div style="position: absolute; top: 15px; right: 15px;"><a href="/admin/delete/{p["id"]}" class="btn-delete" onclick="return confirm(\'Bạn có chắc chắn muốn xóa sản phẩm này không?\');">🗑️ XÓA</a></div>'

    products_html += (
        '<div class="card" style="display: flex; flex-direction: column;'
        ' justify-content: space-between;">'
        + delete_btn
        + '<div>'
        + img_tag
        + '<div style="color: var(--text-secondary); font-size: 11px; font-weight:'
        ' 600;">MÃ SÓ: #'
        + str(p['id'])
        + '</div><div class="product-title">'
        + p['name']
        + '</div><p style="color: var(--text-secondary); font-size: 12px;'
        ' line-height: 1.4;">'
        + p['desc']
        + '</p></div><div><div style="display: flex; justify-content:'
        ' space-between; align-items: center; margin-top: 10px;"><span'
        ' style="font-size: 12px; color: var(--text-secondary);">Kho: <b'
        ' style="color: white;">'
        + str(stock_count)
        + '</b></span><span class="price">'
        + f"{p['price']:,}"
        + 'đ</span></div>'
        + action_btn
        + '</div></div>'
    )

  status_badge = '<span style="color: var(--success); font-weight: bold;">🟢 Đang sẵn sàng nhận đơn</span>' if cay_thue_status['is_ready'] else '<span style="color: var(--primary); font-weight: bold;">🔴 Đang bận (Vui lòng đợi)</span>'
  status_note_box = f'<div style="background: #12131c; padding: 10px; border-radius: 6px; margin-bottom: 15px; font-size: 13px; border: 1px solid var(--border-color);">Trạng thái hiện tại: {status_badge}<br><span style="color: var(--text-secondary);">Thông báo: <b>{cay_thue_status["current_task"]}</b></span></div>'

  cay_thue_html = ''
  for ct in cay_thue_services:
    if cay_thue_status['is_ready']:
      btn_cay = f'<a href="/dat-cay-thue/{ct["id"]}" class="btn rgb-btn" style="margin-top: 12px;">⚡ ĐẶT DỊCH VỤ</a>'
    else:
      btn_cay = f'<button class="btn" style="background: #475569; cursor: not-allowed; margin-top: 12px;" disabled>Đang bận cày cho khách, vui lòng đợi!</button>'

    delete_ct_btn = ''
    if session.get('role') == 'admin':
      delete_ct_btn = f'<div style="position: absolute; top: 15px; right: 15px;"><a href="/admin/delete-cay-thue/{ct["id"]}" class="btn-delete" onclick="return confirm(\'Xóa dịch vụ cày thuê này?\');">🗑️ XÓA</a></div>'

    cay_thue_html += (
        '<div class="card" style="position: relative;">'
        + delete_ct_btn
        + f'<div class="product-title">{ct["name"]}</div>'
        + f'<p style="color: var(--text-secondary); font-size: 12px;">{ct["desc"]}</p>'
        + f'<div class="price">{ct["price"]:,}đ</div>'
        + btn_cay
        + '</div>'
    )
  if not cay_thue_html:
    cay_thue_html = '<p style="color: var(--text-secondary); font-size: 13px;">Chưa có gói cày thuê nào được tạo.</p>'

  nap_html = ''
  if 'username' in session and session.get('role') != 'admin':
    curr_username = session['username']
    suggest_note = f'NAP {curr_username.upper()}'
    nap_html = (
        '<div class="card" style="border: 1px solid var(--success);"><h3'
        ' class="rgb-text" style="margin-top:0;">⚡ NẠP TIỀN</h3><div style="background: #12131c; padding: 15px; border-radius:'
        ' 10px; margin-bottom: 20px; border: 1px solid var(--border-color);"><p'
        ' style="margin: 0 0 8px 0; color: var(--accent); font-weight:'
        ' 600;">📝 1. Chuyển khoản QR siêu tốc:</p><p style="margin: 0; font-size:'
        ' 13px; color: var(--text-secondary);">Nội dung: <b'
        f' style="color: var(--success); font-size: 15px;">{suggest_note}</b>.'
        ' Tự động cộng tiền sau 3 giây!</p></div><div style="text-align:'
        ' center; margin-bottom: 15px;"><img'
        ' src="https://i.ibb.co/0pvhCGz1/zlp-1792493518267.jpg" alt="QR Code"'
        ' style="max-width: 190px; border-radius: 10px; border: 3px solid'
        ' white;"><p style="font-size: 12px; color: var(--text-secondary);'
        ' margin: 8px 0 0 0;">Chủ TK: NGUYEN VAN DUONG</p></div><form'
        ' action="/nap-the" method="POST" style="margin-top: 20px; border-top:'
        ' 1px dashed var(--border-color); padding-top: 20px;"><h4 style="color:'
        ' var(--accent); margin: 0 0 12px 0; font-size: 15px;">2. Gửi Thẻ Cào (Duyệt Tay)</h4><label style="font-size: 13px; color:'
        ' var(--text-secondary);">Nhà mạng:</label><select name="telco"><option'
        ' value="VIETTEL">Viettel</option><option'
        ' value="MOBIFONE">Mobifone</option><option'
        ' value="VINAPHONE">Vinaphone</option><option'
        ' value="VIETNAMOBILE">Vietnamobile</option></select><label'
        ' style="font-size: 13px; color: var(--text-secondary);">Mệnh'
        ' giá:</label><select name="amount"><option value="10000">10.000'
        ' đ</option><option value="20000">20.000 đ</option><option'
        ' value="50000">50.000 đ</option><option value="100000">100.000'
        ' đ</option><option value="200000">200.000 đ</option><option'
        ' value="300000">300.000 đ</option><option value="500000">500.000'
        ' đ</option><option value="1000000">1.000.000'
        ' đ</option></select><input type="text" name="code" placeholder="Mã thẻ'
        ' cào" required><input type="text" name="serial" placeholder="Số Serial"'
        ' required><button type="submit" class="btn rgb-btn" style="margin-top:'
        ' 12px;">GỬI THẺ CÀO DUYỆT</button></form></div>'
    )

  banner_html = """
        <div class="card" style="text-align: center; padding: 10px; border: 1px solid var(--primary); background: linear-gradient(180deg, rgba(255,71,87,0.05), var(--card-bg));">
            <img src="https://i.ibb.co/Z1Yck7SH/7475196962448704520-avatar-png.png" alt="Banner" style="width: 100%; max-height: 250px; object-fit: cover; border-radius: 10px;">
        </div>
        """

  content = (
      banner_html
      + nap_html
      + '<div style="display: grid; grid-template-columns: 1fr; gap: 20px;"><div><h2 class="rgb-text">🔥 DANH MỤC TÀI KHOẢN & TÚI MÙ</h2><div'
      ' style="display: grid; grid-template-columns: 1fr 1fr; gap:'
      ' 12px;">'
      + products_html
      + '</div><h2 class="rgb-text" style="margin-top: 30px;">⚔️ DỊCH VỤ CÀY THUÊ UY TÍN</h2>'
      + status_note_box
      + '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">'
      + cay_thue_html
      + '</div></div><div><div class="card" style="border: 1px solid'
      ' var(--accent); margin-bottom: 20px;"><h3 class="rgb-text" style="'
      ' text-align: center; margin-top: 0;">🏆 TOP NẠP TIỀN</h3>'
      + top_html
      + '</div>'
      + chat_html
      + '</div></div>'
  )
  return render_template_string(BASE_HTML, content=content, users=users)

@app.route('/dat-cay-thue/<int:ct_id>', methods=['GET', 'POST'])
def dat_cay_thue(ct_id):
  if 'username' not in session:
    flash('Vui lòng đăng nhập để đặt dịch vụ cày thuê!')
    return redirect(url_for('login'))
  
  if not cay_thue_status['is_ready']:
    flash('Hiện tại shop đang bận cày cho khách khác, vui lòng đợi!')
    return redirect(url_for('index'))

  service = next((s for s in cay_thue_services if s['id'] == ct_id), None)
  if not service:
    flash('Không tìm thấy gói cày thuê!')
    return redirect(url_for('index'))

  username = session['username']

  if request.method == 'POST':
    username_game = request.form.get('username_game', '').strip()
    password_game = request.form.get('password_game', '').strip()
    note_game = request.form.get('note_game', '').strip()

    if not username_game or not password_game:
      flash('Vui lòng điền đầy đủ tài khoản và mật khẩu game!')
    elif users[username]['balance'] < service['price']:
      flash('Số dư tài khoản không đủ để thanh toán gói cày này!')
    else:
      users[username]['balance'] -= service['price']
      purchase_history.append({
          'user': username,
          'product_name': f"Cày thuê: {service['name']}",
          'account_details': f"TK: {username_game} | Pass: {password_game} | Ghi chú: {note_game}"
      })
      send_telegram_notification(f"⚔️ <b>Có khách đặt cày thuê!</b>\n👤 User web: {username}\n📦 Gói: {service['name']}\n🎮 TK Game: {username_game}\n🔑 Pass: {password_game}\n📝 Ghi chú: {note_game}")
      flash('Đặt cày thuê thành công! Admin sẽ liên hệ và tiến hành cày sớm nhất.')
      return redirect(url_for('lich_su'))

  content = f"""
    <div class="card" style="max-width: 500px; margin: auto; border: 1px solid var(--accent);">
        <h2 class="rgb-text" style="text-align: center;">ĐẶT CÀY THUÊ</h2>
        <p style="color: var(--text-secondary); text-align: center;">Gói: <b>{service['name']}</b></p>
        <p class="price" style="text-align: center;">Giá: {service['price']:,}đ</p>
        <form method="POST">
            <label style="font-size: 13px; color: var(--text-secondary);">Tài khoản Roblox / Email:</label>
            <input type="text" name="username_game" placeholder="Nhập tài khoản game..." required>
            <label style="font-size: 13px; color: var(--text-secondary);">Mật khẩu game:</label>
            <input type="password" name="password_game" placeholder="Nhập mật khẩu game..." required>
            <label style="font-size: 13px; color: var(--text-secondary);">Yêu cầu / Ghi chú thêm (nếu có):</label>
            <textarea name="note_game" placeholder="VD: Nhớ giữ lại trái ác quỷ trong rương..." rows="3"></textarea>
            <button type="submit" class="btn rgb-btn" style="margin-top: 15px;">XÁC NHẬN THANH TOÁN & ĐẶT ĐƠN</button>
        </form>
        <div style="text-align: center; margin-top: 15px;">
            <a href="/" style="color: var(--text-secondary); text-decoration: none; font-size: 13px;">← Quay lại trang chủ</a>
        </div>
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
      flash('Mật khẩu cũ không chính xác!')
    elif len(new_pass) < 3:
      flash('Mật khẩu mới quá ngắn!')
    else:
      users[username]['password'] = new_pass
      flash('Đổi mật khẩu thành công!')
      send_telegram_notification(f"🔒 <b>User đổi mật khẩu!</b>\n👤 User: {username}")
      return redirect(url_for('index'))
      
  content = """
    <div class="card" style="max-width: 420px; margin: auto;">
        <h2 class="rgb-text" style="text-align: center;">ĐỔI MẬT KHẨU</h2>
        <form method="POST">
            <label style="font-size: 13px; color: var(--text-secondary);">Mật khẩu cũ:</label>
            <input type="password" name="old_password" placeholder="Nhập mật khẩu hiện tại..." required>
            <label style="font-size: 13px; color: var(--text-secondary);">Mật khẩu mới:</label>
            <input type="password" name="new_password" placeholder="Nhập mật khẩu mới..." required>
            <button type="submit" class="btn rgb-btn" style="margin-top: 15px;">XÁC NHẬN ĐỔI</button>
        </form>
        <div style="text-align: center; margin-top: 15px;">
            <a href="/" style="color: var(--text-secondary); text-decoration: none; font-size: 13px;">← Quay lại trang chủ</a>
        </div>
    </div>
    """
  return render_template_string(BASE_HTML, content=content, users=users)

@app.route('/tui-mu/<int:product_id>')
def tui_mu(product_id):
  if 'username' not in session:
    flash('Vui lòng đăng nhập để mở túi mù!')
    return redirect(url_for('login'))
  product = next((p for p in products if p['id'] == product_id), None)
  if not product:
    flash('Không tìm thấy sản phẩm!')
    return redirect(url_for('index'))

  images = product.get('images', [])
  if not images:
    images = ['https://i.ibb.co/Z1Yck7SH/7475196962448704520-avatar-png.png']

  slider_slides = ''
  slider_dots = ''
  for i, img in enumerate(images):
    slider_slides += f'<div class="slider-slide"><img src="{img}" alt="Product Image"></div>'
    active_cls = ' active' if i == 0 else ''
    slider_dots += f'<span class="dot{active_cls}" onclick="currentSlide({i})"></span>'

  slider_html = f"""
    <div class="slider-container">
        <div class="slider-track" id="sliderTrack">
            {slider_slides}
        </div>
        {'<button class="slider-btn slider-prev" onclick="prevSlide()">❮</button><button class="slider-btn slider-next" onclick="nextSlide()">❯</button>' if len(images) > 1 else ''}
    </div>
    {'<div class="slider-dots">' + slider_dots + '</div>' if len(images) > 1 else ''}
  """

  content = (
      '<div class="card" style="max-width: 500px; margin: auto; border: 1px solid var(--accent);">'
      + '<h2 class="rgb-text" style="text-align: center;">⚡ MỞ TÚI MÙ: ' + product['name'] + '</h2>'
      + slider_html
      + '<p style="color: var(--text-secondary); text-align: center; margin-top: 10px;">' + product['desc'] + '</p>'
      + '<p class="price" style="text-align: center;">Giá túi: ' + f"{product['price']:,}" + 'đ</p>'
      + '<p style="color: var(--text-secondary); text-align: center;">Kho còn: <b style="color: white;">' + str(len(product['game_accs'])) + '</b> tài khoản</p>'
      + '<div style="margin: 20px 0;"><label style="font-size: 13px; color: var(--text-secondary);">Nhập mã giảm giá:</label><input type="text" id="coupon_code" placeholder="Nhập mã (VD: GIAM5K)"><button type="button" onclick="applyCoupon(' + str(product['price']) + ')" class="btn rgb-btn" style="margin-top: 8px;">Áp dụng mã</button><p id="coupon_msg" style="font-size: 13px; margin-top: 8px; text-align: center;"></p></div>'
      + '<h3 id="final_price_display" style="margin: 15px 0; text-align: center; color: var(--success);">Tổng thanh toán: ' + f"{product['price']:,}" + 'đ</h3>'
      + '<button onclick="xeTui(' + str(product['id']) + ')" class="btn rgb-btn" style="font-size: 16px; padding: 14px;">🔥 XÉ TÚI NGAY</button>'
      + '<div style="text-align: center; margin-top: 15px;"><a href="/" style="color: var(--text-secondary); text-decoration: none; font-size: 13px;">← Quay về trang chủ</a></div>'
      + '</div>'
      + '<script>'
      + 'let slideIndex = 0;'
      + 'function showSlide(index) {'
      + '  const track = document.getElementById("sliderTrack");'
      + '  const slides = document.querySelectorAll(".slider-slide");'
      + '  const dots = document.querySelectorAll(".dot");'
      + '  if (slides.length === 0) return;'
      + '  if (index >= slides.length) slideIndex = 0;'
      + '  if (index < 0) slideIndex = slides.length - 1;'
      + '  track.style.transform = `translateX(-${slideIndex * 100}%)`;'
      + '  dots.forEach((dot, i) => {'
      + '    dot.classList.toggle("active", i === slideIndex);'
      + '  });'
      + '}'
      + 'function nextSlide() { slideIndex++; showSlide(slideIndex); }'
      + 'function prevSlide() { slideIndex--; showSlide(slideIndex); }'
      + 'function currentSlide(n) { slideIndex = n; showSlide(slideIndex); }'
      + 'let currentDiscount = 0;'
      + 'function applyCoupon(basePrice) {'
      + '  let code = document.getElementById("coupon_code").value;'
      + '  fetch("/api/check-coupon", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({code: code})})'
      + '  .then(res => res.json()).then(data => {'
      + '    let msg = document.getElementById("coupon_msg");'
      + '    if(data.success) {'
      + '      currentDiscount = data.discount;'
      + '      let final = Math.max(0, basePrice - currentDiscount);'
      + '      msg.style.color = "var(--success)";'
      + '      msg.innerText = "Áp mã thành công! Giảm " + data.discount.toLocaleString() + "đ";'
      + '      document.getElementById("final_price_display").innerText = "Tổng thanh toán: " + final.toLocaleString() + "đ";'
      + '    } else {'
      + '      currentDiscount = 0;'
      + '      msg.style.color = "var(--primary)";'
      + '      msg.innerText = data.message;'
      + '      document.getElementById("final_price_display").innerText = "Tổng thanh toán: " + basePrice.toLocaleString() + "đ";'
      + '    }'
      + '  });'
      + '}'
      + 'function xeTui(productId) {'
      + '  let code = document.getElementById("coupon_code").value;'
      + '  fetch("/api/buy-random/" + productId, {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({coupon_code: code})})'
      + '  .then(res => res.json()).then(data => {'
      + '    if(data.success) {'
      + '      alert("🎉 Xé túi thành công! Tài khoản của bạn:\\n" + data.account_info);'
      + '      window.location.href = "/lich-su";'
      + '    } else {'
      + '      alert(data.message);'
      + '    }'
      + '  });'
      + '}'
      + '</script>'
  )
  return render_template_string(BASE_HTML, content=content, users=users)

@app.route('/buy/<int:product_id>')
def buy(product_id):
  if 'username' not in session:
    flash('Vui lòng đăng nhập để mua tài khoản!')
    return redirect(url_for('login'))
  username = session['username']
  product = next((p for p in products if p['id'] == product_id), None)
  if not product:
    flash('Không tìm thấy sản phẩm!')
    return redirect(url_for('index'))

  images = product.get('images', [])
  if not images:
    images = ['https://i.ibb.co/Z1Yck7SH/7475196962448704520-avatar-png.png']

  slider_slides = ''
  slider_dots = ''
  for i, img in enumerate(images):
    slider_slides += f'<div class="slider-slide"><img src="{img}" alt="Product Image"></div>'
    active_cls = ' active' if i == 0 else ''
    slider_dots += f'<span class="dot{active_cls}" onclick="currentSlide({i})"></span>'

  slider_html = f"""
    <div class="slider-container">
        <div class="slider-track" id="sliderTrack">
            {slider_slides}
        </div>
        {'<button class="slider-btn slider-prev" onclick="prevSlide()">❮</button><button class="slider-btn slider-next" onclick="nextSlide()">❯</button>' if len(images) > 1 else ''}
    </div>
    {'<div class="slider-dots">' + slider_dots + '</div>' if len(images) > 1 else ''}
  """

  content = f"""
    <div class="card" style="max-width: 500px; margin: auto; border: 1px solid var(--primary);">
        <h2 class="rgb-text" style="text-align: center;">CHI TIẾT SẢN PHẨM</h2>
        {slider_html}
        <div class="product-title" style="font-size: 16px; margin-top: 10px;">{product['name']}</div>
        <p style="color: var(--text-secondary); font-size: 13px;">{product['desc']}</p>
        <p class="price">Giá bán: {product['price']:,}đ</p>
        <p style="color: var(--text-secondary); font-size: 13px;">Kho còn: <b style="color: white;">{len(product['game_accs'])}</b> tài khoản</p>
        
        <div style="margin: 15px 0;">
            <label style="font-size: 13px; color: var(--text-secondary);">Nhập mã giảm giá:</label>
            <input type="text" id="coupon_code" placeholder="Nhập mã (VD: GIAM5K)">
            <button type="button" onclick="applyCoupon({product['price']})" class="btn rgb-btn" style="margin-top: 8px;">Áp dụng mã</button>
            <p id="coupon_msg" style="font-size: 13px; margin-top: 8px; text-align: center;"></p>
        </div>
        
        <h3 id="final_price_display" style="margin: 15px 0; text-align: center; color: var(--success);">Tổng thanh toán: {product['price']:,}đ</h3>
        
        <button onclick="confirmBuy({product['id']})" class="btn rgb-btn" style="font-size: 16px; padding: 14px;">🛒 XÁC NHẬN MUA NGAY</button>
        <div style="text-align: center; margin-top: 15px;">
            <a href="/" style="color: var(--text-secondary); text-decoration: none; font-size: 13px;">← Quay lại trang chủ</a>
        </div>
    </div>
    <script>
    let slideIndex = 0;
    function showSlide(index) {{
      const track = document.getElementById("sliderTrack");
      const slides = document.querySelectorAll(".slider-slide");
      const dots = document.querySelectorAll(".dot");
      if (slides.length === 0) return;
      if (index >= slides.length) slideIndex = 0;
      if (index < 0) slideIndex = slides.length - 1;
      track.style.transform = `translateX(-${slideIndex * 100}%)`;
      dots.forEach((dot, i) => {{
        dot.classList.toggle("active", i === slideIndex);
      }});
    }}
    function nextSlide() {{ slideIndex++; showSlide(slideIndex); }}
    function prevSlide() {{ slideIndex--; showSlide(slideIndex); }}
    function currentSlide(n) {{ slideIndex = n; showSlide(slideIndex); }}

    let currentDiscount = 0;
    function applyCoupon(basePrice) {{
      let code = document.getElementById('coupon_code').value;
      fetch('/api/check-coupon', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({code: code})})
      .then(res => res.json()).then(data => {{
        let msg = document.getElementById('coupon_msg');
        if(data.success) {{
          currentDiscount = data.discount;
          let final = Math.max(0, basePrice - currentDiscount);
          msg.style.color = 'var(--success)';
          msg.innerText = "Áp mã thành công! Giảm " + data.discount.toLocaleString() + "đ";
          document.getElementById('final_price_display').innerText = "Tổng thanh toán: " + final.toLocaleString() + "đ";
        }} else {{
          currentDiscount = 0;
          msg.style.color = 'var(--primary)';
          msg.innerText = data.message;
          document.getElementById('final_price_display').innerText = "Tổng thanh toán: " + basePrice.toLocaleString() + "đ";
        }}
      }});
    }}
    function confirmBuy(productId) {{
      let code = document.getElementById('coupon_code').value;
      fetch('/api/buy-product/' + productId, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({coupon_code: code})})
      .then(res => res.json()).then(data => {{
        if(data.success) {{
          alert("🎉 Mua tài khoản thành công! Thông tin tài khoản:\\n" + data.account_info);
          window.location.href = '/lich-su';
        }} else {{
          alert(data.message);
        }}
      }});
    }}
    </script>
    """
  return render_template_string(BASE_HTML, content=content, users=users)

@app.route('/api/buy-product/<int:product_id>', methods=['POST'])
def api_buy_product(product_id):
  if 'username' not in session:
    return jsonify({'success': False, 'message': 'Vui lòng đăng nhập!'})
  username = session['username']
  product = next((p for p in products if p['id'] == product_id), None)

  if not product or len(product['game_accs']) <= 0:
    return jsonify({'success': False, 'message': 'Sản phẩm đã hết hàng trong kho!'})

  data = request.json or {}
  coupon_code = data.get('coupon_code', '').strip().upper()
  final_price = product['price']
  now_ts = datetime.now().timestamp()

  if coupon_code:
    coupon = next((c for c in coupons_db if c['code'] == coupon_code), None)
    if not coupon or not coupon['is_active'] or now_ts > coupon.get('expiry_date', 0) or (coupon.get('max_uses', 0) > 0 and coupon.get('used_count', 0) >= coupon.get('max_uses', 0)):
      return jsonify({'success': False, 'message': 'Mã giảm giá không hợp lệ, đã hết hạn hoặc hết lượt!'})
    
    final_price = max(0, product['price'] - coupon['discount_amount'])
    coupon['used_count'] = coupon.get('used_count', 0) + 1

  if users[username]['balance'] < final_price:
    return jsonify({'success': False, 'message': 'Số dư tài khoản không đủ!'})

  users[username]['balance'] -= final_price
  acc_info = product['game_accs'].pop(0)

  purchase_history.append({
      'user': username,
      'product_name': product['name'],
      'account_details': acc_info,
  })

  send_telegram_notification(f"🛒 <b>Có khách mua tài khoản!</b>\n👤 User: {username}\n📦 Sản phẩm: {product['name']}\n💰 Giá: {final_price:,}đ\n🔑 Acc: {acc_info}")

  return jsonify({'success': True, 'account_info': acc_info})

@app.route('/api/check-coupon', methods=['POST'])
def check_coupon():
  data = request.json or {}
  code = data.get('code', '').strip().upper()
  now_ts = datetime.now().timestamp()
  
  coupon = next((c for c in coupons_db if c['code'] == code), None)
  
  if not coupon or not coupon['is_active']:
    return jsonify({'success': False, 'message': 'Mã giảm giá không tồn tại hoặc đã bị khóa!'})
    
  if now_ts > coupon.get('expiry_date', 0):
    return jsonify({'success': False, 'message': 'Mã giảm giá đã hết hạn sử dụng!'})
    
  if coupon.get('max_uses', 0) > 0 and coupon.get('used_count', 0) >= coupon.get('max_uses', 0):
    return jsonify({'success': False, 'message': 'Mã giảm giá đã hết lượt sử dụng!'})
    
  return jsonify({'success': True, 'discount': coupon['discount_amount']})

@app.route('/api/buy-random/<int:product_id>', methods=['POST'])
def api_buy_random(product_id):
  if 'username' not in session:
    return jsonify({'success': False, 'message': 'Vui lòng đăng nhập!'})
  username = session['username']
  product = next((p for p in products if p['id'] == product_id), None)

  if not product or len(product['game_accs']) <= 0:
    return jsonify({
        'success': False,
        'message': 'Kho túi mù đã hết tài khoản. Vui lòng liên hệ admin.',
    })

  data = request.json or {}
  coupon_code = data.get('coupon_code', '').strip().upper()
  final_price = product['price']
  now_ts = datetime.now().timestamp()

  if coupon_code:
    coupon = next((c for c in coupons_db if c['code'] == coupon_code), None)
    if not coupon or not coupon['is_active'] or now_ts > coupon.get('expiry_date', 0) or (coupon.get('max_uses', 0) > 0 and coupon.get('used_count', 0) >= coupon.get('max_uses', 0)):
      return jsonify({'success': False, 'message': 'Mã giảm giá không hợp lệ, đã hết hạn hoặc hết lượt!'})
    
    final_price = max(0, product['price'] - coupon['discount_amount'])
    coupon['used_count'] = coupon.get('used_count', 0) + 1

  if users[username]['balance'] < final_price:
    return jsonify({'success': False, 'message': 'Số dư tài khoản không đủ!'})

  users[username]['balance'] -= final_price
  acc_info = product['game_accs'].pop(0)

  purchase_history.append({
      'user': username,
      'product_name': product['name'] + ' (Random)',
      'account_details': acc_info,
  })

  send_telegram_notification(f"🔥 <b>Có khách mua túi mù!</b>\n👤 User: {username}\n📦 Sản phẩm: {product['name']}\n💰 Giá: {final_price:,}đ")

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
    <div class="card" style="max-width: 420px; margin: auto; border: 1px solid var(--primary);">
        <h2 class="rgb-text" style="text-align: center;">ĐĂNG NHẬP</h2>
        <form method="POST">
            <label style="font-size: 13px; color: var(--text-secondary);">Tài khoản:</label>
            <input type="text" name="username" placeholder="Nhập tài khoản..." required>
            <label style="font-size: 13px; color: var(--text-secondary);">Mật khẩu:</label>
            <input type="password" name="password" placeholder="Nhập mật khẩu..." required>
            <button type="submit" class="btn rgb-btn" style="margin-top: 15px;">ĐĂNG NHẬP NGAY</button>
        </form>
    </div>
    """
  return render_template_string(BASE_HTML, content=content, users=users)

@app.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'POST':
    username = request.form['username'].strip()
    password = request.form['password'].strip()
    if not username or not password:
      flash('Vui lòng điền đầy đủ thông tin!')
    elif username in users:
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
    <div class="card" style="max-width: 420px; margin: auto; border: 1px solid #3742fa;">
        <h2 class="rgb-text" style="text-align: center;">ĐĂNG KÝ TÀI KHOẢN</h2>
        <form method="POST">
            <label style="font-size: 13px; color: var(--text-secondary);">Tài khoản mới:</label>
            <input type="text" name="username" placeholder="Tên tài khoản..." required>
            <label style="font-size: 13px; color: var(--text-secondary);">Mật khẩu:</label>
            <input type="password" name="password" placeholder="Mật khẩu bảo mật..." required>
            <button type="submit" class="btn rgb-btn" style="margin-top: 15px;">ĐĂNG KÝ NGAY</button>
        </form>
    </div>
    """
  return render_template_string(BASE_HTML, content=content, users=users)

@app.route('/logout')
def logout():
  session.clear()
  return redirect(url_for('index'))

@app.route('/admin/delete/<int:product_id>')
def delete_product(product_id):
  if 'username' not in session or session.get('role') != 'admin':
    flash('Bạn không có quyền thực hiện hành động này!')
    return redirect(url_for('index'))
  
  global products
  products = [p for p in products if p['id'] != product_id]
  flash('Đã xóa sản phẩm thành công!')
  return redirect(url_for('index'))

@app.route('/admin/delete-cay-thue/<int:ct_id>')
def delete_cay_thue(ct_id):
  if 'username' not in session or session.get('role') != 'admin':
    flash('Bạn không có quyền thực hiện hành động này!')
    return redirect(url_for('index'))
  
  global cay_thue_services
  cay_thue_services = [s for s in cay_thue_services if s['id'] != ct_id]
  flash('Đã xóa dịch vụ cày thuê thành công!')
  return redirect(url_for('admin'))

@app.route('/admin/delete-private-acc/<int:acc_id>')
def delete_private_acc(acc_id):
  if 'username' not in session or session.get('role') != 'admin':
    flash('Bạn không có quyền thực hiện hành động này!')
    return redirect(url_for('index'))
  
  global private_cai_cuoc_db
  private_cai_cuoc_db = [acc for acc in private_cai_cuoc_db if acc['id'] != acc_id]
  flash('Đã xóa ghi chú trong sổ tay thành công!')
  return redirect(url_for('admin'))

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
        send_telegram_notification(f"💵 <b>Nạp tiền QR thành công!</b>\n👤 User: {uname}\n💰 Số tiền: {amount:,}đ")
        return jsonify({'success': True, 'message': f'Đã cộng {amount} cho {uname}'})

  return jsonify({'success': False, 'message': 'Không khớp tài khoản'})

@app.route('/nap-the', methods=['POST'])
def nap_the():
  if 'username' not in session:
    return redirect(url_for('login'))

  telco = request.form['telco']
  code = request.form['code'].strip()
  serial = request.form['serial'].strip()
  amount = int(request.form['amount'])

  cards_queue.append({
      'id': len(cards_queue) + 1,
      'user': session['username'],
      'type': f'Thẻ {telco}',
      'info': f'Seri: {serial} - Mã: {code}',
      'amount': amount,
      'status': 'Đang chờ Admin duyệt',
  })
  
  send_telegram_notification(f"💳 <b>Có thẻ cào mới chờ duyệt!</b>\n👤 User: {session['username']}\n📌 Nhà mạng: {telco} | Trị giá: {amount:,}đ\n🔢 Seri: {serial}\n🔑 Mã: {code}")
  flash('Đã gửi thẻ cào thành công! Vui lòng đợi Admin kiểm tra và duyệt.')

  return redirect(url_for('index'))

@app.route('/admin/duyet-the/<int:card_id>', methods=['POST'])
def duyet_the(card_id):
  if 'username' not in session or session.get('role') != 'admin':
    return redirect(url_for('index'))
  
  for c in cards_queue:
    if c['id'] == card_id and c['status'] == 'Đang chờ Admin duyệt':
      c['status'] = 'Thành công'
      uname = c['user']
      amount = c['amount']
      if uname in users:
        users[uname]['balance'] += amount
        users[uname]['total_deposited'] = users[uname].get('total_deposited', 0) + amount
        send_telegram_notification(f"✅ <b>Admin đã duyệt thẻ thành công!</b>\n👤 User: {uname}\n💰 Số tiền cộng: {amount:,}đ")
        flash(f'Đã duyệt thẻ và cộng {amount:,}đ cho user {uname}!')
      break
  return redirect(url_for('admin'))

@app.route('/admin/huy-the/<int:card_id>', methods=['POST'])
def huy_the(card_id):
  if 'username' not in session or session.get('role') != 'admin':
    return redirect(url_for('index'))
  
  for c in cards_queue:
    if c['id'] == card_id and c['status'] == 'Đang chờ Admin duyệt':
      c['status'] = 'Đã hủy / Thẻ lỗi'
      flash('Đã từ chối thẻ cào này!')
      break
  return redirect(url_for('admin'))

@app.route('/lich-su')
def lich_su():
  if 'username' not in session:
    return redirect(url_for('login'))
  user_history = [
      h for h in purchase_history if h['user'] == session['username']
  ]
  history_html = '<h2 class="rgb-text">📜 LỊCH SỬ GIAO DỊCH & CÀY THUÊ</h2>'
  if not user_history:
    history_html += (
        '<div class="card" style="text-align: center; color:'
        ' var(--text-secondary);"><p>Bạn chưa có lịch sử giao dịch nào.</p></div>'
    )
  else:
    for h in user_history:
      history_html += (
          '<div class="card"><p style="margin: 0 0 5px 0; color:'
          ' var(--text-secondary);"><b>Gói / Sản phẩm:</b> <span style="color:'
          ' white;">'
          + h['product_name']
          + '</span></p><p style="margin: 0;"><b>Chi tiết / Thông tin:</b> <span'
          ' style="color: var(--success); font-weight: 600;">'
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
    send_telegram_notification(f"💬 <b>Có tin nhắn hỗ trợ mới!</b>\n👤 Từ user: {session['username']}\n📝 Nội dung: {msg}")
  return redirect(url_for('index'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
  if 'username' not in session or session.get('role') != 'admin':
    flash('Bạn không có quyền truy cập trang quản trị!')
    return redirect(url_for('index'))

  if request.method == 'POST' and 'add_product' in request.form:
    name = request.form['name']
    price = int(request.form['price'])
    category = request.form['category']
    desc = request.form['desc']
    
    # Xử lý an toàn link ảnh: tách bằng khoảng trắng, dấu phẩy hoặc xuống dòng
    raw_images = request.form.get('images', '').strip()
    if raw_images:
      # Thay thế dấu phẩy và xuống dòng thành dấu cách rồi tách chuỗi an toàn
      cleaned_str = raw_images.replace(',', ' ').replace('\n', ' ')
      images_list = [img.strip() for img in cleaned_str.split(' ') if img.strip()]
    else:
      images_list = ['https://i.ibb.co/Z1Yck7SH/7475196962448704520-avatar-png.png']

    game_acc = request.form['game_acc'].strip()

    existing_product = next((p for p in products if p['name'] == name), None)
    if existing_product:
      if game_acc:
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
          'images': images_list,
          'game_accs': [game_acc] if game_acc else [],
      })
      flash('Đã tạo danh mục sản phẩm mới thành công với nhiều ảnh!')
    return redirect(url_for('admin'))

  if request.method == 'POST' and 'add_cay_thue' in request.form:
    name = request.form['ct_name'].strip()
    price = int(request.form['ct_price'])
    desc = request.form['ct_desc'].strip()
    if name:
      new_id = cay_thue_services[-1]['id'] + 1 if cay_thue_services else 1
      cay_thue_services.append({
          'id': new_id,
          'name': name,
          'price': price,
          'desc': desc
      })
      flash(f'Đã thêm gói cày thuê "{name}" thành công!')
    return redirect(url_for('admin'))

  if request.method == 'POST' and 'add_private_acc' in request.form:
    account = request.form.get('private_account', '').strip()
    note = request.form.get('private_note', '').strip()
    if account:
      new_id = private_cai_cuoc_db[-1]['id'] + 1 if private_cai_cuoc_db else 1
      private_cai_cuoc_db.append({
          'id': new_id,
          'account': account,
          'note': note
      })
      flash('Đã lưu thông tin vào sổ tay cày cuốc thành công!')
    return redirect(url_for('admin'))

  if request.method == 'POST' and 'update_cay_thue_status' in request.form:
    ready_val = request.form.get('is_ready')
    cay_thue_status['is_ready'] = True if ready_val == 'on' else False
    cay_thue_status['current_task'] = request.form.get('current_task', '').strip()
    flash('Đã cập nhật trạng thái cày thuê thành công!')
    return redirect(url_for('admin'))

  if request.method == 'POST' and 'add_coupon' in request.form:
    code = request.form['coupon_code'].strip().upper()
    discount = float(request.form['discount_amount'])
    days = int(request.form.get('expires_in_days', 3))
    max_uses = int(request.form.get('max_uses', 10))
    
    expiry_date = datetime.now().timestamp() + (days * 86400)
    
    if code:
      new_id = coupons_db[-1]['id'] + 1 if coupons_db else 1
      coupons_db.append({
          'id': new_id,
          'code': code,
          'discount_amount': discount,
          'expiry_date': expiry_date,
          'max_uses': max_uses,
          'used_count': 0,
          'is_active': True,
      })
      flash(f'Đã thêm mã "{code}" thành công!')
    return redirect(url_for('admin'))

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

  if request.method == 'POST' and 'reply_msg' in request.form:
    target_user = request.form['target_user']
    reply_text = request.form['reply_text'].strip()
    if reply_text:
      messages_db.append(
          {'user': target_user, 'sender': 'admin', 'message': reply_text}
      )
      flash(f'Đã gửi phản hồi đến "{target_user}"!')
    return redirect(url_for('admin'))

  visitors_html = ''
  if not visitors_history:
    visitors_html = '<p style="color: var(--text-secondary); font-size: 13px;">Chưa có lượt truy cập nào.</p>'
  else:
    for v in visitors_history:
      visitors_html += f'<div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid var(--border-color); font-size: 13px;"><span>🌐 IP: <b style="color: #70a1ff;">{v["ip"]}</b></span><span style="color: var(--accent);">{v["time"]}</span></div>'

  private_accs_html = ''
  if not private_cai_cuoc_db:
    private_accs_html = '<p style="color: var(--text-secondary); font-size: 13px;">Sổ tay trống, chưa có ghi chú nào.</p>'
  else:
    for acc in private_cai_cuoc_db:
      private_accs_html += f'<div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); padding: 10px 0; font-size: 13px;"><div><b style="color: var(--success);">🎮 {acc["account"]}</b><br><span style="color: var(--accent);">📝 Ghi chú: {acc["note"]}</span></div><a href="/admin/delete-private-acc/{acc["id"]}" class="btn-delete" onclick="return confirm(\'Xóa ghi chú này?\');">🗑️ XÓA</a></div>'

  coupons_html = ''
  now_ts = datetime.now().timestamp()
  for c in coupons_db:
    remaining_days = max(0, int((c.get('expiry_date', 0) - now_ts) / 86400))
    used_info = f"Đã dùng: {c.get('used_count', 0)}/{c.get('max_uses', 10)}"
    is_expired = now_ts > c.get('expiry_date', 0)
    status_text = '<span style="color: var(--success);">Đang hoạt động</span>' if (c['is_active'] and not is_expired) else '<span style="color: var(--primary);">Hết hạn / Đã tắt</span>'
    btn_text = 'Tắt' if c['is_active'] else 'Bật lại'
    
    coupons_html += (
        '<div style="display: flex; justify-content: space-between;'
        ' align-items: center; border-bottom: 1px solid var(--border-color);'
        ' padding: 10px 0; font-size: 13px;"><span><b>'
        + c['code']
        + '</b> (-'
        + f"{c['discount_amount']:,.0f}"
        + f'đ)<br><small style="color: var(--text-secondary);">Hạn còn: {remaining_days} ngày | {used_info}</small><br>'
        + status_text
        + '</span><form action="/admin/coupon/toggle/'
        + str(c['id'])
        + '" method="POST" style="margin: 0;"><button type="submit"'
        ' class="rgb-btn" style="border: none; padding: 6px 14px; border-radius:'
        ' 6px; cursor: pointer; font-weight: 600;">'
        + btn_text
        + '</button></form></div>'
    )

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
        '<div class="card" style="background: #12131c; margin-bottom:'
        ' 12px;"><p style="margin: 0 0 8px 0;"><b>Khách hàng: <span'
        ' style="color: #70a1ff;">'
        + cu
        + '</span></b></p><div style="background: #181a25; padding: 10px;'
        ' border-radius: 8px; max-height: 120px; overflow-y: auto; font-size:'
        ' 13px; margin-bottom: 10px; border: 1px solid'
        ' var(--border-color);">'
        + history_render
        + '</div><form method="POST"><input type="hidden" name="target_user"'
        ' value="'
        + cu
        + '"><input type="text" name="reply_text"'
        ' placeholder="Nhập nội dung trả lời..." required style="margin:'
        ' 0 0 8px 0;"><button type="submit" name="reply_msg" class="btn rgb-btn"'
        ' style="padding: 6px; font-size: 12px;">GỬI PHẢN HỒI</button></form></div>'
    )

  cards_html = ''
  if not cards_queue:
    cards_html = '<p style="color: var(--text-secondary); font-size: 13px;">Không có lịch sử nạp tiền nào.</p>'
  else:
    for c in cards_queue:
      action_buttons = ''
      if c['status'] == 'Đang chờ Admin duyệt':
        action_buttons = f"""
          <div style="display: flex; gap: 8px; margin-top: 8px;">
            <form action="/admin/duyet-the/{c['id']}" method="POST" style="margin:0;"><button type="submit" class="btn rgb-btn" style="padding: 6px 12px; font-size: 12px; background: #2ed573;">✔️ DUYỆT</button></form>
            <form action="/admin/huy-the/{c['id']}" method="POST" style="margin:0;"><button type="submit" class="btn rgb-btn" style="padding: 6px 12px; font-size: 12px; background: #ff4757;">❌ HỦY</button></form>
          </div>
        """
      cards_html += (
          '<div class="card" style="margin-bottom: 10px;"><p'
          ' style="margin: 0 0 5px 0;"><b>User:</b> '
          + c['user']
          + ' | <b>Loại:</b> '
          + c['type']
          + ' | <b>Số tiền:</b> <span style="color: var(--accent);">'
          + f"{c['amount']:,}"
          + 'đ</span></p><p style="margin: 0 0 5px 0;"><b>Thông tin:</b> '
          + c['info']
          + '</p><p style="margin: 0 0 5px 0;"><b>Trạng thái:</b> <span'
          ' style="color: var(--success);">'
          + c['status']
          + '</span></p>'
          + action_buttons
          + '</div>'
      )

  checked_attr = 'checked' if cay_thue_status['is_ready'] else ''

  admin_content = (
      '<h2 class="rgb-text">⚙️ TRANG QUẢN TRỊ ADMIN</h2>'
      
      '<div class="card" style="border: 1px solid var(--accent); background: linear-gradient(135deg, rgba(255,165,2,0.05), var(--card-bg));">'
      '<h3 class="rgb-text" style="margin-top: 0;">🤖 Trợ Lý AI Hỗ Trợ Quản Trị Shop</h3>'
      '<p style="font-size: 13px; color: var(--text-secondary);">Nhập yêu cầu của ông (Ví dụ: <i>"Cách tạo thêm mã giảm giá"</i>, <i>"Hướng dẫn duyệt thẻ"</i>, hoặc <i>"Gợi ý tối ưu shop"</i>):</p>'
      '<input type="text" id="ai_prompt" placeholder="Nhập câu hỏi hoặc yêu cầu cho AI...">'
      '<button type="button" onclick="askAdminAI()" class="btn rgb-btn" style="margin-top: 8px;">GỬI YÊU CẦU CHO TRỢ LÝ AI</button>'
      '<div id="ai_response_box" style="display: none; background: #12131c; padding: 12px; border-radius: 8px; margin-top: 12px; border: 1px solid var(--border-color); font-size: 13px; color: var(--success);"></div>'
      '</div>'

      '<script>'
      'function askAdminAI() {'
      '  let prompt = document.getElementById("ai_prompt").value.trim();'
      '  let box = document.getElementById("ai_response_box");'
      '  if(!prompt) { alert("Vui lòng nhập nội dung cần hỏi!"); return; }'
      '  box.style.display = "block";'
      '  box.innerHTML = "⏳ Trợ lý AI đang xử lý yêu cầu của ông...";'
      '  fetch("/api/admin-ai", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({prompt: prompt})})'
      '  .then(res => res.json()).then(data => {'
      '    box.innerHTML = "🤖 <b>Phản hồi từ Trợ lý AI:</b><br>" + data.reply;'
      '  }).catch(err => {'
      '    box.innerHTML = "❌ Lỗi kết nối trợ lý AI, vui lòng thử lại!";'
      '  });'
      '}'
      '</script>'

      '<div class="card" style="border: 1px solid var(--accent);">'
      '<h3 class="rgb-text" style="margin-top: 0;">📒 Sổ Tay Ghi Chú Cày Cuốc Nick (Riêng tư)</h3>'
      '<form method="POST">'
      '<label style="font-size: 13px; color: var(--text-secondary);">Tài khoản game / Mật khẩu:</label>'
      '<input type="text" name="private_account" placeholder="username | password" required>'
      '<label style="font-size: 13px; color: var(--text-secondary);">Ghi chú tiến độ:</label>'
      '<textarea name="private_note" placeholder="Nhập ghi chú chi tiết..." rows="2" style="width: 100%; padding: 12px 15px; margin: 10px 0; background: #12131c; border: 1px solid var(--border-color); color: white; border-radius: 8px; box-sizing: border-box; font-family: \'Poppins\', sans-serif; font-size: 14px;" required></textarea>'
      '<button type="submit" name="add_private_acc" class="btn rgb-btn" style="margin-top: 10px;">LƯU VÀO SỔ TAY</button>'
      '</form>'
      '<div style="background: #12131c; padding: 12px; border-radius: 8px; margin-top: 15px; max-height: 250px; overflow-y: auto; border: 1px solid var(--border-color);">'
      + private_accs_html
      + '</div>'
      '</div>'

      '<div class="card" style="border: 1px solid var(--success);">'
      '<h3 class="rgb-text" style="margin-top: 0;">⚡ Quản Lý Trạng Thái Cày Thuê</h3>'
      '<form method="POST">'
      '<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">'
      f'<input type="checkbox" name="is_ready" {checked_attr} style="width: 20px; height: 20px; accent-color: var(--success);">'
      '<label style="font-size: 14px; font-weight: 600; color: white; margin: 0;">Sẵn sàng nhận đơn cày thuê</label>'
      '</div>'
      '<label style="font-size: 13px; color: var(--text-secondary);">Thông báo trạng thái:</label>'
      f'<input type="text" name="current_task" value="{cay_thue_status["current_task"]}" placeholder="Để trống nếu rảnh...">'
      '<button type="submit" name="update_cay_thue_status" class="btn rgb-btn" style="margin-top: 10px;">CẬP NHẬT TRẠNG THÁI</button>'
      '</form>'
      '</div>'

      '<div class="card" style="border: 1px solid var(--primary);">'
      '<h3 class="rgb-text" style="margin-top: 0;">⚔️ Thêm Gói Cày Thuê Mới</h3>'
      '<form method="POST">'
      '<label style="font-size: 13px; color: var(--text-secondary);">Tên gói cày thuê:</label>'
      '<input type="text" name="ct_name" placeholder="VD: Cày Đảo Bánh..." required>'
      '<label style="font-size: 13px; color: var(--text-secondary);">Giá tiền (VNĐ):</label>'
      '<input type="number" name="ct_price" placeholder="VD: 50000" required>'
      '<label style="font-size: 13px; color: var(--text-secondary);">Mô tả chi tiết:</label>'
      '<input type="text" name="ct_desc" placeholder="Mô tả công việc..." required>'
      '<button type="submit" name="add_cay_thue" class="btn rgb-btn" style="margin-top: 15px;">THÊM GÓI CÀY THUÊ</button>'
      '</form>'
      '</div>'

      '<div class="card" style="border: 1px solid #70a1ff;"><h3 class="rgb-text" style="margin-top: 0;">🌐 Lịch Sử Truy Cập Gần Đây</h3><div style="background: #12131c; padding: 12px; border-radius: 8px; max-height: 200px; overflow-y: auto; border: 1px solid var(--border-color);">'
      + visitors_html
      + '</div></div>'
      
      '<div class="card" style="border: 1px solid var(--primary);">'
      '<h3 class="rgb-text" style="margin-top: 0;">📦 Thêm Sản Phẩm Mới (Hỗ Trợ Nhiều Ảnh)</h3>'
      '<form method="POST">'
      '<label style="font-size: 13px; color: var(--text-secondary);">Tên sản phẩm:</label>'
      '<input type="text" name="name" placeholder="VD: Acc V4 Full..." required>'
      '<label style="font-size: 13px; color: var(--text-secondary);">Phân loại:</label>'
      '<select name="category"><option value="tuichon">Acc Tự Chọn</option><option value="random">Acc Random / Túi Mù</option></select>'
      '<label style="font-size: 13px; color: var(--text-secondary);">Giá tiền (VNĐ):</label>'
      '<input type="number" name="price" placeholder="VD: 30000" required>'
      '<label style="font-size: 13px; color: var(--text-secondary);">Link các ảnh minh họa (Cách nhau bằng dấu cách hoặc xuống dòng):</label>'
      '<textarea name="images" placeholder="https://i.ibb.co/anh1.jpg https://i.ibb.co/anh2.jpg" rows="3" style="width: 100%; padding: 12px 15px; margin: 10px 0; background: #12131c; border: 1px solid var(--border-color); color: white; border-radius: 8px; box-sizing: border-box; font-family: \'Poppins\', sans-serif; font-size: 14px;"></textarea>'
      '<label style="font-size: 13px; color: var(--text-secondary);">Mô tả ngắn:</label>'
      '<input type="text" name="desc" placeholder="Mô tả tài khoản..." required>'
      '<label style="font-size: 13px; color: var(--text-secondary);">Tài khoản game:</label>'
      '<input type="text" name="game_acc" placeholder="username | password">'
      '<button type="submit" name="add_product" class="btn rgb-btn" style="margin-top: 15px;">THÊM VÀO KHO</button>'
      '</form>'
      '</div>'

      '<div class="card" style="border: 1px solid var(--accent);"><h3 class="rgb-text" style="margin-top: 0;">🎟️ Quản Lý Mã Giảm Giá Nâng Cao</h3><form method="POST" style="margin-bottom: 15px;"><input type="text" name="coupon_code" placeholder="Mã (VD: GIAM5K)" required><input type="number" name="discount_amount" placeholder="Số tiền giảm (VNĐ)" required><input type="number" name="expires_in_days" placeholder="Thời hạn (Số ngày)" required><input type="number" name="max_uses" placeholder="Giới hạn số lượt dùng" required><button type="submit" name="add_coupon" class="btn rgb-btn" style="margin-top: 8px;">THÊM MÃ GIẢM GIÁ</button></form><div style="background: #12131c; padding: 12px; border-radius: 8px; border: 1px solid var(--border-color);">'
      + (coupons_html if coupons_html else '<p>Chưa có mã giảm giá nào.</p>')
      + '</div></div>'
      '<div class="card" style="border: 1px solid var(--accent);"><h3 class="rgb-text" style="margin-top: 0;">💰 Cộng tiền cho Thành viên</h3><form method="POST"><input type="text" name="target_username" placeholder="Tên tài khoản khách..." required><input type="number" name="bonus_amount" placeholder="Số tiền cộng (VNĐ)..." required><button type="submit" name="bonus_user" class="btn rgb-btn" style="margin-top: 15px;">CỘNG TIỀN NGAY</button></form></div>'
      '<div class="card" style="border: 1px solid #70a1ff;"><h3 class="rgb-text" style="margin-top: 0;">💬 Tin Nhắn Hỗ Trợ Khách Hàng</h3>'
      + (chat_admin_html if chat_admin_html else '<p>Chưa có tin nhắn nào.</p>')
      + '</div>'
      '<div class="card" style="border: 1px solid var(--success);"><h3 class="rgb-text" style="margin-top: 0;">📋 Quản Lý & Duyệt Thẻ Cào (Duyệt Tay)</h3>'
      + cards_html
      + '</div>'
  )
  return render_template_string(BASE_HTML, content=admin_content, users=users)

@app.route('/api/admin-ai', methods=['POST'])
def admin_ai_handler():
  if 'username' not in session or session.get('role') != 'admin':
    return jsonify({'success': False, 'reply': 'Bạn không có quyền sử dụng tính năng này!'})
  
  data = request.json or {}
  prompt = data.get('prompt', '').strip().lower()
  
  reply = "Tôi là Trợ lý AI của GA GAMING ROBLOX. Ông có thể hỏi tôi về cách thêm sản phẩm, quản lý mã giảm giá, kiểm tra thẻ nạp duyệt tay hoặc hướng dẫn vận hành shop nhé!"
  
  if 'mã giảm giá' in prompt or 'coupon' in prompt:
    reply = "Để tạo mã giảm giá, ông kéo xuống phần <b>Quản Lý Mã Giảm Giá Nâng Cao</b> trong trang admin, điền mã (VD: GIAM5K), số tiền giảm, số ngày hết hạn và bấm nút Thêm Mã Giảm Giá là xong!"
  elif 'nạp tiền' in prompt or 'qr' in prompt or 'thẻ cào' in prompt:
    reply = "Hệ thống nạp QR chạy tự động qua webhook. Riêng thẻ cào đã chuyển sang chế độ <b>Duyệt Tay</b>: khách gửi thẻ sẽ hiển thị trong bảng Quản Lý Thẻ Cào ở trang Admin để ông bấm nút Duyệt hoặc Hủy!"
  elif 'cày thuê' in prompt:
    reply = "Ông có thể quản lý trạng thái rảnh/bận nhận đơn cày thuê ở mục <b>Quản Lý Trạng Thái Cày Thuê</b> ngay phía trên, hoặc thêm các gói cày mới bất cứ lúc nào!"
  elif 'sổ tay' in prompt or 'ghi chú' in prompt:
    reply = "Sổ tay ghi chú cày cuốc là nơi lưu lại tài khoản và mật khẩu game của khách khi họ gửi cày thuê một cách riêng tư, chỉ có tài khoản Admin mới xem và quản lý được."

  return jsonify({'success': True, 'reply': reply})

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
