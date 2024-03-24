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

            # 解压ZIP文件到临时目录
            extract_temp_dir = 'temporary_directory'
            print("开始解压...")
            with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_temp_dir)
            print("解压完成。")
            os.remove(temp_zip_path)  # 删除临时zip文件

            # 将解压出来的SIREN2-main目录下的所有内容移动到指定目录
            source_dir = os.path.join(extract_temp_dir, 'SIREN2-main')
            target_dir = r'.\plugins\SIREN2'
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            for item in os.listdir(source_dir):
                s = os.path.join(source_dir, item)
                d = os.path.join(target_dir, item)
                if os.path.isdir(s):
                    if os.path.exists(d):
                        shutil.rmtree(d)  # 如果目标目录存在，则删除
                    shutil.move(s, target_dir)
                else:
                    if os.path.exists(d):
                        os.remove(d)  # 如果目标文件存在，则删除
                    shutil.move(s, d)

            # 删除临时目录
            shutil.rmtree(extract_temp_dir)
            print("更新完成。")
    else:
        print("\033[1;32m当前已是最新代码。\033[0m")
        
        
if __name__ == '__main__':
    Update()