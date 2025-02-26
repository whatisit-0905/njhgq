#用来给带代码加密
import os
import shutil
import py_compile

import os
import shutil

def copy_to_comTar(source_dir, target_dir, exclude_list):
    """
    将 source_dir 下的所有文件和文件夹复制到 target_dir，
    排除 exclude_list 中的文件或文件夹。
    """
    # 确保目标目录存在
    os.makedirs(target_dir, exist_ok=True)

    for item in os.listdir(source_dir):
        source_item = os.path.join(source_dir, item)
        target_item = os.path.join(target_dir, item)

        # 排除在 exclude_list 中的文件或文件夹
        if item in exclude_list:
            print(f"Excluded: {source_item}")
            continue

        try:
            if os.path.isdir(source_item):
                # 如果是目录，递归调用
                copy_to_comTar(source_item, target_item, [".git"])
            else:
                # 如果是文件，复制到目标位置
                if not source_item.endswith(".git"):
                    shutil.copy2(source_item, target_item)
                print(f"Copied: {source_item} -> {target_item}")
        except PermissionError:
            print(f"Permission denied: {source_item}")
        except Exception as e:
            print(f"Error copying {source_item} to {target_item}: {e}")



def compile_py_to_pyc(target_dir):
    """
    遍历 target_dir 下的所有文件，将 .py 文件编译为 .pyc 文件，并删除原 .py 文件。
    """
    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.endswith('.py'):
                source_file = os.path.join(root, file)  # .py 文件路径
                compiled_file = source_file + 'c'      # .pyc 文件路径
                try:
                    py_compile.compile(source_file, cfile=compiled_file)
                    os.remove(source_file)  # 删除原 .py 文件
                    print(f"Compiled: {source_file} -> {compiled_file}")
                except Exception as e:
                    print(f"Failed to compile {source_file}: {e}")


if __name__ == "__main__":
    # 当前目录
    source_directory = os.getcwd()
    # comTar 文件夹路径
    tar_dir = "hqit-zip\comtar"
    # com_tar_directory = os.path.join(source_directory, tar_dir)
    com_tar_directory = tar_dir

    try:
        # 删除文件夹及其内容
        shutil.rmtree(com_tar_directory)
        print(f"成功删除文件夹: {com_tar_directory}")
    except FileNotFoundError:
        print(f"文件夹不存在: {com_tar_directory}")
    except PermissionError:
        print(f"没有权限删除文件夹: {com_tar_directory}")
    except Exception as e:
        print(f"删除文件夹时发生错误: {e}")

    # 创建 comTar 文件夹
    os.makedirs(com_tar_directory, exist_ok=True)

    # 复制文件到 comTar
    copy_to_comTar(source_directory, com_tar_directory,["dist",tar_dir,"build","templates","static","main.spec",".git","output","debug","hk_utilt","codeZip.py","hqit-zip"])

    # 编译 comTar 下的所有 .py 文件
    compile_py_to_pyc(com_tar_directory)

