#!/usr/bin/env python

"""

Project: SC2 Replay Auto Fixer (星际2录像自动修复工具)
Author: [木马冰河 ]
Contact: [born79230]
Description: 自动监控并修复星际争霸2国服损坏的录像文件
Based on logic from: ProbiusOfficial/StarCraft2-CN-Replay-Repair

"""

# -*- coding: utf-8 -*-
import os
import time
import sys
import ctypes.wintypes

# ==========================================
# 核心设置 (Core Settings)
SEARCH_BYTES = b'\x09\x00\x04\x09\x00\x06\x09\x00'
TARGET_BYTES = b'\x09\x0A\x04\x09\x00\x06\x09\x1E'


# ==========================================

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")


def get_real_documents_path():
    """获取‘我的文档’真实路径"""
    try:
        CSIDL_PERSONAL = 5
        SHGFP_TYPE_CURRENT = 0
        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
        return buf.value
    except:
        return None


def find_sc2_root():
    """
    直接寻找 StarCraft II 总文件夹 (Find StarCraft II root folder)
    """
    log("🔍 正在搜索 StarCraft II 总目录... (Searching for StarCraft II root folder...)")

    possible_roots = []
    doc_path = get_real_documents_path()
    if doc_path: possible_roots.append(doc_path)

    user_home = os.path.expanduser("~")
    possible_roots.extend([
        os.path.join(user_home, "Documents"),
        os.path.join(user_home, "OneDrive", "Documents"),
        r"D:\Documents",
        r"E:\Documents"
    ])

    for root_doc in possible_roots:
        if not root_doc or not os.path.exists(root_doc):
            continue

        sc2_path = os.path.join(root_doc, "StarCraft II")
        # 只要找到了 StarCraft II 文件夹，立刻锁定，不再往下找 Replays 了
        if os.path.exists(sc2_path):
            log(f"✅ 锁定监控目标 (Target Locked): {sc2_path}")
            return sc2_path

    log("❌ 无法自动找到 StarCraft II 文件夹。(Could not find StarCraft II folder.)")
    return None


def get_all_replay_files(root_folder):
    """
    递归扫描所有子文件夹 (Recursively scan all subdirectories)
    """
    all_files = set()
    try:
        # 遍历整个 StarCraft II 文件夹
        for folder_path, dirs, files in os.walk(root_folder):
            for file in files:
                if file.endswith(".SC2Replay") and "_fixed" not in file:
                    full_path = os.path.join(folder_path, file)
                    all_files.add(full_path)
    except Exception as e:
        pass
    return all_files


def fix_replay(file_path):
    try:
        with open(file_path, 'rb') as f:
            content = bytearray(f.read())

        scan_limit = min(len(content), 128)
        offset = content.find(SEARCH_BYTES, 0, scan_limit)

        if offset != -1:
            for i in range(len(TARGET_BYTES)):
                content[offset + i] = TARGET_BYTES[i]

            folder = os.path.dirname(file_path)
            original_name = os.path.basename(file_path)
            new_name = os.path.splitext(original_name)[0] + "_fixed.SC2Replay"
            new_path = os.path.join(folder, new_name)

            with open(new_path, 'wb') as f:
                f.write(content)

            # 显示相对路径，让你知道是在哪修好的
            # Get relative path for display
            try:
                display_path = os.path.relpath(new_path, start=os.path.dirname(os.path.dirname(file_path)))
            except:
                display_path = new_name

            log(f"⚡ [修复成功 Fixed] ...\\{display_path}")
            return True
        return False
    except Exception as e:
        log(f"⚠️ [Error] {e}")
        return False


def main():
    sc2_root = find_sc2_root()

    # 手动模式
    if not sc2_root:
        print("\n" + "=" * 50)
        print("💡 自动搜索失败 (Auto-search failed)")
        print("请手动找到你的【StarCraft II】文件夹 (在我的文档里)")
        print("然后把它【拖拽】到这个黑窗口里，再按回车。")
        print("=" * 50 + "\n")
        try:
            if sys.version_info[0] < 3:
                sc2_root = raw_input("路径 Path: ").strip().replace('"', '')
            else:
                sc2_root = input("路径 Path: ").strip().replace('"', '')
        except:
            pass

    if not sc2_root or not os.path.exists(sc2_root):
        log("❌ 路径无效，程序退出。(Invalid path, exiting.)")
        input("按回车键退出...")
        return

    print("-" * 60)
    log(f"📡 根目录级监控已启动 (Root Level Monitor Started)")
    log(f"📂 监控位置: {sc2_root}")
    log("👉 将扫描该目录下所有深度的 .SC2Replay 文件")
    print("-" * 60)

    try:
        existing_files = get_all_replay_files(sc2_root)
        log(f"ℹ️ 扫描完毕，当前共有 {len(existing_files)} 个录像文件")
    except:
        existing_files = set()

    while True:
        try:
            time.sleep(3)
            current_files = get_all_replay_files(sc2_root)
            new_files = current_files - existing_files

            for full_path in new_files:
                time.sleep(1)
                fix_replay(full_path)

            existing_files = current_files

        except KeyboardInterrupt:
            break
        except Exception:
            pass


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter...")

