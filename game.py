from flask import Flask, request, jsonify, render_template_string, redirect


app = Flask(__name__)

@app.route('/')
def healthcheck():
    html_template =  """"""
     

    return render_template_string(html_template)


if __name__ == '__main__':
    app.run(host = 'localhost', port = 8080, debug = True)  
