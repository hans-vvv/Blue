from flask import Flask
app = Flask(__name__)


@app.route('/')
def hello_world():

    page = """
    <html>
  <head>
    <title>politie.test website</title>
  </head>
  <body>
    <h1>Hello Python World!</h1>

    <p>This is the landing page of <strong>politie.test</strong>.</p>
  </body>
</html>
"""
    return page

if __name__ == '__main__':
  app.run()
