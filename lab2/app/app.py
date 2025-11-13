import random
from flask import Flask, render_template, request, make_response
from faker import Faker

fake = Faker()

app = Flask(__name__)
application = app

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/args')
def args():
    return render_template('args.html')

@app.route('/headers')
def headers():
    return render_template('headers.html')

@app.route('/cookie')
def cookie():
    resp = make_response(render_template('cookie.html'))
    if 'cookie_name' not in request.cookies:
        resp.set_cookie('cookie_name', 'new_cookie')
    else:
        resp.set_cookie('cookie_name', expires=0)
    return resp

@app.route('/form', methods=['GET', 'POST'])
def form():
    return render_template('form.html')


@app.route('/phone_numbr', methods=['GET', 'POST'])
def phone_numbr():
    error = None
    phone = None
    formatted_phone = None

    if request.method == 'POST':
        phone = request.form.get('phone', '')

        if any(c for c in phone if not (c.isdigit() or c in ' +()-.')):
            error = 'Недопустимый ввод. В номере телефона встречаются недопустимые символы.'
        else:
            numbers = ''.join(c for c in phone if c.isdigit())

            if phone[0] == '8' or phone[0:2] == '+7':
                if len(numbers) != 11:
                    error = 'Недопустимый ввод. Неверное количество цифр.'
            else:
                if len(numbers) != 10:
                    error = 'Недопустимый ввод. Неверное количество цифр.'

            if not error:
                if phone[0:2] == '+7':
                    numbers = '8' + numbers[1:]

                if len(numbers) == 11:
                    formatted_phone = f"8-{numbers[1:4]}-{numbers[4:7]}-{numbers[7:9]}-{numbers[9:]}"
                else:
                    formatted_phone = f"8-{numbers[0:3]}-{numbers[3:6]}-{numbers[6:8]}-{numbers[8:]}"

    return render_template('phone_numbr.html', error=error, phone=phone, formatted_phone=formatted_phone)


if __name__ == "__main__":
    app.run(debug=True)