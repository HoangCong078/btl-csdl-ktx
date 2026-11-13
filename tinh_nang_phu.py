"""Tính năng phụ của ứng dụng KTX. Gắn vào app.py bằng 2 dòng, không sửa logic có sẵn.
Cần các tên sau có sẵn trong app.py: tinh_hoa_don, doc_ky."""
import csv
import io
import time
import zipfile
from datetime import datetime

from flask import Response, abort, flash, redirect, render_template, request, send_file, url_for

from db import LoiNghiepVu, ghi, mot_dong, truy_van

# Tên bảng chỉ lấy từ danh sách cố định này, không bao giờ lấy từ dữ liệu người dùng gửi lên
BANG_XUAT = [
    ("sinhvien", "SINHVIEN", "Hồ sơ sinh viên"),
    ("phong", "PHONG", "Danh mục phòng"),
    ("dangky_o", "DANGKY_O", "Lịch sử đăng ký ở"),
    ("khach", "KHACH", "Khách đến thăm"),
    ("luot_tham", "LUOT_THAM", "Các lượt thăm"),
    ("dichvu", "DICHVU", "Danh mục dịch vụ"),
    ("sudung_dv", "SUDUNG_DV", "Các lượt dùng dịch vụ"),
    ("xe", "XE", "Danh mục xe"),
    ("dangky_xe", "DANGKY_XE_THANG", "Vé tháng gửi xe"),
    ("luot_xe", "LUOT_RA_VAO_XE", "Các lượt gửi/lấy xe"),
    ("hoadon", "HOADON", "Hóa đơn"),
    ("chitiet_hoadon", "CHITIET_HOADON", "Chi tiết hóa đơn"),
]
TEN_BANG = {khoa: bang for khoa, bang, _ in BANG_XUAT}
HAN_CACHE_GIAY = 30


def _hom_nay():
    return datetime.now().strftime("%Y-%m-%d")


def _csv_cua_bang(bang):
    """Nội dung CSV (có BOM để Excel đọc đúng tiếng Việt)."""
    cot = [c["Field"] for c in truy_van(f"SHOW COLUMNS FROM {bang}")]
    bo_nho = io.StringIO()
    viet = csv.writer(bo_nho)
    viet.writerow(cot)
    for d in truy_van(f"SELECT * FROM {bang}"):
        viet.writerow(["" if d[c] is None else d[c] for c in cot])
    return "\ufeff" + bo_nho.getvalue()


def dang_ky(app, ctx):
    tinh_hoa_don = ctx["tinh_hoa_don"]
    doc_ky = ctx["doc_ky"]

    # ============ CẢNH BÁO (huy hiệu trên menu) ============
    cache = {"luc": 0.0, "gia_tri": {"hoadon": 0, "tien": 0, "phong": 0}}

    def tinh_canh_bao():
        if time.time() - cache["luc"] < HAN_CACHE_GIAY:
            return cache["gia_tri"]
        bay_gio = datetime.now()
        kq = {"hoadon": 0, "tien": 0, "phong": 0}
        try:   # cảnh báo chỉ là phụ, lỗi ở đây không được làm hỏng cả trang
            da_thu = {r["MaSV"] for r in truy_van(
                "SELECT MaSV FROM HOADON WHERE Thang = %s AND Nam = %s AND TrangThai = 'DaThanhToan'",
                (bay_gio.month, bay_gio.year))}
            for sv in truy_van("SELECT MaSV FROM SINHVIEN"):
                if sv["MaSV"] in da_thu:
                    continue
                _, tong = tinh_hoa_don(sv["MaSV"], bay_gio.month, bay_gio.year)
                if tong["Tong"] > 0:
                    kq["hoadon"] += 1
                    kq["tien"] += tong["Tong"]
            kq["phong"] = mot_dong(
                "SELECT COUNT(*) AS n FROM (SELECT p.SoPhong FROM PHONG p "
                "LEFT JOIN DANGKY_O d ON d.SoPhong = p.SoPhong AND d.NgayKetThuc IS NULL "
                "GROUP BY p.SoPhong, p.SoNguoiToiDa HAVING COUNT(d.MaDKO) >= p.SoNguoiToiDa) t")["n"]
        except Exception:   # noqa: BLE001
            pass
        cache.update(luc=time.time(), gia_tri=kq)
        return kq

    @app.after_request
    def lam_moi_canh_bao(phan_hoi):
        if request.method == "POST":
            cache["luc"] = 0.0   # dữ liệu vừa đổi, lần sau tính lại ngay
        return phan_hoi

    @app.context_processor
    def them_vao_giao_dien():
        return {"canh_bao": tinh_canh_bao()}

    # ============ 1. DASHBOARD (thay hàm trang_chu có sẵn) ============
    def dashboard():
        bay_gio = datetime.now()
        hn = _hom_nay()
        phong = truy_van(
            "SELECT p.SoPhong, p.LoaiPhong, p.SoNguoiToiDa, COUNT(d.MaDKO) AS DangO FROM PHONG p "
            "LEFT JOIN DANGKY_O d ON d.SoPhong = p.SoPhong AND d.NgayKetThuc IS NULL "
            "GROUP BY p.SoPhong, p.LoaiPhong, p.SoNguoiToiDa ORDER BY p.SoPhong")
        xe_hn = mot_dong("SELECT COUNT(*) AS n, COALESCE(SUM(PhiPhatSinh), 0) AS phi FROM LUOT_RA_VAO_XE "
                         "WHERE DATE(ThoiDiem) = %s", (hn,))
        dv_thang = mot_dong(
            "SELECT COALESCE(SUM(SoLuong * DonGiaApDung), 0) AS tien FROM SUDUNG_DV "
            "WHERE YEAR(ThoiDiemSuDung) = %s AND MONTH(ThoiDiemSuDung) = %s",
            (bay_gio.year, bay_gio.month))["tien"]
        return render_template(
            "dashboard.html", hom_nay=hn, thang=bay_gio.month, nam=bay_gio.year, phong=phong,
            so_sv=mot_dong("SELECT COUNT(*) AS n FROM SINHVIEN")["n"],
            tong_cho=sum(p["SoNguoiToiDa"] for p in phong), dang_o=sum(p["DangO"] for p in phong),
            khach_hn=mot_dong("SELECT COUNT(*) AS n FROM LUOT_THAM WHERE DATE(ThoiDiemDen) = %s", (hn,))["n"],
            luot_hn=xe_hn["n"], phi_hn=xe_hn["phi"], dv_thang=dv_thang,
            phong_day=[p for p in phong if p["DangO"] >= p["SoNguoiToiDa"]])

    app.view_functions["trang_chu"] = dashboard

    # ============ 2. SỬA THÔNG TIN SINH VIÊN ============
    @app.route("/sinhvien/sua/<masv>", methods=["POST"])
    def sua_sinhvien(masv):
        f = request.form
        ho_ten, socmt = f.get("HoTen", "").strip(), f.get("SoCMT", "").strip()
        if mot_dong("SELECT 1 AS x FROM SINHVIEN WHERE MaSV = %s", (masv,)) is None:
            flash("Không tìm thấy sinh viên.", "danger")
        elif not ho_ten or not socmt:
            flash("Họ tên và số CMT/CCCD không được để trống.", "danger")
        elif mot_dong("SELECT 1 AS x FROM SINHVIEN WHERE SoCMT = %s AND MaSV <> %s", (socmt, masv)):
            flash(f"Số CMT/CCCD {socmt} đã được dùng bởi sinh viên khác.", "danger")
        else:
            try:
                ghi("UPDATE SINHVIEN SET HoTen = %s, GioiTinh = %s, SDT = %s, SoCMT = %s, NgaySinh = %s, "
                    "Lop = %s, QueQuan = %s WHERE MaSV = %s",
                    (ho_ten, f.get("GioiTinh") or None, f.get("SDT", "").strip() or None, socmt,
                     f.get("NgaySinh") or None, f.get("Lop") or None,
                     f.get("QueQuan", "").strip() or None, masv))
                flash(f"Đã cập nhật thông tin {ho_ten}.", "success")
            except LoiNghiepVu as e:
                flash(str(e), "danger")
        return redirect(url_for("sinhvien"))

    # ============ 3. IN HÓA ĐƠN (Ctrl+P hoặc Lưu thành PDF) ============
    @app.route("/hoadon/<masv>/in")
    def hoadon_in(masv):
        sv = mot_dong("SELECT * FROM SINHVIEN WHERE MaSV = %s", (masv,))
        if sv is None:
            abort(404)
        thang, nam = doc_ky()
        ct, tong = tinh_hoa_don(masv, thang, nam)
        o = mot_dong("SELECT SoPhong FROM DANGKY_O WHERE MaSV = %s AND NgayKetThuc IS NULL", (masv,))
        return render_template("hoadon_in.html", sv=sv, ct=ct, tong=tong, thang=thang, nam=nam,
                               phong=o["SoPhong"] if o else "—",
                               ngay_in=datetime.now().strftime("%d/%m/%Y"))

    # ============ 4. XUẤT CSV ============
    @app.route("/cong-cu")
    def cong_cu():
        ds = [{"khoa": khoa, "bang": bang, "mo_ta": mo_ta,
               "so_dong": mot_dong(f"SELECT COUNT(*) AS n FROM {bang}")["n"]}
              for khoa, bang, mo_ta in BANG_XUAT]
        return render_template("cong_cu.html", ds=ds)

    @app.route("/xuat/<khoa>")
    def xuat_csv(khoa):
        bang = TEN_BANG.get(khoa)
        if bang is None:
            abort(404)
        return Response(_csv_cua_bang(bang), mimetype="text/csv",
                        headers={"Content-Disposition": f"attachment; filename={bang.lower()}.csv"})

    @app.route("/xuat-tat-ca")
    def xuat_tat_ca():
        bo_nho = io.BytesIO()
        with zipfile.ZipFile(bo_nho, "w", zipfile.ZIP_DEFLATED) as z:
            for _, bang, _ in BANG_XUAT:
                z.writestr(f"{bang.lower()}.csv", _csv_cua_bang(bang).encode("utf-8"))
        bo_nho.seek(0)
        return send_file(bo_nho, as_attachment=True, mimetype="application/zip",
                         download_name=f"ktx-sao-luu-{datetime.now().strftime('%Y%m%d-%H%M')}.zip")

    # ============ 7. LỊCH SỬ QUẸT XE THEO TỪNG XE ============
    @app.route("/xe/lich-su/<bien_so>")
    def lich_su_xe(bien_so):
        xe = mot_dong("SELECT * FROM XE WHERE BienSo = %s", (bien_so,))
        if xe is None:
            abort(404)
        hn = _hom_nay()
        ve = truy_van("SELECT v.*, s.HoTen FROM DANGKY_XE_THANG v JOIN SINHVIEN s ON s.MaSV = v.MaSV "
                      "WHERE v.BienSo = %s ORDER BY v.NgayBatDau DESC", (bien_so,))
        for v in ve:
            v["ConHan"] = v["NgayBatDau"] <= hn <= (v["NgayKetThuc"] or "9999-12-31")
        theo_ngay = truy_van(
            "SELECT DATE(l.ThoiDiem) AS Ngay, COUNT(*) AS SoLuot, SUM(l.PhiPhatSinh) AS Phi "
            "FROM LUOT_RA_VAO_XE l JOIN DANGKY_XE_THANG v ON v.MaDKXe = l.MaDKXe WHERE v.BienSo = %s "
            "GROUP BY DATE(l.ThoiDiem) ORDER BY Ngay DESC", (bien_so,))
        chi_tiet = truy_van(
            "SELECT l.MaLuot, l.ThoiDiem, l.LoaiHanhDong, l.PhiPhatSinh FROM LUOT_RA_VAO_XE l "
            "JOIN DANGKY_XE_THANG v ON v.MaDKXe = l.MaDKXe WHERE v.BienSo = %s "
            "ORDER BY l.ThoiDiem DESC, l.MaLuot DESC LIMIT 60", (bien_so,))
        return render_template("lich_su_xe.html", xe=xe, ve=ve, theo_ngay=theo_ngay, chi_tiet=chi_tiet,
                               tong_phi=sum(d["Phi"] or 0 for d in theo_ngay),
                               tong_luot=sum(d["SoLuot"] for d in theo_ngay))

    # ============ 8. HỒ SƠ SINH VIÊN ============
    @app.route("/sinhvien/<masv>")
    def ho_so(masv):
        sv = mot_dong("SELECT * FROM SINHVIEN WHERE MaSV = %s", (masv,))
        if sv is None:
            abort(404)
        bay_gio = datetime.now()
        hn = _hom_nay()
        lich_su_o = truy_van("SELECT * FROM DANGKY_O WHERE MaSV = %s ORDER BY NgayBatDau DESC", (masv,))
        phong_ht = next((d for d in lich_su_o if d["NgayKetThuc"] is None), None)
        ve = truy_van("SELECT v.*, x.LoaiXe FROM DANGKY_XE_THANG v JOIN XE x ON x.BienSo = v.BienSo "
                      "WHERE v.MaSV = %s ORDER BY v.NgayBatDau DESC", (masv,))
        for v in ve:
            v["ConHan"] = v["NgayBatDau"] <= hn <= (v["NgayKetThuc"] or "9999-12-31")
        khach = truy_van("SELECT l.ThoiDiemDen, l.CMTKhach, k.HoTen FROM LUOT_THAM l "
                         "JOIN KHACH k ON k.CMTKhach = l.CMTKhach WHERE l.MaSV = %s "
                         "ORDER BY l.ThoiDiemDen DESC LIMIT 8", (masv,))
        ct, tong = tinh_hoa_don(masv, bay_gio.month, bay_gio.year)
        da_thu = mot_dong("SELECT 1 AS x FROM HOADON WHERE MaSV = %s AND Thang = %s AND Nam = %s "
                          "AND TrangThai = 'DaThanhToan'", (masv, bay_gio.month, bay_gio.year)) is not None
        return render_template("ho_so.html", sv=sv, phong_ht=phong_ht, lich_su_o=lich_su_o, ve=ve,
                               khach=khach, ct=ct, tong=tong, da_thu=da_thu,
                               thang=bay_gio.month, nam=bay_gio.year)