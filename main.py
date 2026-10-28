import logging
import os
import platform
import time
import webbrowser
from flask import Flask, jsonify, request
import pyautogui

# Désactiver les logs HTTP automatiques de Flask/Werkzeug pour garder la console propre
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

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


def reveiller_curseur():
    """Effectue un micro-mouvement invisible pour forcer le système à réafficher le curseur."""
    try:
        pyautogui.moveRel(1, 0)
        pyautogui.moveRel(-1, 0)
    except:
        pass


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


@app.route('/press/<action_type>', methods=['GET', 'POST'])
def press_key(action_type):
    """Exécute une action clavier, souris ou système via un switch/case (match/case)."""
    global ACTIONS_AUTORISEES, MOVE_PIXELS

    if action_type in ACTIONS_AUTORISEES:
        try:
            match action_type:
                case 'fullscreen':
                    pyautogui.press('f')
                    reveiller_curseur()
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
                    reveiller_curseur()
                    pyautogui.click()
                case 'space':
                    pyautogui.press('space')
                    reveiller_curseur()
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

            return jsonify(
                {'status': 'success', 'message': f'Action {action_type} exécutée !'}
            ), 200
        except Exception as e:
            print(f'[-] Erreur lors de l\'exécution de {action_type}: {str(e)}')
            return jsonify({'status': 'error', 'message': str(e)}), 500
    else:
        print(f'[-] Tentative d\'action non autorisée : {action_type}')
        return jsonify(
            {'status': 'error', 'message': 'Action non autorisée'}
        ), 400


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
            pyautogui.write(text, interval=0)
            return jsonify({'status': 'success', 'message': 'Texte saisi !'}), 200
        print("[-] Erreur : Texte vide lors de la tentative de saisie")
        return jsonify({'status': 'error', 'message': 'Texte vide'}), 400
    except Exception as e:
        print(f'[-] Erreur de saisie : {str(e)}')
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/move', methods=['POST'])
def move_mouse():
    """Déplace le curseur de la souris de manière fluide (lissage) sur la machine distante."""
    try:
        data = request.json or {}
        dx = int(data.get('dx', 0))
        dy = int(data.get('dy', 0))
        if dx != 0 or dy != 0:
            # Lissage (interpolation) sur 6 micro-pas répartis sur ~120ms
            steps = 6
            duration = 0.12
            step_dx = dx / steps
            step_dy = dy / steps
            sleep_time = duration / steps

            cur_x = 0.0
            cur_y = 0.0
            for i in range(steps):
                target_x = (i + 1) * step_dx
                target_y = (i + 1) * step_dy
                move_x = round(target_x - cur_x)
                move_y = round(target_y - cur_y)
                if move_x != 0 or move_y != 0:
                    pyautogui.moveRel(move_x, move_y)
                    cur_x += move_x
                    cur_y += move_y
                time.sleep(sleep_time)

        return jsonify({'status': 'success'}), 200
    except Exception as e:
        print(f'[-] Erreur lors du déplacement de la souris : {str(e)}')
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    print('=== Serveur Télécommande PC démarré ===')
    app.run(host='0.0.0.0', port=5000, threaded=True)