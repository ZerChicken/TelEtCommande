from flask import Flask, jsonify
import pyautogui

pyautogui.FAILSAFE = False

app = Flask(__name__)


# Ajout des en-têtes CORS pour autoriser le site web à contacter le serveur Python
@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add(
      'Access-Control-Allow-Headers', 'Content-Type,Authorization'
  )
  response.headers.add(
      'Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS'
  )
  return response


@app.route('/press/<key>', methods=['GET', 'POST'])
def press_key(key):
    # Ajout de 'shift-tab' dans les touches autorisées
    touches_autorisees = ['escape', 'tab', 'shift-tab', 'enter', 'up', 'down', 'left', 'right']

    if key in touches_autorisees:
        try:
            if key == 'shift-tab':
                pyautogui.hotkey('shift', 'tab')
            else:
                pyautogui.press(key)
                
            print(f"[+] Action simulée avec succès : {key}")
            return jsonify({"status": "success", "message": f"Action {key} simulée !"}), 200
        except Exception as e:
            print(f"[-] Erreur lors de la simulation de {key}: {str(e)}")
            return jsonify({"status": "error", "message": str(e)}), 500
    else:
        print(f"[-] Tentative de touche non autorisée : {key}")
        return jsonify({"status": "error", "message": "Touche non autorisée"}), 400


if __name__ == '__main__':
  print('=== Serveur de télécommande démarré ===')
  print('En attente de requêtes via Tailscale...')
  app.run(host='0.0.0.0', port=5000)