#!/usr/bin/env python3
import os
import struct
import random
import lz4.block
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
from dataclasses import dataclass
import threading

@dataclass
class FileEntry:
    name_offset: int; offset: int; compress_size: int; decompress_size: int; paz_index: int; flags: int

def match_lz4_compressed_size(plaintext: bytes, target_comp_size: int, target_orig_size: int, log_fn):
    padding_budget = max(0, target_orig_size - len(plaintext))
    if padding_budget <= 0:
        return plaintext, lz4.block.compress(plaintext, store_size=False)
    
    log_fn(f"    - Calibrating LZ4 (Budget: {padding_budget:,})")
    rng = random.Random(42)
    pool = rng.getrandbits(8 * min(padding_budget, 1024*1024)).to_bytes(min(padding_budget, 1024*1024), 'little')
    if len(pool) < padding_budget: pool = (pool * (padding_budget // len(pool) + 1))[:padding_budget]
    
    low, high = 0, padding_budget
    best_cand = (plaintext, lz4.block.compress(plaintext, store_size=False))
    for _ in range(32):
        nl = (low + high) // 2
        trial = plaintext + pool[:nl] + b"\x00" * (padding_budget - nl)
        packed = lz4.block.compress(trial, store_size=False)
        if len(packed) == target_comp_size: return trial, packed
        if len(packed) < target_comp_size:
            low = nl + 1; best_cand = (trial, packed)
        else:
            high = nl - 1
    return best_cand

def read_pamt(path: Path):
    with path.open("rb") as h:
        h.read(4); p_count, = struct.unpack("<I", h.read(4)); h.read(4 + 12 * p_count)
        d_size, = struct.unpack("<I", h.read(4)); d_data = h.read(d_size)
        n_size, = struct.unpack("<I", h.read(4)); n_names = h.read(n_size)
        h_count, = struct.unpack("<I", h.read(4)); folders = [struct.unpack("<IIII", h.read(16)) for _ in range(h_count)]
        f_count, = struct.unpack("<I", h.read(4)); files = [FileEntry(*struct.unpack("<IIIIHH", h.read(20))) for _ in range(f_count)]
    return d_data, n_names, folders, files

class VfsPathResolver:
    def __init__(self, b): self.b = b
    def get_path(self, off):
        if off == 0xFFFFFFFF or off >= len(self.b): return ""
        parts = []; curr = off
        while curr != 0xFFFFFFFF and curr + 5 <= len(self.b):
            parent_off, n_len = struct.unpack_from("<IB", self.b, curr)
            parts.append(self.b[curr+5:curr+5+n_len].decode("utf-8", errors="replace"))
            curr = parent_off
        return "/".join(reversed(parts))

class FontModGUI:
    def __init__(self, root):
        self.root = root; root.title("Crimson Desert Force Patcher (Mac)"); root.geometry("750x600")
        main_frame = ttk.Frame(root, padding="20"); main_frame.pack(fill=tk.BOTH, expand=True)
        
        default_path = "/Users/cherrymac/Library/Application Support/Steam/steamapps/common/Crimson Desert/CrimsonDesert_Steam.app/Contents/Resources/packages"
        ttk.Label(main_frame, text="Packages Directory:").pack(anchor=tk.W)
        self.game_path = tk.StringVar(value=default_path)
        ttk.Entry(main_frame, textvariable=self.game_path).pack(fill=tk.X, pady=5)
        
        ttk.Label(main_frame, text="Custom Font File:").pack(anchor=tk.W, pady=(10, 0))
        self.font_path = tk.StringVar()
        f_frame = ttk.Frame(main_frame); f_frame.pack(fill=tk.X, pady=5)
        ttk.Entry(f_frame, textvariable=self.font_path).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(f_frame, text="Browse", command=lambda: self.font_path.set(filedialog.askopenfilename())).pack(side=tk.RIGHT)
        
        self.btn_run = ttk.Button(main_frame, text="Force Patch Fonts", command=self.start_mod)
        self.btn_run.pack(fill=tk.X, pady=20)
        
        self.log = scrolledtext.ScrolledText(main_frame, height=15, bg="#1e1e1e", fg="#dcdcdc", font=("Menlo", 10))
        self.log.pack(fill=tk.BOTH, expand=True)

    def log_msg(self, m): self.log.insert(tk.END, m + "\n"); self.log.see(tk.END); self.root.update_idletasks()

    def start_mod(self):
        self.btn_run.state(['disabled'])
        threading.Thread(target=self.run_task, daemon=True).start()

    def run_task(self):
        try:
            pkg_dir = Path(self.game_path.get())
            font_bytes = Path(self.font_path.get()).read_bytes().rstrip(b"\x00")
            
            pamt_path = pkg_dir / "0012" / "0.pamt"
            self.log_msg(f"[*] Reading Package 0012/0.pamt...")
            d_data, n_names, folders, files = read_pamt(pamt_path)
            dr, fr = VfsPathResolver(d_data), VfsPathResolver(n_names)
            folder_map = {i: (dr.get_path(f[1]), f[2], f[2]+f[3]) for i, f in enumerate(folders)}
            
            found_count = 0
            for i, e in enumerate(files):
                fname = fr.get_path(e.name_offset).lower()
                fpath = next((p for fid, (p, start, end) in folder_map.items() if start <= i < end), "").lower()
                
                # 핵심 조건: 경로에 'font'가 포함되고 확장자가 '.ttf'인 모든 파일 타겟팅
                if (".ttf" in fname or ".otf" in fname) and ("font" in fname or "font" in fpath):
                    full_vfs = f"{fpath}/{fname}".strip("/")
                    self.log_msg(f"    [!] Detected: {full_vfs}")
                    
                    if len(font_bytes) > e.decompress_size:
                        self.log_msg(f"    - Skipping (Size limit: {e.decompress_size})")
                        continue
                    
                    _, payload = match_lz4_compressed_size(font_bytes, e.compress_size, e.decompress_size, self.log_msg)
                    paz_path = pkg_dir / "0012" / f"{e.paz_index}.paz"
                    with paz_path.open("r+b") as h:
                        h.seek(e.offset); h.write(payload)
                    self.log_msg(f"    - Patched: {paz_path.name}")
                    found_count += 1

            if found_count > 0:
                self.log_msg(f"\n[!] Success! Total {found_count} font slots updated.")
                messagebox.showinfo("Success", f"{found_count} slots updated!")
            else:
                self.log_msg("\n[?] Still no font slots detected. Checking name filters.")
        except Exception as ex:
            self.log_msg(f"\n[ERROR] {str(ex)}")
        finally:
            self.root.after(0, lambda: self.btn_run.state(['!disabled']))

if __name__ == "__main__":
    root = tk.Tk(); app = FontModGUI(root); root.mainloop()