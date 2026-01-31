# Thaichecker - หมากฮอสไทย

โปรแกรมเกมหมากฮอสไทย (Thai Checkers) เขียนด้วย Python รองรับการเล่นแบบ CLI และ GUI

## กติกาเกม

### กระดาน
- ใช้กระดาน 8×8
- เล่นเฉพาะช่องสีดำ (32 ช่อง)

### ตัวหมาก
- ฝั่งละ 8 ตัว (แทน 12 ตัวแบบ checker ปกติ)
- 2 ชนิด:
  - **MAN** (เบี้ย) - แสดงเป็น W หรือ B
  - **KING** (ฮอส) - แสดงเป็น WK หรือ BK

### การเดิน

#### MAN (เบี้ย)
- เดินเฉียงหน้า 1 ช่อง (ซ้าย/ขวา)
- กิน: กระโดดข้ามศัตรู 1 ตัว ลงช่องถัดไป
- รองรับ multi-jump (กินต่อเนื่อง)

#### KING (ฮอส)
- **Flying King**: เดินเฉียงได้ไกลไม่จำกัด
- กิน: ข้ามศัตรู 1 ตัว แล้วลงจอดได้ทุกช่องว่างหลังตัวที่ถูกข้าม (บนแนวทแยงเดียวกัน)
- รองรับ multi-capture

### การเลื่อนขั้น
- MAN ถึงแถวสุดท้ายฝั่งตรงข้าม → เป็น KING

### กติกาพิเศษ
- **การกินเป็นบังคับ**: ถ้ามีการกินได้ ต้องกินเท่านั้น (ไม่สามารถเดินปกติได้)

## โครงสร้างโปรเจค

```
checker/
├── board.py           # คลาสกระดานและตัวหมาก
├── game_logic.py      # กติกาการเดินและการกิน
├── interface_cli.py   # UI แบบ Command Line
├── interface_gui.py   # UI แบบ Pygame (GUI)
├── main.py           # ไฟล์หลักรันเกม
├── requirements.txt  # Python packages
├── Claude.md         # คู่มือกติกาเกม
└── README.md         # ไฟล์นี้
```

## การติดตั้ง

### 1. สร้าง Virtual Environment

```bash
python3 -m venv .venv
```

### 2. Activate Virtual Environment

```bash
source .venv/bin/activate
```

### 3. ติดตั้ง Dependencies

```bash
pip install -r requirements.txt
```

## วิธีการเล่น

### เล่นแบบ GUI (Pygame) - แนะนำ

```bash
python main.py --mode gui
```

หรือ (default คือ GUI)

```bash
python main.py
```

**วิธีเล่น GUI:**
- คลิกเลือกตัวหมากที่ต้องการเดิน
- จุดสีเขียว = ช่องที่เดินได้
- จุดสีแดง = ช่องที่กินได้
- คลิกที่จุดเพื่อเดิน/กิน
- กด ESC เพื่อออก

### เล่นแบบ CLI (Command Line)

```bash
python main.py --mode cli
```

**วิธีเล่น CLI:**
- ใส่ตำแหน่งตัวหมาก (row col) เช่น: `5 2`
- เลือกหมายเลขการเดินที่ต้องการ
- พิมพ์ `q` เพื่อออก
- พิมพ์ `b` เพื่อกลับไปเลือกตัวหมากใหม่

## ตัวอย่างการเล่น

### CLI Example
```
  0 1 2 3 4 5 6 7
0  B  B  B  B
1  B  B  B  B
2
3
4
5
6  W  W  W  W
7  W  W  W  W

ตาของผู้เล่น: ขาว (WHITE)
เลือกตัวหมากที่จะเดิน (row col): 5 0

การเดินที่เป็นไปได้:
  1. เดิน ไป (4, 1)

เลือกการเดิน (ใส่หมายเลข): 1
```

## การพัฒนาเพิ่มเติม

### การเพิ่มฟีเจอร์ใหม่

1. **AI Player** - เพิ่ม AI ด้วย Minimax/Alpha-Beta Pruning
2. **Web API** - ทำเป็น REST API ด้วย Flask/FastAPI
3. **บันทึกเกม** - Save/Load game state
4. **Replay** - ดูการเล่นย้อนหลัง
5. **Online Multiplayer** - เล่นออนไลน์ผ่าน websocket

### การแก้ไขโค้ด

```python
# ตัวอย่าง: เปลี่ยนขนาดกระดาน GUI
# ใน interface_gui.py
SQUARE_SIZE = 80  # เปลี่ยนขนาดช่อง
PIECE_RADIUS = 30  # เปลี่ยนขนาดตัวหมาก
```

## การทดสอบ

### ทดสอบ CLI
```bash
python interface_cli.py
```

### ทดสอบ GUI
```bash
python interface_gui.py
```

## Troubleshooting

### ปัญหา: Pygame ไม่ติดตั้ง
```bash
pip install --upgrade pip
pip install pygame
```

### ปัญหา: Virtual Environment ไม่ทำงาน
```bash
# ลบและสร้างใหม่
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### ปัญหา: หน้าจอ GUI ไม่แสดง (macOS)
- ลองรัน Python จาก Terminal แทน IDE
- ตรวจสอบว่า Pygame รองรับ macOS version

## License

MIT License - ใช้งานและแก้ไขได้อย่างอิสระ

## Credits

พัฒนาโดย Claude Code
กติกาตาม Thaichecker (หมากฮอสไทย) แบบดั้งเดิม

---

**Happy Playing! สนุกกับการเล่นหมากฮอสไทย!**
