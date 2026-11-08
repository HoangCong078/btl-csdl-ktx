-- ============================================================================
-- PROJECT 2: HỆ THỐNG QUẢN LÝ KÝ TÚC XÁ SINH VIÊN
-- File: KTX_phanDDL.sql
-- Phân việc: Người 1 (Trưởng nhóm) - DDL + Ràng buộc toàn vẹn + Trigger nghiệp vụ
-- Hệ QTCSDL: MySQL 8.0.16+
-- Schema chuẩn: Khớp 100% với Chuong1_YC1.pdf và thuc_the_va_thuoc_tinh_FIXED.docx (12 bảng)
--
-- QUY ƯỚC NGHIỆP VỤ CHỐT TOÀN NHÓM:
-- 1. Tiền phòng tính chẵn tháng: Chỉ cần khoảng thời gian đăng ký ở (NgayBatDau .. NgayKetThuc)
--    giao với tháng M/năm N ít nhất 1 ngày thì tính tròn 1 tháng tiền phòng (theo DonGiaThangApDung).
-- 2. Sức chứa phòng & chỗ ở: Tại mọi thời điểm, số sinh viên đang ở thực tế trong một phòng
--    không vượt quá PHONG.SoNguoiToiDa. Mỗi sinh viên tại một thời điểm chỉ có tối đa 1 đăng ký ở.
-- 3. Vé xe tháng: Đơn giá mặc định 100.000đ/tháng. Tại mọi thời điểm, mỗi sinh viên chỉ được
--    đăng ký tối đa 2 xe vé tháng còn hiệu lực; 1 biển số không thuộc 2 đăng ký trùng thời gian.
-- 4. Lượt gửi/lấy xe vé tháng: Mỗi hành động 'Gui' hoặc 'Lay' được tính là 1 lượt.
--    Trong 1 ngày (theo DATE(ThoiDiem)), 2 lượt đầu tiên của mỗi MaDKXe được miễn phí (0đ),
--    từ lượt thứ 3 trở đi tính 3.000đ/lượt. Nhật ký nhập theo thứ tự thời gian; không sửa
--    MaDKXe/ThoiDiem và chỉ xóa lượt cuối cùng trong ngày. Xe vãng lai không lưu ở bảng này.
-- 5. Chống tính trùng doanh thu (Double-count): Phí vé tháng (100k) và phí phát sinh (3k/lượt)
--    đi qua DANGKY_XE_THANG & LUOT_RA_VAO_XE. Dịch vụ 'Trông xe vãng lai' trong bảng DICHVU
--    chỉ dành cho xe không đăng ký vé tháng.
-- ============================================================================

CREATE DATABASE IF NOT EXISTS KTX
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE KTX;

-- ============================================================================
-- DỌN DẸP TRIGGER & BẢNG ĐỂ CÓ THỂ CHẠY LẠI FILE NHIỀU LẦN
-- ============================================================================
DROP TRIGGER IF EXISTS trg_phong_bu;
DROP TRIGGER IF EXISTS trg_dangky_o_bi;
DROP TRIGGER IF EXISTS trg_dangky_o_bu;
DROP TRIGGER IF EXISTS trg_sudung_dv_bi;
DROP TRIGGER IF EXISTS trg_sudung_dv_bu;
DROP TRIGGER IF EXISTS trg_dangky_xe_bi;
DROP TRIGGER IF EXISTS trg_dangky_xe_bu;
DROP TRIGGER IF EXISTS trg_luot_xe_bi;
DROP TRIGGER IF EXISTS trg_luot_xe_bu;
DROP TRIGGER IF EXISTS trg_luot_xe_bd;
DROP TRIGGER IF EXISTS trg_hoadon_bi;
DROP TRIGGER IF EXISTS trg_cthd_bi;
DROP TRIGGER IF EXISTS trg_cthd_bu;
DROP TRIGGER IF EXISTS trg_cthd_ai;
DROP TRIGGER IF EXISTS trg_cthd_au;
DROP TRIGGER IF EXISTS trg_cthd_ad;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS CHITIET_HOADON;
DROP TABLE IF EXISTS HOADON;
DROP TABLE IF EXISTS LUOT_RA_VAO_XE;
DROP TABLE IF EXISTS DANGKY_XE_THANG;
DROP TABLE IF EXISTS XE;
DROP TABLE IF EXISTS SUDUNG_DV;
DROP TABLE IF EXISTS DICHVU;
DROP TABLE IF EXISTS LUOT_THAM;
DROP TABLE IF EXISTS KHACH;
DROP TABLE IF EXISTS DANGKY_O;
DROP TABLE IF EXISTS SINHVIEN;
DROP TABLE IF EXISTS PHONG;
SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================================
-- NHÓM 1: PHÒNG VÀ SINH VIÊN
-- ============================================================================

-- 1. Bảng PHONG
CREATE TABLE PHONG (
    SoPhong          VARCHAR(10)   NOT NULL,
    LoaiPhong        VARCHAR(50)   NOT NULL,
    DonGia           DECIMAL(12,2) NOT NULL,
    SoNguoiToiDa     INT           NOT NULL,
    PRIMARY KEY (SoPhong),
    CONSTRAINT chk_phong_dongia  CHECK (DonGia >= 0),
    CONSTRAINT chk_phong_succhua CHECK (SoNguoiToiDa > 0)
) ENGINE=InnoDB;

-- 2. Bảng SINHVIEN
CREATE TABLE SINHVIEN (
    MaSV             VARCHAR(20)   NOT NULL,
    HoTen            VARCHAR(100)  NOT NULL,
    GioiTinh         VARCHAR(10)   NULL,
    SDT              VARCHAR(15)   NULL,
    SoCMT            VARCHAR(20)   NOT NULL,
    NgaySinh         DATE          NULL,
    Lop              VARCHAR(30)   NULL,
    QueQuan          VARCHAR(100)  NULL,
    PRIMARY KEY (MaSV),
    CONSTRAINT uq_sinhvien_socmt UNIQUE (SoCMT)
) ENGINE=InnoDB;

-- 3. Bảng DANGKY_O (Bảng lịch sử đăng ký ở)
CREATE TABLE DANGKY_O (
    MaDKO                BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    MaSV                 VARCHAR(20)     NOT NULL,
    SoPhong              VARCHAR(10)     NOT NULL,
    NgayBatDau           DATE            NOT NULL,
    NgayKetThuc          DATE            NULL,
    DonGiaThangApDung    DECIMAL(12,2)   NOT NULL DEFAULT 0,
    PRIMARY KEY (MaDKO),
    INDEX idx_dko_sinhvien_thoigian (MaSV, NgayBatDau, NgayKetThuc),
    INDEX idx_dko_phong_thoigian    (SoPhong, NgayBatDau, NgayKetThuc),
    CONSTRAINT fk_dko_sinhvien FOREIGN KEY (MaSV)
        REFERENCES SINHVIEN(MaSV)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_dko_phong FOREIGN KEY (SoPhong)
        REFERENCES PHONG(SoPhong)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_dko_ngay   CHECK (NgayKetThuc IS NULL OR NgayKetThuc >= NgayBatDau),
    CONSTRAINT chk_dko_dongia CHECK (DonGiaThangApDung >= 0)
) ENGINE=InnoDB;

-- ============================================================================
-- NHÓM 2: KHÁCH ĐẾN THĂM
-- ============================================================================

-- 4. Bảng KHACH
CREATE TABLE KHACH (
    CMTKhach         VARCHAR(20)   NOT NULL,
    HoTen            VARCHAR(100)  NOT NULL,
    NgaySinh         DATE          NULL,
    SDT              VARCHAR(15)   NULL,
    PRIMARY KEY (CMTKhach)
) ENGINE=InnoDB;

-- 5. Bảng LUOT_THAM
CREATE TABLE LUOT_THAM (
    MaLuotTham       BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    CMTKhach         VARCHAR(20)     NOT NULL,
    MaSV             VARCHAR(20)     NOT NULL,
    ThoiDiemDen      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (MaLuotTham),
    INDEX idx_luottham_thoidiem (ThoiDiemDen),
    INDEX idx_luottham_sv_khach (MaSV, CMTKhach, ThoiDiemDen),
    CONSTRAINT fk_luottham_khach FOREIGN KEY (CMTKhach)
        REFERENCES KHACH(CMTKhach)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_luottham_sinhvien FOREIGN KEY (MaSV)
        REFERENCES SINHVIEN(MaSV)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

-- ============================================================================
-- NHÓM 3: DỊCH VỤ
-- ============================================================================

-- 6. Bảng DICHVU
CREATE TABLE DICHVU (
    MaDV             VARCHAR(20)   NOT NULL,
    TenDV            VARCHAR(100)  NOT NULL,
    LoaiDV           VARCHAR(50)   NULL,
    DonGia           DECIMAL(12,2) NOT NULL,
    DonViTinh        VARCHAR(20)   NULL,
    PRIMARY KEY (MaDV),
    CONSTRAINT chk_dichvu_dongia CHECK (DonGia >= 0)
) ENGINE=InnoDB;

-- 7. Bảng SUDUNG_DV
CREATE TABLE SUDUNG_DV (
    MaSuDung         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    MaSV             VARCHAR(20)     NOT NULL,
    MaDV             VARCHAR(20)     NOT NULL,
    ThoiDiemSuDung   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    SoLuong          DECIMAL(10,2)   NOT NULL DEFAULT 1,
    DonGiaApDung     DECIMAL(12,2)   NOT NULL DEFAULT 0,
    PRIMARY KEY (MaSuDung),
    INDEX idx_sudung_thoidiem (ThoiDiemSuDung),
    INDEX idx_sudung_sv_dv    (MaSV, MaDV, ThoiDiemSuDung),
    CONSTRAINT fk_sudung_sinhvien FOREIGN KEY (MaSV)
        REFERENCES SINHVIEN(MaSV)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_sudung_dichvu FOREIGN KEY (MaDV)
        REFERENCES DICHVU(MaDV)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_sudung_soluong CHECK (SoLuong > 0),
    CONSTRAINT chk_sudung_dongia  CHECK (DonGiaApDung >= 0)
) ENGINE=InnoDB;

-- ============================================================================
-- NHÓM 4: GỬI XE VÉ THÁNG
-- ============================================================================

-- 8. Bảng XE
CREATE TABLE XE (
    BienSo           VARCHAR(20) NOT NULL,
    LoaiXe           VARCHAR(30) NOT NULL,
    PRIMARY KEY (BienSo)
) ENGINE=InnoDB;

-- 9. Bảng DANGKY_XE_THANG
CREATE TABLE DANGKY_XE_THANG (
    MaDKXe               BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    MaSV                 VARCHAR(20)     NOT NULL,
    BienSo               VARCHAR(20)     NOT NULL,
    NgayBatDau           DATE            NOT NULL,
    NgayKetThuc          DATE            NULL,
    DonGiaThangApDung    DECIMAL(12,2)   NOT NULL DEFAULT 100000,
    PRIMARY KEY (MaDKXe),
    INDEX idx_dkxe_sinhvien_thoigian (MaSV, NgayBatDau, NgayKetThuc),
    INDEX idx_dkxe_bienso_thoigian   (BienSo, NgayBatDau, NgayKetThuc),
    CONSTRAINT fk_dkxe_sinhvien FOREIGN KEY (MaSV)
        REFERENCES SINHVIEN(MaSV)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_dkxe_xe FOREIGN KEY (BienSo)
        REFERENCES XE(BienSo)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_dkxe_ngay   CHECK (NgayKetThuc IS NULL OR NgayKetThuc >= NgayBatDau),
    CONSTRAINT chk_dkxe_dongia CHECK (DonGiaThangApDung >= 0)
) ENGINE=InnoDB;

-- 10. Bảng LUOT_RA_VAO_XE (Mỗi sự kiện quẹt thẻ là 1 bản ghi)
CREATE TABLE LUOT_RA_VAO_XE (
    MaLuot           BIGINT UNSIGNED     NOT NULL AUTO_INCREMENT,
    MaDKXe           BIGINT UNSIGNED     NOT NULL,
    ThoiDiem         DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP,
    LoaiHanhDong     ENUM('Gui', 'Lay')  NOT NULL,
    PhiPhatSinh      INT                 NOT NULL DEFAULT 0,
    PRIMARY KEY (MaLuot),
    INDEX idx_luotxe_dangky_thoidiem (MaDKXe, ThoiDiem),
    CONSTRAINT fk_luotxe_dangky FOREIGN KEY (MaDKXe)
        REFERENCES DANGKY_XE_THANG(MaDKXe)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_luotxe_phi CHECK (PhiPhatSinh IN (0, 3000))
) ENGINE=InnoDB;

-- ============================================================================
-- NHÓM 5: HÓA ĐƠN THÁNG
-- ============================================================================

-- 11. Bảng HOADON
CREATE TABLE HOADON (
    MaHD             BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    MaSV             VARCHAR(20)     NOT NULL,
    Thang            INT             NOT NULL,
    Nam              INT             NOT NULL,
    NgayLap          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    TrangThai        ENUM('ChuaThanhToan', 'DaThanhToan')
                                     NOT NULL DEFAULT 'ChuaThanhToan',
    TongTien         DECIMAL(14,2)   NOT NULL DEFAULT 0,
    PRIMARY KEY (MaHD),
    CONSTRAINT uq_hoadon_sinhvien_thang_nam UNIQUE (MaSV, Thang, Nam),
    CONSTRAINT fk_hoadon_sinhvien FOREIGN KEY (MaSV)
        REFERENCES SINHVIEN(MaSV)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_hoadon_thang    CHECK (Thang BETWEEN 1 AND 12),
    CONSTRAINT chk_hoadon_nam      CHECK (Nam >= 2000),
    CONSTRAINT chk_hoadon_tongtien CHECK (TongTien >= 0)
) ENGINE=InnoDB;

-- 12. Bảng CHITIET_HOADON (Khớp 100% tài liệu thiết kế chuẩn và sơ đồ EER)
CREATE TABLE CHITIET_HOADON (
    MaCTHD           BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    MaHD             BIGINT UNSIGNED NOT NULL,
    LoaiPhi          ENUM('Phong', 'DichVu', 'XeThang', 'XePhatSinh') NOT NULL,
    DienGiai         VARCHAR(255)    NOT NULL,
    SoLuong          DECIMAL(10,2)   NOT NULL DEFAULT 1,
    DonGiaApDung     DECIMAL(12,2)   NOT NULL,
    ThanhTien        DECIMAL(14,2)   NOT NULL DEFAULT 0,
    MaDKO            BIGINT UNSIGNED NULL,
    MaSuDung         BIGINT UNSIGNED NULL,
    MaLuot           BIGINT UNSIGNED NULL,
    PRIMARY KEY (MaCTHD),
    INDEX idx_cthd_hoadon (MaHD),
    UNIQUE KEY uq_cthd_dko_hoadon (MaHD, MaDKO),
    UNIQUE KEY uq_cthd_sudung     (MaSuDung),
    UNIQUE KEY uq_cthd_luot       (MaLuot),
    CONSTRAINT fk_cthd_hoadon FOREIGN KEY (MaHD)
        REFERENCES HOADON(MaHD)
        ON UPDATE CASCADE ON DELETE CASCADE,
    -- Lưu ý: 3 FK nguồn (MaDKO, MaSuDung, MaLuot) nằm trong CHECK chk_cthd_mot_nguon nên phải dùng
    -- RESTRICT; MySQL không cho ON UPDATE/DELETE CASCADE/SET NULL trên cột có CHECK (lỗi 3823).
    CONSTRAINT fk_cthd_dko FOREIGN KEY (MaDKO)
        REFERENCES DANGKY_O(MaDKO)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT fk_cthd_sudung FOREIGN KEY (MaSuDung)
        REFERENCES SUDUNG_DV(MaSuDung)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT fk_cthd_luotxe FOREIGN KEY (MaLuot)
        REFERENCES LUOT_RA_VAO_XE(MaLuot)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT chk_cthd_soluong   CHECK (SoLuong > 0),
    CONSTRAINT chk_cthd_dongia    CHECK (DonGiaApDung >= 0),
    CONSTRAINT chk_cthd_thanhtien CHECK (ThanhTien >= 0),
    -- Ràng buộc nguồn phát sinh ứng với 3 FK chuẩn trên sơ đồ EER (Hình 6.1):
    -- + Phong:      bắt buộc có MaDKO
    -- + DichVu:     bắt buộc có MaSuDung
    -- + XeThang:    3 FK nguồn đều NULL (tổng hợp theo sinh viên và kỳ hóa đơn)
    -- + XePhatSinh: bắt buộc có MaLuot (quan hệ 1:1 ánh xạ từng lượt quẹt vượt 3.000đ)
    CONSTRAINT chk_cthd_mot_nguon CHECK (
        (LoaiPhi = 'Phong'      AND MaDKO IS NOT NULL AND MaSuDung IS NULL     AND MaLuot IS NULL)
        OR
        (LoaiPhi = 'DichVu'     AND MaDKO IS NULL     AND MaSuDung IS NOT NULL AND MaLuot IS NULL)
        OR
        (LoaiPhi = 'XeThang'    AND MaDKO IS NULL     AND MaSuDung IS NULL     AND MaLuot IS NULL)
        OR
        (LoaiPhi = 'XePhatSinh' AND MaDKO IS NULL     AND MaSuDung IS NULL     AND MaLuot IS NOT NULL)
    )
) ENGINE=InnoDB;

-- ============================================================================
-- HỆ THỐNG TRIGGER KIỂM TRA RÀNG BUỘC & TỰ ĐỘNG HÓA NGHIỆP VỤ
-- ============================================================================
DELIMITER $$

-- ----------------------------------------------------------------------------
-- TRIGGER BẢNG PHONG: Chặn giảm sức chứa thấp hơn số sinh viên đang ở thực tế
-- ----------------------------------------------------------------------------
CREATE TRIGGER trg_phong_bu
BEFORE UPDATE ON PHONG
FOR EACH ROW
BEGIN
    DECLARE v_max_nguoi INT DEFAULT 0;

    IF NEW.SoNguoiToiDa < OLD.SoNguoiToiDa THEN
        SELECT COALESCE(MAX(cnt), 0) INTO v_max_nguoi
        FROM (
            SELECT (
                SELECT COUNT(*)
                FROM DANGKY_O d2
                WHERE d2.SoPhong = OLD.SoPhong
                  AND d2.NgayBatDau <= p.NgayBatDau
                  AND COALESCE(d2.NgayKetThuc, '9999-12-31') >= p.NgayBatDau
            ) AS cnt
            FROM DANGKY_O p
            WHERE p.SoPhong = OLD.SoPhong
        ) AS sub;

        IF v_max_nguoi > NEW.SoNguoiToiDa THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Loi: Khong the giam suc chua thap hon so sinh vien da dang ky o!';
        END IF;
    END IF;
END$$

-- ----------------------------------------------------------------------------
-- TRIGGER BẢNG DANGKY_O: Tự động điền giá, chống trùng lặp lịch sử & quá tải phòng
-- ----------------------------------------------------------------------------
CREATE TRIGGER trg_dangky_o_bi
BEFORE INSERT ON DANGKY_O
FOR EACH ROW
BEGIN
    DECLARE v_suc_chua INT DEFAULT 0;
    DECLARE v_gia_phong DECIMAL(12,2) DEFAULT 0;
    DECLARE v_sv_trung INT DEFAULT 0;
    DECLARE v_so_nguoi_tai_new INT DEFAULT 0;
    DECLARE v_max_nguoi_trong_ky INT DEFAULT 0;
    DECLARE v_new_end DATE;

    SET v_new_end = COALESCE(NEW.NgayKetThuc, '9999-12-31');

    SELECT SoNguoiToiDa, DonGia INTO v_suc_chua, v_gia_phong
    FROM PHONG
    WHERE SoPhong = NEW.SoPhong;

    IF NEW.DonGiaThangApDung IS NULL OR NEW.DonGiaThangApDung <= 0 THEN
        SET NEW.DonGiaThangApDung = v_gia_phong;
    END IF;

    SELECT COUNT(*) INTO v_sv_trung
    FROM DANGKY_O d
    WHERE d.MaSV = NEW.MaSV
      AND d.NgayBatDau <= v_new_end
      AND COALESCE(d.NgayKetThuc, '9999-12-31') >= NEW.NgayBatDau;

    IF v_sv_trung > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Loi: Sinh vien da co dang ky o phong khac trong khoang thoi gian nay!';
    END IF;

    SELECT COUNT(*) INTO v_so_nguoi_tai_new
    FROM DANGKY_O d
    WHERE d.SoPhong = NEW.SoPhong
      AND d.NgayBatDau <= NEW.NgayBatDau
      AND COALESCE(d.NgayKetThuc, '9999-12-31') >= NEW.NgayBatDau;

    SELECT COALESCE(MAX(cnt), 0) INTO v_max_nguoi_trong_ky
    FROM (
        SELECT (
            SELECT COUNT(*)
            FROM DANGKY_O d2
            WHERE d2.SoPhong = NEW.SoPhong
              AND d2.NgayBatDau <= p.NgayBatDau
              AND COALESCE(d2.NgayKetThuc, '9999-12-31') >= p.NgayBatDau
        ) AS cnt
        FROM DANGKY_O p
        WHERE p.SoPhong = NEW.SoPhong
          AND p.NgayBatDau > NEW.NgayBatDau
          AND p.NgayBatDau <= v_new_end
    ) AS sub;

    IF v_so_nguoi_tai_new >= v_suc_chua OR v_max_nguoi_trong_ky >= v_suc_chua THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Loi: Phong da du so nguoi toi da, khong the dang ky them!';
    END IF;
END$$

CREATE TRIGGER trg_dangky_o_bu
BEFORE UPDATE ON DANGKY_O
FOR EACH ROW
BEGIN
    DECLARE v_suc_chua INT DEFAULT 0;
    DECLARE v_gia_phong DECIMAL(12,2) DEFAULT 0;
    DECLARE v_sv_trung INT DEFAULT 0;
    DECLARE v_so_nguoi_tai_new INT DEFAULT 0;
    DECLARE v_max_nguoi_trong_ky INT DEFAULT 0;
    DECLARE v_new_end DATE;

    SET v_new_end = COALESCE(NEW.NgayKetThuc, '9999-12-31');

    SELECT SoNguoiToiDa, DonGia INTO v_suc_chua, v_gia_phong
    FROM PHONG
    WHERE SoPhong = NEW.SoPhong;

    IF NEW.DonGiaThangApDung IS NULL OR NEW.DonGiaThangApDung <= 0 THEN
        SET NEW.DonGiaThangApDung = v_gia_phong;
    END IF;

    SELECT COUNT(*) INTO v_sv_trung
    FROM DANGKY_O d
    WHERE d.MaSV = NEW.MaSV
      AND d.MaDKO <> OLD.MaDKO
      AND d.NgayBatDau <= v_new_end
      AND COALESCE(d.NgayKetThuc, '9999-12-31') >= NEW.NgayBatDau;

    IF v_sv_trung > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Loi: Sinh vien da co dang ky o phong khac trong khoang thoi gian nay!';
    END IF;

    SELECT COUNT(*) INTO v_so_nguoi_tai_new
    FROM DANGKY_O d
    WHERE d.SoPhong = NEW.SoPhong
      AND d.MaDKO <> OLD.MaDKO
      AND d.NgayBatDau <= NEW.NgayBatDau
      AND COALESCE(d.NgayKetThuc, '9999-12-31') >= NEW.NgayBatDau;

    SELECT COALESCE(MAX(cnt), 0) INTO v_max_nguoi_trong_ky
    FROM (
        SELECT (
            SELECT COUNT(*)
            FROM DANGKY_O d2
            WHERE d2.SoPhong = NEW.SoPhong
              AND d2.MaDKO <> OLD.MaDKO
              AND d2.NgayBatDau <= p.NgayBatDau
              AND COALESCE(d2.NgayKetThuc, '9999-12-31') >= p.NgayBatDau
        ) AS cnt
        FROM DANGKY_O p
        WHERE p.SoPhong = NEW.SoPhong
          AND p.MaDKO <> OLD.MaDKO
          AND p.NgayBatDau > NEW.NgayBatDau
          AND p.NgayBatDau <= v_new_end
    ) AS sub;

    IF v_so_nguoi_tai_new >= v_suc_chua OR v_max_nguoi_trong_ky >= v_suc_chua THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Loi: Phong da du so nguoi toi da, khong the cap nhat dang ky!';
    END IF;
END$$

-- ----------------------------------------------------------------------------
-- TRIGGER BẢNG SUDUNG_DV: Tự động lấy đơn giá hiện hành từ danh mục dịch vụ
-- ----------------------------------------------------------------------------
CREATE TRIGGER trg_sudung_dv_bi
BEFORE INSERT ON SUDUNG_DV
FOR EACH ROW
BEGIN
    DECLARE v_gia_dv DECIMAL(12,2) DEFAULT 0;
    IF NEW.DonGiaApDung IS NULL OR NEW.DonGiaApDung <= 0 THEN
        SELECT DonGia INTO v_gia_dv FROM DICHVU WHERE MaDV = NEW.MaDV;
        SET NEW.DonGiaApDung = COALESCE(v_gia_dv, 0);
    END IF;
END$$

CREATE TRIGGER trg_sudung_dv_bu
BEFORE UPDATE ON SUDUNG_DV
FOR EACH ROW
BEGIN
    DECLARE v_gia_dv DECIMAL(12,2) DEFAULT 0;
    IF NEW.DonGiaApDung IS NULL OR NEW.DonGiaApDung <= 0 THEN
        SELECT DonGia INTO v_gia_dv FROM DICHVU WHERE MaDV = NEW.MaDV;
        SET NEW.DonGiaApDung = COALESCE(v_gia_dv, 0);
    END IF;
END$$

-- ----------------------------------------------------------------------------
-- TRIGGER BẢNG DANGKY_XE_THANG: Chặn tối đa 2 xe/SV và không trùng biển số
-- ----------------------------------------------------------------------------
CREATE TRIGGER trg_dangky_xe_bi
BEFORE INSERT ON DANGKY_XE_THANG
FOR EACH ROW
BEGIN
    DECLARE v_so_xe_tai_new INT DEFAULT 0;
    DECLARE v_max_xe_trong_ky INT DEFAULT 0;
    DECLARE v_trung_bienso INT DEFAULT 0;
    DECLARE v_new_end DATE;

    SET v_new_end = COALESCE(NEW.NgayKetThuc, '9999-12-31');

    SELECT COUNT(*) INTO v_trung_bienso
    FROM DANGKY_XE_THANG d
    WHERE d.BienSo = NEW.BienSo
      AND d.NgayBatDau <= v_new_end
      AND COALESCE(d.NgayKetThuc, '9999-12-31') >= NEW.NgayBatDau;

    IF v_trung_bienso > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Loi: Bien so xe nay da co dang ky ve thang con hieu luc trong khoang thoi gian nay!';
    END IF;

    SELECT COUNT(*) INTO v_so_xe_tai_new
    FROM DANGKY_XE_THANG d
    WHERE d.MaSV = NEW.MaSV
      AND d.NgayBatDau <= NEW.NgayBatDau
      AND COALESCE(d.NgayKetThuc, '9999-12-31') >= NEW.NgayBatDau;

    SELECT COALESCE(MAX(cnt), 0) INTO v_max_xe_trong_ky
    FROM (
        SELECT (
            SELECT COUNT(*)
            FROM DANGKY_XE_THANG d2
            WHERE d2.MaSV = NEW.MaSV
              AND d2.NgayBatDau <= p.NgayBatDau
              AND COALESCE(d2.NgayKetThuc, '9999-12-31') >= p.NgayBatDau
        ) AS cnt
        FROM DANGKY_XE_THANG p
        WHERE p.MaSV = NEW.MaSV
          AND p.NgayBatDau > NEW.NgayBatDau
          AND p.NgayBatDau <= v_new_end
    ) AS sub;

    IF v_so_xe_tai_new >= 2 OR v_max_xe_trong_ky >= 2 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Loi: Moi sinh vien chi duoc dang ky toi da 2 xe ve thang con hieu luc!';
    END IF;
END$$

CREATE TRIGGER trg_dangky_xe_bu
BEFORE UPDATE ON DANGKY_XE_THANG
FOR EACH ROW
BEGIN
    DECLARE v_so_xe_tai_new INT DEFAULT 0;
    DECLARE v_max_xe_trong_ky INT DEFAULT 0;
    DECLARE v_trung_bienso INT DEFAULT 0;
    DECLARE v_new_end DATE;

    SET v_new_end = COALESCE(NEW.NgayKetThuc, '9999-12-31');

    SELECT COUNT(*) INTO v_trung_bienso
    FROM DANGKY_XE_THANG d
    WHERE d.BienSo = NEW.BienSo
      AND d.MaDKXe <> OLD.MaDKXe
      AND d.NgayBatDau <= v_new_end
      AND COALESCE(d.NgayKetThuc, '9999-12-31') >= NEW.NgayBatDau;

    IF v_trung_bienso > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Loi: Bien so xe nay da co dang ky ve thang con hieu luc trong khoang thoi gian nay!';
    END IF;

    SELECT COUNT(*) INTO v_so_xe_tai_new
    FROM DANGKY_XE_THANG d
    WHERE d.MaSV = NEW.MaSV
      AND d.MaDKXe <> OLD.MaDKXe
      AND d.NgayBatDau <= NEW.NgayBatDau
      AND COALESCE(d.NgayKetThuc, '9999-12-31') >= NEW.NgayBatDau;

    SELECT COALESCE(MAX(cnt), 0) INTO v_max_xe_trong_ky
    FROM (
        SELECT (
            SELECT COUNT(*)
            FROM DANGKY_XE_THANG d2
            WHERE d2.MaSV = NEW.MaSV
              AND d2.MaDKXe <> OLD.MaDKXe
              AND d2.NgayBatDau <= p.NgayBatDau
              AND COALESCE(d2.NgayKetThuc, '9999-12-31') >= p.NgayBatDau
        ) AS cnt
        FROM DANGKY_XE_THANG p
        WHERE p.MaSV = NEW.MaSV
          AND p.MaDKXe <> OLD.MaDKXe
          AND p.NgayBatDau > NEW.NgayBatDau
          AND p.NgayBatDau <= v_new_end
    ) AS sub;

    IF v_so_xe_tai_new >= 2 OR v_max_xe_trong_ky >= 2 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Loi: Moi sinh vien chi duoc dang ky toi da 2 xe ve thang con hieu luc!';
    END IF;
END$$

-- ----------------------------------------------------------------------------
-- TRIGGER BẢNG LUOT_RA_VAO_XE: Kiểm tra hạn vé & Tự động tính phí 0đ / 3.000đ
-- ----------------------------------------------------------------------------
CREATE TRIGGER trg_luot_xe_bi
BEFORE INSERT ON LUOT_RA_VAO_XE
FOR EACH ROW
BEGIN
    DECLARE v_hop_le INT DEFAULT 0;
    DECLARE v_so_luot_truoc INT DEFAULT 0;
    DECLARE v_thoi_diem_cuoi DATETIME DEFAULT NULL;

    SELECT COUNT(*) INTO v_hop_le
    FROM DANGKY_XE_THANG d
    WHERE d.MaDKXe = NEW.MaDKXe
      AND DATE(NEW.ThoiDiem) >= d.NgayBatDau
      AND DATE(NEW.ThoiDiem) <= COALESCE(d.NgayKetThuc, '9999-12-31');

    IF v_hop_le = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Loi: Thoi diem gui/lay xe khong nam trong thoi han hieu luc cua ve thang!';
    END IF;

    SELECT MAX(l.ThoiDiem) INTO v_thoi_diem_cuoi
    FROM LUOT_RA_VAO_XE l
    WHERE l.MaDKXe = NEW.MaDKXe
      AND DATE(l.ThoiDiem) = DATE(NEW.ThoiDiem);

    IF v_thoi_diem_cuoi IS NOT NULL AND NEW.ThoiDiem < v_thoi_diem_cuoi THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Loi: Phai nhap luot xe theo thu tu thoi gian trong ngay!';
    END IF;

    SELECT COUNT(*) INTO v_so_luot_truoc
    FROM LUOT_RA_VAO_XE l
    WHERE l.MaDKXe = NEW.MaDKXe
      AND DATE(l.ThoiDiem) = DATE(NEW.ThoiDiem)
      AND l.ThoiDiem <= NEW.ThoiDiem;

    IF v_so_luot_truoc < 2 THEN
        SET NEW.PhiPhatSinh = 0;
    ELSE
        SET NEW.PhiPhatSinh = 3000;
    END IF;
END$$

CREATE TRIGGER trg_luot_xe_bu
BEFORE UPDATE ON LUOT_RA_VAO_XE
FOR EACH ROW
BEGIN
    DECLARE v_hop_le INT DEFAULT 0;
    DECLARE v_so_luot_truoc INT DEFAULT 0;

    IF NEW.MaDKXe <> OLD.MaDKXe OR NEW.ThoiDiem <> OLD.ThoiDiem THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Loi: Khong duoc sua MaDKXe/ThoiDiem cua nhat ky quet xe!';
    END IF;

    SELECT COUNT(*) INTO v_hop_le
    FROM DANGKY_XE_THANG d
    WHERE d.MaDKXe = NEW.MaDKXe
      AND DATE(NEW.ThoiDiem) >= d.NgayBatDau
      AND DATE(NEW.ThoiDiem) <= COALESCE(d.NgayKetThuc, '9999-12-31');

    IF v_hop_le = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Loi: Thoi diem gui/lay xe khong nam trong thoi han hieu luc cua ve thang!';
    END IF;

    SELECT COUNT(*) INTO v_so_luot_truoc
    FROM LUOT_RA_VAO_XE l
    WHERE l.MaDKXe = NEW.MaDKXe
      AND DATE(l.ThoiDiem) = DATE(NEW.ThoiDiem)
      AND l.MaLuot <> OLD.MaLuot
      AND (l.ThoiDiem < NEW.ThoiDiem
           OR (l.ThoiDiem = NEW.ThoiDiem AND l.MaLuot < OLD.MaLuot));

    IF v_so_luot_truoc < 2 THEN
        SET NEW.PhiPhatSinh = 0;
    ELSE
        SET NEW.PhiPhatSinh = 3000;
    END IF;
END$$

CREATE TRIGGER trg_luot_xe_bd
BEFORE DELETE ON LUOT_RA_VAO_XE
FOR EACH ROW
BEGIN
    DECLARE v_so_luot_sau INT DEFAULT 0;

    SELECT COUNT(*) INTO v_so_luot_sau
    FROM LUOT_RA_VAO_XE l
    WHERE l.MaDKXe = OLD.MaDKXe
      AND DATE(l.ThoiDiem) = DATE(OLD.ThoiDiem)
      AND (l.ThoiDiem > OLD.ThoiDiem
           OR (l.ThoiDiem = OLD.ThoiDiem AND l.MaLuot > OLD.MaLuot));

    IF v_so_luot_sau > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Loi: Chi duoc xoa luot xe cuoi cung trong ngay de tranh sai phi cac luot sau!';
    END IF;
END$$

-- ----------------------------------------------------------------------------
-- TRIGGER BẢNG HOADON & CHITIET_HOADON: Đồng bộ tự động tổng tiền & kiểm tra chéo
-- ----------------------------------------------------------------------------
CREATE TRIGGER trg_hoadon_bi
BEFORE INSERT ON HOADON
FOR EACH ROW
BEGIN
    SET NEW.TongTien = 0;
END$$

CREATE TRIGGER trg_cthd_bi
BEFORE INSERT ON CHITIET_HOADON
FOR EACH ROW
BEGIN
    DECLARE v_sv_hoadon VARCHAR(20) DEFAULT NULL;
    DECLARE v_sv_nguon VARCHAR(20) DEFAULT NULL;
    DECLARE v_thang INT DEFAULT NULL;
    DECLARE v_nam INT DEFAULT NULL;
    DECLARE v_ngay_dau DATE;
    DECLARE v_ngay_cuoi DATE;
    DECLARE v_so_luong DECIMAL(10,2) DEFAULT 1;
    DECLARE v_don_gia DECIMAL(12,2) DEFAULT NULL;
    DECLARE v_so_dang_ky INT DEFAULT 0;
    DECLARE v_tong_gia_xe DECIMAL(12,2) DEFAULT 0;
    DECLARE v_not_found BOOLEAN DEFAULT FALSE;
    DECLARE v_da_co INT DEFAULT 0;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_not_found = TRUE;

    SELECT MaSV, Thang, Nam
      INTO v_sv_hoadon, v_thang, v_nam
    FROM HOADON
    WHERE MaHD = NEW.MaHD;

    IF v_not_found OR v_sv_hoadon IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Hoa don khong ton tai!';
    END IF;

    SET v_ngay_dau = STR_TO_DATE(
        CONCAT(v_nam, '-', LPAD(v_thang, 2, '0'), '-01'), '%Y-%m-%d'
    );
    SET v_ngay_cuoi = LAST_DAY(v_ngay_dau);

    IF NEW.LoaiPhi = 'Phong' THEN

        SET v_not_found = FALSE;
        SELECT MaSV, DonGiaThangApDung
          INTO v_sv_nguon, v_don_gia
        FROM DANGKY_O
        WHERE MaDKO = NEW.MaDKO
          AND NgayBatDau <= v_ngay_cuoi
          AND COALESCE(NgayKetThuc, '9999-12-31') >= v_ngay_dau;

        IF v_not_found THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Dang ky o khong hop le trong thang hoa don!';
        END IF;

        SET v_so_luong = 1;

    ELSEIF NEW.LoaiPhi = 'DichVu' THEN

        SET v_not_found = FALSE;
        SELECT MaSV, SoLuong, DonGiaApDung
          INTO v_sv_nguon, v_so_luong, v_don_gia
        FROM SUDUNG_DV
        WHERE MaSuDung = NEW.MaSuDung
          AND ThoiDiemSuDung >= v_ngay_dau
          AND ThoiDiemSuDung < v_ngay_cuoi + INTERVAL 1 DAY;

        IF v_not_found THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Luot su dung dich vu khong thuoc thang hoa don!';
        END IF;

    ELSEIF NEW.LoaiPhi = 'XeThang' THEN

        SELECT COUNT(*), COALESCE(SUM(DonGiaThangApDung), 0)
          INTO v_so_dang_ky, v_tong_gia_xe
        FROM DANGKY_XE_THANG
        WHERE MaSV = v_sv_hoadon
          AND NgayBatDau <= v_ngay_cuoi
          AND COALESCE(NgayKetThuc, '9999-12-31') >= v_ngay_dau;

        IF v_so_dang_ky = 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Sinh vien khong co dang ky xe thang trong ky hoa don!';
        END IF;

        SELECT COUNT(*) INTO v_da_co
        FROM CHITIET_HOADON
        WHERE MaHD = NEW.MaHD AND LoaiPhi = 'XeThang';

        IF v_da_co > 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Hoa don nay da co dong phi xe thang (da gop tat ca xe cua sinh vien)!';
        END IF;

        SET v_sv_nguon = v_sv_hoadon;
        SET v_so_luong = 1;
        SET v_don_gia = v_tong_gia_xe;

    ELSEIF NEW.LoaiPhi = 'XePhatSinh' THEN

        SET v_not_found = FALSE;
        SELECT dk.MaSV, l.PhiPhatSinh
          INTO v_sv_nguon, v_don_gia
        FROM LUOT_RA_VAO_XE l
        JOIN DANGKY_XE_THANG dk ON dk.MaDKXe = l.MaDKXe
        WHERE l.MaLuot = NEW.MaLuot
          AND l.PhiPhatSinh = 3000
          AND l.ThoiDiem >= v_ngay_dau
          AND l.ThoiDiem < v_ngay_cuoi + INTERVAL 1 DAY;

        IF v_not_found THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Luot ra vao xe khong thuoc thang hoa don hoac khong phat sinh phi 3000d!';
        END IF;

        SET v_so_luong = 1;

    END IF;

    IF v_sv_nguon IS NULL OR v_sv_nguon <> v_sv_hoadon THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Nguon phi khong thuoc sinh vien cua hoa don!';
    END IF;

    IF v_so_luong IS NULL OR v_so_luong <= 0
       OR v_don_gia IS NULL OR v_don_gia < 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'So luong hoac don gia khong hop le!';
    END IF;

    SET NEW.SoLuong = v_so_luong;
    SET NEW.DonGiaApDung = v_don_gia;
    SET NEW.ThanhTien = ROUND(NEW.SoLuong * NEW.DonGiaApDung, 2);
END$$

CREATE TRIGGER trg_cthd_bu
BEFORE UPDATE ON CHITIET_HOADON
FOR EACH ROW
BEGIN
    DECLARE v_sv_hoadon VARCHAR(20) DEFAULT NULL;
    DECLARE v_sv_nguon VARCHAR(20) DEFAULT NULL;
    DECLARE v_thang INT DEFAULT NULL;
    DECLARE v_nam INT DEFAULT NULL;
    DECLARE v_ngay_dau DATE;
    DECLARE v_ngay_cuoi DATE;
    DECLARE v_so_luong DECIMAL(10,2) DEFAULT 1;
    DECLARE v_don_gia DECIMAL(12,2) DEFAULT NULL;
    DECLARE v_so_dang_ky INT DEFAULT 0;
    DECLARE v_tong_gia_xe DECIMAL(12,2) DEFAULT 0;
    DECLARE v_not_found BOOLEAN DEFAULT FALSE;
    DECLARE v_da_co INT DEFAULT 0;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_not_found = TRUE;

    SELECT MaSV, Thang, Nam
      INTO v_sv_hoadon, v_thang, v_nam
    FROM HOADON
    WHERE MaHD = NEW.MaHD;

    IF v_not_found OR v_sv_hoadon IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Hoa don khong ton tai!';
    END IF;

    SET v_ngay_dau = STR_TO_DATE(
        CONCAT(v_nam, '-', LPAD(v_thang, 2, '0'), '-01'), '%Y-%m-%d'
    );
    SET v_ngay_cuoi = LAST_DAY(v_ngay_dau);

    IF NEW.LoaiPhi = 'Phong' THEN

        SET v_not_found = FALSE;
        SELECT MaSV, DonGiaThangApDung
          INTO v_sv_nguon, v_don_gia
        FROM DANGKY_O
        WHERE MaDKO = NEW.MaDKO
          AND NgayBatDau <= v_ngay_cuoi
          AND COALESCE(NgayKetThuc, '9999-12-31') >= v_ngay_dau;

        IF v_not_found THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Dang ky o khong hop le trong thang hoa don!';
        END IF;

        SET v_so_luong = 1;

    ELSEIF NEW.LoaiPhi = 'DichVu' THEN

        SET v_not_found = FALSE;
        SELECT MaSV, SoLuong, DonGiaApDung
          INTO v_sv_nguon, v_so_luong, v_don_gia
        FROM SUDUNG_DV
        WHERE MaSuDung = NEW.MaSuDung
          AND ThoiDiemSuDung >= v_ngay_dau
          AND ThoiDiemSuDung < v_ngay_cuoi + INTERVAL 1 DAY;

        IF v_not_found THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Luot su dung dich vu khong thuoc thang hoa don!';
        END IF;

    ELSEIF NEW.LoaiPhi = 'XeThang' THEN

        SELECT COUNT(*), COALESCE(SUM(DonGiaThangApDung), 0)
          INTO v_so_dang_ky, v_tong_gia_xe
        FROM DANGKY_XE_THANG
        WHERE MaSV = v_sv_hoadon
          AND NgayBatDau <= v_ngay_cuoi
          AND COALESCE(NgayKetThuc, '9999-12-31') >= v_ngay_dau;

        IF v_so_dang_ky = 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Sinh vien khong co dang ky xe thang trong ky hoa don!';
        END IF;

        SELECT COUNT(*) INTO v_da_co
        FROM CHITIET_HOADON
        WHERE MaHD = NEW.MaHD AND LoaiPhi = 'XeThang' AND MaCTHD <> OLD.MaCTHD;

        IF v_da_co > 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Hoa don nay da co dong phi xe thang (da gop tat ca xe cua sinh vien)!';
        END IF;

        SET v_sv_nguon = v_sv_hoadon;
        SET v_so_luong = 1;
        SET v_don_gia = v_tong_gia_xe;

    ELSEIF NEW.LoaiPhi = 'XePhatSinh' THEN

        SET v_not_found = FALSE;
        SELECT dk.MaSV, l.PhiPhatSinh
          INTO v_sv_nguon, v_don_gia
        FROM LUOT_RA_VAO_XE l
        JOIN DANGKY_XE_THANG dk ON dk.MaDKXe = l.MaDKXe
        WHERE l.MaLuot = NEW.MaLuot
          AND l.PhiPhatSinh = 3000
          AND l.ThoiDiem >= v_ngay_dau
          AND l.ThoiDiem < v_ngay_cuoi + INTERVAL 1 DAY;

        IF v_not_found THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Luot ra vao xe khong thuoc thang hoa don hoac khong phat sinh phi 3000d!';
        END IF;

        SET v_so_luong = 1;

    END IF;

    IF v_sv_nguon IS NULL OR v_sv_nguon <> v_sv_hoadon THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Nguon phi khong thuoc sinh vien cua hoa don!';
    END IF;

    IF v_so_luong IS NULL OR v_so_luong <= 0
       OR v_don_gia IS NULL OR v_don_gia < 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'So luong hoac don gia khong hop le!';
    END IF;

    SET NEW.SoLuong = v_so_luong;
    SET NEW.DonGiaApDung = v_don_gia;
    SET NEW.ThanhTien = ROUND(NEW.SoLuong * NEW.DonGiaApDung, 2);
END$$

CREATE TRIGGER trg_cthd_ai
AFTER INSERT ON CHITIET_HOADON
FOR EACH ROW
BEGIN
    UPDATE HOADON
    SET TongTien = TongTien + NEW.ThanhTien
    WHERE MaHD = NEW.MaHD;
END$$

CREATE TRIGGER trg_cthd_au
AFTER UPDATE ON CHITIET_HOADON
FOR EACH ROW
BEGIN
    IF OLD.MaHD = NEW.MaHD THEN
        UPDATE HOADON
        SET TongTien = TongTien + NEW.ThanhTien - OLD.ThanhTien
        WHERE MaHD = NEW.MaHD;
    ELSE
        UPDATE HOADON
        SET TongTien = TongTien - OLD.ThanhTien
        WHERE MaHD = OLD.MaHD;

        UPDATE HOADON
        SET TongTien = TongTien + NEW.ThanhTien
        WHERE MaHD = NEW.MaHD;
    END IF;
END$$

CREATE TRIGGER trg_cthd_ad
AFTER DELETE ON CHITIET_HOADON
FOR EACH ROW
BEGIN
    UPDATE HOADON
    SET TongTien = TongTien - OLD.ThanhTien
    WHERE MaHD = OLD.MaHD;
END$$

DELIMITER ;

USE KTX;

SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE CHITIET_HOADON; TRUNCATE TABLE HOADON; TRUNCATE TABLE LUOT_RA_VAO_XE;
TRUNCATE TABLE DANGKY_XE_THANG; TRUNCATE TABLE XE; TRUNCATE TABLE SUDUNG_DV; TRUNCATE TABLE DICHVU;
TRUNCATE TABLE LUOT_THAM; TRUNCATE TABLE KHACH; TRUNCATE TABLE DANGKY_O;
TRUNCATE TABLE SINHVIEN; TRUNCATE TABLE PHONG;
SET FOREIGN_KEY_CHECKS = 1;

SET @hn = CURDATE();
SET @hq = DATE_SUB(CURDATE(), INTERVAL 1 DAY);

INSERT INTO PHONG VALUES
 ('P101', 'Thường', 500000, 4), ('P102', 'Thường', 500000, 2), ('P201', 'Chất lượng cao', 900000, 2),('V101','Hoàng Gia',5000000,1);

INSERT INTO SINHVIEN (MaSV, HoTen, GioiTinh, SDT, SoCMT, NgaySinh, Lop, QueQuan) VALUES
 ('B24DCCN001', 'Nguyễn Văn An',  'Nam', '0901234567', '001206000001', '2006-03-21', 'B24CQCN01-B', 'Hà Nam'),
 ('B24DCCN002', 'Trần Thị Bình',  'Nữ',  '0912345678', '001206000002', '2006-07-09', 'B24CQCN02-B', 'Nam Định'),
 ('B24DCCN003', 'Lê Văn Cường',   'Nam', '0987654321', '001205000003', '2005-11-30', 'B24CQCN03-B', 'Thanh Hóa'),
 ('B24DCCN004', 'Phạm Thị Dung',  'Nữ',  '0933111222', '001206000004', '2006-01-15', 'B24CQCN01-B', 'Hải Dương'),
 ('B24DCCN005', 'Hoàng Minh Đức', 'Nam', '0944555666', '001206000005', '2006-09-02', 'B24CQCN02-B', 'Nghệ An'),
 ('B24DCCN006', 'Vũ Thị Hà',      'Nữ',  NULL,         '001206000006', '2006-05-27', 'B24CQCN03-B', 'Bắc Ninh'),
 ('B24DCCN007', 'Nguyễn Văn A',   'Nam', NULL,         '000000000001', '2006-01-01', 'B24CQCN03-B', 'Hà Nội'),
 ('B24DCCN008', 'Nguyễn Văn B',   'Nam', NULL,         '000000000002', '2006-01-01', 'B24CQCN03-B', 'Hà Nội'),
 ('B24DCCN009', 'Nguyễn Văn C',   'Nam', NULL,         '000000000003', '2006-01-01', 'B24CQCN03-B', 'Hà Lội');

INSERT INTO DANGKY_O (MaSV, SoPhong, NgayBatDau, NgayKetThuc, DonGiaThangApDung) VALUES
 ('B24DCCN001', 'P101', DATE_SUB(@hn, INTERVAL 60 DAY), NULL, 500000),
 ('B24DCCN003', 'P101', DATE_SUB(@hn, INTERVAL 60 DAY), NULL, 500000),
 ('B24DCCN005', 'P101', DATE_SUB(@hn, INTERVAL 50 DAY), NULL, 500000),
 ('B24DCCN002', 'P102', DATE_SUB(@hn, INTERVAL 60 DAY), NULL, 500000),
 ('B24DCCN004', 'P102', DATE_SUB(@hn, INTERVAL 45 DAY), NULL, 500000),
 ('B24DCCN008', 'V101', DATE_SUB(@hn, INTERVAL 60 DAY), NULL, 5000000);

INSERT INTO KHACH (CMTKhach, HoTen, NgaySinh, SDT) VALUES
 ('038200000001', 'Nguyễn Thị Lan', '1978-05-12', '0903111222'),
 ('038200000002', 'Trần Văn Hùng',  '1980-09-03', '0903333444'),
 ('038200000003', 'Lê Thu Hà',      '2005-02-20', NULL);

INSERT INTO LUOT_THAM (CMTKhach, MaSV, ThoiDiemDen) VALUES
 ('038200000001', 'B24DCCN001', TIMESTAMP(@hn, '09:30:00')),
 ('038200000001', 'B24DCCN001', TIMESTAMP(@hq, '08:15:00')),
 ('038200000002', 'B24DCCN002', TIMESTAMP(DATE_SUB(@hn, INTERVAL 2 DAY), '15:00:00')),
 ('038200000003', 'B24DCCN001', TIMESTAMP(DATE_SUB(@hn, INTERVAL 9 DAY), '18:20:00')),
 ('038200000002', 'B24DCCN002', TIMESTAMP(DATE_SUB(@hn, INTERVAL 40 DAY), '10:00:00')),
 ('038200000001', 'B24DCCN003', TIMESTAMP(@hn, '14:45:00'));

INSERT INTO DICHVU (MaDV, TenDV, LoaiDV, DonGia, DonViTinh) VALUES
 ('DV01', 'Giặt là', 'Giặt là', 15000, 'kg'), ('DV02', 'Ăn uống', 'Ăn uống', 30000, 'suất'),
 ('DV03', 'Trông xe vãng lai', 'Trông xe', 3000, 'lượt'), ('DV04', 'Cho thuê xe', 'Cho thuê xe', 50000, 'lần');

-- DonGiaApDung để trống: trigger trg_sudung_dv_bi tự lấy từ DICHVU
INSERT INTO SUDUNG_DV (MaSV, MaDV, ThoiDiemSuDung, SoLuong) VALUES
 ('B24DCCN001', 'DV01', TIMESTAMP(DATE_SUB(@hn, INTERVAL 20 DAY), '18:00:00'), 3),
 ('B24DCCN001', 'DV02', TIMESTAMP(DATE_SUB(@hn, INTERVAL 18 DAY), '12:00:00'), 4),
 ('B24DCCN001', 'DV02', TIMESTAMP(DATE_SUB(@hn, INTERVAL 10 DAY), '12:10:00'), 2),
 ('B24DCCN002', 'DV01', TIMESTAMP(DATE_SUB(@hn, INTERVAL 15 DAY), '19:00:00'), 2),
 ('B24DCCN002', 'DV04', TIMESTAMP(DATE_SUB(@hn, INTERVAL 12 DAY), '09:00:00'), 1),
 ('B24DCCN002', 'DV02', TIMESTAMP(DATE_SUB(@hn, INTERVAL 5 DAY),  '18:30:00'), 3),
 ('B24DCCN003', 'DV02', TIMESTAMP(DATE_SUB(@hn, INTERVAL 22 DAY), '12:00:00'), 5),
 ('B24DCCN003', 'DV03', TIMESTAMP(DATE_SUB(@hn, INTERVAL 3 DAY),  '07:30:00'), 2),
 ('B24DCCN003', 'DV01', TIMESTAMP(DATE_SUB(@hn, INTERVAL 45 DAY), '20:00:00'), 4),
 ('B24DCCN001', 'DV04', TIMESTAMP(@hq, '15:00:00'), 2),
 ('B24DCCN004', 'DV02', TIMESTAMP(@hn, '12:00:00'), 1),
 ('B24DCCN005', 'DV01', TIMESTAMP(DATE_SUB(@hn, INTERVAL 2 DAY), '19:30:00'), 2);

INSERT INTO XE (BienSo, LoaiXe) VALUES
 ('29A1-12345', 'Xe máy'), ('29B2-67890', 'Xe máy'), ('XD-B24DCCN001', 'Xe đạp'), ('29MD-11111', 'Xe điện');

-- NgayKetThuc NULL = vé còn hiệu lực. B24DCCN001 đủ 2 xe; vé 29MD-11111 của B24DCCN003 đã hủy.
INSERT INTO DANGKY_XE_THANG (MaSV, BienSo, NgayBatDau, NgayKetThuc, DonGiaThangApDung) VALUES
 ('B24DCCN001', '29A1-12345',    DATE_SUB(@hn, INTERVAL 40 DAY), NULL, 100000),
 ('B24DCCN001', 'XD-B24DCCN001', DATE_SUB(@hn, INTERVAL 40 DAY), NULL, 100000),
 ('B24DCCN002', '29B2-67890',    DATE_SUB(@hn, INTERVAL 30 DAY), NULL, 100000),
 ('B24DCCN003', '29MD-11111',    DATE_SUB(@hn, INTERVAL 45 DAY), DATE_SUB(@hn, INTERVAL 30 DAY), 100000);

-- PhiPhatSinh do trigger tự tính: hôm qua xe 29A1-12345 có lượt 3 và 4 mất 3.000đ; hôm nay đã 2 lượt
INSERT INTO LUOT_RA_VAO_XE (MaDKXe, ThoiDiem, LoaiHanhDong) VALUES
 (1, TIMESTAMP(@hq, '06:50:00'), 'Gui'), (1, TIMESTAMP(@hq, '07:30:00'), 'Lay'),
 (1, TIMESTAMP(@hq, '12:00:00'), 'Gui'), (1, TIMESTAMP(@hq, '12:30:00'), 'Lay'),
 (2, TIMESTAMP(@hq, '07:05:00'), 'Gui'), (2, TIMESTAMP(@hq, '17:20:00'), 'Lay'),
 (3, TIMESTAMP(@hq, '07:10:00'), 'Gui'), (3, TIMESTAMP(@hq, '17:25:00'), 'Lay'),
 (1, TIMESTAMP(@hn, '06:50:00'), 'Gui'), (1, TIMESTAMP(@hn, '07:30:00'), 'Lay');

-- Ba hóa đơn mẫu của tháng chạy file: An, Bình đã thanh toán; Cường chưa thanh toán.
-- Chỉ lấy các khoản thu thuộc kỳ hóa đơn, kể cả khi chạy vào đầu tháng/đầu năm.
SET @dau_ky_hd = CAST(DATE_FORMAT(@hn, '%Y-%m-01') AS DATE);
SET @cuoi_ky_hd = LAST_DAY(@hn);

START TRANSACTION;

INSERT INTO HOADON (MaSV, Thang, Nam, TrangThai) VALUES
 ('B24DCCN001', MONTH(@hn), YEAR(@hn), 'DaThanhToan'),
 ('B24DCCN002', MONTH(@hn), YEAR(@hn), 'DaThanhToan'),
 ('B24DCCN003', MONTH(@hn), YEAR(@hn), 'ChuaThanhToan');

DROP TEMPORARY TABLE IF EXISTS tmp_hoadon_mau;

CREATE TEMPORARY TABLE tmp_hoadon_mau AS
SELECT MaHD, MaSV, Thang, Nam
FROM HOADON
WHERE Thang = MONTH(@hn) AND Nam = YEAR(@hn);

-- DonGiaApDung truyền 0 làm giá trị ban đầu; trigger trg_cthd_bi lấy lại giá
-- và số lượng từ nguồn, tính ThanhTien; trigger trg_cthd_ai cộng vào TongTien.
-- Tiền phòng: tính đủ một tháng cho mỗi đăng ký ở giao với kỳ hóa đơn.
INSERT INTO CHITIET_HOADON (MaHD, LoaiPhi, DienGiai, SoLuong, DonGiaApDung, MaDKO)
SELECT h.MaHD, 'Phong', CONCAT('Tiền phòng ', d.SoPhong, ' (tính chẵn tháng)'),
       1, 0, d.MaDKO
FROM tmp_hoadon_mau h
JOIN DANGKY_O d ON d.MaSV = h.MaSV
WHERE h.Thang = MONTH(@hn) AND h.Nam = YEAR(@hn)
  AND d.NgayBatDau <= @cuoi_ky_hd
  AND COALESCE(d.NgayKetThuc, '9999-12-31') >= @dau_ky_hd;

-- Dịch vụ: mỗi lượt sử dụng trong tháng là một dòng chi tiết có MaSuDung.
INSERT INTO CHITIET_HOADON (MaHD, LoaiPhi, DienGiai, SoLuong, DonGiaApDung, MaSuDung)
SELECT h.MaHD, 'DichVu', CONCAT('Dịch vụ ', v.TenDV), 1, 0, u.MaSuDung
FROM tmp_hoadon_mau h
JOIN SUDUNG_DV u ON u.MaSV = h.MaSV
JOIN DICHVU v ON v.MaDV = u.MaDV
WHERE h.Thang = MONTH(@hn) AND h.Nam = YEAR(@hn)
  AND u.ThoiDiemSuDung >= @dau_ky_hd
  AND u.ThoiDiemSuDung < @cuoi_ky_hd + INTERVAL 1 DAY;

-- Vé tháng: đúng một dòng/hóa đơn; trigger tự cộng giá của tất cả vé trong kỳ.
INSERT INTO CHITIET_HOADON (MaHD, LoaiPhi, DienGiai, SoLuong, DonGiaApDung)
SELECT h.MaHD, 'XeThang', 'Phí vé tháng xe (gộp tất cả xe)', 1, 0
FROM tmp_hoadon_mau h
WHERE h.Thang = MONTH(@hn) AND h.Nam = YEAR(@hn)
  AND EXISTS (
      SELECT 1 FROM DANGKY_XE_THANG d
      WHERE d.MaSV = h.MaSV
        AND d.NgayBatDau <= @cuoi_ky_hd
        AND COALESCE(d.NgayKetThuc, '9999-12-31') >= @dau_ky_hd
  );

-- Phí xe phát sinh: chỉ lấy lượt có phí 3.000đ và thuộc tháng hóa đơn.
INSERT INTO CHITIET_HOADON (MaHD, LoaiPhi, DienGiai, SoLuong, DonGiaApDung, MaLuot)
SELECT h.MaHD, 'XePhatSinh', 'Phí gửi/lấy xe phát sinh', 1, 0, l.MaLuot
FROM tmp_hoadon_mau h
JOIN DANGKY_XE_THANG d ON d.MaSV = h.MaSV
JOIN LUOT_RA_VAO_XE l ON l.MaDKXe = d.MaDKXe
WHERE h.Thang = MONTH(@hn) AND h.Nam = YEAR(@hn)
  AND l.PhiPhatSinh = 3000
  AND l.ThoiDiem >= @dau_ky_hd
  AND l.ThoiDiem < @cuoi_ky_hd + INTERVAL 1 DAY;

COMMIT;

-- BTL CSDL - Project 2: Quan ly ky tuc xa
-- Nguoi 2: Bon truy van theo yeu cau YC2
-- Chay sau KTX_phanDDL.sql va du_lieu_mau.sql

USE KTX;
-- Dong bo chuoi trong phien lam viec voi collation cua CSDL.
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;

-- =========================================================
-- TRUY VAN 1: TONG TIEN MOI SINH VIEN PHAI TRA TRONG THANG
-- =========================================================

-- Doi hai gia tri nay de xem thang khac.
SET @thang = MONTH(CURDATE());
SET @nam = YEAR(CURDATE());

-- NULL: xem tat ca; hoac dien ma nhu 'B24DCCN001'.
SET @ma_sv = NULL;
-- Chi can doi NULL thanh 'B24DCCN001' de loc; WHERE tu chuan hoa collation.

SET @dau_thang = STR_TO_DATE(
    CONCAT(@nam, '-', @thang, '-01'),
    '%Y-%c-%d'
);
SET @thang_sau = DATE_ADD(@dau_thang, INTERVAL 1 MONTH);

WITH cac_khoan AS (
    -- 1. Tien phong: dang ky giao voi thang thi tinh du thang.
    SELECT
        MaSV,
        'Phong' AS LoaiPhi,
        DonGiaThangApDung AS ThanhTien
    FROM DANGKY_O
    WHERE NgayBatDau < @thang_sau
      AND (
          NgayKetThuc IS NULL
          OR NgayKetThuc >= @dau_thang
      )

    UNION ALL

    -- 2. Tien dich vu theo gia da luu luc su dung.
    SELECT
        MaSV,
        'DichVu',
        SoLuong * DonGiaApDung
    FROM SUDUNG_DV
    WHERE ThoiDiemSuDung >= @dau_thang
      AND ThoiDiemSuDung < @thang_sau

    UNION ALL

    -- 3. Tien ve thang cua cac xe co hieu luc trong thang.
    SELECT
        MaSV,
        'XeThang',
        DonGiaThangApDung
    FROM DANGKY_XE_THANG
    WHERE NgayBatDau < @thang_sau
      AND (
          NgayKetThuc IS NULL
          OR NgayKetThuc >= @dau_thang
      )

    UNION ALL

    -- 4. Phi gui/lay xe phat sinh.
    SELECT
        d.MaSV,
        'XePhatSinh',
        l.PhiPhatSinh
    FROM LUOT_RA_VAO_XE l
    JOIN DANGKY_XE_THANG d ON d.MaDKXe = l.MaDKXe
    WHERE l.ThoiDiem >= @dau_thang
      AND l.ThoiDiem < @thang_sau
      AND l.PhiPhatSinh > 0
),
tong_theo_sv AS (
    SELECT
        MaSV,
        SUM(CASE WHEN LoaiPhi = 'Phong'
                 THEN ThanhTien ELSE 0 END) AS TienPhong,
        SUM(CASE WHEN LoaiPhi = 'DichVu'
                 THEN ThanhTien ELSE 0 END) AS TienDichVu,
        SUM(CASE WHEN LoaiPhi = 'XeThang'
                 THEN ThanhTien ELSE 0 END) AS TienVeXe,
        SUM(CASE WHEN LoaiPhi = 'XePhatSinh'
                 THEN ThanhTien ELSE 0 END) AS PhiXePhatSinh,
        SUM(ThanhTien) AS TongPhaiTra
    FROM cac_khoan
    GROUP BY MaSV
)
SELECT
    s.MaSV,
    s.HoTen,
    s.SoCMT,
    s.NgaySinh,
    s.Lop,
    s.QueQuan,
    @thang AS Thang,
    @nam AS Nam,
    t.TienPhong,
    t.TienDichVu,
    t.TienVeXe,
    t.PhiXePhatSinh,
    t.TongPhaiTra
FROM SINHVIEN s
JOIN tong_theo_sv t ON t.MaSV = s.MaSV
WHERE @ma_sv IS NULL
   OR s.MaSV = CONVERT(@ma_sv USING utf8mb4) COLLATE utf8mb4_unicode_ci
ORDER BY s.MaSV;

-- =========================================================
-- TRUY VAN 2: TIEN TUNG DICH VU CUA MOI SINH VIEN
-- TRONG KHOANG TU NGAY DEN NGAY
-- =========================================================

SET @tu_ngay = DATE_SUB(CURDATE(), INTERVAL 30 DAY);
SET @den_ngay = CURDATE();

SELECT
    s.MaSV,
    s.HoTen,
    s.Lop,
    v.MaDV,
    v.TenDV,
    v.DonViTinh,
    SUM(u.SoLuong) AS TongSoLuong,
    SUM(u.SoLuong * u.DonGiaApDung) AS TongTien
FROM SUDUNG_DV u
JOIN SINHVIEN s ON s.MaSV = u.MaSV
JOIN DICHVU v ON v.MaDV = u.MaDV
WHERE u.ThoiDiemSuDung >= @tu_ngay
  AND u.ThoiDiemSuDung < DATE_ADD(@den_ngay, INTERVAL 1 DAY)
GROUP BY
    s.MaSV, s.HoTen, s.Lop,
    v.MaDV, v.TenDV, v.DonViTinh
ORDER BY s.MaSV, v.MaDV;

-- =========================================================
-- TRUY VAN 3: SINH VIEN, KHACH THAM VA SO LAN DEN THAM
-- =========================================================

-- Chon 'tuan' hoac 'thang'.
SET @ky_tham = _utf8mb4'thang' COLLATE utf8mb4_unicode_ci;

-- Ngay bat ky nam trong tuan/thang can xem.
SET @ngay_moc = CURDATE();

SET @tu_tham = CASE
    WHEN @ky_tham = 'tuan'
        THEN DATE_SUB(
            @ngay_moc,
            INTERVAL WEEKDAY(@ngay_moc) DAY
        )
    ELSE CAST(DATE_FORMAT(@ngay_moc, '%Y-%m-01') AS DATE)
END;

-- Moc ket thuc khong duoc tinh vao khoang.
SET @den_tham = CASE
    WHEN @ky_tham = 'tuan'
        THEN DATE_ADD(@tu_tham, INTERVAL 7 DAY)
    ELSE DATE_ADD(@tu_tham, INTERVAL 1 MONTH)
END;

SELECT
    s.MaSV,
    s.HoTen AS HoTenSinhVien,
    s.Lop,
    k.CMTKhach,
    k.HoTen AS HoTenKhach,
    k.NgaySinh AS NgaySinhKhach,
    k.SDT AS SDTKhach,
    COUNT(*) AS SoLanDenTham,
    MAX(l.ThoiDiemDen) AS LanDenGanNhat
FROM LUOT_THAM l
JOIN SINHVIEN s ON s.MaSV = l.MaSV
JOIN KHACH k ON k.CMTKhach = l.CMTKhach
WHERE l.ThoiDiemDen >= @tu_tham
  AND l.ThoiDiemDen < @den_tham
GROUP BY
    s.MaSV, s.HoTen, s.Lop,
    k.CMTKhach, k.HoTen, k.NgaySinh, k.SDT
ORDER BY s.MaSV, SoLanDenTham DESC, k.CMTKhach;

-- =========================================================
-- TRUY VAN 4: DOANH THU TUNG DICH VU THEO 12 THANG
-- =========================================================

SET @nam_doanh_thu = YEAR(CURDATE());
SET @dau_nam = MAKEDATE(@nam_doanh_thu, 1);
SET @nam_sau = DATE_ADD(@dau_nam, INTERVAL 1 YEAR);

WITH RECURSIVE cac_thang AS (
    SELECT 1 AS Thang

    UNION ALL

    SELECT Thang + 1
    FROM cac_thang
    WHERE Thang < 12
),
doanh_thu AS (
    SELECT
        MaDV,
        MONTH(ThoiDiemSuDung) AS Thang,
        SUM(SoLuong * DonGiaApDung) AS TongTien
    FROM SUDUNG_DV
    WHERE ThoiDiemSuDung >= @dau_nam
      AND ThoiDiemSuDung < @nam_sau
    GROUP BY MaDV, MONTH(ThoiDiemSuDung)
)
SELECT
    v.MaDV,
    v.TenDV,
    v.DonViTinh,
    @nam_doanh_thu AS Nam,
    t.Thang,
    COALESCE(d.TongTien, 0) AS DoanhThu
FROM DICHVU v
CROSS JOIN cac_thang t
LEFT JOIN doanh_thu d
    ON d.MaDV = v.MaDV
   AND d.Thang = t.Thang
ORDER BY v.MaDV, t.Thang;
