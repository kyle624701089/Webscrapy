# -*- coding: utf-8 -*-
import os
import xlrd
import xlwt
import numpy as np
import pandas as pd
import folium
import webbrowser
from folium.plugins import HeatMap


# 打开excel文件
def open_excel(file='test.xls'):
    try:
        data = xlrd.open_workbook(file)
        return data
    except:
        print("ERROR WITH OPEN_EXCEL!")




# 将list中的内容写入一个新的file文件
def testXlwt(file='new.xls', list=[]):
    book = xlwt.Workbook()  # 创建一个Excel
    sheet1 = book.add_sheet('hello')  # 在其中创建一个名为hello的sheet
    i = 0  # 行序号
    for app in list:  # 遍历list每一行
        j = 0  # 列序号
        for x in app:  # 遍历该行中的每个内容（也就是每一列的）
            sheet1.write(i, j, x)  # 在新sheet中的第i行第j列写入读取到的x值
            j = j+1  # 列号递增
        i = i+1  # 行号递增
    # sheet1.write(0,0,'cloudox') #往sheet里第一行第一列写一个数据
    # sheet1.write(1,0,'ox') #往sheet里第二行第一列写一个数据
    book.save(file)  # 创建保存文件

def mkdir(path):

	folder = os.path.exists(path)

	if not folder:                   #判断是否存在文件夹如果不存在则创建为文件夹
		os.makedirs(path)            #makedirs 创建文件时如果路径不存在会创建这个路径


# 去除文件中的空白数据（地址不明晰导致的API无法识别），结果保存至 "./true" 文件夹
def delete_empty(file='test.xls', colnameindex=0, by_index=0):      #  colnameindex：表头列名所在行的索引（0表示没有表头）  ，by_index：表的索引
    path = "./result"
    path_xls = path+"/"+file
    data = open_excel(path_xls)  # 打开excel文件
    table = data.sheets()[by_index]  # 根据sheet序号来获取excel中的sheet
    nrows = table.nrows  # 行数
#    ncols = table.ncols  # 列数
    if nrows > 0:
        colnames = table.row_values(colnameindex)
        list = []  # 装读取结果的序列
        for rownum in range(0, nrows):  # 遍历每一行的内容
            row = table.row_values(rownum)  # 根据行号获取行
            if row:  # 如果行存在
                app = []  # 一行的内容
                for i in range(len(colnames)):  # 一列列地读取行的内容
                    app.append(row[i])  # 纬度所在列
                if app[4] != "":                    # 如果纬度数据不为空
                    list.append(app)
        mkdir("./true")
        testXlwt('./true/true_' + file, list)  # 调用写函数，讲list内容写到一个新文件中
        return list



def localoutlierfactor(data, predict, k):
    from sklearn.neighbors import LocalOutlierFactor
    clf = LocalOutlierFactor(
        n_neighbors=k + 1, algorithm='auto', contamination=0.1, n_jobs=-1)  # 调用所有CPU
    clf.fit(data)
    # 记录 k 邻域距离
    predict['k distances'] = clf.kneighbors(predict)[0].max(axis=1)
    # 记录 LOF 离群因子，做相反数处理
    predict['local outlier factor'] = - \
        clf._decision_function(predict.iloc[:, :-1])
    return predict


# 可视化 LOF 离群检测，并将图片保存至 ./img 文件夹
def plot_lof(name,result, method):
    import matplotlib.pyplot as plt
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    plt.figure(figsize=(8, 4)).add_subplot(111)
    plt.scatter(result[result['local outlier factor'] > method].index,
                result[result['local outlier factor'] > method]['local outlier factor'], c='red', s=50,
                marker='.', alpha=None,
                label='离群点')
    plt.scatter(result[result['local outlier factor'] <= method].index,
                result[result['local outlier factor'] <= method]['local outlier factor'], c='black', s=50,
                marker='.', alpha=None, label='正常点')
    plt.hlines(method, -2, 2 + max(result.index), linestyles='--')
    plt.xlim(-2, 2 + max(result.index))
    plt.title('LOF局部离群点检测 of normal_'+name, fontsize=13)
    plt.ylabel('局部离群因子', fontsize=15)
    plt.legend()
    mkdir("./img")
    plt.savefig('./img/LOF局部离群点检测 of normal_ '+name+'.png', dpi=300, bbox_inches='tight')#文件命名为Jiangsu.png存储
    plt.show()



def lof(name,data, predict=None, k=5, method=1, plot=True):
    import pandas as pd
    # 判断是否传入测试数据，若没有传入则测试数据赋值为训练数据
    try:
        if predict == None:
            predict = data.copy()
    except Exception:
        pass
    predict = pd.DataFrame(predict)
    # 计算 LOF 离群因子
    predict = localoutlierfactor(data, predict, k)
    if plot == True:
        plot_lof(name,predict, method)
    # 根据阈值划分离群点与正常点
    outliers = predict[predict['local outlier factor']
                       > method].sort_values(by='local outlier factor')
    inliers = predict[predict['local outlier factor'] <=
                      method].sort_values(by='local outlier factor')
    return outliers, inliers


# 通过离群点分析涮选正常的点绘制热力图，并存储修正后的文件，路径为 ./normal
def heatmap_lof():
    path = "./true/"  # 无空白数据文件夹目录
    files = os.listdir(path)  # 得到文件夹下的所有文件名称
    final_data_manchong = []  # 绘制慢充热力图
    final_data_kuaichong = []  # 绘制快充热力图
    File_manchong = open("heatmap_baidu_manchong.txt", "w")  # 百度地图格式文件夹
    File_kuaichong = open("heatmap_baidu_kuaichong.txt", "w")  # 百度地图格式文件夹
    count = 0 # 用于控制合并 DataFrame
    for file in files:
        # 读取各省份数据,并从第一行插入表头，同时第一行的 index 变成 00
        posi = pd.read_excel(path + file)
        posi_T = posi.T
        posi_T.insert(0, '00', posi.columns)
        posi = posi_T.T
        # 重新设置列标题
        posi.columns = ['name', 'address',
                        'kuaichong', 'manchong', 'lat', 'lon']

        # 提取数据
        num = len(posi)
        lat = np.array(posi["lat"][0:num], dtype=float)  # 获取纬度值
        lon = np.array(posi["lon"][0:num], dtype=float)        # 获取经度值
        manchong = np.array(posi["manchong"][0:num],
                            dtype=float)    # 获取慢充桩数，转化为numpy浮点型
        kuaichong = np.array(posi["kuaichong"][0:num],
                             dtype=float)    # 获取快充桩数，转化为numpy浮点型

        name = np.array(posi["name"][0:num])
        address = np.array(posi["address"][0:num])

        # 更新数据
        data_LOF = np.vstack([lat, lon]).T   # 生成 LOF 输入集
        if len(data_LOF) > 40:         # 部分省份数据不够，不进行离群点分析
            outliers1, inliers1 = lof(file,data_LOF, k=15, method=8)  # k 太小无法剔除异常点
            lat = np.delete(lat, outliers1.index)
            lon = np.delete(lon, outliers1.index)
            manchong = np.delete(manchong, outliers1.index)  # 删除指定 index 的数据
            kuaichong = np.delete(kuaichong, outliers1.index)  # 删除指定 index 的数据
            name = np.delete(name, outliers1.index)  # 删除指定 index 的数据
            address = np.delete(address, outliers1.index)  # 删除指定 index 的数据

        # 导出每个省份的正常数据
        integrate = np.vstack([name, address, kuaichong, manchong, lat, lon]).T
        province_normal = pd.DataFrame(integrate)
        province_normal.columns = ['name', 'address',
                                   'kuaichong', 'manchong', 'lat', 'lon']

        if count == 0:
            CHina_normal = province_normal
        else:
            CHina_normal = CHina_normal.append(province_normal)

        # 输出每一个省份的无误数据
        mkdir("./normal")
        writer = pd.ExcelWriter('./normal/' + file)
        province_normal.to_excel(
            writer, file, float_format='%.5f')  # float_format 控制精度
        writer.save()

        num = len(lat)
        data_manchong = []           # 每个省份正常慢充数据
        data_kuaichong = []             # 每个省份正常快充数据
        # 准备热力图数据
        for i in range(num):
            data_manchong[len(data_manchong):len(data_manchong)] = [
                [lat[i], lon[i], manchong[i]]]
            data_kuaichong[len(data_kuaichong):len(data_kuaichong)] = [
                [lat[i], lon[i], kuaichong[i]]]
            #  样式：   print("{'count': '%d', 'lat': '%f', 'lng': '%f'}," % (manchong[i],lat[i], lon[i]))
            index_manchong = "{'count': '" + \
                str(manchong[i])+"', 'lat': '"+str(lat[i]) + \
                "', 'lng': '"+str(lon[i])+"'},"

            index_kuaichong = "{'count': '" + \
                str(kuaichong[i])+"', 'lat': '"+str(lat[i]) + \
                "', 'lng': '"+str(lon[i])+"'},"
            File_manchong.write(str(index_manchong) + "\n")   # 按照百度格式写进文文件
            File_kuaichong.write(str(index_kuaichong) + "\n")

        data_manchong = [[lat[i], lon[i], manchong[i]]
                         for i in range(num)]  # 将数据制作成[lats,lons,weights]的形式

        data_kuaichong = [[lat[i], lon[i], kuaichong[i]]
                          for i in range(num)]  # 将数据制作成[lats,lons,weights]的形式

        # 合并全国的热力图信息
        final_data_manchong[len(final_data_manchong):len(
            final_data_manchong)] = data_manchong
        final_data_kuaichong[len(final_data_kuaichong):len(
            final_data_kuaichong)] = data_kuaichong

        count += 1


    #  保存全国的无误数据
    writer = pd.ExcelWriter("china_normal.xls")
    CHina_normal.to_excel(writer, file, float_format='%.5f')  # float_format 控制精度
    writer.save()
    # 关闭文件写入
    File_manchong.close()
    File_kuaichong.close()


    # 绘制热力图
    map_manchong = folium.Map(location=[35, 110], zoom_start=7,
                              tiles='Stamen Terrain')  # 绘制Map，开始缩放程度是5倍
    HeatMap(final_data_manchong, radius=10).add_to(
        map_manchong)  # 将热力图添加到前面建立的map里

    map_kuaichong = folium.Map(location=[35, 110], zoom_start=7,
                               tiles='Stamen Terrain')  # 绘制Map，开始缩放程度是5倍
    HeatMap(final_data_kuaichong, radius=10).add_to(
        map_kuaichong)  # 将热力图添加到前面建立的map里

    # 建立交互地图 Marker
    #  marker_cluster = plugins.MarkerCluster().add_to(map_osm)for name,row in full.iterrows():
    #    folium.RegularPolygonMarker([row["lat"], row["lon"]], popup="{0}:{1}".format(row["cities"], row["GDP"]),number_of_sides=10,radius=5).add_to(marker_cluster)

    map_manchong.save("manchong.html")     # 保存为html文件
    map_kuaichong.save("kuaichong.html")     # 保存为html文件
    webbrowser.open("manchong.html")  # 默认浏览器打开
    webbrowser.open("kuaichong.html")  # 默认浏览器打开




def main():
    path = "./result"  # 文件夹目录
    files = os.listdir(path)  # 得到文件夹下的所有文件名称

     #  去除掉由于地址不准确或者省内无充电站的数据
    for file in files:
        delete_empty(file)
    # 清洗数据并绘制热力图
    heatmap_lof()


if __name__ == "__main__":
    main()
