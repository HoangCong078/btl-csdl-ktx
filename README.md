# Hệ thống quản lý ký túc xá sinh viên

Bài tập lớn môn Cơ sở dữ liệu · Project 2 · Nhóm 10
Thành viên: Lê Hiếu Kiên · Hoàng Chiến Công · Nguyễn Văn Khang

Ứng dụng web dành cho **nhân viên ban quản lý ký túc xá**. Sinh viên không tự đăng nhập: khi cần đăng ký phòng, gửi xe hoặc sử dụng dịch vụ, sinh viên đến quầy và nhân viên nhập thông tin vào hệ thống. Ứng dụng viết bằng Flask (Python), dữ liệu lưu trong MySQL.

Mục lục nhanh: [Hướng dẫn chạy](#hướng-dẫn-chạy-ứng-dụng) · [Bốn truy vấn theo đề](#bốn-truy-vấn-theo-yêu-cầu-của-đề) · [Kiểm tra ràng buộc](#kiểm-tra-các-ràng-buộc) · [Tính năng bổ sung](#tính-năng-bổ-sung) · [Quy ước](#các-quy-ước-đã-thống-nhất)

File SQL nộp cho yêu cầu 2 là `KTX.sql`. Phạm vi và cách kiểm tra phần backend nằm trong [BAN_GIAO_BACKEND.md](BAN_GIAO_BACKEND.md).

---

## Yêu cầu môi trường

- **Python 3.10 trở lên**
- **MySQL 8.0.16 trở lên**. Các phiên bản cũ hơn bỏ qua ràng buộc `CHECK` nên không phù hợp
- Công cụ chạy file `.sql`: MySQL Workbench hoặc dòng lệnh `mysql`

## Hướng dẫn chạy ứng dụng

Các lệnh dưới đây viết cho PowerShell trên Windows. Với macOS hoặc Linux, thay lệnh kích hoạt môi trường ảo bằng `source venv/bin/activate` và dùng `export` thay cho `$env:`.

**Bước 1. Tải mã nguồn**

```powershell
git clone https://github.com/HoangCong078/btl-csdl-ktx.git
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

`KTX.sql` gồm ba phần theo thứ tự: tạo 12 bảng và trigger, nạp dữ liệu mẫu, chạy 4 truy vấn.

**Chạy lại `KTX.sql` sẽ xóa và tạo lại các bảng trong cơ sở dữ liệu `KTX`. Chỉ dùng trên dữ liệu bài tập hoặc sau khi đã sao lưu dữ liệu cần giữ.**

*Cách 1: MySQL Workbench.* Kết nối đến máy chủ MySQL, chọn **File → Open SQL Script**, mở `KTX.sql` và chạy toàn bộ file. Kiểm tra mục **Action Output** không có lỗi đỏ.

*Cách 2: dòng lệnh.* Tại thư mục dự án, đăng nhập MySQL:

```powershell
mysql --default-character-set=utf8mb4 -u root -p
```

Khi thấy dấu nhắc `mysql>`, chạy:

```sql
SOURCE KTX.sql;
SHOW TABLES;
SELECT COUNT(*) AS SoSinhVien FROM SINHVIEN;
exit;
```

Nếu không tìm thấy file, dùng đường dẫn tuyệt đối với dấu `/`. PowerShell không hỗ trợ cú pháp nhập file bằng dấu `<` như Command Prompt.

Các file thành phần:

- `KTX_phanDDL.sql`: tạo cơ sở dữ liệu `KTX`, gồm 12 bảng và 16 trigger.
- `du_lieu_mau.sql`: 9 sinh viên, 4 phòng, 6 lượt thăm, 4 dịch vụ, 12 lượt sử dụng dịch vụ, 4 vé xe, 10 lượt quẹt và 3 hóa đơn mẫu. Ngày tháng được tính theo ngày chạy file.
- `truy_van-yc2.sql`: 4 truy vấn độc lập, chạy riêng nhiều lần mà không xóa dữ liệu.

Chỉ chọn **một** cách nạp ban đầu: file gộp `KTX.sql`, hoặc lần lượt ba file thành phần.

**Bước 4. Khai báo mật khẩu MySQL**

```powershell
$env:KTX_DB_PASSWORD = "mật_khẩu_mysql"
```

Mật khẩu chỉ tồn tại trong cửa sổ terminal đang mở và không được ghi vào mã nguồn. Mở terminal mới thì cần khai báo lại. Nếu MySQL không dùng tài khoản `root` hoặc máy chủ `localhost`, khai báo thêm `KTX_DB_USER`, `KTX_DB_HOST`, `KTX_DB_PORT`, `KTX_DB_NAME` theo cách tương tự.

**Bước 5. Khởi động ứng dụng**

```powershell
python app.py
```

Truy cập **http://localhost:5000** bằng trình duyệt. MySQL dùng cổng 3306, ứng dụng web dùng cổng 5000. Giữ cửa sổ PowerShell đang chạy trong lúc sử dụng; nhấn **Ctrl + C** để dừng.

> **Khi chưa cài MySQL:** có thể xem giao diện bằng bản demo dùng dữ liệu giả: `python demo_fe/demo_app.py`. Dữ liệu của bản demo chỉ lưu trong bộ nhớ và mất khi tắt ứng dụng. Các ràng buộc trong bản demo do mã Python kiểm tra, không phải trigger của MySQL. Bản demo không có các tính năng bổ sung.

---

## Bốn truy vấn theo yêu cầu của đề

| Yêu cầu của đề | Vị trí trong ứng dụng | Cách sử dụng |
|---|---|---|
| **1.** Số tiền mỗi sinh viên phải trả theo tháng (tiền phòng, dịch vụ, gửi xe) | Menu **Hóa đơn** (`/hoadon`) | Chọn tháng, năm; có thể lọc theo phòng, lớp. Nhấn **Chi tiết** để xem từng sinh viên |
| **2.** Sinh viên, tên dịch vụ và tổng tiền từng dịch vụ trong khoảng ngày | Menu **Dịch vụ** (`/dichvu`), tab *Tiền theo sinh viên* | Chọn từ ngày, đến ngày |
| **3.** Sinh viên và khách đến thăm theo tuần hoặc tháng, kèm số lần mỗi khách đến | Menu **Khách thăm** (`/khach`), tab *Số lần mỗi khách* | Chọn Theo tuần, Theo tháng hoặc Tất cả |
| **4.** Doanh thu của từng dịch vụ theo tháng | Menu **Doanh thu** (`/doanhthu`) | Chọn năm, bảng và biểu đồ hiển thị đủ 12 tháng |
| **5.** Kiểm tra các ràng buộc | Xem phần tiếp theo | |

Để đối chiếu bằng SQL, mở `truy_van-yc2.sql` trong Workbench, chạy `USE KTX;` và `SET NAMES ...` ở đầu file. Mỗi truy vấn cần chạy cả các dòng `SET` đặt tham số và toàn bộ câu `SELECT`/`WITH` phía sau. Chọn cùng tháng/năm hoặc khoảng ngày trên web, để bộ lọc phòng/lớp ở "Tất cả".

- Truy vấn 1: tiền phòng, dịch vụ, vé xe, phí xe và tổng tiền theo `MaSV`. Đặt `@ma_sv = NULL` để xem tất cả, hoặc mã sinh viên để xem riêng.
- Truy vấn 2: theo sinh viên và dịch vụ, trong khoảng từ ngày đến ngày.
- Truy vấn 3: đặt `@ky_tham` là `tuan` hoặc `thang`, dùng cùng ngày mốc với web. Truy vấn độc lập chưa có chế độ `tatca` như giao diện.
- Truy vấn 4: SQL trả 12 dòng/tháng cho mỗi dịch vụ; web hiển thị thành cột T1 đến T12. Dấu "–" trên web ứng với số 0 trong SQL.

### Luồng hóa đơn

Mở trang Hóa đơn hoặc Chi tiết chỉ **tính** khoản phải trả từ dữ liệu phòng, dịch vụ và xe. Khi bấm **Đánh dấu đã thu**, nếu chưa có hóa đơn của kỳ đó thì ứng dụng tạo `HOADON` và `CHITIET_HOADON`; nếu đã có thì cập nhật trạng thái. Hóa đơn đã lưu vẫn được tính lại từ dữ liệu nguồn khi xem, nên cần thống nhất trước khi sửa dữ liệu nguồn của kỳ đã chốt.

## Kiểm tra các ràng buộc

Ràng buộc được kiểm tra ở hai lớp: biểu mẫu và hai hàm dùng chung `check_phong(masv, so_phong, ngay)`, `check_xe(masv, bien_so, loai, ngay)` trong `app.py` (trả `None` nếu hợp lệ, hoặc thông báo lỗi tiếng Việt), rồi **trigger MySQL** kiểm tra lại trước khi lưu. Dù dữ liệu được gửi trực tiếp vào cơ sở dữ liệu, trigger vẫn từ chối.

- **Phòng đã đủ người thì không xếp thêm được.** Tại trang *Phòng*, phòng đã đủ người chỉ hiển thị nút "Đã đầy" (ví dụ P102 ngay sau khi nạp dữ liệu mẫu). Có thể xếp thêm sinh viên vào một phòng còn chỗ cho đủ người rồi thử xếp tiếp.
- **Mỗi sinh viên đăng ký tối đa 2 xe vé tháng.** Tại trang *Xe*, chọn **Đăng ký vé**. Sinh viên đã có 2 xe (ví dụ Nguyễn Văn An) không thể chọn thêm.
- **Mỗi xe được miễn phí 2 lượt gửi/lấy mỗi ngày, từ lượt thứ 3 thu 3.000đ.** Ngay sau khi nạp dữ liệu mẫu, quét xe `29A1-12345` trong cùng ngày (xe đã có 2 lượt mẫu hôm đó): lượt này báo thu 3.000đ. Nếu kiểm tra vào ngày khác, quét đủ 3 lượt để thử. Số tiền do trigger tự tính, ứng dụng chỉ đọc lại.
- **Chỉ được xóa lượt quét cuối cùng trong ngày.** Thử xóa một lượt cũ ở bảng *Vừa quét*, hệ thống từ chối và nêu lý do.

## Tính năng bổ sung

| # | Tính năng | Vị trí và cách dùng |
|---|---|---|
| 1 | Trang tổng quan | Trang chủ (`/`): số liệu trong ngày, tình trạng phòng, khung "Cần chú ý" |
| 2 | Sửa thông tin sinh viên | Trang *Sinh viên*, nút bút chì ở mỗi dòng |
| 3 | In hóa đơn | *Hóa đơn* → **Chi tiết** → **In hóa đơn**; dùng **In / Lưu PDF** của trình duyệt |
| 4 | Xuất CSV và sao lưu | Menu **Công cụ**: tải từng bảng ra CSV (mở được bằng Excel) hoặc sao lưu tất cả thành file `.zip` |
| 5 | Biểu đồ doanh thu | Trang *Doanh thu*: biểu đồ cột chồng theo tháng và theo dịch vụ |
| 6 | Cảnh báo | Huy hiệu trên menu *Hóa đơn* (số hóa đơn tháng này chưa thu) và *Phòng* (số phòng đã đầy) |
| 7 | Lịch sử gửi/lấy xe theo từng xe | Từ *Hồ sơ sinh viên*, bấm biển số xe (`/xe/lich-su/<biển số>`) |
| 8 | Hồ sơ sinh viên | Bấm tên sinh viên ở trang *Sinh viên*: thông tin, lịch sử ở, xe, khách thăm, tiền tháng này |
| 9 | Sắp xếp bảng theo cột | Bấm tiêu đề cột của bất kỳ bảng. Cột tên sắp theo tên trước, họ sau |
| 10 | Chế độ sáng/tối | Nút ở chân menu, ghi nhớ lựa chọn trên trình duyệt |

## Các quy ước đã thống nhất

Đề bài không quy định hết mọi chi tiết, nên nhóm thống nhất các quy ước sau.

- **Tiền phòng tính chẵn tháng.** Một bản đăng ký ở giao với tháng nào dù chỉ một ngày thì tháng đó tính đủ tiền phòng, đúng theo đề. Đơn giá được lưu tại thời điểm đăng ký, nên đổi giá phòng về sau không làm thay đổi hóa đơn cũ.
- **Vé tháng gửi xe** có đơn giá 100.000đ mỗi tháng và không có hạn cố định. Vé có hiệu lực cho đến khi được hủy (lúc đó trường `NgayKetThuc` được điền). Mỗi tháng vé còn hiệu lực được tính một lần 100.000đ vào hóa đơn.
- **Xe đạp không có biển số.** Hệ thống dùng mã sinh viên làm mã xe, ví dụ `XD-B24DCCN001`. Xe đạp được nhận diện bằng thẻ sinh viên, xe máy và xe điện bằng biển số (mô phỏng camera đọc biển số).
- **Mỗi lần gửi hoặc lấy xe tính là một lượt.** Lượt đầu tiên của xe là Gửi, các lượt sau luân phiên giữa Lấy và Gửi. Số lượt đếm theo từng vé xe, trong phạm vi một ngày dương lịch.
- **Tuần tính từ thứ Hai đến Chủ nhật** trong truy vấn khách đến thăm.
- **Xe vãng lai** (không có vé tháng) thu tiền trực tiếp và không lưu vào cơ sở dữ liệu, đúng theo yêu cầu của đề.

## Cấu trúc thư mục

```
btl-csdl-ktx/
├── app.py                # ứng dụng Flask kết nối MySQL
├── db.py                 # kết nối MySQL, chuyển lỗi từ trigger sang tiếng Việt
├── tinh_nang_phu.py      # các tính năng bổ sung (gắn vào app.py)
├── KTX.sql               # file nộp YC2: DDL + dữ liệu mẫu + 4 truy vấn
├── KTX_phanDDL.sql       # tạo cơ sở dữ liệu, 12 bảng và trigger
├── du_lieu_mau.sql       # dữ liệu mẫu
├── truy_van-yc2.sql      # bốn truy vấn độc lập
├── BAN_GIAO_BACKEND.md   # phạm vi, kiểm tra và điểm cần thống nhất
├── requirements.txt      # danh sách thư viện Python
├── templates/            # giao diện HTML (Jinja2 và Bootstrap)
├── static/               # CSS và JavaScript
└── demo_fe/              # bản demo dùng dữ liệu giả, chạy được khi chưa có MySQL
```

## Xử lý các sự cố thường gặp

| Hiện tượng | Cách xử lý |
|---|---|
| PowerShell báo dấu `<` không được hỗ trợ | Đăng nhập `mysql -u root -p`, rồi dùng `SOURCE KTX.sql;` trong MySQL |
| `Access denied ... using password: NO` | Dừng ứng dụng, khai báo `$env:KTX_DB_PASSWORD` trong cùng cửa sổ rồi chạy lại |
| `Access denied ... using password: YES` | Kiểm tra mật khẩu, tài khoản và máy chủ khớp với kết nối trong Workbench |
| `Unknown database 'KTX'` | Chưa nạp SQL, hoặc `KTX_DB_NAME` đang trỏ sang cơ sở dữ liệu khác |
| Trang báo không kết nối được MySQL | Kiểm tra dịch vụ MySQL, cổng 3306 và các biến cấu hình |
| `cryptography package is required` | Chạy lại `pip install -r requirements.txt` |
| Lỗi 1267, 1442 hoặc 3823 khi chạy SQL | Đã được xử lý trong bản hiện tại; kiểm tra đang dùng đúng các file SQL mới nhất trong kho mã |
| Không thấy dữ liệu theo kỳ | Ngày trong dữ liệu mẫu được cố định lúc nạp; chọn kỳ chứa ngày đã nạp hoặc nạp lại `KTX.sql` |
| Giao diện không có biểu tượng hoặc phông chữ | Giao diện tải Bootstrap, biểu tượng và biểu đồ từ CDN, cần kết nối Internet |

## Cập nhật file SQL nộp bài

Sau khi sửa một trong ba file SQL thành phần, tạo lại `KTX.sql` từ PowerShell tại thư mục dự án:

```powershell
Get-Content -LiteralPath 'KTX_phanDDL.sql','du_lieu_mau.sql','truy_van-yc2.sql' -Encoding UTF8 |
    Set-Content -LiteralPath 'KTX.sql' -Encoding UTF8
```

Kiểm tra lại file gộp trên dữ liệu bài tập trước khi nộp.