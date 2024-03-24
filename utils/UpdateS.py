import subprocess
import zipfile
import os
import hashlib
import shutil
import requests

def Update():
    # 获取GitHub上__init__.py文件的最新内容
    url = "https://api.github.com/repos/extrant/SIREN2/contents/version.txt"
    headers = {'Accept': 'application/vnd.github.v3.raw'}
    response = requests.get(url, headers=headers)
    remote_file_contents = response.text

    # 计算远程文件的哈希值
    remote_hash = hashlib.sha256(remote_file_contents.encode('utf-8')).hexdigest()

    # 计算本地__init__.py文件的哈希值
    local_file_path = '.\plugins\SIREN2\\version.txt'
    with open(local_file_path, 'r', encoding='utf-8') as file:
        local_file_contents = file.read()
    local_hash = hashlib.sha256(local_file_contents.encode('utf-8')).hexdigest()

    if remote_hash != local_hash:
        print("\033[1;31m检测到新版本，文件version有更新\033[0m")
        print("\033[1;32m更新完成后请手动重启FFD")
        update = input("是否更新到最新的代码? (y/n): \033[0m")
        if update.lower() == 'y':
            # 设置下载ZIP文件的URL
            zip_url = "https://github.com/extrant/SIREN2/archive/refs/heads/main.zip"
            # 设置ZIP文件的本地路径
            temp_zip_path = 'temp.zip'
            # 使用PowerShell下载ZIP文件
            ps_command = f"Invoke-WebRequest -Uri {zip_url} -OutFile {temp_zip_path}"
            subprocess.run(["powershell", "-Command", ps_command], check=True)
            print("下载完成。")
            extract_temp_dir = 'temporary_directory'
            print("开始解压...")
            with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_temp_dir)
            print("解压完成。")
            os.remove(temp_zip_path)  # 删除临时zip文件

            source_dir = os.path.join(extract_temp_dir, 'SIREN2-main')
            target_dir = r'.\plugins\SIREN2'
            for root, dirs, files in os.walk(source_dir):
                relative_path = os.path.relpath(root, source_dir)
                target_root = os.path.join(target_dir, relative_path)
                try:
                    if not os.path.exists(target_root):
                        os.makedirs(target_root)
                    for file in files:
                        source_file = os.path.join(root, file)
                        target_file = os.path.join(target_root, file)
                        if os.path.exists(target_file):
                            os.remove(target_file)
                        shutil.move(source_file, target_file)
                except:
                    print(f"无法处理目录 {target_file}，可能有文件正在被占用。")

            try:
                shutil.rmtree(extract_temp_dir)
            except OSError as e:
                print(f"无法删除临时目录 {extract_temp_dir}，可能有文件正在被占用。")
            print("更新完成。")
    else:
        print("\033[1;32m当前已是最新代码。\033[0m")
        
        
if __name__ == '__main__':
    Update()