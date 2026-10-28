import logging
import os
import platform
import webbrowser
from flask import Flask, jsonify, request
import pyautogui

# Désactiver les logs HTTP automatiques de Flask/Werkzeug pour garder la console propre
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

pyautogui.FAILSAFE = False
pyautogui.PAUSE = (
    0  # Supprime le délai par défaut de PyAutoGUI pour une réactivité instantanée
)

app = Flask(__name__)

# Variables constantes globales
ACTIONS_AUTORISEES = (
    'fullscreen',
    'scrollup',
    'scrolldown',
    'pageup',
    'pagedown',
    'enter',
    'up',
    'down',
    'left',
    'right',
    'volumeup',
    'volumedown',
    'volumemute',
    'click',
    'ctrl-w',
    'browser-back',
    'browser-forward',
    'space',
    'sleep',
)

MOVE_PIXELS = 20


@app.after_request
def after_request(response):
    """Ajoute les en-têtes CORS à chaque réponse HTTP sortante."""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add(
        'Access-Control-Allow-Headers', 'Content-Type,Authorization'
    )
    response.headers.add(
        'Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS'
    )
    return response

def reveiller_curseur():
    """Effectue un micro-mouvement invisible pour forcer le système à réafficher le curseur."""
    try:
        pyautogui.moveRel(1, 0)
        pyautogui.moveRel(-1, 0)
    except:
        pass

@app.route('/press/<action_type>', methods=['GET', 'POST'])
def press_key(action_type):
    global ACTIONS_AUTORISEES, MOVE_PIXELS

    if action_type in ACTIONS_AUTORISEES:
        try:
            match action_type:
                case 'fullscreen':
                    pyautogui.press('f')
                    reveiller_curseur() # Réaffiche le curseur en sortant/entrant du plein écran
                case 'pageup' | 'scrollup':
                    pyautogui.press('pageup')
                case 'pagedown' | 'scrolldown':
                    pyautogui.press('pagedown')
                case 'ctrl-w':
                    pyautogui.hotkey('ctrl', 'w')
                case 'browser-back':
                    pyautogui.hotkey('alt', 'left')
                case 'browser-forward':
                    pyautogui.hotkey('alt', 'right')
                case 'click':
                    reveiller_curseur() # Force l'affichage du curseur avant de cliquer
                    pyautogui.click()
                case 'space':
                    pyautogui.press('space')
                    reveiller_curseur() # Réveille le curseur si une barre de contrôle vidéo s'affiche
                case 'volumemute':
                    pyautogui.press('volumemute')
                case 'sleep':
                    system_os = platform.system()
                    if system_os == 'Windows':
                        os.system('rundll32.exe powrprof.dll,SetSuspendState 0,0,0')
                    elif system_os == 'Linux':
                        os.system('systemctl suspend')
                    elif system_os == 'Darwin':
                        os.system('pmset sleepnow')
                case 'up':
                    pyautogui.moveRel(0, -MOVE_PIXELS)
                case 'down':
                    pyautogui.moveRel(0, MOVE_PIXELS)
                case 'left' | 'right':
                    pyautogui.press(action_type)
                case 'volumeup' | 'volumedown':
                    pyautogui.press(action_type)
                case _:
                    pyautogui.press(action_type)

            return jsonify({'status': 'success', 'message': f'Action {action_type} exécutée !'}), 200
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    else:
        return jsonify({'status': 'error', 'message': 'Action non autorisée'}), 400

@app.route('/open-url', methods=['POST'])
def open_url():
    """Ouvre une URL directement dans le navigateur de la machine distante."""
    try:
        data = request.json or {}
        url = data.get('url', '')
        if url:
            webbrowser.open(url)
            return jsonify({'status': 'success', 'message': 'URL ouverte !'}), 200
        print("[-] Erreur : URL vide lors de la tentative d'ouverture")
        return jsonify({'status': 'error', 'message': 'URL vide'}), 400
    except Exception as e:
        print(f"[-] Erreur lors de l'ouverture de l'URL : {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/type', methods=['POST'])
def type_text():
    """Simule la saisie clavier d'une chaîne de texte sur la machine distante."""
    try:
        data = request.json or {}
        text = data.get('text', '')
        if text:
            pyautogui.write(
                text, interval=0
            )  # Frappe instantanée sans délai par caractère
            return jsonify({'status': 'success', 'message': 'Texte saisi !'}), 200
        print("[-] Erreur : Texte vide lors de la tentative de saisie")
        return jsonify({'status': 'error', 'message': 'Texte vide'}), 400
    except Exception as e:
        print(f'[-] Erreur de saisie : {str(e)}')
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/move', methods=['POST'])
def move_mouse():
    """Déplace le curseur de la souris de manière relative sur la machine distante."""
    try:
        data = request.json or {}
        dx = int(data.get('dx', 0))
        dy = int(data.get('dy', 0))
        if dx != 0 or dy != 0:
            pyautogui.moveRel(dx, dy)
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        print(f'[-] Erreur lors du déplacement de la souris : {str(e)}')
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    print('=== Serveur Télécommande PC démarré ===')
    # threaded=True permet de traiter les requêtes en parallèle (vital pour le joystick et la fluidité)
    app.run(host='0.0.0.0', port=5000, threaded=True)