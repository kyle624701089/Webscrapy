# Python 网络爬虫实战与数据可视化

本仓库主要涵盖作者实践 python 网络爬虫与数据可视化的实例，代码示例仅供分享与学习使用，**不可用于任何商业目的**

## 全国电动汽车充电站数据爬取

> 第一个爬虫实战示例，具体细节可参考[爬虫实战：全国电动汽车充电站数据](http://equations.online/2018/12/09/chargebar/)

爬取对象为北汽新能源[网站](http://www.bjev520.com/jsp/beiqi/pcmap/do/index.jsp)提供的数据，简单的可视化后效果

<img src="https://i.loli.net/2018/12/15/5c14dfa87fdc8.png" width="700px" />

> 这点数据直接手工录入不就好了吗 :dizzy_face:

### 环境配置

本仓库示例代码均在 python 3.5 上运行测试，执行程序前请**安装代码中程序包**

然后先克隆项目内容

```git
git clone https://github.com/Equationliu/Webscrapy.git
```

#### chrome driver

##### Windows 安装

从[官网](http://chromedriver.chromium.org/downloads)上下载最新版本后解压至项目路径 `./chargebar/` 即可

##### ubuntu 安装

待定

### 开始爬取

```bash
cd chargebar
python chargebar_scrapy_main.py -h 
```

以上可获取帮助文档：

> usage: chargebar_scrapy_main.py [-h][--range RANGE] [--Retry_max RETRY_MAX][--convert CONVERT] [--ak AK]
>
> chargebar scrapy
>
> 1. **--range** ：the range you want to Grab, set '--range =全国' to
>    ​  grab all of the Charging piles of China
> 2.  -**-Retry_max** ：max times of retring to Convert coordinates
> 3. **--convert** whether get the Latitude and longitude
> 4. -**-ak** ：  Baidu API

 其中`--range` 设定为爬取的范围，若只需要获得全国各省份的总数据则设置`--range=全国` ，若须获得某省份具体充电桩数据，则设置 `--range=湖南省` ,不指定则缺省为青海省

`--Retry_max` 缺省为 3，可不必调整，防止调用百度API时某一次无法返回经纬度

`--convert` 控制是否调用百度 API 实现地址转经纬度，缺省为 NO

如果你设置了 `--convert=Yes` ，请务必输入你的百度 ak，`--ak=这里是你的ak` 因为缺省的是一串无效字符

**示例：**

```bash
python chargebar_scrapy_main.py --range=全国   ## 获取各省份充电站总数据
python chargebar_scrapy_main.py --range=云南省   ## 获取云南省充电桩
python chargebar_scrapy_main.py --range=云南省 --convert=Yes --ak=你的ak    ## 获取云南省充电桩并调用百度API转换地址为经纬度
```

> 注意：百度API 一天进行经纬度转换次数上限是6000次，也就是说一个 ak 无法获得全国所有数据

其中数目较多的北京省数据抓取时间

```
grabing complete in 17m 60s
```

### 数据清洗

执行上述程序将在目录 `./chargebar/result/` 下生成各省份数据文件，之所以要进行数据洗涤是因为部分充电站所给的地址不够准确导致百度API无法进行转换，可能会有如下报错：

```
百度找不到这个地方呢！或 API 额度已超限！
百度找不到这个地方呢！或 API 额度已超限！
百度找不到这个地方呢！或 API 额度已超限！
```

除此之外，即便是识别出了地址，地址也不一定准确，实验发现部分省份的数据竟指向了其他省份，并且数量并不低，再修改正则表达式较比较繁琐，而且出于学习角度并不需要十分精确的数据，故而使用了**离群点检测（LOF）**进行一个数据的清洗

```
python wash_data.py
```

> 实验发现发生了大偏差的数据点离群因子会非常高，根据实验取 k=8 ,即离群因子大于 8认为数据没有偏差

以上海市和山西省为例

<img src="https://i.loli.net/2018/12/15/5c14d9f340d03.png" width="700px" />

> 可以清楚的看出上海市的部分离群点与大部分点相差巨大，经实验发现山西的所有点确实在省内，不属于**省级的离群点** 。

### 可视化

清洗数据的代码 `wash_data.py` 中会绘制数据的热力图

<img src="https://i.loli.net/2018/12/15/5c14dd983934e.jpg" width="700px" />

可见快充和慢充还是不太一样的，快充就只有北京最为“燥热”

但是感觉上述可视化还不够呀，至少不够震撼，下面该 Echarts 登场了