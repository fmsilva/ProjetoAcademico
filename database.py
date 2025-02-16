import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

DB_FILE = "projeto_academico.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Para aceder às colunas por nome
    return conn

def criar_tabelas():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Tabelas (coloque aqui o código SQL para criar as tabelas que forneceu)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS utilizadores (
            id_utilizador INTEGER PRIMARY KEY AUTOINCREMENT,
            utilizador VARCHAR(50) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            nome VARCHAR(100) NOT NULL ,
            onedrive_apikey varchar(200),
            astrometrykey varchar(200)
        );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_utilizador ON utilizadores(utilizador);")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fotografias (
            id_fotografia INTEGER PRIMARY KEY AUTOINCREMENT,
            id_utilizador INTEGER NOT NULL,
            nome_ficheiro VARCHAR(255) NOT NULL,
            caminho_ficheiro VARCHAR(512) NOT NULL,
            data_hora DATETIME NOT NULL,
            upload_cloud integer ,
            upload_astrometry integer,
            -- Metadados FITS comuns
            fits_bitpix INTEGER,
            fits_naxis INTEGER,
            fits_naxis1 INTEGER,
            fits_naxis2 INTEGER,
            fits_exposure FLOAT,
            fits_telescope VARCHAR(100),
            fits_instrument VARCHAR(100),
            fits_observer VARCHAR(100),
            fits_object VARCHAR(100),
            fits_ra FLOAT,
            fits_dec FLOAT,
            fits_filter VARCHAR(50),
            fits_date_obs DATETIME,
            fits_airmass FLOAT,
            fits_gain FLOAT,
            fits_temp_ccd FLOAT,
            
            -- Campos de Astrometria
            astrometria_processada BOOLEAN DEFAULT FALSE,
            data_processamento_astrometria DATETIME,
            wcs_crval1 DOUBLE,
            wcs_crval2 DOUBLE,
            wcs_crpix1 DOUBLE,
            wcs_crpix2 DOUBLE,
            wcs_cd1_1 DOUBLE,
            wcs_cd1_2 DOUBLE,
            wcs_cd2_1 DOUBLE,
            wcs_cd2_2 DOUBLE,
            escala_pixel DOUBLE,
            angulo_rotacao DOUBLE,
            precisao_astrometrica DOUBLE,

            FOREIGN KEY (id_utilizador) REFERENCES utilizadores(id_utilizador)
                ON DELETE RESTRICT
                ON UPDATE CASCADE
        );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fotos_utilizador ON fotografias(id_utilizador);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fotos_data ON fotografias(data_hora);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fotos_objeto ON fotografias(fits_object);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fotos_astrometria ON fotografias(astrometria_processada);")

    conn.commit()
    conn.close()

def verificar_credenciais(utilizador, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM utilizadores WHERE utilizador = ?", (utilizador,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user["password"], password):
        return True
    return False

def registar_utilizador(utilizador, password, nome):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_password = generate_password_hash(password)
    try:
        cursor.execute("""
            INSERT INTO utilizadores (utilizador, password, nome) 
            VALUES (?, ?, ?)
        """, (utilizador, hashed_password, nome))
        conn.commit()
        return True
    except sqlite3.IntegrityError:  # Utilizador já existe
        return False
    finally:
        conn.close()

# Funções para inserir, consultar, atualizar e apagar dados (fotos, etc.)
# ... (Implemente aqui as funções CRUD para a tabela de fotografias) ...

