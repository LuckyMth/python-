
import os
import re


if __name__ == '__main__':
    work_dir = r'C:\Users\J7834\Desktop\宜宾西53\20220317'
    # 文件筛选
    exp_fil1 = r"ETCClient.*\.log"
    exp_fil2 = r"Lane.*\.log"

    lst_fil = os.listdir(work_dir)
    str_fil = "\n".join(lst_fil)
    lst_fil1 = re.findall(exp_fil1, str_fil)
    lst_fil2 = re.findall(exp_fil2, str_fil)

    with open(work_dir + "\\1pre_ETCClient.log", "wb") as fil1:
        for tem_i in range(len(lst_fil1)-1, -1, -1):
            path_in = work_dir + "\\" + lst_fil1[tem_i]
            with open(path_in, "rb") as fil2:
                fil1.write(fil2.read())
            fil2.close()
        fil1.close()

    with open(work_dir + "\\1pre_Lane.log", "wb") as fil1:
        for tem_i in range(len(lst_fil2)-1, -1, -1):
            path_in = work_dir + "\\" + lst_fil2[tem_i]
            with open(path_in, "rb") as fil2:
                fil1.write(fil2.read())
            fil2.close()
        fil1.close()
