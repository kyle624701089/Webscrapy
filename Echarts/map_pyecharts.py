from pyecharts import Map
import pandas as pd
import numpy as np

posi = pd.read_excel("province_China.xlsx")
num = len(posi)
manchong = np.array(posi["manchong"][0:num],
                            dtype=float)    # 获取慢充桩数，转化为numpy浮点型
kuaichong = np.array(posi["kuaichong"][0:num],
                             dtype=float)    # 获取快充桩数，转化为numpy浮点型
total = np.array(posi["total"][0:num])    # 获取充电站数目

name = np.array(posi["name"][0:num])

''' 为了输入下方的省份名称而进行的格式输出
for i in range(len(posi)):
    print("\""+name[i]+"\",")
'''

#value = [155, 10, 66, 78, 33, 80, 190, 53, 49.6]
value = total

attr = [
"安徽","北京","重庆","福建","广东","广西","贵州","甘肃","河北","黑龙江","河南","湖北","湖南","海南","吉林","江苏","江西",
"辽宁","内蒙古","宁夏","青海","山西","上海","山东","四川","陕西","天津","西藏","新疆","云南","浙江",
]
# background_color ='#293C55'
# width=1200, height=600
# renderer='svg'

map = Map("中国充电站数目分布图", subtitle = '数据来源于北汽新能源', width=1400, height=700,title_pos='center')
# map = Map("Map 结合 VisualMap 示例", width=1200, height=600)
map.use_theme('chalk')
map.add(
    "",
    attr,
    value,
    visual_range = [0,3131],
    visual_text_color ="#FFFFFF",
    maptype="china",
    is_visualmap=True,
    visual_pos ='73%',
    visual_top = '38%',
  #  visual_text_color="#000",
    legend_pos  = 'center',
)
map.render("中国充电站分布.png")
