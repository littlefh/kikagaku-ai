# coding: utf-8

#　必要なモジュールのインポート
from flask import Flask, request, render_template, redirect, url_for
import json
import requests
import io
import os
import base64
from PIL import Image, PngImagePlugin
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# Flaskオブジェクトをインスタンス化
app = Flask(__name__)

# バックエンドURLを環境変数より取得
load_dotenv()  # take environment variables from .env.
api_url = os.getenv('API_URL', None)

# トップページ
@app.route('/')
def route():
    # AIいらすとやページにリダイレクト
    return redirect(url_for('irasutoya'))

# AIいらすとや
@app.route('/irasutoya', methods = ['GET', 'POST'])
def irasutoya():
    # POST メソッドの条件の定義
    if request.method == 'POST':
        prompt = request.form.get('prompt')
        seed = request.form.get('seed')
        img = generate(prompt, seed)
        dict = { "image": img }
        return json.dumps(dict)

    # GET メソッドの定義
    elif request.method == 'GET':
        return render_template('irasutoya.html')


def gettime():
    d = datetime.now(timezone(timedelta(hours=+9)))
    dt = d.strftime('%Y%m%d_%H%M%S')
    return dt

# 画像生成
def generate(words, seed):
    if api_url is None:
        print('no api_url')
        return None
    prompt = "<hypernet:irasutoya_hypternetwork:1> an irasutoya style illustration of " + words
    params = {
    #  "restore_faces": False,
    #  "face_restorer": "CodeFormer",
    #  "codeformer_weight": 0.5,
    "prompt": prompt,
    #  "negative_prompt": "lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry",
    "seed": int(seed),
    #  "seed_enable_extras": False,
    #  "subseed": -1,
    #  "subseed_strength": 0,
    #  "seed_resize_from_h": 0,
    #  "seed_resize_from_w": 0,
    "sampler_name": "Euler a",
    "steps": 20,
    "cfg_scale": 7,
    #  "denoising_strength": 0.35,
    #  "batch_count": 1,
    #  "batch_size": 1,
    #  "base_size": 512,
    #  "max_size": 768,
    #  "tiling": False,
    #  "highres_fix": False,
    #  "firstphase_height": 512,
    #  "firstphase_width": 512,
    #  "upscaler_name": "None",
    #  "filter_nsfw": False,
    #  "include_grid": False,
    #  "sample_path": "outputs/krita-out",
    "width": 512,
    "height": 512
    }
    # 画像生成
    response = requests.post(url=f'{api_url}/sdapi/v1/txt2img', json=params)
    if response.status_code != requests.codes.ok:
        print(response.status_code)
        return None
    
    r = response.json()
    for img in r['images']:
        image = Image.open(io.BytesIO(base64.b64decode(img.split(",",1)[0])))
        png_payload = {
            "image": 'data:image/png;base64,{}'.format(img)
        }
        # 画像情報を取得
        response2 = requests.post(url=f'{api_url}/sdapi/v1/png-info', json=png_payload)

        # 画像情報をPNGのメタデータとして設定
        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("parameters", response2.json().get("info"))
#        # デバッグ用の画像保存
#        image.save(f'output_{gettime()}.png', pnginfo=pnginfo)

        # 画面表示用のbase64に変換
        buf = io.BytesIO()
        image.save(buf, 'png', pnginfo=pnginfo)
        base64_str = base64.b64encode(buf.getvalue()).decode('utf-8')
        base64_data = 'data:image/png;base64,{}'.format(base64_str)
        return base64_data

if __name__ == '__main__':
    app.run(debug=True) # デバッグ用、コード変更時に自動リロードされる
#    app.run()