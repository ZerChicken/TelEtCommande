import logging
import os
import platform
import time
import threading
import webbrowser
from flask import Flask, jsonify, request
import pyautogui

# Désactiver les logs HTTP automatiques pour garder la console propre
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

app = Flask(__name__)

# Gestion des rafales uniquement pour les actions uniques (clics, touches)
_rafale_lock = threading.Lock()
_derniere_action_timer = None
_action_en_attente = None
FENETRE_RAFALE = 0.05

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


def planifier_derniere_action(action_func, description="action"):
    global _derniere_action_timer, _action_en_attente

    with _rafale_lock:
        if _derniere_action_timer is not None:
            _derniere_action_timer.cancel()
        
        _action_en_attente = (action_func, description)

        def _executer():
            global _action_en_attente, _derniere_action_timer
            with _rafale_lock:
                func_to_run = _action_en_attente
                _action_en_attente = None
                _derniere_action_timer = None
            
            if func_to_run:
                f, desc = func_to_run
                try:
                    f()
                except Exception as e:
                    print(f"[-] Erreur lors de l'exécution de {desc}: {str(e)}")

        _derniere_action_timer = threading.Timer(FENETRE_RAFALE, _executer)
        _derniere_action_timer.start()


def verifier_age_et_extraire_t():
    t_val = request.args.get('t')
    if not t_val and request.is_json:
        data = request.get_json(silent=True) or {}
        t_val = data.get('t') or data.get('timestamp')
    
    if t_val:
        try:
            t_float = float(t_val)
            if t_float > 10**11:
                t_float /= 1000.0
            return time.time() - t_float
        except (ValueError, TypeError):
            pass
    return None


@app.route('/press/<action_type>', methods=['GET', 'POST'])
def press_key(action_type):
    global ACTIONS_AUTORISEES, MOVE_PIXELS

    if action_type in ACTIONS_AUTORISEES:
        age = verifier_age_et_extraire_t()
        if age is not None and age > 5.0:
            return jsonify({'status': 'ignored', 'message': 'Action trop ancienne'}), 200

        def action_to_execute():
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

        planifier_derniere_action(action_to_execute, f"action {action_type}")
        return jsonify({'status': 'success'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Action non autorisée'}), 400


@app.route('/open-url', methods=['POST'])
def open_url():
    try:
        data = request.json or {}
        url = data.get('url', '')
        if url:
            age = verifier_age_et_extraire_t()
            if age is not None and age > 5.0:
                return jsonify({'status': 'ignored'}), 200
            planifier_derniere_action(lambda: webbrowser.open(url), f"open-url {url}")
            return jsonify({'status': 'success'}), 200
        return jsonify({'status': 'error'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/type', methods=['POST'])
def type_text():
    try:
        data = request.json or {}
        text = data.get('text', '')
        if text:
            age = verifier_age_et_extraire_t()
            if age is not None and age > 5.0:
                return jsonify({'status': 'ignored'}), 200
            planifier_derniere_action(lambda: pyautogui.write(text, interval=0), "type_text")
            return jsonify({'status': 'success'}), 200
        return jsonify({'status': 'error'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/move', methods=['POST'])
def move_mouse():
    """EXÉCUTION INSTANTANÉE DIRECTE (Pas de timer) pour une fluidité maximale du joystick."""
    try:
        data = request.get_json(silent=True) or {}
        dx = int(data.get('dx', 0))
        dy = int(data.get('dy', 0))
        if dx != 0 or dy != 0:
            age = verifier_age_et_extraire_t()
            if age is not None and age > 5.0:
                return jsonify({'status': 'ignored'}), 200
            pyautogui.moveRel(dx, dy)
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        print(f'[-] Erreur lors du déplacement de la souris : {str(e)}')
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    print('=== PC Remote Control Server Started ===')
    print('Press Ctrl+C to stop the server.')
    app.run(host='0.0.0.0', port=5000, threaded=True)