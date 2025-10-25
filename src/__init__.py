from flask import Flask 
from flask_cors import CORS
from .resources import users_bp
from .views.home import bp 
import socket
import qrcode
import ssl  # Importar o módulo SSL
import os

def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)    
    
    # app.register_blueprint(users_bp, prefix="/api")
    app.register_blueprint(bp)    
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()

    # Gerar QR Code para HTTPS
    url_https = f"https://{ip}:5000"  # Agora com HTTPS
    url_http = f"http://{ip}:5000"    # Mantém HTTP também
    
    qr = qrcode.make(url_https)
    qr.save("qrcode_https.png")
    print(f"✅ QR Code HTTPS salvo como 'qrcode_https.png'")
    
    qr_http = qrcode.make(url_http)
    qr_http.save("qrcode_http.png")
    print(f"✅ QR Code HTTP salvo como 'qrcode_http.png'")

    return app

def run_app_with_ssl(app):
    """Executa o app Flask com SSL"""
    # Obter IP local
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    
    print("🔐 INICIANDO SERVIDOR COM SSL...")
    print(f"📱 URLs disponíveis:")
    print(f"   🔒 HTTPS (Geolocation): https://{ip}:5000")
    print(f"   🔓 HTTP: http://{ip}:5000")
    print("⚠️  No navegador, aceite o certificado de segurança")
    
    try:
        # Opção 1: SSL automático (mais simples)
        app.run(
            host='0.0.0.0', 
            port=5000, 
            ssl_context='adhoc',  # Gera certificado SSL automaticamente
            debug=True
        )
    except Exception as e:
        print(f"❌ Erro com SSL automático: {e}")
        print("🔄 Tentando com SSL manual...")
        
        # Opção 2: SSL manual com certificados gerados
        try:
            # Gera certificados self-signed (apenas desenvolvimento)
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            context.load_cert_chain('cert.pem', 'key.pem')  # Você precisará gerar estes arquivos
            
            app.run(
                host='0.0.0.0', 
                port=5000, 
                ssl_context=context,
                debug=True
            )
        except:
            print("❌ SSL manual falhou. Executando sem SSL...")
            app.run(host='0.0.0.0', port=5000, debug=True)

# Se estiver executando este arquivo diretamente
if __name__ == '__main__':
    app = create_app()
    run_app_with_ssl(app)