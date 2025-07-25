from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Configuração da app e da base de dados
app = Flask(__name__)
app.secret_key = 'chave-super-secreta'  # muda isto em produção
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db = SQLAlchemy(app)

# Modelo da Tarefa
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
# Modelo do Usuário
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    tasks = db.relationship('Task', backref='user', lazy=True)

# Página principal
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']

    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Task(content=task_content, user_id=user_id)
        db.session.add(new_task)
        db.session.commit()
        return redirect('/')

    tasks = Task.query.filter_by(user_id=user_id).order_by(Task.id).all()
    return render_template('index.html', tasks=tasks)


# Página de login

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect('/')
        else:
            return 'Credenciais inválidas'

    return render_template('login.html')

# Registro de usuário
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        if User.query.filter_by(username=username).first():
            return 'Usuário já existe!'

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')

    return render_template('register.html')
# Logout do usuário
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/login')


# Apagar tarefa
@app.route('/delete/<int:id>')
def delete(id):
    task = Task.query.get_or_404(id)

    try:
        db.session.delete(task)
        db.session.commit()
        return redirect('/')
    except:
        return 'Erro ao apagar tarefa'

# Marcar como concluída
@app.route('/complete/<int:id>')
def complete(id):
    task = Task.query.get_or_404(id)
    task.completed = not task.completed

    try:
        db.session.commit()
        return redirect('/')
    except:
        return 'Erro ao atualizar tarefa'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
