
import os
import re
import chardet


# 检测源文件编码并返回
def fil_coding_detect(src_file):
    char_detect = str()
    with open(src_file, "rb") as fi:
        for row in fi:
            tmp = chardet.detect(row)
            code = tmp.get("encoding")
            if code == "utf-8":
                char_detect = "utf-8"
            else:
                char_detect = "gb18030"
            break
        fi.close()
    return char_detect


if __name__ == '__main__':
    work_dir = r'E:\学习和工作\问题单\车道\四川省\达渝\达州南\专入53\20220305'
    # 文件筛选
    exp_fil1 = r"ETCClient.*\.log"
    exp_fil2 = r"Lane.*\.log"

    lst_fil = os.listdir(work_dir)
    str_fil = "\n".join(lst_fil)
    lst_fil1 = re.findall(exp_fil1, str_fil)
    lst_fil2 = re.findall(exp_fil2, str_fil)

    with open(work_dir + "\\1pre_ETCClient.log", "w+", encoding="utf8") as fil1:
        for tem_i in range(len(lst_fil1)-1, -1, -1):
            path_in = work_dir + "\\" + lst_fil1[tem_i]
            cod = fil_coding_detect(path_in)
            with open(path_in, "r", encoding=cod) as fil2:
                fil1.write(fil2.read())
            fil2.close()
        fil1.close()

    with open(work_dir + "\\1pre_Lane.log", "w+", encoding="utf8") as fil1:
        for tem_i in range(len(lst_fil2)-1, -1, -1):
            path_in = work_dir + "\\" + lst_fil2[tem_i]
            cod = fil_coding_detect(path_in)
            with open(path_in, "r", encoding=cod) as fil2:
                fil1.write(fil2.read())
            fil2.close()
        fil1.close()

