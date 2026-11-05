from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, Producto

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta_super_segura' # Necesario para sesiones
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tienda.db' # Base de datos local
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Si no está logueado, redirige aquí

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- RUTAS ---

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Verificar si existe
        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            flash('El usuario ya existe')
            return redirect(url_for('register'))
        
        nuevo_user = User(username=username)
        nuevo_user.set_password(password)
        db.session.add(nuevo_user)
        db.session.commit()
        flash('Registro exitoso, por favor inicia sesión')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('productos'))
        else:
            flash('Credenciales incorrectas')
    return render_template('login.html')

@app.route('/productos')
@login_required # Solo usuarios registrados pueden ver esto (VIP)
def productos():
    # Aquí consultamos las tortas a la base de datos
    lista_tortas = Producto.query.all()
    return render_template('productos.html', tortas=lista_tortas)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- INICIALIZAR DB Y DATOS DE PRUEBA ---
with app.app_context():
    db.create_all()
    # Si no hay productos, creamos 5 tortas de prueba
    if Producto.query.count() == 0:
        tortas_prueba = [
            Producto(nombre="Torta de Chocolate", descripcion="Deliciosa torta de chocolate belga con relleno de ganache.", precio=25.00, imagen_url="https://via.placeholder.com/150"),
            Producto(nombre="Torta de Vainilla", descripcion="Clásica torta de vainilla con crema pastelera y fresas.", precio=22.00, imagen_url="https://via.placeholder.com/150"),
            Producto(nombre="Torta Red Velvet", descripcion="Espectacular torta roja con frosting de queso crema.", precio=28.00, imagen_url="https://via.placeholder.com/150"),
            Producto(nombre="Torta de Fresa", descripcion="Torta esponjosa con capas de fresas naturales y crema.", precio=24.00, imagen_url="https://via.placeholder.com/150"),
            Producto(nombre="Torta de Limón", descripcion="Refrescante torta de limón con merengue italiano.", precio=20.00, imagen_url="https://via.placeholder.com/150"),
        ]
        db.session.add_all(tortas_prueba)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)