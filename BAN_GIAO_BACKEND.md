# Bàn giao SQL và backend của Người 2

Ngày kiểm tra: 08/11/2026. Nhánh bàn giao: `feature/backend`.

## Thành phần bàn giao

| Thành phần | Nội dung |
|---|---|
| `KTX.sql` | File nộp YC2, ghép lần lượt DDL, dữ liệu mẫu và 4 truy vấn. |
| `KTX_phanDDL.sql` | DDL của Người 1: 12 bảng, 16 trigger; đưa kèm để chạy đầy đủ. |
| `du_lieu_mau.sql` | 4 phòng, 9 sinh viên, 6 lượt thăm, 4 dịch vụ, 12 lượt sử dụng dịch vụ, 4 vé xe, 10 lượt quẹt, 3 hóa đơn. |
| `truy_van-yc2.sql` | 4 truy vấn độc lập; xử lý collation khi lọc mã sinh viên. |
| `app.py`, `db.py` | Backend Flask, kết nối MySQL, truy vấn và giao dịch ghi dữ liệu. |
| `README.md`, `requirements.txt` | Hướng dẫn chạy trên PowerShell/Workbench và thư viện của dự án. |

Giao diện `templates/`, `static/` và bản demo đi kèm từ nhánh frontend. Việc có các file trong nhánh backend không đồng nghĩa toàn bộ chúng do Người 2 viết.

## Chạy từ đầu

1. Tải nhánh `feature/backend`, tạo môi trường Python và cài `requirements.txt` theo README.
2. Trên MySQL dành cho bài tập, chạy toàn bộ `KTX.sql` bằng Workbench hoặc lệnh `SOURCE` trong MySQL. File này xóa và tạo lại các bảng trong `KTX`.
3. Trong cùng cửa sổ PowerShell sẽ chạy app, đặt biến `KTX_DB_PASSWORD` bằng mật khẩu MySQL của máy đó. Không lưu mật khẩu vào mã nguồn.
4. Chạy `python app.py`, mở `http://localhost:5000`.
5. Xem `/hoadon`, `/dichvu`, `/khach`, `/doanhthu`; chọn cùng kỳ với SQL để đối chiếu.

Ngày của dữ liệu mẫu được tính tại lúc import. Để kiểm tra về sau, chọn kỳ chứa ngày đã import; không cần xóa/nạp lại dữ liệu chỉ để xem kết quả.

## Hàm dùng chung cho frontend

```python
check_phong(masv, so_phong, ngay)
check_xe(masv, bien_so, loai, ngay)
```

Hai hàm nằm trong `app.py`, trả `None` nếu hợp lệ hoặc chuỗi thông báo lỗi tiếng Việt. Không ghi dữ liệu, không gọi `flash()` và không cần request của Flask; chúng vẫn cần kết nối MySQL để tra cứu. Truyền ngày dưới dạng `YYYY-MM-DD`; chuẩn hóa biển số hoặc tạo mã xe đạp trước khi gọi `check_xe`.

Các route `/phong/xep` và `/xe/dangky` đã sử dụng hai hàm này. Trigger tiếp tục kiểm tra lại lúc ghi vào database. Trang dịch vụ dùng `/dichvu`, tương ứng phần `/sudung` trong bản phân công ban đầu.

## Kết quả kiểm tra tự động

Thực hiện trên một MySQL tạm độc lập, không sử dụng database đang chạy của người dùng. Môi trường: Python 3.13.6, Flask 3.1.3, PyMySQL 1.2.3, MySQL 8.0.46.

| Nội dung | Kết quả |
|---|---|
| Import trọn `KTX.sql` trên MySQL 8.0.46 | Đạt; đủ 12 bảng, 16 trigger, 9 sinh viên, 3 hóa đơn và 10 dòng chi tiết mẫu. |
| Kiểm tra thư viện bằng `pip check` trong môi trường hiện có | Đạt; không phát hiện phụ thuộc bị thiếu/xung đột. |
| Kiểm tra cú pháp 4 file Python chính | Đạt. |
| 9 URL: `/`, `/sinhvien`, `/phong`, `/khach`, `/dichvu`, `/xe`, `/hoadon`, `/doanhthu`, chi tiết hóa đơn | Đạt; HTTP 200 sau chuyển hướng, dùng Flask test client kết nối MySQL thật. |
| Đối chiếu 4 truy vấn SQL với dữ liệu truyền vào trang web, cùng kỳ | Đạt; tiền hóa đơn, tiền dịch vụ, số lần thăm và doanh thu theo tháng khớp. |
| Lọc tất cả, mã sinh viên cụ thể và mã không tồn tại khi kết nối dùng collation 0900 | Đạt; không có lỗi 1267. |
| Xếp sinh viên vào phòng đầy | Bị chặn, không thêm bản ghi. |
| Xếp sinh viên vào phòng còn chỗ | Lưu bản đăng ký thành công. |
| Đăng ký xe thứ 3 còn hiệu lực | Bị chặn, không thêm vé. |
| Đăng ký xe hợp lệ | Lưu vé thành công. |
| Thêm lượt quẹt thứ 3 trong ngày vào MySQL | Trigger tính phí 3.000đ. |
| Đánh dấu đã thu cho sinh viên chưa có hóa đơn của kỳ | Tạo được hóa đơn và chi tiết, trạng thái `DaThanhToan`. |

Kiểm tra HTTP dùng dữ liệu/render của Flask; chưa phải kiểm thử trình duyệt tự động. Việc tải thư viện lại từ mạng trên một máy hoàn toàn mới chưa được kiểm chứng trong đợt này. Người 2 đã xác nhận tự kiểm tra giao diện trước khi yêu cầu chuẩn bị bản bàn giao.

## Điểm cần thống nhất khi tích hợp

- Hiện chỉ xem trang Hóa đơn thì chưa lưu. Nút **Đánh dấu đã thu** vừa tạo hóa đơn nếu chưa tồn tại, vừa ghi nhận thanh toán. Chưa có thao tác lập hóa đơn chưa thanh toán riêng.
- Khi xem hóa đơn đã lưu, giao diện vẫn tính lại từ dữ liệu nguồn; nếu nguồn thay đổi, số hiển thị có thể lệch bản đã chốt. Việc tách bước lập/thanh toán và đọc bản chốt cần một thay đổi nghiệp vụ riêng.
- SQL truy vấn 3 hỗ trợ tuần/tháng; giao diện có thêm chế độ Tất cả.
- File `KTX.sql` là bản gộp. Sau khi thay đổi file thành phần, tạo lại theo lệnh trong README rồi kiểm tra trước khi nộp.
- Nhóm review nhánh `feature/backend` trước khi gộp vào `main`; kiểm tra xung đột với nhánh frontend và DDL của Người 1. Không merge tự động trong bước bàn giao.

So sánh nhánh để review: https://github.com/HoangCong078/btl-csdl-ktx/compare/main...feature/backend
