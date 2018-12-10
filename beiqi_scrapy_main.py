# -*- coding: utf-8 -*-
import re
import time  # 需要导入的模块
import xlwt
import argparse
import requests
from bs4 import BeautifulSoup
from urllib.request import quote
from selenium import webdriver
from geopy.geocoders import baidu
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# 解析输入参数
def parse_args():
    """Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description="Re-ID feature extractor")
    parser.add_argument(
        "--range",
        default="青海省",
        help="the range you want to Grab, set '--mot_dir = all' to grab"
        "all of the Charging piles of China")
    parser.add_argument(
        "--Retry_max",
        default="3",
        help="the max times of retring to Convert coordinates")
    parser.add_argument(
        "--convert",
        default="No",
        help="whether get the Latitude and longitude ")
    return parser.parse_args()

# 获取静态网页的源代码


def get_one_page(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) ''Chrome/51.0.2704.63 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            return response.text
        else:
            print(response.status_code)
            return None
    except:
        print('访问 http 发生错误... ')
        return None


def main():
    since = time.time()   # 记录程序时间
    args = parse_args()  # 解析输入参数
    Retry_max = args.Retry_max  # 解析经纬度最大重试次数

    if args.range == "全国":  # 仅获取各省的数据

        # 创建表格,添加工作表
        book = xlwt.Workbook(encoding='utf-8', style_compression=0)
        sheet_province = book.add_sheet('全国', cell_overwrite_ok=True)

        # 打开起始页面
        url = 'http://www.bjev520.com/jsp/beiqi/pcmap/do/index.jsp'
        all_html = get_one_page(url)

        # 按类（class）解析 html 文件得到所有省份名称
        model = 'http://www.bjev520.com/jsp/beiqi/pcmap/do/pcMap.jsp?chargingTypeId=&companyId=&chargingBrandId=&brandStatuId=&cityName='
        soup = BeautifulSoup(all_html, "lxml")
        province = soup.find_all(name='td', attrs={"class": "sel-city-td-sf"})

        # 配置 Selenium web驱动器,网站中部分数据由 ajax 动态加载
        #   driver = webdriver.PhantomJS(executable_path="phantomjs.exe")
        # 由于 PhantomJS 马上会被淘汰改用 headless chromedriver
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        driver = webdriver.Chrome('chromedriver.exe', options=chrome_options)

        i = 0
        for province_id in province:
            if i < len(province)-1:  # 网页中最后一行为港澳台，没有相关数据
                a = province[i].a.get_text()  # 当前省份名称：如 浙江省：
                sheet_province.write(i, 0, a[:-1])  # a[:-1] 去掉最后一个字符：冒号
                url_each_province = model + quote(a[:-1])  # quote 实现网址中的中文编码
                driver.get(url_each_province)

                #  此处 Web driver 似乎不需要等待也可以提取到省级的数据，直接 REquest 是不可以的
                #    time.sleep(3)  这是最糟糕的等待加载方案

                total = driver.find_element_by_id('dianzhan').text
                sheet_province.write(i, 1, int(total))   # 总充电站数

                fast = driver.find_element_by_id('kuaichong').text
                sheet_province.write(i, 2, int(fast))   # 快充桩数

                man = driver.find_element_by_id('manchong').text
                sheet_province.write(i, 3, int(man))   # 慢充桩数

                # 可视化：
                print(a[:-1], ":", "\t", "总充电站：", "\t", total, "\t",
                      "快充桩：", "\t", fast, "\t", "慢充桩：", "\t", man)

                i += 1
        # 输出
        book.save('province.xls')

    else:  # 抓取某一个省份具体充电桩
        # 创建表格,添加工作表
        final_data = xlwt.Workbook(encoding='utf-8', style_compression=0)
        sheet_province = final_data.add_sheet(
            args.range, cell_overwrite_ok=True)

        # 打开起始页面
        url = 'http://www.bjev520.com/jsp/beiqi/pcmap/do/index.jsp'
        all_html = get_one_page(url)

        # 初始化字典，记录省份的总充电站数目
        Dictionary_province = {}
        print("\n Grabing province : %s " % args.range)
        model = 'http://www.bjev520.com/jsp/beiqi/pcmap/do/pcMap.jsp?chargingTypeId=&companyId=&chargingBrandId=&brandStatuId=&cityName='
        url_now = model + quote(args.range)  # quote 实现中文的编码
        print("Grabing url : %s " % url_now)

        # 配置 Selenium web驱动器,网站中部分数据由 ajax 动态加载
        #   driver = webdriver.PhantomJS(executable_path="phantomjs.exe")
        # 由于 PhantomJS 马上会被淘汰改用 headless chromedriver
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        driver = webdriver.Chrome('chromedriver.exe', options=chrome_options)
        driver.get(url_now)
        try:
            element = WebDriverWait(driver, 5).until(             # 直到指定 id 出现方才抓取，此案例中不是必要语句
                EC.presence_of_element_located((By.ID, "left"))
            )
            total = driver.find_element_by_id('dianzhan').text
            # 将省份总量存入字典
            Dictionary_province[args.range] = int(total)

            kuaichong = driver.find_element_by_id('kuaichong').text
            manchong = driver.find_element_by_id('manchong').text
            print("\n总充电站数：%s，快充桩：%s，慢充桩：%s" % (total, kuaichong, manchong))

            # 调转到嵌入的 iframe
            driver.switch_to.frame('left')         # iframe标签的name属性     最重要的一步
            soup = BeautifulSoup(driver.page_source, "html.parser")

            # 读取每一个充电站
            status = soup.find_all('a')
            # 该省份充电站数目
            Max = Dictionary_province[args.range]

            i = 0
            count = 0
            model = 'http://www.bjev520.com/'

            while i < Max:
                url_now = model + status[i].get('href')

            #    # 这里同样不能用静态页面的方法处理
            #    driver_sub = webdriver.Chrome('chromedriver.exe', options=chrome_options)
           #         driver.get(url_now)

                all_html = get_one_page(url_now)
                soup_location = BeautifulSoup(all_html, "lxml")

                # 充电站名称
                name = soup_location.find_all(
                    name='div', attrs={"class": "news-top"})
                sheet_province.write(i, 0, name[0].p.get_text())
                # 充电站地址
                location = soup_location.find_all(
                    name='div', attrs={"class": "news-a"})
                sheet_province.write(i, 1, location[0].p.get_text())
                # 充电站充电桩
                charge = soup_location.find_all(
                    name='div', attrs={"class": "news-c"})  # 由于部分只有快充或者慢充，正则匹配似乎比较方便
                pattern_fast = re.compile('快充数量：(.*?)个', re.S)
                pattern_low = re.compile('慢充数量：(.*?)个', re.S)
                kuaichong = re.findall(pattern_fast, str(charge[0]))
                manchong = re.findall(pattern_low, str(charge[0]))
                # 输出
                if len(kuaichong) == 0:
                    sheet_province.write(i, 2, 0)  # 没有快充
                    fast = 0
                else:
                    sheet_province.write(i, 2, int(kuaichong[0]))
                    fast = kuaichong[0]

                if len(manchong) == 0:
                    sheet_province.write(i, 3, 0)    # 没有慢充
                    low = 0
                else:
                    sheet_province.write(i, 3, int(manchong[0]))
                    low = manchong[0]

                if args.convert == "Yes":
                    # 调用 API
                    p = location[0].p.get_text()
                    ak = 'YXCMciIa0nG12tm7lOU8kLreIPa91zPr'
                    b = baidu.Baidu(ak)

                    # 去除无用信息
                    s = location[0].p.get_text()
                    delete_banjiao = re.sub(
                         u"\\(.*?\\)|\\{.*?}|\\[.*?]", "", s)
                    s = bytes(delete_banjiao, encoding="utf8")
                    delete_quanjiao = re.sub(
                           u"\\（.*?）|\\{.*?}|\\[.*?]|\\【.*?】", "", s.decode())

                    try:
                            location_api = b.geocode(delete_quanjiao)
                            sheet_province.write(i, 4, location_api.latitude)
                            sheet_province.write(i, 5, location_api.longitude)
                            print(i, "/",Max, '\t',  "快充：", '\t', int(fast), '\t', "慢充：", '\t', int(low), '\t', "纬度：", '\t', location_api.latitude, '\t', "经度：", '\t', location_api.longitude)  # 当前充电站的链接
                    except:
                            print(
                                '百度找不到这个地方呢！')
                            count += 1
                            if count < int(Retry_max):
                                i -= 1
                            else:
                                count = 0

                else:
                    print(i, "/",Max,  '\t',  "快充：", '\t', int(fast),
                          '\t', "慢充：", '\t', int(low))  # 当前充电站的链接

                i += 1
        #    driver_detail = webdriver.PhantomJS(executable_path="phantomjs.exe")
        #    driver_detail.get( list_src.get_attribute("src"))
        finally:
            driver.quit()

        # 耗时统计
        time_elapsed = time.time() - since
        print('\n Grabing complete in {:.0f}m {:.0f}s'.format(
            time_elapsed // 60, time_elapsed % 60))  # 打印出来时间

        # 输出
        output = "detail_of_" + args.range + ".xls"
        final_data.save(output)


if __name__ == "__main__":
    main()
