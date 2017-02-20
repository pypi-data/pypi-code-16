import json
import time
import urllib.parse
import urllib.request
import urllib.response


def qzone_query(time, f):
    values = {}
    values['t'] = '0.5588449318876649'
    values['g_tk'] = '562013905'
    data = urllib.parse.urlencode(values)
    urldata = "https://h5.qzone.qq.com/webapp/json/secretList/getSecretActFeeds" + "?" + data;
    postdata = {
        'refresh_type': '2',
        'relation_type:': '8',
        'uin': qq,
        'attach_info': 'endtime=' + time + '&offset=0&tlistsec=0&tlistusec=0&recomfeed='
    }
    form = urllib.parse.urlencode(postdata)
    request = urllib.request.Request(str(urldata), form.encode('UTF-8'))
    request.add_header('User-Agent',
                       'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Mobile Safari/537.36')
    request.add_header('Upgrade-Insecure-Requests', '1')
    request.add_header('Content-Type', 'application/x-www-form-urlencoded')
    request.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
    request.add_header('Cookie',
                       'RK=+QV7NrXTO1; __Q_w_s__QZN_TodoMsgCnt=1; pgv_pvi=1171475456; pac_uid=1_' + qq + '; __Q_w_s__appDataSeed=1; QZ_FE_WEBP_SUPPORT=1; cpu_performance_v8=49; __Q_w_s_hat_seed=1; eas_sid=l1K4D853Z2l0N4O1v3j7N1k2V6; tvfe_boss_uuid=9b7dd380f357dbf9; ptui_loginuin=' + qq + '; luin=o0' + qq + '; lskey=0001000082d8ad4a7784d408419b17f112e10130e4a421459e7ae2650db724340340aabbe27a1a2f08ab5dcc; o_cookie=' + qq + '; pgv_pvid=4880253720; ptisp=ctc; ptcz=acf228d81f9db945b43f47060081f914f27abe05ddc84547b831359775b76ec9; pt2gguin=o0' + qq + '; uin=o0' + qq + '; skey=@gfybLQyKR; p_uin=o0' + qq + '; p_skey=SH9HbMwsrSmloNg-PvVpB6ZHFRodwaIpaHjSzb5cr8c_; pt4_token=cK7toXmbMoYwjNmLHr6Cc1urlv-fbu*ewp*4bDJQ0Ok_')
    response = urllib.request.urlopen(request)
    s = response.read().decode('UTF-8')
    struct = json.loads(s)
    for node in struct['data']['all_feeds_data']:
        isself = node['singlefeed']['1']['user']['is_owner']
        orglikekey = node['singlefeed']['0']['orglikekey']
        curlikekey = node['singlefeed']['0']['curlikekey']
        uid = node['singlefeed']['1']['user']['uid']
        text = node['singlefeed']['4']['summary']
        date = node['singlefeed']['0']['time']
        text = text.replace("\n", "<br>")
        if (isself == 1):
            print(str(date) + ',' + qq + ',' + text, file=f)
    try:
        return int(struct['data']['all_feeds_data'][9]['singlefeed']['0']['time'])
    except Exception as e:
        try:
            return int(struct['data']['all_feeds_data'][8]['singlefeed']['0']['time'])
        except Exception as e:
            try:
                return int(struct['data']['all_feeds_data'][7]['singlefeed']['0']['time'])
            except Exception as e:
                try:
                    return int(struct['data']['all_feeds_data'][6]['singlefeed']['0']['time'])
                except Exception as e:
                    try:
                        return int(struct['data']['all_feeds_data'][5]['singlefeed']['0']['time'])
                    except Exception as e:
                        try:
                            return int(struct['data']['all_feeds_data'][4]['singlefeed']['0']['time'])
                        except Exception as e:
                            try:
                                return int(struct['data']['all_feeds_data'][3]['singlefeed']['0']['time'])
                            except Exception as e:
                                try:
                                    return int(struct['data']['all_feeds_data'][2]['singlefeed']['0']['time'])
                                except Exception as e:
                                    try:
                                        return int(struct['data']['all_feeds_data'][1]['singlefeed']['0']['time'])
                                    except Exception as e:
                                        try:
                                            return int(struct['data']['all_feeds_data'][0]['singlefeed']['0']['time'])
                                        except Exception as e:
                                            return 1

def qzonesecret(qqlist,outdata):
	qf = open(qqlist, encoding="utf-8")
	f = open(outdata, 'w+', encoding='utf-8')
	while 1:
		qq = qf.readline()
		qq = qq.replace("\n", "")
		if qq == '':
			break
		t = int(time.time())
		while (t >= 1484841600):
			time.sleep(1)
			print("Outputing Data of QQ " + qq + 'and time of ' + str(t))
			t = qzone_query(str(t), f) - 1
