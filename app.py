#!/usr/bin/env python
# coding=utf-8

import requests
import json
import random
from datetime import datetime
from flask import Flask
from flask import render_template, session, redirect, url_for, flash
# from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_moment import Moment

import configparser,os

#################################################################################
#由配置文件引入所需变量
#################################################################################

proDir = os.path.dirname(os.path.realpath(__file__))
print(proDir)
configPath = os.path.join(proDir,"config.txt")

cp = configparser.ConfigParser()
cp.read(configPath)

url=cp.get('zabbix1', 'zabbix_url')
user=cp.get('zabbix1', 'zabbix_user')
password=cp.get('zabbix1', 'zabbix_pass')
header=cp.get('zabbix1', 'zabbix_header')
header=json.loads(header)
# print(url,user,header,password)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ssss'

# manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)

class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/', methods=['GET','POST'])
def index():
    name = None
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Looks like you have changed your name!')
        session['name'] = form.name.data
        return redirect(url_for('index'))
    return render_template('index.html',form=form, name=session.get('name'))

@app.route('/user/<name>')
def show_template(name):
    return render_template('user.html', name=name)

# if __name__ == '__main__':
#     manager.run()






class ZabbixApi():
    def __init__(self,url,header,user,password):
        self.url = url
        self.header = header
        self.user = user
        self.password = password

    def loginid(self):
        data = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "user": self.user,
                "password": self.password,
            },
            "id": random.randint(1,10)
        }
        data = json.dumps(data)
        r = requests.post(url=self.url,headers=self.header,data=data)
        dict = json.loads(r.text)
        # print(r)
        # print(r.status_code)
        # print(r.text)
        r.close()
        authID = dict['result']
        print(authID)
        return authID

    def get_data(self,data):
        r = requests.post(url=self.url,headers=self.header,data=data)
        return r

    def host_get(self, authid):
        data = {
                "jsonrpc": "2.0",
                "method": "host.get",
                "params": {
                    "output": ["hostid" , "name", "status","host"],
                    "selectInterfaces": ["interfaceid",'ip']
                },
                "auth": authid,
                "id": random.randint(1,10)
            }
        data=json.dumps(data)
        # print(data)
        res = self.get_data(data)
        print(res.apparent_encoding)
        res.close()
        print(res.text)
        print(type(res))
        res = res.json()['result']
        print(res)
        for item in res:
            # print(item)
            item['interfaces'] = item['interfaces'][0]['ip']
        print(res)
        # 返回列表
        return res


# url = 'http://zabbix.51eanj.com/zabbix/api_jsonrpc.php'
# header = {"Content-Type": "application/json"}
# print(type(header))
# user = 'Admin'
# passwd = '1qaz2wsx'
za = ZabbixApi(url,header,user,password)
authid=za.loginid()
print(authid)

@app.route('/host_list')
def show_host():
    host_list = za.host_get(authid)
    return render_template('host_list.html',host_list=host_list)
