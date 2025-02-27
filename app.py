from flask import Flask, render_template, request, redirect, url_for, session
from datetime import date, datetime, timedelta
import os


# Funções de outros módulos (onedrive_utils, astrometry_utils) aqui
from database import consultar_fotos_data, criar_tabelas, verificar_credenciais, registar_utilizador, enviar_foto_bd



app = Flask(__name__)
app.secret_key = "uma_chave_secreta_super_segura"  # MUITO IMPORTANTE: Mude isto para algo realmente secreto!
UPLOAD_FOLDER = 'c:\\Users\\Astrofotografia\\Downloads\\'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ASTROMETRY_API_KEY = "aqpdlyzudqutrakk" # Chave da API NOVA.ASTROMETRY.NET
ASTROMETRY_URL = "http://nova.astrometry.net/api/"


# Configurações de variaveis de ambiente
utilizador_navegacao = ""

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
    utilizador_navegacao = utilizador
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
@app.route("/inserir_fotos", methods=['GET'])
def inserir_fotos():
    return render_template("inserir_fotos.html")

@app.route("/consultar")
def consultar():
    return render_template("consultar_fotos.html")

@app.route("/sincronizar")
def sincronizar():
    return render_template("sincronizar_com_onedrive.html")

@app.route("/manutencao")
def manutencao():
    return render_template("manutencao.html")

@app.route("/astrometria")
def astrometria():
    return render_template("astrometria.html")

# Submenus de Consultar
@app.route("/consultar/data")

def consultar_data(id_utilizador, data_inicio, data_fim):
    data_fim = date.today()
    data_inicio = data_fim - timedelta(days=9)
    fotos_encontradas = consultar_fotos_data(utilizador_navegacao, data_inicio, data_fim)
    return render_template('fotos_data.html', fotos=fotos_encontradas)

@app.route("/consultar/objeto")
def consultar_objeto():
    return render_template("consultar_objecto.html")

@app.route("/consultar/astrometria")
def consultar_astrometria_submenu():
    return render_template("consultar_astrometria.html")

# Sair do sub menu consultar 
@app.route("/consultar/voltar")
def consultar_voltar():
    return render_template("menu.html")

# Sair do sub menu manutencao
@app.route("/manutencao/voltar")
def manutencao_voltar():
    return render_template("menu.html")

# Sair do sub menu da astrometria
@app.route("/astrometria/voltar")
def astrometria_voltar():
    return render_template("menu.html")


# Submenus de Manutenção
@app.route("/manutencao/base_dados")
def manutencao_base_dados():
   return render_template("manutencao_base_dados.html")

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

# upload da foto
@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        if 'foto' not in request.files:
            return 'Nenhum arquivo enviado'
        foto = request.files['foto']
        if foto.filename == '':
            return 'Nenhum arquivo selecionado'
        if foto:
            # Obtém a data e hora atual
            data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Monta o nome do arquivo e o caminho
            nome_ficheiro = foto.filename
            caminho_ficheiro = os.path.join(app.config['UPLOAD_FOLDER'], nome_ficheiro)

            # Salva o arquivo
            #foto.save(caminho_ficheiro)

            # Insere os dados na base de dados
            enviar_foto_bd(utilizador_navegacao, nome_ficheiro, caminho_ficheiro, data_hora)

            return redirect(url_for('menu'))

            
    return 'Erro no upload'


if __name__ == "__main__":
    criar_tabelas()  # Garante que as tabelas são criadas
    app.run(debug=True, host='0.0.0.0', port=5000)  # Permite acesso de outros dispositivos na rede
    