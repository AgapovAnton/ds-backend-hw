from flask import Flask, request
from models.plate_reader import PlateReader
import logging
import io
from PIL import UnidentifiedImageError
import requests


app = Flask(__name__)
plate_reader = PlateReader.load_from_file('./model_weights/plate_reader_model.pth')
URL_IMAGES = 'http://51.250.83.169:7878/images/'


@app.route('/')
def hello():
    return '<h1><center>Hello!<?center><?h1>'


# ip:port/toUpper?s=hello
@app.route('/toUpper')
def to_upper():
    if 's' not in request.args:
        return 'invalid args', 400

    s = request.args['s']
    return {
        'result': s.upper(),
    }


# /readNumber <- img bin
# {"name": "о128но11"}
@app.route('/readNumber', methods=["POST"])
def read_number():
    body = request.get_data()
    im = io.BytesIO(body)
    try:
        res = plate_reader.read_text(im)
    except UnidentifiedImageError:
        return {"error": "invalid image"}, 400
    return {"name": res}


# ip:port/ID?s <- img binary
@app.route('/ID')
def id():
    if 's' not in request.args:
        return 'invalid args', 400

    id_img = request.args['s']
    url_curr_img = 'http://51.250.83.169:7878/images/{x}'.format(x = id_img)

    p = requests.get(url_curr_img, stream=True)
    im = io.BytesIO(p.content)
    
    try:
        res = plate_reader.read_text(im)
    except UnidentifiedImageError:
        return {"error": "invalid image"}, 400
    
    return {"name": res}



if __name__ == '__main__':
    logging.basicConfig(
        format='[%(levelname)s] [%(asctime)s] %(message)s',
        level=logging.INFO,
    )

    app.config['JSON_AS_ASCII'] = False
    app.run(host='0.0.0.0', port=8080, debug=True)
