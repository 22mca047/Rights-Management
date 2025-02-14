from flask import Flask, render_template, request, redirect, url_for, session
from sqlalchemy import create_engine, text

app = Flask(__name__)
app.secret_key = 'h1i2t3'
engine = create_engine('mysql+pymysql://root:root@localhost:3306/my_db')


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/roleassign', methods=['GET', 'POST'])
def roleassign():
    if request.method == 'POST':
        user_id = request.form['user_id']
        can_add = 'can_add' in request.form
        can_update = 'can_update' in request.form
        can_delete = 'can_delete' in request.form
        print(can_add, can_update, can_delete, 'user : ', user_id)
        connection = engine.connect()
        query = text("""INSERT INTO role (user_id, can_add, can_update, can_delete)
            VALUES (:user_id, :can_add, :can_update, :can_delete)
            ON DUPLICATE KEY UPDATE
            can_add = VALUES(can_add),
            can_update = VALUES(can_update),
            can_delete = VALUES(can_delete)""")

        connection.execute(query,
                           {'user_id': user_id, 'can_add': can_add, 'can_update': can_update, 'can_delete': can_delete})
        connection.commit()
        return redirect('right')


@app.route('/userhome', methods=['GET', 'POST'])
def userhome():
    id = session.get('id')
    print("session id : ", id)
    connection = engine.connect()
    query1 = text("select * from rights where id=:id")
    result1 = connection.execute(query1, {'id': id}).fetchone()
    print(result1)
    query2 = text("""SELECT r.*, ro.can_add, ro.can_update, ro.can_delete
                FROM rights r
                LEFT JOIN role ro ON r.id = ro.user_id""")
    result2 = connection.execute(query2).fetchall()
    print(result2)
    return render_template('user-home.html', result1=result1, result2=result2)


@app.route('/right', methods=['GET', 'POST'])
def right():
    id = session.get('id')
    print(id)
    connection = engine.connect()
    quary = text("select * from rights where id=:id")
    result1 = connection.execute(quary, {'id': id}).fetchone()
    print(result1)
    query2 = text("""
                SELECT r.*, ro.can_add, ro.can_update, ro.can_delete
                FROM rights r
                LEFT JOIN role ro ON r.id = ro.user_id
            """)
    result2 = connection.execute(query2).fetchall()
    print(result2)
    connection.commit()
    return render_template('right-manage.html', result1=result1, result2=result2)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        print(email)
        connection = engine.connect()
        query = text("select * from rights where email=:email")
        result = connection.execute(query, {'email': email}).fetchone()

        if result[2] == email and result[3] == password:
            session['id'] = result[0]
            print(result[5])
            if result[5] == '1':
                return redirect(url_for('right'))
            else:
                return redirect(url_for('userhome'))

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        email = request.form['email']
        password = request.form['password']
        cpassword = request.form['cpassword']
        connection = engine.connect()
        if password != cpassword:
            msg = "Please Check Password and Conform Password"
            return redirect(url_for('register', msg=msg))
        quary = text("insert into rights (name, email, password, age) values (:name, :email, :password, :age)")
        connection.execute(quary, {'name': name, 'email': email, 'password': password, 'age': age})
        connection.commit()
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/edituser', methods=['GET', 'POST'])
def edituser():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        email = request.form['email']
        password = request.form['password']
        id = request.form['id']
        connection = engine.connect()
        query = text("update rights set name=:name, email=:email, password=:password, age=:age where id=:id")
        result = connection.execute(query, {'name': name, 'email': email, 'password': password, 'age': age, 'id': id})
        connection.commit()
        return redirect(url_for('userhome'))

    else:
        id = request.args.get('id')
        connection = engine.connect()
        quary = text("select * from rights where id=:id")
        result = connection.execute(quary, {'id': id}).fetchone()
        connection.commit()
        return render_template('edit-user.html', result=result)


@app.route('/adduser', methods=['GET', 'POST'])
def adduser():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        email = request.form['email']
        password = request.form['password']
        cpassword = request.form['cpassword']
        connection = engine.connect()
        if password != cpassword:
            msg = "Please Check Password and Conform Password"
            return redirect(url_for('register', msg=msg))
        quary = text("insert into rights (name, email, password, age) values (:name, :email, :password, :age)")
        connection.execute(quary, {'name': name, 'email': email, 'password': password, 'age': age})
        connection.commit()
        return redirect(url_for('userhome'))
    return render_template('Add-User.html')


@app.route('/deleteuser')
def deleteuser():
    id = request.args.get('id')
    connection = engine.connect()
    quary = text("delete from rights where id=:id")
    connection.execute(quary, {'id': id})
    connection.commit()
    return redirect(url_for('userhome'))


if __name__ == '__main__':
    app.run(debug=True)
