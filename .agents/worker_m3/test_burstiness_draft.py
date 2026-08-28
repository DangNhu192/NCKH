import re
import math

CONTENTBETA_VIETNAMESE_CLICHES = [
    ("Trong bối cảnh hiện nay", "Thực tế khảo sát cho thấy"),
    ("Trong bối cảnh hiện tại", "Thực tiễn chứng minh"),
    ("Không thể phủ nhận rằng", "Rõ ràng"),
    ("Đóng vai trò quan trọng", "giữ vị trí then chốt"),
    ("Đóng vai trò vô cùng quan trọng", "trực tiếp quyết định"),
    ("Đóng vai trò then chốt", "giữ vai trò trung tâm"),
    ("Là một trong những yếu tố", "là nhân tố trực tiếp"),
    ("Bức tranh toàn cảnh", "bối cảnh chung"),
    ("Nói một cách khác", "nói cách khác"),
    ("Có thể nói rằng", "thực chất"),
    ("Có thể thấy rằng", "dữ liệu chỉ ra"),
    ("Đáng chú ý là", "đáng lưu tâm là"),
    ("Cần lưu ý rằng", "cần nhấn mạnh rằng"),
    ("Điểm nổi bật", "điểm cốt lõi"),
    ("Kỷ nguyên 4.0", "thời đại số"),
    ("Thời đại số hóa", "quá trình chuyển đổi số"),
    ("Bước tiến vượt bậc", "đột phá lớn"),
    ("Giải pháp toàn diện", "giải pháp đồng bộ"),
    ("Tối ưu hóa toàn diện", "nâng cao hiệu suất"),
    ("Mở ra một chương mới", "tạo bước ngoặt"),
    ("Mở khóa tiềm năng", "khai thác tối đa thế mạnh"),
    ("Nâng tầm giá trị", "gia tăng giá trị thực tế"),
    ("Thay đổi cuộc chơi", "tạo bước ngoặt phát triển"),
    ("Như một con dao hai lưỡi", "tiềm ẩn cả cơ hội lẫn rủi ro"),
    ("Hành trình chuyển đổi", "giai đoạn thực thi"),
    ("Lan tỏa giá trị", "nhân rộng hiệu quả"),
    ("Thúc đẩy đổi mới sáng tạo", "thúc đẩy sáng tạo liên tục"),
    ("Hãy cùng khám phá", "khảo sát chi tiết"),
    ("Tiềm năng to lớn", "lợi thế đáng kể"),
    ("Điều quan trọng là", "trọng tâm là"),
    ("Một cách hiển nhiên", "rõ ràng"),
    ("Dễ dàng nhận thấy", "số liệu khẳng định"),
    ("Nhìn chung,", "Xét về tổng thể,"),
    ("Tóm lại,", "Sau cùng,"),
    ("Tổng kết lại,", "Qua phân tích,"),
]

def calculate_burstiness(text: str) -> float:
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if len(s.strip().split()) >= 2]
    if len(sentences) < 2:
        return 0.0
    lens = [len(s.split()) for s in sentences]
    mean_len = sum(lens) / len(lens)
    variance = sum((l - mean_len) ** 2 for l in lens) / len(lens)
    return math.sqrt(variance)

text_sample = "Trong bối cảnh hiện nay, việc nghiên cứu chuyển đổi số đóng vai trò vô cùng quan trọng đối với các doanh nghiệp. Không thể phủ nhận rằng các công nghệ mới mang lại nhiều lợi ích thiết thực cho quá trình vận hành sản xuất. Có thể thấy rằng hiệu suất làm việc đã tăng trưởng 28.5% khi áp dụng giải pháp toàn diện này."

print("Original text:", text_sample)
print("Original Burstiness sigma:", calculate_burstiness(text_sample))
