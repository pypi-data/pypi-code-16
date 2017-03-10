#!/usr/bin/env python
# coding:utf-8

import os

from bs4 import BeautifulSoup

from .utils import (Soup, HTTPRequest, table_print, validate_login,
                   quit, clear, rinput)


class Score:
    def __init__(self, usrname='0', usrpswd='0', user_type=u"学生",
                 display=True):
        self.usrname = usrname
        self.usrpswd = usrpswd
        self.user_type = user_type
        self.display = display
        self.http_request = HTTPRequest()


    def login(self):
        '''
        模拟登录教务系统
        :param username:
        :param pswd:
        :return: 登录状态
        '''
        login_url = 'http://219.242.68.34/Login.aspx'

        form_data = {
            "ToolkitScriptManager1": "ToolkitScriptManager1|btnLogin",
            "ToolkitScriptManager1_HiddenField": "",
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "__VIEWSTATE": (
                "/wEPDwULLTEzMzI5MDg5NTdkZLijHQ2AP8RlCsoyMA5wGxkp7N/Eu"
                "+tNRGRIjssUUJzA"
            ),
            "__VIEWSTATEGENERATOR": "C2EE9ABB",
            "__EVENTVALIDATION": (
                "/wEdAAkh8ZU3Gnyvn5kXEKbCJUIRDFTzKcXJqLg+OeJ6QAEa2nY2+"
                "Mc6SrnAqio3oCKbxYah3xa5rLP/Bn9R8gnPYyv9Y/jNR+V3Y2V63r"
                "/uGJ6o3e8y1uAcWHw+joLTxl+mj+XJMG57d9TuD5oRZdFmOwSdT3X"
                "UHy040LsOHhWYhzfBA6KeKEbp39eHc9mbdvkCgxBZmNzqpPs6SHyh"
                "2ECtT46MMRcPc39Fn2KuRL/PbaoRvw=="
            ),
            "txtUser": self.usrname,
            "txtPassword": self.usrpswd,
            "rbLx": self.user_type,
            "__ASYNCPOST": "true",
            "btnLogin": " 登 录 "
        }


        response = self.http_request.post(login_url, data=form_data).text
        return validate_login(
            response,
            validator={
                "pageRedirect": {'status': True, 'info': "登录成功"},
                u"密码不正确": {'status': False, 'info': "密码错误"},
            },
            default={'status': False, 'info': "登录失败"}
        )

    def get_info(self):
        '''
        通过登录会话session获取学生信息
        :param sess:
        :return: 学生信息
        '''
        ifo_url = 'http://219.242.68.34/xuesheng/xsxx.aspx'
        soup = Soup(self.http_request.session, ifo_url)
        data = {}
        data['a.姓名'] = soup.find(id="ctl00_ContentPlaceHolder1_lblXm").text
        data['b.身份证号'] = soup.find(id="ctl00_ContentPlaceHolder1_lblSfz").text
        data['c.学号'] = soup.find(id="ctl00_ContentPlaceHolder1_lblXh").text
        data['d.班级'] = soup.find(id="ctl00_ContentPlaceHolder1_className").text
        data['e.院系'] = soup.find(id="ctl00_ContentPlaceHolder1_collegeName").text
        if self.display is True:
            tabletitle = [item[2:] for item in sorted(data.keys())]
            cont = [data[item] for item in sorted(data.keys())]
            table_print(tabletitle, cont)

        return data

    def get_score_by_url(self, url, lst_name='lessons', type=None):
        soup = Soup(self.http_request.session, url)
        data = {}
        _lessons = soup.find_all('tr', {'onmouseover': True})
        data['nums'] = len(_lessons)
        data[lst_name] = []
        for item in _lessons:
            _temp = item.find_all('span')
            data[lst_name].append([ele.text for ele in _temp if ele.text.strip()])
        if type == 's':
            self.average = soup.find(id="ctl00_ContentPlaceHolder1_lblpjcj").text
            self.total = soup.find(id="ctl00_ContentPlaceHolder1_lblKcms").text
            self.credit = soup.find( id="ctl00_ContentPlaceHolder1_lblXfs").text
            data['average'] = self.average
            data['total'] = self.total
            data['credit'] = self.credit

        return data

    def get_score(self):
        score_url = 'http://219.242.68.34/xuesheng/cjcx.aspx'

        return self.get_score_by_url(score_url, lst_name='lessons', type='s')

    def get_npass_lesson(self):
        npass_url = 'http://219.242.68.34/xuesheng/cxcjcx.aspx'
        return self.get_score_by_url(npass_url, 'npass')


#    def get_score(self):
#        score_url = 'http://219.242.68.34/xuesheng/cjcx.aspx'
#        soup = Soup(self.http_request.session, score_url)
#        all_scoreifo = [item.text.strip() for item in soup.find_all('td')]
#        indexs = all_scoreifo[0::10]
#        coursenum = all_scoreifo[1::10]
#        years = all_scoreifo[2::10]
#        terms = all_scoreifo[3::10]
#        times = all_scoreifo[4::10]
#        units = all_scoreifo[5::10]
#        natures = all_scoreifo[7::10]
#        courses = all_scoreifo[8::10]
#        scores = map(lambda x: ' / '.join(x),
#                     [item.split('\n') for item in all_scoreifo[9::10]])
#        self.average = soup.find(id="ctl00_ContentPlaceHolder1_lblpjcj").text
#        self.total = soup.find(id="ctl00_ContentPlaceHolder1_lblKcms").text
#        self.credit = soup.find( id="ctl00_ContentPlaceHolder1_lblXfs").text
#
#        tabletitle = ['序号', '课程', '成绩', '学分', '学年', '学期', '性质']
#        conts = []
#        conts = {
#            'nums': 0,
#            'lessons': []
#        }
#
#        for index, timee, year, term, unit, nature, course, score in \
#                zip(coursenum, times, years, terms, units, natures, courses, scores):
#            temp = [index, year, term, timee, unit, nature, course.strip(), score.replace('\n', '')]
#            conts['lessons'].append(temp)
#        conts['nums'] = len(conts['lessons'])
#        conts['average'] = self.average
#        conts['credit'] = self.credit
#        if self.display:
#            table_print(tabletitle, conts['lessons'])
#            table_print(['平均成绩','课程门数', '已获得学分'],
#                        [[conts['average'],
#                          conts['nums'],
#                          conts['credit']]])
#        return conts


    def get_elective(self):
        """
        获取选修课信息
        """
        eleurl = 'http://219.242.68.34/xuesheng/xsxk.aspx'
        form_data= {
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "__VIEWSTATE": (
                "/wEPDwULLTE1NDU0NjAxMDUPZBYCZg9kFgICAw9kFgICAQ9k"
                "FgICAw8QDxYGHg1EYXRhVGV4dEZpZWxkBQRrenNtHg5EYXRh"
                "VmFsdWVGaWVsZAUDa3poHgtfIURhdGFCb3VuZGdkEBUgJzIw"
                "MTctMjAxOOWtpuW5tOesrOS4gOWtpuacn+mAieS/ruivvue7"
                "hBcxNi0xN+esrOS6jOWtpuacn+WFrOmAiRcxNi0xN+esrOS4"
                "gOWtpuacn+WFrOmAiRcxNS0xNuesrOS6jOWtpuacn+WFrOmA"
                "iRcxNS0xNuesrOS4gOWtpuacn+WFrOmAiRcxNC0xNeesrOS6"
                "jOWtpuacn+WFrOmAiRcxNC0xNeesrOS4gOWtpuacn+WFrOmA"
                "iRcxMy0xNOesrOS6jOWtpuacn+WFrOmAiRcxMy0xNOesrOS4"
                "gOWtpuacn+WFrOmAiRnoi7Hor63nu7zlkIjmioDog73ln7nl"
                "hbsxFzEyLTEz56ys5LqM5a2m5pyf5YWs6YCJGeiLseivree7"
                "vOWQiOaKgOiDveWfueWFuzEXMTItMTPnrKzkuIDlrabmnJ/lh"
                "azpgIkXMTEtMTLnrKzkuozlrabmnJ/lhazpgIkXMTEtMTLnr"
                "KzkuIDlrabmnJ/lhazpgIkXMTAtMTHnrKzkuozlrabmnJ/lh"
                "azpgIkXMTAtMTHnrKzkuIDlrabmnJ/lhazpgIkXMDktMTDnr"
                "KzkuozlrabmnJ/lhazpgIkXMDktMTDnrKzkuIDlrabmnJ/lh"
                "azpgIkXMDgtMDnnrKzkuozlrabmnJ/lhazpgIkXMDgtMDnnr"
                "KzkuIDlrabmnJ/lhazpgIkXMDctMDjnrKzkuozlrabmnJ/lh"
                "azpgIkXMDctMDjnrKzkuIDlrabmnJ/lhazpgIkXMDYtMDfnr"
                "KzkuozlrabmnJ/lhazpgIkXMDYtMDfnrKzkuIDlrabmnJ/lh"
                "azpgIkXMDUtMDbnrKzkuozlrabmnJ/lhazpgIkXMDUtMDbnr"
                "KzkuIDlrabmnJ/lhazpgIkXMDQtMDXnrKzkuozlrabmnJ/lh"
                "azpgIkXMDQtMDXnrKzkuIDlrabmnJ/lhazpgIkXMDMtMDTnr"
                "KzkuozlrabmnJ/lhazpgIkXMDMtMDTnrKzkuIDlrabmnJ/lh"
                "azpgIkXMDItMDPnrKzkuozlrabmnJ/lhazpgIkVIAMzNzADM"
                "zUwAzMyNAMzMjEDMzE4AzMxNAMzMTMDMzAyAzI0MwMyNDIDM"
                "jQxAzI0MAMyMzkDMjM4AzIzNwMyMzYDMjM1AzIzNAMyMzMDM"
                "jMyAzIzMQMyMzADMjI5AzIyOAMyMjcDMjI2AzIxNgMyMTUDM"
                "jE0AzIxMwMyMTIDMjEwFCsDIGdnZ2dnZ2dnZ2dnZ2dnZ2dnZ"
                "2dnZ2dnZ2dnZ2dnZ2dnFgFmZGSw1zc2s74URoSnb4939YdTe"
                "PhePiySgYeGG6HE2bZQ8A=="
            ),
            "__VIEWSTATEGENERATOR": "E7E695A4",
            "ctl00$ContentPlaceHolder1$drplKcz": '321',
            "ctl00$ContentPlaceHolder1$btnYxkc": "查 看"
        }
        ss = self.http_request.post(eleurl, data=form_data)
        soup = BeautifulSoup(ss.text, 'html.parser')
        all_num = soup.find_all('td')
        all_item = [item.text for item in all_num]
        indexs = all_item[1::5]
        times = [item[4:].strip() for item in all_item[2::5]]
        courses = [item.split()[0] for item in all_item[4::5]]
        teachers = [item.split()[1] for item in all_item[4::5]]
        tabletitle = ['序号', '课程组', '课程名称', '任课教师']
        conts = {}
        conts['lessons'] = []
        for index, time, course, teacher in zip(indexs, times, courses, teachers):
            temp = [index, time, course, teacher]
            conts.get('lessons').append(temp)
        if self.display:
            table_print(tabletitle, conts.get('lessons'))
        conts['nums'] = len(conts.get('lessons'))
        return conts

    def cli(self):
        prompt = '''
        +===========================+
        |   [0]查成绩               |
        |   [1]个人信息             |
        |   [2]选修课               |
        |   [3]登录其他账号         |
        |   [4]清除历史记录         |
        |   [5]安全退出             |
        +===========================+
        >>> '''
        self.usrname = rinput('学号: ')
        self.usrpswd = rinput('密码: 00000000\b\b\b\b\b\b\b\b')

        status = self.login()
        if status['status']:
            choice = True
            choice_dict = {
                '0': self.get_score,
                '1': self.get_info,
                '2': self.elective,
                '3': self.cli,
                '4': clear,
                '5': quit
            }
            while choice is True:
                usr_choice = rinput('\r'+prompt).strip()[0]
                os.system('clear')
                if usr_choice in choice_dict:
                    choice_dict.get(usr_choice)()
                    choice = usr_choice not in "35"
                else:
                    print('Input incorrect..again!')
        else:
            print(status['info'])

            cho = rinput('Any key to continue, [q] to quit.')

            if cho == 'q':
                quit()
            else:
                self.cli()

if __name__ == '__main__':
    os.system('clear')
    start = Score()
    start.cli()
