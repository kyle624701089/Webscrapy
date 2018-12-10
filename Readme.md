## 北汽新能源充电桩数据爬取

PhantomJS浏览器 安装参考 [动态加载页面的解决方案与爬虫代理](https://www.freebuf.com/news/topnews/97275.html)

get_province.py 效率有待优化

若调用API转化经纬度，get_detail_province.py 每次跑报错的 index 会不一样，估计是调用 api 或者网络的问题，测试只需取消以下代码的注释

```python
    '''
    # 调用 API
    p = location[0].p.get_text()
    lat = getlnglat(p)['result']['location']['lat']
    lng = getlnglat(p)['result']['location']['lng']
    sheet_anhui.write(i,4,lat)
    sheet_anhui.write(i,5,lng)
    '''
```

> 未调用能跑完，，，，

改进待续~