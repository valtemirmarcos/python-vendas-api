from flask import request, send_from_directory, abort
app = None

def init_route_imagens(flask_app):
    global app
    app = flask_app

    @app.route('/imgs/<path:filename>')
    def imgs(filename):
        IMAGES_FOLDER = 'static/imgs'
        if request.path.startswith('/imgs'):
            return send_from_directory(IMAGES_FOLDER, filename)
        else:
            # return send_from_directory(IMAGES_FOLDER, 'semfoto.jpg')
            abort(403)


