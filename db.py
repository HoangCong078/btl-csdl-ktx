"""Kết nối MySQL cho app KTX. Cấu hình qua biến môi trường, không ghi mật khẩu vào code."""
import os
from decimal import Decimal

import pymysql
from pymysql.constants import FIELD_TYPE
from pymysql.converters import conversions

CAU_HINH = {
    "host": os.getenv("KTX_DB_HOST", "localhost"),
    "port": int(os.getenv("KTX_DB_PORT", "3306")),
    "user": os.getenv("KTX_DB_USER", "root"),
    "password": os.getenv("KTX_DB_PASSWORD", ""),
    "database": os.getenv("KTX_DB_NAME", "KTX"),
    "charset": "utf8mb4",
}


def _chuoi(v):
    return v.decode() if isinstance(v, (bytes, bytearray)) else v


def _so(v):
    d = Decimal(_chuoi(v))
    return int(d) if d == d.to_integral_value() else float(d)


# Ngày giờ giữ dạng chuỗi 'YYYY-MM-DD HH:MM:SS' (templates đang dùng chuỗi); DECIMAL thành số
_CONV = conversions.copy()
_CONV[FIELD_TYPE.DATE] = _chuoi
_CONV[FIELD_TYPE.DATETIME] = _chuoi
_CONV[FIELD_TYPE.NEWDECIMAL] = _so
_CONV[FIELD_TYPE.DECIMAL] = _so


class LoiNghiepVu(Exception):
    """Lỗi do ràng buộc/trigger của CSDL, thông báo đã dịch sang tiếng Việt."""


def dich_loi(e):
    ma = e.args[0] if e.args else 0
    noi_dung = str(e.args[1]) if len(e.args) > 1 else str(e)
    if ma == 1644:   # SIGNAL SQLSTATE '45000' từ trigger
        return noi_dung.replace("Loi: ", "", 1)
    if ma == 1062:
        return "Dữ liệu bị trùng (khóa hoặc giá trị duy nhất đã tồn tại)."
    if ma in (1451, 1217):
        return "Không thể xóa hoặc sửa vì dữ liệu này đang được dùng ở nơi khác."
    if ma == 1452:
        return "Dữ liệu tham chiếu không tồn tại."
    if ma == 3819:
        return "Dữ liệu vi phạm ràng buộc kiểm tra (CHECK)."
    return f"Lỗi CSDL ({ma}): {noi_dung}"


def ket_noi():
    return pymysql.connect(**CAU_HINH, conv=_CONV, cursorclass=pymysql.cursors.DictCursor)


def truy_van(sql, tham_so=None):
    """SELECT: trả về list dict."""
    cn = ket_noi()
    try:
        with cn.cursor() as cur:
            cur.execute(sql, tham_so)
            return list(cur.fetchall())
    finally:
        cn.close()


def mot_dong(sql, tham_so=None):
    ds = truy_van(sql, tham_so)
    return ds[0] if ds else None


def giao_dich(ham):
    """Chạy ham(cursor) trong một giao dịch. Lỗi ràng buộc thì rollback và raise LoiNghiepVu."""
    cn = ket_noi()
    try:
        with cn.cursor() as cur:
            kq = ham(cur)
        cn.commit()
        return kq
    except pymysql.MySQLError as e:
        cn.rollback()
        raise LoiNghiepVu(dich_loi(e)) from e
    finally:
        cn.close()


def ghi(sql, tham_so=None):
    """INSERT/UPDATE/DELETE. Trả về (số dòng bị ảnh hưởng, id vừa chèn)."""
    def chay(cur):
        cur.execute(sql, tham_so)
        return cur.rowcount, cur.lastrowid
    return giao_dich(chay)


def kiem_tra_ket_noi():
    try:
        ket_noi().close()
        return None
    except pymysql.MySQLError as e:
        return str(e)