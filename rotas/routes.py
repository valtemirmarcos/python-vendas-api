from flask import Flask, jsonify, request, send_from_directory, abort
from config.db import db

app = None  # Placeholder for Flask app instance

def init_routes(flask_app):
  global app
  app = flask_app

  from controllers.usuariosController import usuariosController

  usuarios_ctl = usuariosController()

  @app.route('/login', methods=['POST'])
  def usuarios_login():
      return usuarios_ctl.login()

  @app.route('/imgs/<path:filename>')
  def imgs(filename):
      IMAGES_FOLDER = 'static/imgs'
      if request.path.startswith('/imgs'):
          return send_from_directory(IMAGES_FOLDER, filename)
      else:
          abort(403)