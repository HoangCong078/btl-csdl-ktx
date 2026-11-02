-- ============================================================================
-- PROJECT 2: HỆ THỐNG QUẢN LÝ KÝ TÚC XÁ SINH VIÊN
-- File: KTX_phanDDL.sql
-- Phân việc: Người 1 (Trưởng nhóm) - DDL + Ràng buộc toàn vẹn + Trigger nghiệp vụ
-- Hệ QTCSDL: MySQL 8.0.16+
-- Schema chuẩn: Khớp 100% với BAO_CAO_YC1.pdf và thuc_the_va_thuoc_tinh_FIXED_2.docx (12 bảng)
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
    CONSTRAINT fk_cthd_dko FOREIGN KEY (MaDKO)
        REFERENCES DANGKY_O(MaDKO)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_cthd_sudung FOREIGN KEY (MaSuDung)
        REFERENCES SUDUNG_DV(MaSuDung)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_cthd_luotxe FOREIGN KEY (MaLuot)
        REFERENCES LUOT_RA_VAO_XE(MaLuot)
        ON UPDATE CASCADE ON DELETE RESTRICT,
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
    DECLARE v_hop_le_xe INT DEFAULT 0;

    SELECT MaSV INTO v_sv_hoadon
    FROM HOADON
    WHERE MaHD = NEW.MaHD;

    IF NEW.LoaiPhi = 'Phong' THEN
        SELECT d.MaSV INTO v_sv_nguon
        FROM DANGKY_O d
        JOIN HOADON h ON h.MaHD = NEW.MaHD
        WHERE d.MaDKO = NEW.MaDKO
          AND d.NgayBatDau <= LAST_DAY(STR_TO_DATE(CONCAT(h.Nam, '-', LPAD(h.Thang, 2, '0'), '-01'), '%Y-%m-%d'))
          AND COALESCE(d.NgayKetThuc, '9999-12-31') >= STR_TO_DATE(CONCAT(h.Nam, '-', LPAD(h.Thang, 2, '0'), '-01'), '%Y-%m-%d');

    ELSEIF NEW.LoaiPhi = 'DichVu' THEN
        SELECT sd.MaSV INTO v_sv_nguon
        FROM SUDUNG_DV sd
        JOIN HOADON h ON h.MaHD = NEW.MaHD
        WHERE sd.MaSuDung = NEW.MaSuDung
          AND YEAR(sd.ThoiDiemSuDung) = h.Nam
          AND MONTH(sd.ThoiDiemSuDung) = h.Thang;

    ELSEIF NEW.LoaiPhi = 'XeThang' THEN
        SELECT COUNT(*) INTO v_hop_le_xe
        FROM DANGKY_XE_THANG d
        JOIN HOADON h ON h.MaHD = NEW.MaHD
        WHERE d.MaSV = h.MaSV
          AND d.NgayBatDau <= LAST_DAY(STR_TO_DATE(CONCAT(h.Nam, '-', LPAD(h.Thang, 2, '0'), '-01'), '%Y-%m-%d'))
          AND COALESCE(d.NgayKetThuc, '9999-12-31') >= STR_TO_DATE(CONCAT(h.Nam, '-', LPAD(h.Thang, 2, '0'), '-01'), '%Y-%m-%d');

        IF v_hop_le_xe > 0 THEN
            SET v_sv_nguon = v_sv_hoadon;
        END IF;

    ELSEIF NEW.LoaiPhi = 'XePhatSinh' THEN
        -- Ánh xạ 1:1 theo MaLuot với lượt quẹt thực tế phát sinh 3.000đ trong kỳ hóa đơn
        SELECT dk.MaSV INTO v_sv_nguon
        FROM LUOT_RA_VAO_XE l
        JOIN DANGKY_XE_THANG dk ON dk.MaDKXe = l.MaDKXe
        JOIN HOADON h ON h.MaHD = NEW.MaHD
        WHERE l.MaLuot = NEW.MaLuot
          AND l.PhiPhatSinh = 3000
          AND YEAR(l.ThoiDiem) = h.Nam
          AND MONTH(l.ThoiDiem) = h.Thang;
    END IF;

    IF v_sv_hoadon IS NULL OR v_sv_nguon IS NULL OR v_sv_nguon <> v_sv_hoadon THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Loi: Khoan phi khong thuoc sinh vien/ky hoa don hoac khong phat sinh chi phi!';
    END IF;

    SET NEW.ThanhTien = ROUND(NEW.SoLuong * NEW.DonGiaApDung, 2);
END$$

CREATE TRIGGER trg_cthd_bu
BEFORE UPDATE ON CHITIET_HOADON
FOR EACH ROW
BEGIN
    DECLARE v_sv_hoadon VARCHAR(20) DEFAULT NULL;
    DECLARE v_sv_nguon VARCHAR(20) DEFAULT NULL;
    DECLARE v_hop_le_xe INT DEFAULT 0;

    SELECT MaSV INTO v_sv_hoadon
    FROM HOADON
    WHERE MaHD = NEW.MaHD;

    IF NEW.LoaiPhi = 'Phong' THEN
        SELECT d.MaSV INTO v_sv_nguon
        FROM DANGKY_O d
        JOIN HOADON h ON h.MaHD = NEW.MaHD
        WHERE d.MaDKO = NEW.MaDKO
          AND d.NgayBatDau <= LAST_DAY(STR_TO_DATE(CONCAT(h.Nam, '-', LPAD(h.Thang, 2, '0'), '-01'), '%Y-%m-%d'))
          AND COALESCE(d.NgayKetThuc, '9999-12-31') >= STR_TO_DATE(CONCAT(h.Nam, '-', LPAD(h.Thang, 2, '0'), '-01'), '%Y-%m-%d');

    ELSEIF NEW.LoaiPhi = 'DichVu' THEN
        SELECT sd.MaSV INTO v_sv_nguon
        FROM SUDUNG_DV sd
        JOIN HOADON h ON h.MaHD = NEW.MaHD
        WHERE sd.MaSuDung = NEW.MaSuDung
          AND YEAR(sd.ThoiDiemSuDung) = h.Nam
          AND MONTH(sd.ThoiDiemSuDung) = h.Thang;

    ELSEIF NEW.LoaiPhi = 'XeThang' THEN
        SELECT COUNT(*) INTO v_hop_le_xe
        FROM DANGKY_XE_THANG d
        JOIN HOADON h ON h.MaHD = NEW.MaHD
        WHERE d.MaSV = h.MaSV
          AND d.NgayBatDau <= LAST_DAY(STR_TO_DATE(CONCAT(h.Nam, '-', LPAD(h.Thang, 2, '0'), '-01'), '%Y-%m-%d'))
          AND COALESCE(d.NgayKetThuc, '9999-12-31') >= STR_TO_DATE(CONCAT(h.Nam, '-', LPAD(h.Thang, 2, '0'), '-01'), '%Y-%m-%d');

        IF v_hop_le_xe > 0 THEN
            SET v_sv_nguon = v_sv_hoadon;
        END IF;

    ELSEIF NEW.LoaiPhi = 'XePhatSinh' THEN
        SELECT dk.MaSV INTO v_sv_nguon
        FROM LUOT_RA_VAO_XE l
        JOIN DANGKY_XE_THANG dk ON dk.MaDKXe = l.MaDKXe
        JOIN HOADON h ON h.MaHD = NEW.MaHD
        WHERE l.MaLuot = NEW.MaLuot
          AND l.PhiPhatSinh = 3000
          AND YEAR(l.ThoiDiem) = h.Nam
          AND MONTH(l.ThoiDiem) = h.Thang;
    END IF;

    IF v_sv_hoadon IS NULL OR v_sv_nguon IS NULL OR v_sv_nguon <> v_sv_hoadon THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Loi: Khoan phi khong thuoc sinh vien/ky hoa don hoac khong phat sinh chi phi!';
    END IF;

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