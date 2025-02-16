from flask import Flask, render_template, request, redirect, url_for, session
from database import criar_tabelas, verificar_credenciais, registar_utilizador
# Importe as funções de outros módulos (onedrive_utils, astrometry_utils) aqui

app = Flask(__name__)
app.secret_key = "uma_chave_secreta_super_segura"  # MUITO IMPORTANTE: Mude isto para algo realmente secreto!

# Rotas

@app.route("/")
def index():
    if "utilizador" in session:
        return redirect(url_for("menu"))  # Redireciona para o menu se já estiver autenticado
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    utilizador = request.form["utilizador"]
    password = request.form["password"]

    if verificar_credenciais(utilizador, password):
        session["utilizador"] = utilizador  # Armazena o utilizador na sessão
        return redirect(url_for("menu"))
    else:
        return render_template("index.html", erro="Credenciais inválidas.")

@app.route("/registar", methods=["POST"])
def registar():
    utilizador = request.form["utilizador"]
    password = request.form["password"]
    nome = request.form["nome"]

    if registar_utilizador(utilizador, password, nome):
        return redirect(url_for("index"))  # Redireciona após registo bem-sucedido
    else:
        return render_template("index.html", erro="Erro ao registar utilizador.")
    
@app.route("/logout")
def logout():
    session.pop("utilizador", None)  # Remove o utilizador da sessão
    return redirect(url_for("index"))


@app.route("/menu")
def menu():
    if "utilizador" not in session:
        return redirect(url_for("index"))  # Protege a rota do menu
    return render_template("menu.html")

# Rotas para os submenus (coloque aqui as rotas para cada item do menu)
@app.route("/inserir_fotos")
def inserir_fotos():
    return render_template("inserir_fotos.html")

@app.route("/consultar")
def consultar():
    return render_template("consultar_fotos.html")

@app.route("/sincronizar")
def sincronizar():
    return render_template("sincronizar_onedrive.html")

@app.route("/manutencao")
def manutencao():
    return render_template("manutencao.html")

@app.route("/astrometria")
def astrometria():
    return render_template("astrometria.html")

# Submenus de Consultar
@app.route("/consultar/data")
def consultar_data():
    return render_template("consultar_data.html")

@app.route("/consultar/objeto")
def consultar_objeto():
    return render_template("consultar_objecto.html")

@app.route("/consultar/astrometria")
def consultar_astrometria_submenu():
    return render_template("consultar_astrometria.html")

# Submenus de Manutenção
@app.route("/manutencao/bd")
def manutencao_bd():
    return render_template("manutencao_bd.html")

@app.route("/manutencao/cloud")
def manutencao_cloud():
    return render_template("manutencao_cloud.html")

@app.route("/manutencao/utilizadores")
def manutencao_utilizadores():
    return render_template("manutencao_utilizadores.html")

# Submenus de Astrometria
@app.route("/astrometria/enviar")
def enviar_astrometria():
    return render_template("enviar_astrometria.html")

@app.route("/astrometria/verificar")
def verificar_astrometria():
    return render_template("verificar_astrometria.html")




if __name__ == "__main__":
    criar_tabelas()  # Garante que as tabelas são criadas
    app.run(debug=True, host='0.0.0.0', port=5000)  # Permite acesso de outros dispositivos na rede
    