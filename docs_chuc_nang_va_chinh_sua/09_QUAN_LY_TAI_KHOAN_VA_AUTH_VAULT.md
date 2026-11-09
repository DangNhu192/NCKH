# 🔐 KHO QUẢN LÝ BẢN QUYỀN, NGƯỜI DÙNG & AUTH VAULT (SECURITY VAULT)

## 🎯 VỊ TRÍ & ĐẶC TẢ MODULE
- **Giao diện:** Tab 9 (`#admin-tab`), Modal Cài Đặt (`#modal-settings`), Modal Nâng Cấp Gói (`#modal-payment`).
- **File Frontend:** `static/js/admin.js`, `static/js/auth.js`, `static/js/settings.js`, `static/js/onboarding.js`
- **File Backend:** `modules/auth/`, `modules/admin_needle/`, `auth_vault/`

## 🔗 QUY TRÌNH LIÊN KẾT LIÊN THÔNG (INTERLINK PROTOCOL)
- **Đầu vào (Input Tiếp Nhận):**
  - Người dùng nhập API Key (Gemini, OpenAI, Zotero) tại Modal Cài Đặt hoặc kích hoạt License Key.
- **Xử lý Bảo Mật & Mã Hóa:**
  - Mã hóa AES-256-CBC với Salt 128-bit & IV ngẫu nhiên, lưu vào `auth_vault/profiles/user_*.vault.json`.
  - Băm mật khẩu PBKDF2-HMAC-SHA256 (100.000 iterations), ký số License Keys HMAC-SHA256.
- **Đầu ra (Output Bàn Giao Liên Thông):**
  - ➔ **Cung cấp cho TOÀN BỘ 8 Tab Nghiên Cứu:** Tự động giải mã trong suốt trong RAM khi có lệnh gọi AI (Transparent In-Memory Decryption) mà không lưu bản rõ trên đĩa.

## ⚖️ TUÂN THỦ 4 QUY TẮC BẤT BIẾN & ĐẠO ĐỨC NGHIÊN CỨU
1. **Evidence First & Zero Fabrication:** Bảo mật tuyệt đối thông tin bản quyền và dữ liệu người dùng.
2. **In-Place DOM Word (.docx):** Đồng bộ cấu hình lưu trữ thư mục tùy chỉnh.
3. **Chuẩn hóa số thập phân tiếng Việt:** Áp dụng cho các bảng phân tích quota.
4. **Chuẩn hóa hóa học & toán học:** Không can thiệp.

## 📝 NHẬT KÝ YÊU CẦU & KẾT QUẢ XỬ LÝ
- **Yêu cầu 1:** Tạo folder riêng để quản lý key và user có mã hóa Hash, lưu trữ phương thức mã hóa và công cụ giải mã.
  - *Kết quả:* Đã xây dựng `auth_vault/` với AES-256 + PBKDF2 + HMAC, CLI `tools_decrypt_vault.py` và tài liệu hướng dẫn.
- **[2026-08-25 11:18] Yêu cầu 2:** Thiết lập Super Admin `admin@websuper.edu.vn`, chặn hoàn toàn người dùng thường truy cập Quản trị người dùng & Key (HTTP 403).
- **[2026-08-25 11:32] Yêu cầu 3:** Khắc phục triệt để lỗi phân quyền Admin tài khoản Google. Ép buộc phân quyền: Duy nhất email `admin@websuper.edu.vn` mới có quyền Admin, toàn bộ tài khoản Google khác tự động gán role Researcher/User và chặn toàn bộ quyền Admin từ Backend đến Frontend.
- **Yêu cầu 4 (2026-08-26 - Multi-Agent & E2E Validation):**
  - *Kết quả:* Xác thực toàn diện cơ chế bảo mật và phân quyền JWT Bearer qua `test_server_load.py` (8/8 tests PASS), bảo đảm 100% các endpoint được bảo vệ đúng quyền hạn và chịu tải đồng thời 15 luồng an toàn.
- **[2026-11-09] Yêu cầu 5 (Vercel Serverless & Google Identity Services Fallback):**
  - *Vấn đề:* Khi chạy trên Vercel, ứng dụng thiếu file config.json và /api/status kiểm tra kết nối mạng đồng bộ gây timeout, dẫn đến lỗi giao diện 'Không thể kết nối máy chủ để lấy Google Client ID'.
  - *Kết quả:*
    1. Bổ sung DEFAULT_GOOGLE_CLIENT_ID = '198440047477-bfob93g9cee52l63if9bmnbuuathvgmr.apps.googleusercontent.com' trong modules/auth/auth_service.py để luôn trả về Client ID hợp lệ ngay cả khi không có config.json.
    2. Chuyển đổi kiểm tra kết nối trong /api/status (modules/auth/auth_router.py) sang cơ chế non-blocking, phản hồi < 50ms và không gây nghẽn Serverless function.
    3. Nâng cấp initGoogleAuthUI() tại static/js/auth.js với cơ chế fallback 2 tầng tại Frontend, tự động hiển thị Google Identity Services (GIS) button và có cảnh báo thân thiện nếu bị chặn tiện ích quảng cáo.
    4. Kiểm thử tự động qua TestClient(app) xác nhận /api/status và /api/config đạt chuẩn 100% (HTTP 200).
