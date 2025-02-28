#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__auther__ = 'tsuno teppei'

from socket import create_connection
from ssl import create_default_context, DER_cert_to_PEM_cert, CERT_NONE
from smtplib import SMTP
from OpenSSL import crypto
from datetime import datetime, timezone
import argparse
import json

# 定数
TIMEOUT = 5
DATA_F_CERT = '%Y%m%d%H%M%S%z'
DATA_F_OUTPUT = '%Y-%m-%d %H:%M:%S %Z'
PKEY_TYPE = {
    crypto.TYPE_RSA: 'RSA',
    crypto.TYPE_DSA: 'DSA',
    crypto.TYPE_DH: 'DH',
    crypto.TYPE_EC: 'Elliptic Curve',
}

# 変数初期化
result = {'code':0, 'data':{}}

# 引数処理
parser = argparse.ArgumentParser()
parser.add_argument('endpoint', type=str)
parser.add_argument('--port', '-p', type=int, default=443)
parser.add_argument('--vhostname', '-v', type=str, default=None)
parser.add_argument('--type', '-t', choices=['https', 'smtp'], default='https')
parser.add_argument('--check-hostname', '-ch', choices=['YES', 'NO'], default='NO')
params = parser.parse_args()

# 接続設定、バーチャルホスト名利用の場合の指定
endpoint = (params.endpoint, params.port)
hostname = params.vhostname if params.vhostname else params.endpoint
protocolType = params.type

try:
    # SSL証明書取得
    context = create_default_context()
    if params.check_hostname == 'NO':
        context.check_hostname = False
        context.verify_mode = CERT_NONE
    if protocolType == 'smtp':
        with SMTP(*endpoint) as smtp:
            smtp.starttls(context=context)
            cert = smtp.sock.getpeercert(True)
    else:
        with create_connection(endpoint, timeout=TIMEOUT) as targetEndpoint:
            with context.wrap_socket(targetEndpoint, server_hostname=hostname) as targetCert:
                cert = targetCert.getpeercert(True)
    # 証明書情報取得
    cert = DER_cert_to_PEM_cert(cert)
    loadCert = crypto.load_certificate(crypto.FILETYPE_PEM, cert.encode('utf-8'))
    startDate = datetime.strptime(loadCert.get_notBefore().decode(), DATA_F_CERT)
    endDate = datetime.strptime(loadCert.get_notAfter().decode(), DATA_F_CERT)
    timeLeft = endDate - datetime.now(timezone.utc)
    result['data'] = {
        'serialNumber': loadCert.get_serial_number(),
        'version': loadCert.get_version(),
        'issuer': loadCert.get_issuer().O,
        'cn': loadCert.get_subject().CN,
        'fingerprintSha1': loadCert.digest('sha1').decode(),
        'fingerprintSha256': loadCert.digest('sha256').decode(),
        'sigunatureAlgorithm': loadCert.get_signature_algorithm().decode(),
        'publicKeyAlgorithm': PKEY_TYPE[loadCert.get_pubkey().type()],
        'publicKeyBits': loadCert.get_pubkey().bits(),
        'startDate': startDate.strftime(DATA_F_OUTPUT),
        'endDate': endDate.strftime(DATA_F_OUTPUT),
        'timeLeft': int(timeLeft.total_seconds()),
    }
except Exception as e:
    # エラー時の処理
    result['code'] = 1
    result['data'] = {'error': str(e)}

# 結果出力
print(json.dumps(result))
exit()
#EOF