# Hệ thống quản lý ký túc xá sinh viên

Bài tập lớn môn Cơ sở dữ liệu · Project 2 · Nhóm 10
Thành viên: Lê Hiếu Kiên · Hoàng Chiến Công · Nguyễn Văn Khang

Ứng dụng web dành cho **nhân viên ban quản lý ký túc xá**. Sinh viên không tự đăng nhập: khi cần đăng ký phòng, gửi xe hoặc sử dụng dịch vụ, sinh viên đến quầy và nhân viên nhập thông tin vào hệ thống. Ứng dụng viết bằng Flask (Python), dữ liệu lưu trong MySQL.

Hai phần quan trọng nhất của tài liệu: [Hướng dẫn chạy ứng dụng](#hướng-dẫn-chạy-ứng-dụng) và [Bốn truy vấn theo yêu cầu của đề](#bốn-truy-vấn-theo-yêu-cầu-của-đề).

Bản bàn giao của Người 2 nằm trên nhánh `feature/backend`. File nộp YC2 là `KTX.sql`; xem [biên bản bàn giao backend](BAN_GIAO_BACKEND.md) để biết phạm vi và cách kiểm tra.

---

## Yêu cầu môi trường

- **Python 3.10 trở lên**; môi trường kiểm tra bản bàn giao được ghi trong `BAN_GIAO_BACKEND.md`.
- **MySQL 8.0.16 trở lên**. Các phiên bản cũ hơn bỏ qua ràng buộc `CHECK` nên không phù hợp
- Công cụ chạy file `.sql`: MySQL Workbench hoặc dòng lệnh `mysql`

## Hướng dẫn chạy ứng dụng

Các lệnh dưới đây viết cho PowerShell trên Windows. Với macOS hoặc Linux, thay lệnh kích hoạt môi trường ảo bằng `source venv/bin/activate` và dùng `export` thay cho `$env:`.

**Bước 1. Tải mã nguồn**

```powershell
git clone --branch feature/backend https://github.com/HoangCong078/btl-csdl-ktx.git
cd btl-csdl-ktx
```

**Bước 2. Tạo môi trường ảo và cài thư viện**

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Nếu PowerShell báo "running scripts is disabled", chạy một lần lệnh
`Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned` rồi kích hoạt lại môi trường ảo. Thay đổi này chỉ áp dụng cho cửa sổ PowerShell hiện tại.

**Bước 3. Tạo cơ sở dữ liệu**

`KTX.sql` gồm ba phần theo thứ tự: tạo 12 bảng và trigger, nạp dữ liệu mẫu, chạy 4 truy vấn YC2.

**Chạy lại `KTX.sql` sẽ xóa và tạo lại các bảng trong cơ sở dữ liệu `KTX`. Chỉ dùng trên dữ liệu bài tập hoặc sau khi đã sao lưu dữ liệu cần giữ.**

Cách 1 — MySQL Workbench: kết nối đến máy chủ MySQL, chọn **File → Open SQL Script**, mở `KTX.sql`, bỏ chọn vùng văn bản nếu có, rồi chạy toàn bộ file. Kiểm tra mục **Action Output** không có lỗi đỏ.

Cách 2 — từ PowerShell tại thư mục dự án, đăng nhập MySQL:

```powershell
mysql --default-character-set=utf8mb4 -u root -p
```

Nhập mật khẩu khi được hỏi. Khi thấy dấu nhắc `mysql>`, chạy:

```sql
SOURCE KTX.sql;
SHOW TABLES;
SELECT COUNT(*) AS SoSinhVien FROM SINHVIEN;
exit;
```

Nếu không tìm thấy file, dùng đường dẫn tuyệt đối với dấu `/`, ví dụ `SOURCE D:/daihoc/ki_2_nam_3/BTL_CSDL/KTX.sql;`. PowerShell không hỗ trợ cú pháp nhập file bằng dấu `<` như Command Prompt.

- `KTX_phanDDL.sql` tạo cơ sở dữ liệu `KTX`, gồm 12 bảng và 16 trigger.
- `du_lieu_mau.sql` nạp **9 sinh viên, 4 phòng, 6 lượt thăm, 4 dịch vụ, 12 lượt sử dụng dịch vụ, 4 vé xe, 10 lượt quẹt và 3 hóa đơn mẫu**. Ngày tháng được tính theo ngày chạy file.
- `truy_van-yc2.sql` chứa 4 truy vấn độc lập. Có thể chạy riêng file này nhiều lần mà không xóa dữ liệu.

Nếu muốn chạy từng file thành phần thay cho file gộp, chạy lần lượt `SOURCE KTX_phanDDL.sql;`, `SOURCE du_lieu_mau.sql;`, `SOURCE truy_van-yc2.sql;` trong MySQL. Chỉ chọn một cách nạp ban đầu.

**Bước 4. Khai báo mật khẩu MySQL**

```powershell
$env:KTX_DB_PASSWORD = "mật_khẩu_mysql"
```

Mật khẩu chỉ tồn tại trong cửa sổ terminal đang mở và không được ghi vào mã nguồn. Mở terminal mới thì cần khai báo lại. Nếu MySQL không dùng tài khoản `root` hoặc máy chủ `localhost`, khai báo thêm các biến `KTX_DB_USER`, `KTX_DB_HOST`, `KTX_DB_PORT`, `KTX_DB_NAME` theo cách tương tự.

**Bước 5. Khởi động ứng dụng**

```powershell
python app.py
```

Sau đó truy cập **http://localhost:5000** bằng trình duyệt.

MySQL dùng cổng **3306**, còn web Flask dùng cổng **5000**. Giữ cửa sổ PowerShell đang chạy trong lúc dùng web; nhấn **Ctrl + C** để dừng. Nếu mật khẩu đã khai báo trước khi khởi động mà vẫn lỗi, xem bảng xử lý sự cố bên dưới.

> **Khi chưa cài MySQL:** vẫn có thể xem giao diện bằng bản demo dùng dữ liệu giả: `python demo_fe/demo_app.py`. Dữ liệu của bản demo chỉ lưu trong bộ nhớ và mất khi tắt ứng dụng. Các ràng buộc trong bản demo do mã Python kiểm tra, không phải trigger của MySQL.

---

## Bốn truy vấn theo yêu cầu của đề

| Yêu cầu của đề | Vị trí trong ứng dụng | Cách sử dụng |
|---|---|---|
| **1.** Số tiền mỗi sinh viên phải trả theo tháng (tiền phòng, dịch vụ, gửi xe) | Menu **Hóa đơn** (`/hoadon`) | Chọn tháng, năm; có thể lọc theo phòng, lớp. Nhấn **Chi tiết** để xem từng sinh viên |
| **2.** Sinh viên, tên dịch vụ và tổng tiền từng dịch vụ trong khoảng ngày | Menu **Dịch vụ** (`/dichvu`), tab *Tiền theo sinh viên* | Chọn từ ngày, đến ngày |
| **3.** Sinh viên và khách đến thăm theo tuần hoặc tháng, kèm số lần mỗi khách đến | Menu **Khách thăm** (`/khach`), tab *Số lần mỗi khách* | Chọn Theo tuần, Theo tháng hoặc Tất cả |
| **4.** Doanh thu của từng dịch vụ theo tháng | Menu **Doanh thu** (`/doanhthu`) | Chọn năm, bảng hiển thị đủ 12 tháng |
| **5.** Kiểm tra các ràng buộc | Xem phần tiếp theo | |

Để chạy SQL đối chiếu, mở `truy_van-yc2.sql` trong Workbench và chạy `USE KTX;` cùng `SET NAMES ...` ở đầu file. Mỗi truy vấn cần chạy cả các dòng `SET` đặt tham số và toàn bộ câu `SELECT`/`WITH` phía sau. Chọn cùng tháng/năm hoặc khoảng ngày trên web, để bộ lọc phòng/lớp ở “Tất cả”.

- Truy vấn 1: so sánh tiền phòng, dịch vụ, vé xe, phí xe và tổng tiền theo `MaSV`. Đặt `@ma_sv = NULL` để xem tất cả, hoặc mã sinh viên để xem riêng.
- Truy vấn 2: so sánh theo sinh viên và dịch vụ, trong cùng khoảng từ ngày đến ngày.
- Truy vấn 3: chọn `@ky_tham` là `tuan` hoặc `thang`, dùng cùng ngày mốc với web. Truy vấn độc lập chưa có chế độ `tatca` như giao diện.
- Truy vấn 4: SQL trả 12 dòng/tháng cho mỗi dịch vụ; web hiển thị các tháng thành cột T1–T12. Dấu “–” trên web tương ứng số 0 trong SQL.

### Luồng hóa đơn hiện tại

Mở trang Hóa đơn hoặc Chi tiết chỉ tính khoản phải trả từ dữ liệu phòng, dịch vụ và xe. Khi bấm **Đánh dấu đã thu**, nếu chưa có hóa đơn của kỳ đó thì ứng dụng tạo `HOADON` và `CHITIET_HOADON`; nếu đã có thì cập nhật trạng thái. Giao diện hiện chưa có nút lập hóa đơn chưa thanh toán riêng, và vẫn tính lại số tiền từ dữ liệu nguồn khi xem hóa đơn đã lưu. Vì vậy cần thống nhất với nhóm trước khi sửa dữ liệu nguồn của kỳ đã chốt.

## Kiểm tra các ràng buộc

Ràng buộc được kiểm tra ở form và hai hàm dùng chung `check_phong(masv, so_phong, ngay)`, `check_xe(masv, bien_so, loai, ngay)` trong `app.py`. Các hàm trả `None` nếu hợp lệ, hoặc thông báo lỗi tiếng Việt; không ghi dữ liệu và không cần ngữ cảnh request của Flask. Trigger MySQL kiểm tra lại trước khi lưu. Mã xe cần được chuẩn hóa hoặc tạo mã xe đạp trước khi gọi `check_xe`; ngày truyền vào có dạng `YYYY-MM-DD`.

- **Phòng đã đủ người thì không xếp thêm được.** Tại trang *Phòng*, phòng P102 đang đủ 2/2 người nên chỉ hiển thị nút "Đã đầy". Có thể xếp thêm một sinh viên vào P101 cho đủ 4/4 rồi thử xếp tiếp.
- **Mỗi sinh viên đăng ký tối đa 2 xe vé tháng.** Tại trang *Xe*, chọn **Đăng ký vé**. Sinh viên Nguyễn Văn An đã có 2 xe nên không thể chọn thêm.
- **Mỗi xe được miễn phí 2 lượt gửi/lấy mỗi ngày, từ lượt thứ 3 thu 3.000đ.** Ngay sau khi nạp dữ liệu mẫu, quét xe `29A1-12345` trong cùng ngày (xe đã có 2 lượt mẫu hôm đó). Lượt này sẽ báo thu 3.000đ. Nếu kiểm tra vào ngày khác, quét đủ 3 lượt để thử. Số tiền do trigger trong MySQL tự tính, ứng dụng chỉ đọc lại kết quả.
- **Chỉ được xóa lượt quét cuối cùng trong ngày.** Thử xóa một lượt cũ ở bảng *Vừa quét*, hệ thống sẽ từ chối và nêu rõ lý do.

## Các quy ước đã thống nhất

Đề bài không quy định hết mọi chi tiết, nên nhóm thống nhất các quy ước sau để thuận tiện cho việc đọc mã nguồn.

- **Tiền phòng tính chẵn tháng.** Một bản đăng ký ở giao với tháng nào dù chỉ một ngày thì tháng đó tính đủ tiền phòng, đúng theo đề. Đơn giá được lưu tại thời điểm đăng ký, nên việc đổi giá phòng về sau không làm thay đổi hóa đơn cũ.
- **Vé tháng gửi xe** có đơn giá 100.000đ mỗi tháng và không quy định hạn cố định. Vé có hiệu lực cho đến khi được hủy (lúc đó trường `NgayKetThuc` được điền). Mỗi tháng vé còn hiệu lực được tính một lần 100.000đ vào hóa đơn.
- **Xe đạp không có biển số.** Hệ thống dùng mã sinh viên làm mã xe, ví dụ `XD-B24DCCN001`. Nhờ đó xe đạp được nhận diện bằng thẻ sinh viên, còn xe máy và xe điện được nhận diện bằng biển số (mô phỏng camera đọc biển số).
- **Mỗi lần gửi hoặc lấy xe tính là một lượt.** Lượt đầu tiên của xe là Gửi, các lượt sau luân phiên giữa Lấy và Gửi. Số lượt được đếm theo từng vé xe, trong phạm vi một ngày dương lịch.
- **Tuần được tính từ thứ Hai đến Chủ nhật** trong truy vấn khách đến thăm.
- **Xe vãng lai** (không có vé tháng) được thu tiền trực tiếp và không lưu vào cơ sở dữ liệu, đúng theo yêu cầu của đề.

## Cấu trúc thư mục

```
btl-csdl-ktx/
├── app.py                # ứng dụng Flask kết nối MySQL (bản chính)
├── db.py                 # kết nối MySQL, chuyển lỗi từ trigger sang tiếng Việt
├── KTX.sql               # file nộp YC2: DDL + dữ liệu mẫu + 4 truy vấn
├── KTX_phanDDL.sql       # tạo cơ sở dữ liệu, 12 bảng và trigger
├── du_lieu_mau.sql       # dữ liệu mẫu
├── truy_van-yc2.sql      # bốn truy vấn độc lập
├── BAN_GIAO_BACKEND.md   # phạm vi, kiểm tra và điểm cần thống nhất
├── requirements.txt      # danh sách thư viện Python
├── templates/            # giao diện HTML (Jinja2 và Bootstrap)
├── static/               # tệp CSS
└── demo_fe/              # bản demo dùng dữ liệu giả, chạy được khi chưa có MySQL
```

## Xử lý các sự cố thường gặp

| Hiện tượng | Cách xử lý |
|---|---|
| PowerShell báo dấu `<` không được hỗ trợ | Đăng nhập `mysql -u root -p`, rồi dùng `SOURCE KTX.sql;` trong MySQL. |
| `Access denied ... using password: NO` | Dừng app, khai báo đúng `$env:KTX_DB_PASSWORD` trong cùng cửa sổ rồi chạy lại. Kiểm tra chữ cuối là `PASSWORD`, không phải `PASSWORK`. |
| `Access denied ... using password: YES` | Kiểm tra mật khẩu, tài khoản và máy chủ khớp kết nối Workbench. |
| `Unknown database 'KTX'` | Chưa nạp SQL, hoặc `KTX_DB_NAME` đang trỏ sang cơ sở dữ liệu khác. |
| Trang báo không kết nối được MySQL | Kiểm tra dịch vụ MySQL, cổng 3306 và các biến cấu hình. |
| `cryptography package is required` | Chạy lại `pip install -r requirements.txt`. |
| Lỗi 1267 khi lọc `@ma_sv` | Dùng bản mới của `truy_van-yc2.sql`, chạy lại phần `SET` và toàn bộ truy vấn. Bản này đã chuẩn hóa collation cho phép so sánh mã sinh viên. |
| Lỗi 1442 khi nạp chi tiết hóa đơn | Dùng bản mới của `du_lieu_mau.sql`/`KTX.sql`, trong đó đọc danh sách hóa đơn từ bảng tạm trước khi trigger cập nhật tổng tiền. |
| Lỗi 3823 ở `CHITIET_HOADON` | Kiểm tra đang dùng DDL mới; ba khóa ngoại nguồn đã dùng `ON UPDATE RESTRICT`. |
| Không thấy dữ liệu theo kỳ | Kiểm tra ngày trong dữ liệu mẫu và bộ lọc; ngày được cố định lúc nạp mẫu, không tự đổi khi mở web vào ngày khác. |

## Cập nhật file SQL nộp bài

Sau khi sửa một trong ba file SQL thành phần, tạo lại `KTX.sql` từ PowerShell tại thư mục dự án:

```powershell
Get-Content -LiteralPath 'KTX_phanDDL.sql','du_lieu_mau.sql','truy_van-yc2.sql' -Encoding UTF8 |
    Set-Content -LiteralPath 'KTX.sql' -Encoding UTF8
```

Kiểm tra lại file gộp trên dữ liệu bài tập trước khi nộp. Khi cần đọc kết quả truy vấn trên dữ liệu đang có, chỉ chạy `truy_van-yc2.sql`.
