#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__auther__ = 'tsuno teppei'

from os import path
import csv
import json
import argparse

# 定数
CONF_DIR = '/var/lib/zabbix/conf.d'

# 引数処理
parser = argparse.ArgumentParser()
parser.add_argument('CSV', type=str)
params = parser.parse_args()

# 相対パスで上位ディレクトリに移動禁止、拡張子は削除
params.CSV = params.CSV.replace('../', '').replace('.csv', '')
targetCsv = path.join(CONF_DIR, params.CSV + '.csv')

# CSVファイル読み込み
try:
    with open(targetCsv, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    result = {'code': 0, 'data': rows}
except Exception as e:
    result = {'code': 1, 'error': str(e)}

# 結果出力
print(json.dumps(result))
exit()
#EOF    