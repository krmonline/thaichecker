"""
main.py - ไฟล์หลักสำหรับเริ่มเกม Thaichecker
"""

import sys
import argparse


def main():
    """ฟังก์ชันหลักสำหรับเริ่มเกม"""
    parser = argparse.ArgumentParser(description='Thaichecker - หมากฮอสไทย')
    parser.add_argument(
        '--mode',
        choices=['cli', 'gui'],
        default='gui',
        help='เลือก interface mode: cli (command line) หรือ gui (pygame)'
    )

    args = parser.parse_args()

    print("=" * 50)
    print("ยินดีต้อนรับสู่ Thaichecker - หมากฮอสไทย")
    print("=" * 50)

    if args.mode == 'cli':
        print("กำลังเริ่มเกมแบบ Command Line...")
        from interface_cli import CLI
        game = CLI()
        game.run()

    elif args.mode == 'gui':
        print("กำลังเริ่มเกมแบบ GUI (Pygame)...")
        try:
            from interface_gui import GUI
            game = GUI()
            game.run()
        except ImportError as e:
            print(f"Error: ไม่สามารถโหลด Pygame ได้")
            print(f"กรุณาติดตั้ง pygame โดยใช้: pip install pygame")
            print(f"หรือรัน: pip install -r requirements.txt")
            sys.exit(1)


if __name__ == "__main__":
    main()
