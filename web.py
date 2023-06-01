from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def begin():    
    return render_template('begin.html')

@app.route('/upload')
def upload(): #跳转个页面在这里加一个，然后在html文件里把这个页面放到上面例如 href = "/upload"
    return render_template('upload.html')
if __name__ == '__main__':
    app.run(debug=True,port=8080)
