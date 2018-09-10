#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Flask, render_template

app = Flask(__name__)
app.config['SECRET_KEY'] = 'GFybLeHB/lEQX'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./shose.db'


@app.route('/')
def index():
    return render_template('index.html')
