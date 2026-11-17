import os
import json
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

CONFIG_FILE = "git_deployer_config.json"

class GitHubDeployerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BV KOREA - GitHub 맞춤형 배포 매니저")
        self.root.geometry("620x680")
        self.root.configure(bg="#F4F6F9")
        self.root.resizable(False, False)

        # 저장된 설정 불러오기 (기본값 포함)
        self.config = self.load_config()
        self.setup_ui()

    def load_config(self):
        default_config = {
            "user_name": "syoa12345-beep",
            "user_email": "syoa12345@gmail.com",
            "repo_url": "https://github.com/syoa12345-beep/BV-KOREA.git",
            "project_dir": r"P:\BV_KOREA\BV_KOREA_MV_MAKER\서버업로드"
        }
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    for key in default_config:
                        if not loaded.get(key):
                            loaded[key] = default_config[key]
                    return loaded
            except Exception:
                pass
        return default_config

    def save_config(self):
        data = {
            "user_name": self.entry_name.get().strip(),
            "user_email": self.entry_email.get().strip(),
            "repo_url": self.entry_url.get().strip(),
            "project_dir": self.entry_dir.get().strip()
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def setup_ui(self):
        # 상단 헤더
        header_frame = tk.Frame(self.root, bg="#1E293B", height=70)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        tk.Label(
            header_frame, text="🚀 GitHub 맞춤형 배포 매니저",
            font=("맑은 고딕", 15, "bold"), fg="#FFFFFF", bg="#1E293B"
        ).pack(pady=(12, 2))
        tk.Label(
            header_frame, text="상황에 맞게 '새로 등록' 또는 '빠른 업로드' 버튼을 선택해 주세요.",
            font=("맑은 고딕", 9), fg="#94A3B8", bg="#1E293B"
        ).pack()

        # 입력 폼 카드 영역
        form_frame = tk.Frame(self.root, bg="#FFFFFF", bd=1, relief="solid", padx=20, pady=15)
        form_frame.pack(padx=20, pady=15, fill="x")

        # 1. 사용자 이름
        tk.Label(form_frame, text="1. Git 사용자 이름 (영문)", font=("맑은 고딕", 9, "bold"), bg="#FFFFFF", fg="#334155").grid(row=0, column=0, sticky="w", pady=(0, 3))
        self.entry_name = tk.Entry(form_frame, font=("맑은 고딕", 10), width=55, relief="solid", bd=1)
        self.entry_name.insert(0, self.config["user_name"])
        self.entry_name.grid(row=1, column=0, columnspan=2, sticky="we", pady=(0, 10), ipady=4)

        # 2. 이메일 주소
        tk.Label(form_frame, text="2. GitHub 가입 이메일 주소", font=("맑은 고딕", 9, "bold"), bg="#FFFFFF", fg="#334155").grid(row=2, column=0, sticky="w", pady=(0, 3))
        self.entry_email = tk.Entry(form_frame, font=("맑은 고딕", 10), width=55, relief="solid", bd=1)
        self.entry_email.insert(0, self.config["user_email"])
        self.entry_email.grid(row=3, column=0, columnspan=2, sticky="we", pady=(0, 10), ipady=4)

        # 3. 원격 저장소 URL
        tk.Label(form_frame, text="3. GitHub 저장소 주소 (.git으로 끝나는 HTTPS URL)", font=("맑은 고딕", 9, "bold"), bg="#FFFFFF", fg="#334155").grid(row=4, column=0, sticky="w", pady=(0, 3))
        self.entry_url = tk.Entry(form_frame, font=("맑은 고딕", 10), width=55, relief="solid", bd=1)
        self.entry_url.insert(0, self.config["repo_url"])
        self.entry_url.grid(row=5, column=0, columnspan=2, sticky="we", pady=(0, 10), ipady=4)

        # 4. 작업 폴더 경로
        tk.Label(form_frame, text="4. 업로드할 로컬 폴더 경로", font=("맑은 고딕", 9, "bold"), bg="#FFFFFF", fg="#334155").grid(row=6, column=0, sticky="w", pady=(0, 3))
        self.entry_dir = tk.Entry(form_frame, font=("맑은 고딕", 10), width=45, relief="solid", bd=1)
        self.entry_dir.insert(0, self.config["project_dir"])
        self.entry_dir.grid(row=7, column=0, sticky="we", pady=(0, 5), ipady=4)

        btn_browse = tk.Button(
            form_frame, text="폴더 찾기", font=("맑은 고딕", 9, "bold"),
            bg="#E2E8F0", fg="#1E293B", relief="flat", cursor="hand2", command=self.browse_folder
        )
        btn_browse.grid(row=7, column=1, sticky="e", padx=(8, 0), pady=(0, 5), ipady=3, ipadx=8)

        # 버튼 영역 (용도별로 명확하게 2개 배치)
        btn_frame = tk.Frame(self.root, bg="#F4F6F9")
        btn_frame.pack(padx=20, pady=(0, 10), fill="x")

        # 1. 새로 등록용 (최초 설정 + 초기화 + 연결)
        self.btn_new_setup = tk.Button(
            btn_frame, text="🖥️ [새로 등록] PC 재설치 최초 설정", font=("맑은 고딕", 10, "bold"),
            bg="#2563EB", fg="#FFFFFF", activebackground="#1D4ED8", activeforeground="#FFFFFF",
            relief="flat", cursor="hand2", command=lambda: self.run_in_thread(self.action_new_setup)
        )
        self.btn_new_setup.pack(side="left", expand=True, fill="x", padx=(0, 5), ipady=12)

        # 2. 업로드 전용 (평소 수정 후 업로드만 할 때)
        self.btn_only_upload = tk.Button(
            btn_frame, text="⚡ [업로드] 평소 수정분 반영 (Push)", font=("맑은 고딕", 10, "bold"),
            bg="#10B981", fg="#FFFFFF", activebackground="#059669", activeforeground="#FFFFFF",
            relief="flat", cursor="hand2", command=lambda: self.run_in_thread(self.action_only_upload)
        )
        self.btn_only_upload.pack(side="left", expand=True, fill="x", padx=(5, 0), ipady=12)

        # 실행 로그 출력창
        log_frame = tk.Frame(self.root, bg="#F4F6F9")
        log_frame.pack(padx=20, pady=(0, 15), fill="both", expand=True)

        tk.Label(log_frame, text="실시간 진행 상태 로그", font=("맑은 고딕", 9, "bold"), bg="#F4F6F9", fg="#475569").pack(anchor="w", pady=(0, 3))
        self.log_area = scrolledtext.ScrolledText(
            log_frame, font=("Consolas", 9), bg="#0F172A", fg="#38BDF8",
            relief="solid", bd=1, state="disabled", height=9
        )
        self.log_area.pack(fill="both", expand=True)

    def log(self, message):
        self.log_area.config(state="normal")
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state="disabled")

    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.entry_dir.get())
        if folder:
            self.entry_dir.delete(0, tk.END)
            self.entry_dir.insert(0, os.path.normpath(folder))

    def validate_inputs(self):
        name = self.entry_name.get().strip()
        email = self.entry_email.get().strip()
        url = self.entry_url.get().strip()
        directory = self.entry_dir.get().strip()

        if not name or not email or not url or not directory:
            messagebox.showwarning("입력 확인", "모든 항목을 입력해 주세요.")
            return False
        if not url.endswith(".git"):
            messagebox.showwarning("주소 확인", "저장소 주소는 반드시 '.git'으로 끝나야 합니다.")
            return False
        if not os.path.isdir(directory):
            messagebox.showerror("경로 오류", "지정한 로컬 폴더 경로가 존재하지 않습니다.")
            return False
        self.save_config()
        return True

    def exec_git(self, cmd, cwd):
        self.log(f"> {cmd}")
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        process = subprocess.run(
            cmd, cwd=cwd, shell=True, capture_output=True, text=True,
            encoding="utf-8", errors="replace", startupinfo=startupinfo
        )
        if process.stdout.strip():
            self.log(process.stdout.strip())
        if process.stderr.strip():
            self.log(process.stderr.strip())
        return process.returncode

    def run_in_thread(self, target_func):
        if not self.validate_inputs():
            return
        threading.Thread(target=target_func, daemon=True).start()

    def action_new_setup(self):
        """[새로 등록용] 윈도우 재설치 등 처음 환경 세팅 시 실행"""
        self.log("\n=== 🖥️ [새로 등록] 최초 설정 및 저장소 연결 시작 ===")
        name = self.entry_name.get().strip()
        email = self.entry_email.get().strip()
        url = self.entry_url.get().strip()
        cwd = self.entry_dir.get().strip()

        # 1. 글로벌 Git 계정 설정
        self.exec_git(f'git config --global user.name "{name}"', cwd)
        self.exec_git(f'git config --global user.email "{email}"', cwd)

        # 2. 로컬 저장소 초기화 및 원격 연결
        if not os.path.exists(os.path.join(cwd, ".git")):
            self.exec_git("git init", cwd)
            self.exec_git("git branch -M main", cwd)
            self.exec_git(f"git remote add origin {url}", cwd)
        else:
            self.log("[안내] 이미 .git 폴더가 존재하므로 원격 주소만 갱신합니다.")
            self.exec_git("git branch -M main", cwd)
            self.exec_git("git remote remove origin", cwd)
            self.exec_git(f"git remote add origin {url}", cwd)

        # 3. 최초 동기화 및 업로드까지 세트로 완료
        self.exec_git("git pull origin main --allow-unrelated-histories -X ours", cwd)
        self.exec_git("git add .", cwd)
        self.exec_git('git commit -m "Initial setup and deploy"', cwd)
        code = self.exec_git("git push -u origin main", cwd)

        if code == 0:
            self.log("=== [최초 등록 성공!] 환경 설정 및 첫 업로드가 완료되었습니다. ===")
            messagebox.showinfo("완료", "최초 설정 및 등록이 완벽하게 완료되었습니다!")
        else:
            self.log("=== [확인 필요] 인증창이나 에러 메시지를 확인해 주세요. ===")

    def action_only_upload(self):
        """[업로드 전용] 평소 파일 수정 후 반영할 때 실행"""
        self.log("\n=== ⚡ [업로드 전용] 수정 파일 동기화 및 푸시 시작 ===")
        cwd = self.entry_dir.get().strip()

        # 평소에는 설정 과정 없이 바로 풀, 애드, 커밋, 푸시만 수행
        self.exec_git("git pull origin main --allow-unrelated-histories -X ours", cwd)
        self.exec_git("git add .", cwd)
        self.exec_git('git commit -m "Update web files"', cwd)
        code = self.exec_git("git push origin main", cwd)

        if code == 0:
            self.log("=== [업로드 성공!] 1~2분 뒤 웹사이트에 반영됩니다. (Ctrl+F5) ===")
            messagebox.showinfo("완료", "업로드가 성공적으로 완료되었습니다!\n1~2분 뒤 웹사이트에서 Ctrl+F5를 눌러 확인하세요.")
        else:
            self.log("=== [확인 필요] 로그 또는 인증창을 확인해 주세요. ===")

if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubDeployerApp(root)
    root.mainloop()