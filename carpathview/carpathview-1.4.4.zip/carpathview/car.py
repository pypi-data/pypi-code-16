# -*- coding: utf-8 -*-
from jinja2 import Template

path_template = '''<!DOCTYPE html>
<html lang="zh">

<head>
    <title> 车辆路径图 </title>
    <!-- <meta charset="utf-8" /> -->
    <!-- <meta name="viewport" content="width=device-width, initial-scale=1.0"> -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.0.3/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.0.3/dist/leaflet.js"></script>
    <script src="https://unpkg.com/vue/dist/vue.js"></script>
    <!--font awesome-->
    <link href="https://cdn.bootcss.com/font-awesome/4.6.3/css/font-awesome.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://unpkg.com/leaflet-easybutton@2.0.0/src/easy-button.css">
    <script src="https://unpkg.com/leaflet-easybutton@2.0.0/src/easy-button.js"></script>
</head>

<body>
    <!-- <div id="mapid" style="width:600px; height:400px"></div> -->
    <div id="mapid" style="height:800px"></div>
    <!-- 必须指定高度 -->

    <script>
        var app = new Vue({
            el: '#mapid',
            data: {
                message: 'Hello Vue!',
                latlngs: [
                    {% for lat,lng in latlngs %}
                        [ {{ lat }}, {{ lng }} ],
                    {% endfor %}
                ],
                time: [
                    {% for i in times %}
                        '{{i.hour}}:{{i.minute}}:{{i.second}}',
                    {% endfor %}
                ],
                num: 0,
                colors: ['purple', 'pink', 'orange', 'yellow', 'green', 'blue'],
                deltatime: {{ deltatime }},
            },
            mounted: function () {
                this.$nextTick(function () {
                    // 代码保证 this.$el 在 document 中
                    this.initMap();
                    this.genPath();
                    this.addButton();
                    setTimeout(this.pathRun, 1000);
                })
            },
            methods: {
                initMap() {
                    this.mymap = L.map('mapid', {
                        zoom: 7, //初始聚焦程度
                        center: this.latlngs[0], // [lat, lng] [纬度, 经度]
                        minZoom: 3, //最宽广，越小越宽广
                        maxZoom: 18, //最细致，越大越细致
                    });
                    L.tileLayer(
                        'https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}', {
                            subdomains: ["1", "2", "3", "4"], //可用子域名，用于浏览器并发请求
                            attribution: "&copy; 高德地图", //可以修改为其它内容
                    }).addTo(this.mymap); //添加tile层到地图
                    
                    this.marker = L.marker(this.latlngs[0]).addTo(this.mymap);
                    this.marker.bindPopup(this.time[0]).openPopup();
                },
                genPath() {
                    L.polyline(this.latlngs).addTo(this.mymap);
                    <!-- 替换为下面for产生的彩色太丑，算了。。。 -->
                    <!-- for (var i=0; i<this.latlngs.length; i++) { -->
                        <!-- L.polyline( -->
                            <!-- this.latlngs.slice(i,i+2),  -->
                            <!-- {color: this.colors[i%this.colors.length]} -->
                        <!-- ).addTo(this.mymap); -->
                    <!-- } -->
                    
                    this.mymap.fitBounds(this.latlngs);
                    this.runline = L.polyline([], {color: 'red'}).addTo(this.mymap);
                },
                pathRun(){
                    if ( this.num > (this.latlngs.length-1) ){
                        this.num = 0
                    }
                    this.marker.setLatLng(this.latlngs[this.num])
                    this.marker.getPopup().setContent(this.time[this.num])
                    this.runline.addLatLng(this.latlngs[this.num])
                    this.num += 1
                    if (this.changeView != null){
                        this.changeView()
                    }
                    <!-- changeView用于改变视域中心 -->
                    setTimeout(this.pathRun, {{deltatime}})
                }, 
                addButton() { 
                    // https://github.com/CliffCloud/Leaflet.EasyButton
                    L.easyButton('fa-refresh', this.refresh).addTo(this.mymap);
                    
                    L.easyButton('fa-taxi', this.follow).addTo(this.mymap);
                    this.followstate = false;
                },
                refresh() {
                    this.mymap.fitBounds(this.latlngs);
                },
                follow() {
                    if(this.followstate == true){
                        this.followstate = false;
                        this.changeView = null;
                        this.refresh();
                        this.marker.closePopup();
                        <!-- 必须要关闭Popup，要不然会自动位移使popup在视域中显示 -->
                    }
                    else{
                        this.followstate = true;
                        this.changeView = this._changeView ;
                        this.marker.openPopup();
                    }
                },
                _changeView(){
                    this.mymap.setView(this.marker.getLatLng());
                },
            }
        })
    </script>
</body>

</html>
'''

def producePath(latlngs,times,deltatime=50,filename="./path_rendering.html"):

    rendering = Template(path_template).render(
                    latlngs = latlngs,
                    times = times,
                    deltatime = deltatime,
                ) 
    # .values生成array, 在模板中使用 for lat,lng in array 解包
    with open(filename, 'w', encoding='utf-8') as path_rendering:
        path_rendering.write(rendering)
