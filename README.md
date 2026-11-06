# Hệ thống quản lý ký túc xá sinh viên

Bài tập lớn môn Cơ sở dữ liệu · Project 2 · Nhóm 10
Thành viên: Lê Hiếu Kiên · Hoàng Chiến Công · Nguyễn Văn Khang

Ứng dụng web dành cho **nhân viên ban quản lý ký túc xá**. Sinh viên không tự đăng nhập: khi cần đăng ký phòng, gửi xe hoặc sử dụng dịch vụ, sinh viên đến quầy và nhân viên nhập thông tin vào hệ thống. Ứng dụng viết bằng Flask (Python), dữ liệu lưu trong MySQL.

Hai phần quan trọng nhất của tài liệu: [Hướng dẫn chạy ứng dụng]() và [Bốn truy vấn theo yêu cầu của đề]().

---

## Yêu cầu môi trường

- **Python 3.10 trở lên** (đã chạy thử trên Python 3.12 và 3.14)
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
`Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` rồi kích hoạt lại môi trường ảo.

**Bước 3. Tạo cơ sở dữ liệu**

Chạy lần lượt hai file sau (mở trong MySQL Workbench rồi bấm biểu tượng tia sét, hoặc dùng dòng lệnh):

```powershell
mysql -u root -p < KTX_phanDDL.sql
mysql -u root -p < du_lieu_mau.sql
```

- `KTX_phanDDL.sql` tạo cơ sở dữ liệu `KTX`, gồm 12 bảng và các trigger kiểm tra ràng buộc. File có thể chạy lại nhiều lần vì tự xóa phiên bản cũ trước khi tạo.
- `du_lieu_mau.sql` nạp dữ liệu mẫu gồm 6 sinh viên, 3 phòng, các lượt khách thăm, dịch vụ và xe. Ngày tháng trong dữ liệu mẫu được tính **theo ngày chạy**, nên thời điểm nào chạy cũng có số liệu để xem.

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

## Kiểm tra các ràng buộc

Ràng buộc được kiểm tra ở hai lớp. Lớp thứ nhất nằm ở giao diện, giúp tránh nhập sai. Lớp thứ hai là **trigger trong MySQL**, đóng vai trò chốt chặn cuối cùng: dù dữ liệu được gửi trực tiếp vào cơ sở dữ liệu thì trigger vẫn từ chối.

- **Phòng đã đủ người thì không xếp thêm được.** Tại trang *Phòng*, phòng P102 đang đủ 2/2 người nên chỉ hiển thị nút "Đã đầy". Có thể xếp thêm một sinh viên vào P101 cho đủ 4/4 rồi thử xếp tiếp.
- **Mỗi sinh viên đăng ký tối đa 2 xe vé tháng.** Tại trang *Xe*, chọn **Đăng ký vé**. Sinh viên Nguyễn Văn An đã có 2 xe nên không thể chọn thêm.
- **Mỗi xe được miễn phí 2 lượt gửi/lấy mỗi ngày, từ lượt thứ 3 thu 3.000đ.** Tại trang *Xe*, quét xe `29A1-12345` (hôm nay xe đã có 2 lượt). Lượt này sẽ báo thu 3.000đ. Số tiền do trigger trong MySQL tự tính, ứng dụng chỉ đọc lại kết quả.
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
├── KTX_phanDDL.sql       # tạo cơ sở dữ liệu, 12 bảng và trigger
├── du_lieu_mau.sql       # dữ liệu mẫu
├── requirements.txt      # danh sách thư viện Python
├── templates/            # giao diện HTML (Jinja2 và Bootstrap)
├── static/               # tệp CSS
└── demo_fe/              # bản demo dùng dữ liệu giả, chạy được khi chưa có MySQL
```

## Xử lý các sự cố thường gặp

    | Hiện tượng                                                    | Nguyên nhân thường gặp 

    | `Access denied for user 'root'`                               | Chưa khai báo `KTX_DB_PASSWORD` trong cửa sổ terminal đang dùng |

    | `Unknown database 'KTX'`                                      | Chưa chạy file `KTX_phanDDL.sql` |

    | Trang báo "Không làm việc được với MySQL"                     | MySQL chưa được bật, hoặc sai tài khoản, mật khẩu. Dòng thông báo kèm theo nêu rõ nguyên nhân |

    | `cryptography package is required`                            | Chạy lại `pip install -r requirements.txt` |

    | Khi chạy file SQL báo lỗi **3823** ở bảng `CHITIET_HOADON`    | Đổi ba khóa ngoại `fk_cthd_dko`, `fk_cthd_sudung`,              `fk_cthd_luotxe` từ `ON UPDATE CASCADE` thành `ON UPDATE RESTRICT` rồi chạy lại |
    
    | Không thấy số liệu ở tuần hoặc tháng khác                      | Dữ liệu mẫu chỉ trải trong khoảng hai tháng gần ngày chạy; nên chọn kỳ gần hơn |
