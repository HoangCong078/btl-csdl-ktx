from datetime import datetime, timedelta

from flask import Flask, flash, redirect, render_template, request, url_for
from markupsafe import escape
from pymysql import MySQLError

from db import LoiNghiepVu, giao_dich, ghi, kiem_tra_ket_noi, mot_dong, truy_van

app = Flask(__name__)
app.secret_key = "ktx-dev"

GIA_VE_THANG = 100000
TOI_DA_XE = 2
MIEN_PHI_NGAY = 2
PHI_PHAT_SINH = 3000
DS_LOP = ["B24CQCN01-B", "B24CQCN02-B", "B24CQCN03-B"]
DS_LOAI_PHONG = ["Thường", "Chất lượng cao"]
DS_LOAI_XE = ["Xe đạp", "Xe máy", "Xe điện"]


# ===================== HIỂN THỊ VÀ TIỆN ÍCH =====================
@app.template_filter("ngay")
def f_ngay(chuoi):
    try:
        return datetime.strptime(chuoi, "%Y-%m-%d").strftime("%d/%m/%Y")
    except (ValueError, TypeError):
        return chuoi or ""


@app.template_filter("gio")
def f_gio(chuoi):
    for dang in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(chuoi, dang).strftime("%H:%M %d/%m/%Y")
        except (ValueError, TypeError):
            pass
    return chuoi or ""


@app.template_filter("gio_giay")
def f_gio_giay(chuoi):
    try:
        return datetime.strptime(chuoi, "%Y-%m-%d %H:%M:%S").strftime("%H:%M:%S %d/%m/%Y")
    except (ValueError, TypeError):
        return chuoi or ""


@app.template_filter("tien")
def f_tien(so):
    try:
        return f"{int(so):,}".replace(",", ".") + "đ"
    except (ValueError, TypeError):
        return so


@app.errorhandler(MySQLError)
def loi_csdl(e):
    return (f"<h3>Không làm việc được với MySQL</h3><p>{escape(str(e))}</p>"
            "<p>Kiểm tra MySQL đang chạy, đã import KTX_phanDDL.sql và du_lieu_mau.sql, "
            "và biến môi trường KTX_DB_PASSWORD.</p>"), 503


def hom_nay():
    return datetime.now().strftime("%Y-%m-%d")


def hop_le_ngay(chuoi):
    try:
        datetime.strptime(chuoi, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def chuan_hoa(chuoi):
    return chuoi.strip().upper().replace(" ", "")


def doc_ky():
    bay_gio = datetime.now()
    try:
        thang = int(request.args.get("thang", bay_gio.month))
        nam = int(request.args.get("nam", bay_gio.year))
        if not (1 <= thang <= 12 and 2000 <= nam <= 2100):
            raise ValueError
    except ValueError:
        thang, nam = bay_gio.month, bay_gio.year
    return thang, nam


def danh_sach_nam(nam):
    nam_nay = datetime.now().year
    return sorted({nam_nay - 1, nam_nay, nam_nay + 1, nam})


def khoang_ky(ky, ngay_tc):
    """(từ ngày, đến ngày) của tuần (thứ Hai - Chủ nhật) hoặc tháng chứa ngay_tc."""
    if ky == "tuan":
        tu = ngay_tc - timedelta(days=ngay_tc.weekday())
        den = tu + timedelta(days=6)
    elif ky == "thang":
        tu = ngay_tc.replace(day=1)
        den = (tu + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    else:
        return None, None
    return tu.strftime("%Y-%m-%d"), den.strftime("%Y-%m-%d")


def dau_cuoi_thang(thang, nam):
    dau = datetime(nam, thang, 1)
    cuoi = (dau + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    return dau.strftime("%Y-%m-%d"), cuoi.strftime("%Y-%m-%d")


def thuc_hien(sql, tham_so, thanh_cong, loai="success"):
    """Ghi vào CSDL rồi báo kết quả. Trả về True nếu thành công."""
    try:
        ghi(sql, tham_so)
    except LoiNghiepVu as e:
        flash(str(e), "danger")
        return False
    flash(thanh_cong, loai)
    return True


# ===================== TRA CỨU DÙNG CHUNG =====================
SV_KEM_PHONG = """SELECT s.*, COALESCE(d.SoPhong, '') AS Phong FROM SINHVIEN s
                  LEFT JOIN DANGKY_O d ON d.MaSV = s.MaSV AND d.NgayKetThuc IS NULL
                  ORDER BY s.HoTen"""


def tim_sv(masv):
    return mot_dong("SELECT * FROM SINHVIEN WHERE MaSV = %s", (masv,))


def tim_phong(so_phong):
    return mot_dong("SELECT * FROM PHONG WHERE SoPhong = %s", (so_phong,))


def so_nguoi_dang_o(so_phong):
    return mot_dong("SELECT COUNT(*) AS n FROM DANGKY_O WHERE SoPhong = %s AND NgayKetThuc IS NULL",
                    (so_phong,))["n"]


def dang_ky_dang_o(masv):
    return mot_dong("SELECT * FROM DANGKY_O WHERE MaSV = %s AND NgayKetThuc IS NULL", (masv,))


# ===================== TRANG CHỦ =====================
@app.route("/")
def trang_chu():
    return redirect(url_for("sinhvien"))


# ===================== SINH VIÊN =====================
@app.route("/sinhvien", methods=["GET", "POST"])
def sinhvien():
    form = {}
    if request.method == "POST":
        form = request.form
        masv, socmt = form["MaSV"].strip(), form["SoCMT"].strip()
        if mot_dong("SELECT 1 AS x FROM SINHVIEN WHERE MaSV = %s", (masv,)):
            flash(f"Mã sinh viên {masv} đã tồn tại.", "danger")
        elif mot_dong("SELECT 1 AS x FROM SINHVIEN WHERE SoCMT = %s", (socmt,)):
            flash(f"Số CMT/CCCD {socmt} đã được dùng bởi sinh viên khác.", "danger")
        elif thuc_hien(
                "INSERT INTO SINHVIEN (MaSV, HoTen, GioiTinh, SDT, SoCMT, NgaySinh, Lop, QueQuan) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (masv, form["HoTen"].strip(), form["GioiTinh"], form["SDT"].strip() or None, socmt,
                 form["NgaySinh"] or None, form["Lop"], form["QueQuan"].strip() or None),
                "Thêm sinh viên thành công."):
            return redirect(url_for("sinhvien"))
    return render_template("sinhvien.html", ds=truy_van(SV_KEM_PHONG), ds_lop=DS_LOP, form=form)


@app.route("/sinhvien/xoa/<masv>", methods=["POST"])
def xoa_sinhvien(masv):
    if dang_ky_dang_o(masv):
        flash(f"Không thể xóa sinh viên {masv} vì đang ở phòng. Hãy trả phòng trước.", "danger")
    else:
        try:
            ghi("DELETE FROM SINHVIEN WHERE MaSV = %s", (masv,))
            flash(f"Đã xóa sinh viên {masv}.", "warning")
        except LoiNghiepVu:
            flash(f"Không thể xóa {masv}: sinh viên đã có lịch sử (ở, dịch vụ, xe, hóa đơn).", "danger")
    return redirect(url_for("sinhvien"))


# ===================== PHÒNG (gồm xếp người, trả phòng) =====================
@app.route("/phong", methods=["GET", "POST"])
def phong():
    form = {}
    if request.method == "POST":
        form = request.form
        so_phong = form["SoPhong"].strip().upper()
        try:
            don_gia, toi_da = int(form["DonGia"]), int(form["SoNguoiToiDa"])
        except ValueError:
            don_gia = toi_da = 0
            flash("Đơn giá và số người tối đa phải là số nguyên.", "danger")
        if don_gia and toi_da:
            if tim_phong(so_phong):
                flash(f"Phòng {so_phong} đã tồn tại.", "danger")
            elif don_gia <= 0 or toi_da <= 0:
                flash("Đơn giá và số người tối đa phải lớn hơn 0.", "danger")
            elif thuc_hien("INSERT INTO PHONG (SoPhong, LoaiPhong, DonGia, SoNguoiToiDa) VALUES (%s, %s, %s, %s)",
                           (so_phong, form["LoaiPhong"], don_gia, toi_da), f"Đã thêm phòng {so_phong}."):
                return redirect(url_for("phong"))

    o = truy_van("SELECT d.MaDKO, d.MaSV, d.SoPhong, s.HoTen FROM DANGKY_O d "
                 "JOIN SINHVIEN s ON s.MaSV = d.MaSV WHERE d.NgayKetThuc IS NULL ORDER BY s.HoTen")
    ds = []
    for p in truy_van("SELECT * FROM PHONG ORDER BY SoPhong"):
        nguoi = [n for n in o if n["SoPhong"] == p["SoPhong"]]
        ds.append({**p, "Nguoi": nguoi, "DangO": len(nguoi)})
    ds_sv_trong = truy_van("SELECT s.* FROM SINHVIEN s WHERE NOT EXISTS (SELECT 1 FROM DANGKY_O d "
                           "WHERE d.MaSV = s.MaSV AND d.NgayKetThuc IS NULL) ORDER BY s.HoTen")
    return render_template("phong.html", ds=ds, ds_loai=DS_LOAI_PHONG, ds_sv_trong=ds_sv_trong,
                           form=form, hom_nay=hom_nay())


@app.route("/phong/xoa/<so_phong>", methods=["POST"])
def xoa_phong(so_phong):
    if so_nguoi_dang_o(so_phong) > 0:
        flash(f"Không thể xóa phòng {so_phong} vì đang có người ở.", "danger")
    else:
        try:
            ghi("DELETE FROM PHONG WHERE SoPhong = %s", (so_phong,))
            flash(f"Đã xóa phòng {so_phong}.", "warning")
        except LoiNghiepVu:
            flash(f"Không thể xóa {so_phong}: phòng đã có lịch sử đăng ký ở.", "danger")
    return redirect(url_for("phong"))


@app.route("/phong/xep", methods=["POST"])
def xep_phong():
    masv, so_phong, ngay = request.form["MaSV"], request.form["SoPhong"], request.form["NgayBatDau"]
    sv, p = tim_sv(masv), tim_phong(so_phong)
    loi = None
    if not hop_le_ngay(ngay):
        loi = "Ngày bắt đầu không hợp lệ."
    elif sv is None:
        loi = "Không tìm thấy sinh viên đã chọn."
    elif p is None:
        loi = "Không tìm thấy phòng đã chọn."
    elif dang_ky_dang_o(masv):
        loi = f"{sv['HoTen']} đang ở phòng {dang_ky_dang_o(masv)['SoPhong']}. Hãy trả phòng cũ trước."
    elif so_nguoi_dang_o(so_phong) >= p["SoNguoiToiDa"]:
        loi = f"Phòng {so_phong} đã đủ {p['SoNguoiToiDa']}/{p['SoNguoiToiDa']} người."
    if loi:
        flash(loi, "danger")
    else:   # trigger trg_dangky_o_bi kiểm tra lại một lần nữa ở phía CSDL
        thuc_hien("INSERT INTO DANGKY_O (MaSV, SoPhong, NgayBatDau, NgayKetThuc, DonGiaThangApDung) "
                  "VALUES (%s, %s, %s, NULL, %s)", (masv, so_phong, ngay, p["DonGia"]),
                  f"Đã xếp {sv['HoTen']} vào phòng {so_phong}.")
    return redirect(url_for("phong"))


@app.route("/phong/tra/<int:ma_dko>", methods=["POST"])
def tra_phong(ma_dko):
    thuc_hien("UPDATE DANGKY_O SET NgayKetThuc = GREATEST(CURDATE(), NgayBatDau) "
              "WHERE MaDKO = %s AND NgayKetThuc IS NULL", (ma_dko,), "Đã trả phòng.", "warning")
    return redirect(url_for("phong"))


# ===================== KHÁCH THĂM =====================
@app.route("/khach", methods=["GET", "POST"])
def khach():
    form = {}
    if request.method == "POST":
        form = request.form
        cmt, masv = form["CMTKhach"].strip(), form["MaSV"]
        thoi_diem = form["ThoiDiemDen"].replace("T", " ")
        da_co = mot_dong("SELECT 1 AS x FROM KHACH WHERE CMTKhach = %s", (cmt,)) is not None
        loi = None
        try:
            datetime.strptime(thoi_diem, "%Y-%m-%d %H:%M")
        except ValueError:
            loi = "Thời điểm đến không hợp lệ."
        if loi is None and tim_sv(masv) is None:
            loi = "Không tìm thấy sinh viên được thăm."
        if loi is None and not da_co and (not form["HoTen"].strip() or not form["NgaySinh"]):
            loi = "Khách mới cần nhập đủ họ tên và ngày sinh."
        if loi:
            flash(loi, "danger")
        else:
            def luu(cur):
                if not da_co:
                    cur.execute("INSERT INTO KHACH (CMTKhach, HoTen, NgaySinh, SDT) VALUES (%s, %s, %s, %s)",
                                (cmt, form["HoTen"].strip(), form["NgaySinh"], form["SDT"].strip() or None))
                cur.execute("INSERT INTO LUOT_THAM (CMTKhach, MaSV, ThoiDiemDen) VALUES (%s, %s, %s)",
                            (cmt, masv, thoi_diem))
            try:
                giao_dich(luu)
                flash("Đã ghi nhận lượt thăm.", "success")
                return redirect(url_for("khach"))
            except LoiNghiepVu as e:
                flash(str(e), "danger")

    ky = request.args.get("ky", "tuan")
    if ky not in ("tuan", "thang", "tatca"):
        ky = "tuan"
    bay_gio = datetime.now()
    try:
        ngay_tc = datetime.strptime(request.args.get("ngay", ""), "%Y-%m-%d")
    except ValueError:
        ngay_tc = bay_gio
    tu, den = khoang_ky(ky, ngay_tc)
    dieu_kien, tham_so = ("WHERE DATE(l.ThoiDiemDen) BETWEEN %s AND %s", (tu, den)) if tu else ("", ())

    tu_khoa = ("FROM LUOT_THAM l JOIN KHACH k ON k.CMTKhach = l.CMTKhach "
               "JOIN SINHVIEN s ON s.MaSV = l.MaSV ")
    # Truy vấn 3 của đề: sinh viên, khách đến thăm và số lần mỗi khách đến
    ds_thongke = truy_van(
        "SELECT l.MaSV, s.HoTen AS HoTenSV, s.Lop, l.CMTKhach, k.HoTen AS HoTenKhach, "
        "COUNT(*) AS SoLan, MAX(l.ThoiDiemDen) AS LanCuoi " + tu_khoa + dieu_kien +
        " GROUP BY l.MaSV, s.HoTen, s.Lop, l.CMTKhach, k.HoTen ORDER BY l.MaSV, SoLan DESC", tham_so)
    ds_chitiet = truy_van(
        "SELECT l.MaLuotTham, l.ThoiDiemDen, l.CMTKhach, l.MaSV, k.HoTen AS HoTenKhach, s.HoTen AS HoTenSV "
        + tu_khoa + dieu_kien + " ORDER BY l.ThoiDiemDen DESC", tham_so)

    return render_template("khach.html", form=form, ds_sv=truy_van("SELECT * FROM SINHVIEN ORDER BY HoTen"),
                           ds_khach=truy_van("SELECT * FROM KHACH ORDER BY HoTen"),
                           ds_thongke=ds_thongke, ds_chitiet=ds_chitiet, ky=ky,
                           ngay=ngay_tc.strftime("%Y-%m-%d"), tu=tu, den=den,
                           so_khach=len({d["CMTKhach"] for d in ds_chitiet}),
                           so_sv=len({d["MaSV"] for d in ds_chitiet}),
                           bay_gio=bay_gio.strftime("%Y-%m-%dT%H:%M"))

# ===================== DỊCH VỤ =====================
@app.route("/dichvu", methods=["GET", "POST"])
def dichvu():
    form = {}
    if request.method == "POST":
        form = request.form
        masv, madv = form["MaSV"], form["MaDV"]
        thoi_diem = form["ThoiDiemSuDung"].replace("T", " ")
        dv = mot_dong("SELECT * FROM DICHVU WHERE MaDV = %s", (madv,))
        loi = None
        try:
            so_luong = int(form["SoLuong"])
            if so_luong <= 0:
                loi = "Số lượng phải lớn hơn 0."
        except ValueError:
            loi = "Số lượng phải là số nguyên."
        if loi is None:
            try:
                datetime.strptime(thoi_diem, "%Y-%m-%d %H:%M")
            except ValueError:
                loi = "Thời điểm sử dụng không hợp lệ."
        if loi is None and tim_sv(masv) is None:
            loi = "Không tìm thấy sinh viên đã chọn."
        if loi is None and dv is None:
            loi = "Không tìm thấy dịch vụ đã chọn."
        if loi:
            flash(loi, "danger")
        elif thuc_hien(   # đơn giá lấy từ danh mục dịch vụ tại thời điểm ghi nhận
                "INSERT INTO SUDUNG_DV (MaSV, MaDV, ThoiDiemSuDung, SoLuong, DonGiaApDung) "
                "VALUES (%s, %s, %s, %s, %s)", (masv, madv, thoi_diem, so_luong, dv["DonGia"]),
                f"Đã ghi nhận: {dv['TenDV']} x {so_luong}."):
            return redirect(url_for("dichvu"))

    tu = request.args.get("tu", (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
    den = request.args.get("den", hom_nay())
    loc_phong, loc_lop = request.args.get("phong", ""), request.args.get("lop", "")
    if not (hop_le_ngay(tu) and hop_le_ngay(den)):
        tu, den = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"), hom_nay()
    if tu > den:
        flash("Ngày bắt đầu phải không muộn hơn ngày kết thúc.", "danger")
        tu, den = den, tu

    dieu_kien, tham_so = "DATE(u.ThoiDiemSuDung) BETWEEN %s AND %s", [tu, den]
    if loc_phong:
        dieu_kien += " AND d.SoPhong = %s"
        tham_so.append(loc_phong)
    if loc_lop:
        dieu_kien += " AND s.Lop = %s"
        tham_so.append(loc_lop)
    # Truy vấn 2 của đề: sinh viên, tên dịch vụ, tổng tiền mỗi dịch vụ trong khoảng ngày
    ds_thongke = truy_van(
        "SELECT s.MaSV, s.HoTen AS HoTenSV, s.Lop, COALESCE(d.SoPhong, '—') AS Phong, v.TenDV, v.DonViTinh, "
        "SUM(u.SoLuong) AS SoLuong, SUM(u.SoLuong * u.DonGiaApDung) AS TongTien "
        "FROM SUDUNG_DV u JOIN SINHVIEN s ON s.MaSV = u.MaSV JOIN DICHVU v ON v.MaDV = u.MaDV "
        "LEFT JOIN DANGKY_O d ON d.MaSV = s.MaSV AND d.NgayKetThuc IS NULL "
        "WHERE " + dieu_kien +
        " GROUP BY s.MaSV, s.HoTen, s.Lop, d.SoPhong, v.MaDV, v.TenDV, v.DonViTinh "
        "ORDER BY Phong, s.MaSV, v.TenDV", tham_so)
    ds_gan_day = truy_van(
        "SELECT u.MaSuDung, u.ThoiDiemSuDung, u.SoLuong, u.SoLuong * u.DonGiaApDung AS ThanhTien, "
        "s.HoTen AS HoTenSV, v.TenDV FROM SUDUNG_DV u JOIN SINHVIEN s ON s.MaSV = u.MaSV "
        "JOIN DICHVU v ON v.MaDV = u.MaDV ORDER BY u.ThoiDiemSuDung DESC LIMIT 8")
    return render_template("dichvu.html", form=form, ds_sv=truy_van(SV_KEM_PHONG),
                           ds_dichvu=truy_van("SELECT * FROM DICHVU ORDER BY MaDV"),
                           ds_phong=[p["SoPhong"] for p in truy_van("SELECT SoPhong FROM PHONG ORDER BY SoPhong")],
                           ds_lop=DS_LOP, ds_thongke=ds_thongke, ds_gan_day=ds_gan_day, tu=tu, den=den,
                           loc_phong=loc_phong, loc_lop=loc_lop,
                           tong_tien=sum(d["TongTien"] for d in ds_thongke),
                           bay_gio=datetime.now().strftime("%Y-%m-%dT%H:%M"))


@app.route("/dichvu/xoa/<int:ma>", methods=["POST"])
def xoa_luot_dung(ma):
    thuc_hien("DELETE FROM SUDUNG_DV WHERE MaSuDung = %s", (ma,), f"Đã xóa lượt sử dụng #{ma}.", "warning")
    return redirect(url_for("dichvu"))


# ===================== XE (vé tháng + quẹt xe) =====================
def con_han(d, ngay=None):
    """Vé còn hiệu lực khi ngày nằm trong [NgayBatDau, NgayKetThuc]; NgayKetThuc NULL = chưa hủy."""
    ngay = ngay or hom_nay()
    return d["NgayBatDau"] <= ngay <= (d["NgayKetThuc"] or "9999-12-31")


def dem_xe_hieu_luc(masv):
    return sum(1 for d in truy_van("SELECT * FROM DANGKY_XE_THANG WHERE MaSV = %s", (masv,)) if con_han(d))


def ve_con_han_cua_bien(bien_so):
    return next((d for d in truy_van("SELECT * FROM DANGKY_XE_THANG WHERE BienSo = %s", (bien_so,))
                 if con_han(d)), None)


def tao_ma_xe_dap(masv):
    """Xe đạp không có biển số: dùng mã sinh viên làm mã xe (XD-<MaSV>)."""
    ma = f"XD-{masv}"
    return ma + "-2" if ve_con_han_cua_bien(ma) else ma


def luot_trong_ngay(ma_dkxe, ngay):
    return mot_dong("SELECT COUNT(*) AS n FROM LUOT_RA_VAO_XE WHERE MaDKXe = %s AND DATE(ThoiDiem) = %s",
                    (ma_dkxe, ngay))["n"]


def hanh_dong_tiep(ma_dkxe):
    """Lượt đầu của xe là Gửi, sau đó luân phiên Lấy / Gửi."""
    r = mot_dong("SELECT LoaiHanhDong FROM LUOT_RA_VAO_XE WHERE MaDKXe = %s "
                 "ORDER BY ThoiDiem DESC, MaLuot DESC LIMIT 1", (ma_dkxe,))
    return "Gui" if r is None or r["LoaiHanhDong"] == "Lay" else "Lay"


def phi_luot_tiep(ma_dkxe, ngay):
    return PHI_PHAT_SINH if luot_trong_ngay(ma_dkxe, ngay) >= MIEN_PHI_NGAY else 0


def nhan_dien_xe(ma_quet):
    """Camera quét biển số, hoặc thẻ sinh viên (xe đạp). Trả về (vé tháng, lỗi)."""
    ma = chuan_hoa(ma_quet)
    if not ma:
        return None, "Chưa nhận được mã quét."
    ve = truy_van("SELECT v.*, x.LoaiXe FROM DANGKY_XE_THANG v JOIN XE x ON x.BienSo = v.BienSo")
    for d in ve:
        if chuan_hoa(d["BienSo"]) == ma and con_han(d):
            return d, None
    if any(chuan_hoa(d["BienSo"]) == ma for d in ve):
        return None, f"Vé tháng của xe {ma_quet.strip()} đã bị hủy, cần đăng ký lại."
    sv = mot_dong("SELECT MaSV FROM SINHVIEN WHERE UPPER(MaSV) = %s", (ma,))
    if sv:
        xe_dap = [d for d in ve if d["MaSV"] == sv["MaSV"] and con_han(d) and d["LoaiXe"] == "Xe đạp"]
        if not xe_dap:
            return None, f"Sinh viên {sv['MaSV']} không có xe đạp vé tháng còn hiệu lực."
        return min(xe_dap, key=lambda d: d["MaDKXe"]), None
    return None, (f"Không nhận diện được '{ma_quet.strip()}': không phải xe vé tháng. "
                  "Xe vãng lai thu tiền trực tiếp, không lưu hệ thống.")


@app.route("/xe")
def xe():
    hn = hom_nay()
    ve = truy_van("SELECT v.*, s.HoTen, x.LoaiXe FROM DANGKY_XE_THANG v "
                  "JOIN SINHVIEN s ON s.MaSV = v.MaSV JOIN XE x ON x.BienSo = v.BienSo")
    bien_con_han = {d["BienSo"] for d in ve if con_han(d)}
    ds_ve = [{**d, "ConHan": con_han(d), "DaCoVeMoi": d["BienSo"] in bien_con_han,
              "SoLuot": luot_trong_ngay(d["MaDKXe"], hn),
              "TiepTheo": "Gửi" if hanh_dong_tiep(d["MaDKXe"]) == "Gui" else "Lấy",
              "PhiTiep": phi_luot_tiep(d["MaDKXe"], hn)} for d in ve]
    ds_ve.sort(key=lambda d: (not d["ConHan"], -d["MaDKXe"]))

    ds_sv = truy_van(
        "SELECT s.*, COALESCE(d.SoPhong, '') AS Phong, "
        "(SELECT COUNT(*) FROM DANGKY_XE_THANG v WHERE v.MaSV = s.MaSV AND v.NgayBatDau <= CURDATE() "
        "AND COALESCE(v.NgayKetThuc, '9999-12-31') >= CURDATE()) AS SoXe "
        "FROM SINHVIEN s LEFT JOIN DANGKY_O d ON d.MaSV = s.MaSV AND d.NgayKetThuc IS NULL ORDER BY s.HoTen")
    ds_gan_day = truy_van(
        "SELECT l.MaLuot, l.ThoiDiem, l.LoaiHanhDong, l.PhiPhatSinh, v.BienSo, s.HoTen "
        "FROM LUOT_RA_VAO_XE l JOIN DANGKY_XE_THANG v ON v.MaDKXe = l.MaDKXe "
        "JOIN SINHVIEN s ON s.MaSV = v.MaSV ORDER BY l.ThoiDiem DESC, l.MaLuot DESC LIMIT 8")
    return render_template("xe.html", ds_ve=ds_ve, ds_sv=ds_sv, ds_gan_day=ds_gan_day,
                           ds_phong=[p["SoPhong"] for p in truy_van("SELECT SoPhong FROM PHONG ORDER BY SoPhong")],
                           ds_lop=DS_LOP, ds_loai=DS_LOAI_XE, toi_da=TOI_DA_XE, gia=GIA_VE_THANG,
                           mien_phi=MIEN_PHI_NGAY, phi=PHI_PHAT_SINH, hom_nay=hn)


@app.route("/xe/quet", methods=["POST"])
def quet_xe():
    d, loi = nhan_dien_xe(request.form.get("MaQuet", ""))
    if loi:
        flash(loi, "danger")
        return redirect(url_for("xe"))
    bay_gio = datetime.now()
    hanh_dong = hanh_dong_tiep(d["MaDKXe"])
    thu_tu = luot_trong_ngay(d["MaDKXe"], bay_gio.strftime("%Y-%m-%d")) + 1
    try:   # phí 0đ / 3.000đ do trigger trg_luot_xe_bi tự tính, app chỉ đọc lại
        _, ma_moi = ghi("INSERT INTO LUOT_RA_VAO_XE (MaDKXe, ThoiDiem, LoaiHanhDong, PhiPhatSinh) "
                        "VALUES (%s, %s, %s, 0)", (d["MaDKXe"], bay_gio.strftime("%Y-%m-%d %H:%M:%S"), hanh_dong))
    except LoiNghiepVu as e:
        flash(str(e), "danger")
        return redirect(url_for("xe"))
    phi = mot_dong("SELECT PhiPhatSinh FROM LUOT_RA_VAO_XE WHERE MaLuot = %s", (ma_moi,))["PhiPhatSinh"]
    ten = (tim_sv(d["MaSV"]) or {}).get("HoTen", d["MaSV"])
    ten_hd = "GỬI" if hanh_dong == "Gui" else "LẤY"
    if phi:
        flash(f"{ten_hd} xe {d['BienSo']} ({ten}) - lượt {thu_tu} trong ngày, thu {f_tien(phi)}.", "warning")
    else:
        flash(f"{ten_hd} xe {d['BienSo']} ({ten}) - lượt {thu_tu} trong ngày, miễn phí.", "success")
    return redirect(url_for("xe"))


@app.route("/xe/dangky", methods=["POST"])
def xe_thang():
    form = request.form
    masv, loai, ngay = form.get("MaSV", ""), form.get("LoaiXe", ""), form.get("NgayBatDau", "")
    bien_so = form.get("BienSo", "").strip().upper()
    if loai == "Xe đạp":
        bien_so = tao_ma_xe_dap(masv)
    loi = None
    if not hop_le_ngay(ngay):
        loi = "Ngày bắt đầu không hợp lệ."
    elif ngay > hom_nay():
        loi = "Ngày bắt đầu không được ở tương lai."
    elif tim_sv(masv) is None:
        loi = "Không tìm thấy sinh viên đã chọn."
    elif not bien_so:
        loi = "Vui lòng nhập biển số xe."
    elif loai not in DS_LOAI_XE:
        loi = "Loại xe không hợp lệ."
    elif dem_xe_hieu_luc(masv) >= TOI_DA_XE:
        loi = f"Sinh viên {masv} đã đủ {TOI_DA_XE}/{TOI_DA_XE} xe vé tháng."
    elif ve_con_han_cua_bien(bien_so):
        loi = f"Xe {bien_so} đang có vé còn hạn của {ve_con_han_cua_bien(bien_so)['MaSV']}."
    if loi:
        flash(loi, "danger")
        return redirect(url_for("xe"))

    def luu(cur):   # trigger trg_dangky_xe_bi kiểm tra lại tối đa 2 xe và trùng biển số
        cur.execute("INSERT IGNORE INTO XE (BienSo, LoaiXe) VALUES (%s, %s)", (bien_so, loai))
        cur.execute("INSERT INTO DANGKY_XE_THANG (MaSV, BienSo, NgayBatDau, NgayKetThuc, DonGiaThangApDung) "
                    "VALUES (%s, %s, %s, NULL, %s)", (masv, bien_so, ngay, GIA_VE_THANG))
    try:
        giao_dich(luu)
        flash(f"Đã đăng ký vé tháng cho xe {bien_so}.", "success")
    except LoiNghiepVu as e:
        flash(str(e), "danger")
    return redirect(url_for("xe"))


@app.route("/xe/huy/<int:ma>", methods=["POST"])
def huy_xe(ma):
    thuc_hien("UPDATE DANGKY_XE_THANG SET NgayKetThuc = GREATEST(CURDATE(), NgayBatDau) "
              "WHERE MaDKXe = %s AND NgayKetThuc IS NULL", (ma,), "Đã hủy vé tháng.", "warning")
    return redirect(url_for("xe"))


@app.route("/xe/xoa/<int:ma>", methods=["POST"])
def xoa_luot_xe(ma):   # trigger trg_luot_xe_bd chỉ cho xóa lượt cuối cùng trong ngày
    thuc_hien("DELETE FROM LUOT_RA_VAO_XE WHERE MaLuot = %s", (ma,), f"Đã xóa lượt quét #{ma}.", "warning")
    return redirect(url_for("xe"))


# ===================== HÓA ĐƠN (truy vấn 1 của đề) =====================
def khoan_thu(masv, thang, nam):
    """Các khoản thu của một sinh viên trong tháng, mỗi khoản gắn với bản ghi nguồn."""
    dau, cuoi = dau_cuoi_thang(thang, nam)
    kq = []
    # 1) Tiền phòng chẵn tháng: bản đăng ký nào giao với tháng thì tính đủ đơn giá tháng
    for r in truy_van("SELECT MaDKO, SoPhong, DonGiaThangApDung FROM DANGKY_O WHERE MaSV = %s "
                      "AND NgayBatDau <= %s AND COALESCE(NgayKetThuc, '9999-12-31') >= %s", (masv, cuoi, dau)):
        kq.append({"Loai": "Phong", "DienGiai": f"Tiền phòng {r['SoPhong']} (tính chẵn tháng)",
                   "SoLuong": 1, "DonGia": r["DonGiaThangApDung"], "MaDKO": r["MaDKO"]})
    # 2) Dịch vụ
    for r in truy_van("SELECT u.MaSuDung, u.SoLuong, u.DonGiaApDung, v.TenDV, v.DonViTinh FROM SUDUNG_DV u "
                      "JOIN DICHVU v ON v.MaDV = u.MaDV WHERE u.MaSV = %s "
                      "AND DATE(u.ThoiDiemSuDung) BETWEEN %s AND %s ORDER BY u.ThoiDiemSuDung", (masv, dau, cuoi)):
        kq.append({"Loai": "DichVu", "DienGiai": f"Dịch vụ {r['TenDV']} ({r['DonViTinh'] or ''})",
                   "SoLuong": r["SoLuong"], "DonGia": r["DonGiaApDung"], "MaSuDung": r["MaSuDung"]})
    # 3) Vé tháng xe: mỗi tháng vé còn hiệu lực thì tính 1 lần (giống tiền phòng)
    for r in truy_van("SELECT BienSo, DonGiaThangApDung FROM DANGKY_XE_THANG WHERE MaSV = %s "
                      "AND NgayBatDau <= %s AND COALESCE(NgayKetThuc, '9999-12-31') >= %s", (masv, cuoi, dau)):
        kq.append({"Loai": "XeThang", "DienGiai": f"Vé tháng xe {r['BienSo']}",
                   "SoLuong": 1, "DonGia": r["DonGiaThangApDung"]})
    # 4) Phí gửi/lấy xe phát sinh (từ lượt thứ 3 trong ngày)
    for r in truy_van("SELECT l.MaLuot, l.PhiPhatSinh FROM LUOT_RA_VAO_XE l "
                      "JOIN DANGKY_XE_THANG v ON v.MaDKXe = l.MaDKXe WHERE v.MaSV = %s AND l.PhiPhatSinh > 0 "
                      "AND DATE(l.ThoiDiem) BETWEEN %s AND %s", (masv, dau, cuoi)):
        kq.append({"Loai": "XePhatSinh", "DienGiai": "Phí gửi/lấy xe phát sinh",
                   "SoLuong": 1, "DonGia": r["PhiPhatSinh"], "MaLuot": r["MaLuot"]})
    for k in kq:
        k["ThanhTien"] = k["SoLuong"] * k["DonGia"]
    return kq


def tinh_hoa_don(masv, thang, nam):
    """(các dòng hiển thị đã gộp, tổng theo từng loại)."""
    khoan = khoan_thu(masv, thang, nam)
    ct, nhom = [], {}
    for k in khoan:
        if k["Loai"] in ("DichVu", "XePhatSinh"):   # gộp các lượt cùng dịch vụ thành một dòng
            g = nhom.setdefault(k["DienGiai"], {"DienGiai": k["DienGiai"], "SoLuong": 0, "ThanhTien": 0})
            g["SoLuong"] += k["SoLuong"]
            g["ThanhTien"] += k["ThanhTien"]
        else:
            ct.append(k)
    ct += list(nhom.values())

    def cong(loai):
        return sum(k["ThanhTien"] for k in khoan if k["Loai"] == loai)
    tong = {"TienPhong": cong("Phong"), "TienDV": cong("DichVu"),
            "TienVe": cong("XeThang"), "TienPhi": cong("XePhatSinh")}
    tong["Tong"] = sum(tong.values())
    return ct, tong


def chot_hoa_don(masv, thang, nam, da_thanh_toan):
    """Ghi hóa đơn và các dòng chi tiết vào HOADON / CHITIET_HOADON. TongTien do trigger cộng dồn."""
    khoan = khoan_thu(masv, thang, nam)

    def luu(cur):
        cur.execute("INSERT INTO HOADON (MaSV, Thang, Nam, TrangThai) VALUES (%s, %s, %s, %s)",
                    (masv, thang, nam, "DaThanhToan" if da_thanh_toan else "ChuaThanhToan"))
        ma_hd = cur.lastrowid
        for k in khoan:
            cur.execute("INSERT INTO CHITIET_HOADON (MaHD, LoaiPhi, DienGiai, SoLuong, DonGiaApDung, "
                        "MaDKO, MaSuDung, MaLuot) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                        (ma_hd, k["Loai"], k["DienGiai"], k["SoLuong"], k["DonGia"],
                         k.get("MaDKO"), k.get("MaSuDung"), k.get("MaLuot")))
    giao_dich(luu)


def hoa_don_da_thu(thang, nam):
    return {r["MaSV"] for r in truy_van("SELECT MaSV FROM HOADON WHERE Thang = %s AND Nam = %s "
                                        "AND TrangThai = 'DaThanhToan'", (thang, nam))}


@app.route("/hoadon")
def hoadon():
    thang, nam = doc_ky()
    loc_phong, loc_lop = request.args.get("phong", ""), request.args.get("lop", "")
    da_thu_set = hoa_don_da_thu(thang, nam)
    ds = []
    for sv in truy_van(SV_KEM_PHONG):
        if (loc_phong and sv["Phong"] != loc_phong) or (loc_lop and sv["Lop"] != loc_lop):
            continue
        _, tong = tinh_hoa_don(sv["MaSV"], thang, nam)
        if tong["Tong"] == 0:
            continue
        ds.append({**sv, "Phong": sv["Phong"] or "—", **tong, "DaThu": sv["MaSV"] in da_thu_set})
    tong_cong = sum(d["Tong"] for d in ds)
    da_thu = sum(d["Tong"] for d in ds if d["DaThu"])
    return render_template("hoadon.html", ds=ds, thang=thang, nam=nam, ds_nam=danh_sach_nam(nam),
                           ds_phong=[p["SoPhong"] for p in truy_van("SELECT SoPhong FROM PHONG ORDER BY SoPhong")],
                           ds_lop=DS_LOP, loc_phong=loc_phong, loc_lop=loc_lop,
                           tong_cong=tong_cong, da_thu=da_thu, chua_thu=tong_cong - da_thu)


@app.route("/hoadon/<masv>")
def hoadon_chitiet(masv):
    sv = tim_sv(masv)
    if sv is None:
        flash("Không tìm thấy sinh viên.", "danger")
        return redirect(url_for("hoadon"))
    thang, nam = doc_ky()
    ct, tong = tinh_hoa_don(masv, thang, nam)
    p = dang_ky_dang_o(masv)
    return render_template("hoadon_chitiet.html", sv=sv, ct=ct, tong=tong, thang=thang, nam=nam,
                           phong=p["SoPhong"] if p else "—", da_thu=masv in hoa_don_da_thu(thang, nam))


@app.route("/hoadon/<masv>/thu", methods=["POST"])
def hoadon_thu(masv):
    try:
        thang, nam = int(request.form["thang"]), int(request.form["nam"])
    except (KeyError, ValueError):
        flash("Thiếu thông tin tháng/năm.", "danger")
        return redirect(url_for("hoadon"))
    hd = mot_dong("SELECT MaHD, TrangThai FROM HOADON WHERE MaSV = %s AND Thang = %s AND Nam = %s",
                  (masv, thang, nam))
    if hd is None:   # chưa có hóa đơn: chốt hóa đơn (ghi các dòng chi tiết) và đánh dấu đã thu
        try:
            chot_hoa_don(masv, thang, nam, True)
            flash(f"Đã chốt và ghi nhận thu tiền tháng {thang}/{nam} của {masv}.", "success")
        except LoiNghiepVu as e:
            flash(str(e), "danger")
    elif hd["TrangThai"] == "DaThanhToan":
        thuc_hien("UPDATE HOADON SET TrangThai = 'ChuaThanhToan' WHERE MaHD = %s", (hd["MaHD"],),
                  "Đã bỏ đánh dấu đã thu.", "warning")
    else:
        thuc_hien("UPDATE HOADON SET TrangThai = 'DaThanhToan' WHERE MaHD = %s", (hd["MaHD"],),
                  f"Đã ghi nhận thu tiền tháng {thang}/{nam} của {masv}.")
    return redirect(url_for("hoadon_chitiet", masv=masv, thang=thang, nam=nam))


# ===================== DOANH THU DỊCH VỤ (truy vấn 4 của đề) =====================
@app.route("/doanhthu")
def doanhthu():
    bay_gio = datetime.now()
    try:
        nam = int(request.args.get("nam", bay_gio.year))
        if not 2000 <= nam <= 2100:
            raise ValueError
    except ValueError:
        nam = bay_gio.year
    rows = truy_van(
        "SELECT v.MaDV, v.TenDV, v.DonViTinh, MONTH(u.ThoiDiemSuDung) AS Thang, "
        "SUM(u.SoLuong * u.DonGiaApDung) AS Tien FROM DICHVU v "
        "LEFT JOIN SUDUNG_DV u ON u.MaDV = v.MaDV AND YEAR(u.ThoiDiemSuDung) = %s "
        "GROUP BY v.MaDV, v.TenDV, v.DonViTinh, MONTH(u.ThoiDiemSuDung) ORDER BY v.MaDV", (nam,))
    hang_theo_ma, tong_thang = {}, [0] * 12
    for r in rows:
        h = hang_theo_ma.setdefault(r["MaDV"], {"MaDV": r["MaDV"], "TenDV": r["TenDV"],
                                                "DonViTinh": r["DonViTinh"], "Thang": [0] * 12})
        if r["Thang"]:
            h["Thang"][r["Thang"] - 1] = r["Tien"]
            tong_thang[r["Thang"] - 1] += r["Tien"]
    hang = list(hang_theo_ma.values())
    for h in hang:
        h["Tong"] = sum(h["Thang"])
    return render_template("doanhthu.html", hang=hang, tong_thang=tong_thang, tong_nam=sum(tong_thang),
                           nam=nam, ds_nam=danh_sach_nam(nam),
                           thang_ht=bay_gio.month if nam == bay_gio.year else 0)


if __name__ == "__main__":
    loi = kiem_tra_ket_noi()
    if loi:
        print("CẢNH BÁO: chưa kết nối được MySQL:", loi)
    app.run(debug=True)