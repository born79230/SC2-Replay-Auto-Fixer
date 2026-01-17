# -*- coding: utf-8 -*-
"""
Project: StarCraft 2 Replay Cleaner (星际2录像清洗器)
Author: born79230
Theme: Heart of the Swarm / Abathur
Description: 一次性扫描并修复所有残留的损坏录像，不常驻后台
"""
import os
import time
import sys
import ctypes.wintypes
import msvcrt

# ==========================================
# 🧬 基因序列设置
# ==========================================
SEARCH_BYTES = b'\x09\x00\x04\x09\x00\x06\x09\x00'
TARGET_BYTES = b'\x09\x0A\x04\x09\x00\x06\x09\x1E'


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")


def print_banner():
    print("\n" + "=" * 60)
    print("      🧬  STARCRAFT II REPLAY CLEANER  🧬")
    print("      -----------------------------------")
    print("      👤  Operator : born79230")
    print("      💬  Message  : Patch detected. Adaptation required.")
    print("                      (检测到补丁。需进行适应)")
    print("      ⚔️  Mission  : Purge defective samples.")
    print("                      (清除残次样本)")
    print("=" * 60 + "\n")


def get_real_documents_path():
    try:
        CSIDL_PERSONAL = 5
        SHGFP_TYPE_CURRENT = 0
        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
        return buf.value
    except:
        return None


def find_sc2_root():
    log("👁️‍🗨️ 正在检索主巢位置... (Locating Hive Cluster...)")

    possible_roots = []
    doc_path = get_real_documents_path()
    if doc_path: possible_roots.append(doc_path)

    user_home = os.path.expanduser("~")
    possible_roots.extend([
        os.path.join(user_home, "Documents"),
        os.path.join(user_home, "OneDrive", "Documents"),
        r"D:\Documents", r"E:\Documents"
    ])

    for root_doc in possible_roots:
        if not root_doc or not os.path.exists(root_doc):
            continue
        sc2_path = os.path.join(root_doc, "StarCraft II")
        if os.path.exists(sc2_path):
            log(f"✅ 锁定目标 (Target Verified): {sc2_path}")
            return sc2_path
    log("❌ 无法连接主巢心智。")
    return None


def get_all_replay_files(root_folder):
    all_files = set()
    try:
        for folder_path, dirs, files in os.walk(root_folder):
            for file in files:
                # 依然只找 .SC2Replay 且没有被修复过的
                if file.endswith(".SC2Replay") and "_fixed" not in file:
                    full_path = os.path.join(folder_path, file)
                    all_files.add(full_path)
    except Exception:
        pass
    return all_files


def fix_replay(file_path):
    try:
        folder = os.path.dirname(file_path)
        original_name = os.path.basename(file_path)
        new_name = os.path.splitext(original_name)[0] + "_fixed.SC2Replay"
        new_path = os.path.join(folder, new_name)

        if os.path.exists(new_path):
            return False

        with open(file_path, 'rb') as f:
            content = bytearray(f.read())

        scan_limit = min(len(content), 128)
        offset = content.find(SEARCH_BYTES, 0, scan_limit)

        if offset != -1:
            for i in range(len(TARGET_BYTES)):
                content[offset + i] = TARGET_BYTES[i]

            with open(new_path, 'wb') as f:
                f.write(content)

            try:
                display_path = os.path.relpath(new_path, start=os.path.dirname(os.path.dirname(file_path)))
            except:
                display_path = new_name

            log(f"🧬 [进化完成] ...\\{display_path}")
            return True
        return False
    except Exception:
        return False


def main():
    print_banner()
    time.sleep(1)

    sc2_root = find_sc2_root()
    if not sc2_root:
        print("\n请手动将【StarCraft II】文件夹拖拽至此：")
        try:
            if sys.version_info[0] < 3:
                sc2_root = raw_input("Path: ").strip().replace('"', '')
            else:
                sc2_root = input("Path: ").strip().replace('"', '')
        except:
            pass

    if not sc2_root or not os.path.exists(sc2_root):
        return

    print("-" * 60)
    log(f"📂 扫描区域: {sc2_root}")
    print("-" * 60)

    # 1. 扫描
    all_existing_files = get_all_replay_files(sc2_root)
    count = len(all_existing_files)

    if count == 0:
        log("✅ 未发现残次样本。基因库完美。")
        log("Sequence complete.")
        time.sleep(3)
        return

    log(f"🔎 发现 {count} 个潜在的旧时代样本。")
    print("\n❓ 是否执行批量进化？(Evolve all?)")
    print("   按 [Y] 键确认 | 按 [N] 或其他键退出")

    # 2. 询问 (阻塞式，不倒计时了，等你决定)
    while True:
        if msvcrt.kbhit():
            key = msvcrt.getch().lower()
            if key == b'y':
                print("\n🧬 指令确认。进化开始。")
                break
            else:
                print("\n🛑 操作取消。")
                return
        time.sleep(0.1)

    # 3. 执行修复
    log("🚀 正在重组基因链... (Processing...)")
    fixed_count = 0
    for f in all_existing_files:
        if fix_replay(f):
            fixed_count += 1

    # 4. 结束
    print("-" * 60)
    if fixed_count == 0:
        log("✅ 所有样本此前已进化完毕。")
    else:
        log(f"✅ 进化完成。共处理 {fixed_count} 个样本。")

    log("🏁 任务结束。阿巴瑟离线。")
    print("\n[按任意键退出...]")
    msvcrt.getch()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter...")