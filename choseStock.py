#!/usr/bin/env python
# -*- coding: utf-8 -*-


import requests
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy()
app.config['SECRET_KEY'] = 'GFybLeHB/lEQX'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./shose.db'
app.config['TOKEN'] = '5e9f7dc2-cc65-4e60-a8ba-47d13e401b7a'
JSON_DATA = {
    'token': '',
    'stockCodes': [],
    'metrics': []
}


class Stock:
    id = db.Column(db.Integer, index=True, primary_key=True, autoincrement=True)
    code = db.Column(db.String(12), index=True, unique=True)
    name = db.Column(db.String(16), index=True, unique=True)



class LixingerStock:
    
    def __init__(self, area="cn"):
        self.token = app.config['TOKEN']
        self.area = area

    def fundamental(self, *args):
        json_data = JSON_DATA
        json_data['token'] = self.token
        json_data['stockCodes'] = list(*args)
        json_data['metrics'] = [
            'd_pe_ttm', 'd_pe_ttm_pos10', 'd_pe_ttm_pos_all',
            'pb', 'pb_pos10', 'pb_pos_all',
            'pe_ttm', 'pe_ttm_pos10', 'pe_ttm_pos_all'
        ]
        return requests.post('https://open.lixinger.com/api/a/stock/fundamental', json=json_data).json()

    def industry(self, *args):
        json_data = JSON_DATA
        json_data['token'] = self.token
        json_data['metrics'] = [
            'q.profitStatement.bi.t',
            'q.balanceSheet.ar.t',
            'q.balanceSheet.s.t',
            'q.balanceSheet.tca_tcl_r.t'
        ]
        json_data['stockCodes'] = list(*args)
        return requests.post('https://open.lixinger.com/api/a/stock/fs/industry', json=json_data).json()


def init_industry(stock):
    JSON_DATA['startDate'] = '2014-01-01'
    JSON_DATA['endDate'] = '2018-09-07'
    s = LixingerStock()
    st = [stock]
    return s.industry(st)['data']


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/excellent', methods=['GET', 'POST'])
def excellent():
    if request.method == 'POST':
        stock_code = [request.form.get('stockCode')]

    return render_template('excellent.html', excellent='active')
    

@app.route('/cheap')
def cheap():
    return render_template('cheap.html', cheap='active')
