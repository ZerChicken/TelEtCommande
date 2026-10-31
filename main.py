import logging
import os
import platform
import time
import threading
import webbrowser
from flask import Flask, jsonify, request
import pyautogui

# Désactiver les logs HTTP automatiques de Flask/Werkzeug pour garder la console propre
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

app = Flask(__name__)

# Gestion des rafales (Debounce / Coalescing) pour ne garder que la dernière action
_rafale_lock = threading.Lock()
_derniere_action_timer = None
_action_en_attente = None
FENETRE_RAFALE = 0.25  # Fenêtre de 250 ms pour regrouper les actions simultanées

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


def planifier_derniere_action(action_func, description="action"):
    """
    Enregistre l'action et ne planifie l'exécution que de la TOUTE DERNIÈRE action 
    reçue pendant la fenêtre de rafale (anti-flood de reconnexion ou clics multiples).
    """
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
    """Vérifie si un paramètre de temps 't' est présent (en GET ou JSON) et calcule son âge."""
    t_val = request.args.get('t')
    if not t_val and request.is_json:
        data = request.get_json(silent=True) or {}
        t_val = data.get('t') or data.get('timestamp')
    
    if t_val:
        try:
            t_float = float(t_val)
            # Si le timestamp est en millisecondes (ex: Date.now()), le convertir en secondes
            if t_float > 10**11:
                t_float /= 1000.0
            age = time.time() - t_float
            return age
        except (ValueError, TypeError):
            pass
    return None


@app.route('/press/<action_type>', methods=['GET', 'POST'])
def press_key(action_type):
    """Exécute une action clavier, souris ou système via un switch/case avec protection anti-rafale."""
    global ACTIONS_AUTORISEES, MOVE_PIXELS

    if action_type in ACTIONS_AUTORISEES:
        # Vérification de l'âge (> 5 secondes -> ignoré)
        age = verifier_age_et_extraire_t()
        if age is not None and age > 5.0:
            print(f"[i] Action {action_type} ignorée car trop ancienne (âge: {age:.1f}s)")
            return jsonify({'status': 'ignored', 'message': 'Action trop ancienne ignorée'}), 200

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
        return jsonify(
            {'status': 'success', 'message': f'Action {action_type} mise en file d\'attente !'}
        ), 200
    else:
        print(f'[-] Tentative d\'action non autorisée : {action_type}')
        return jsonify(
            {'status': 'error', 'message': 'Action non autorisée'}
        ), 400


@app.route('/open-url', methods=['POST'])
def open_url():
    """Ouvre une URL directement dans le navigateur avec protection anti-rafale."""
    try:
        data = request.json or {}
        url = data.get('url', '')
        if url:
            age = verifier_age_et_extraire_t()
            if age is not None and age > 5.0:
                return jsonify({'status': 'ignored', 'message': 'URL trop ancienne ignorée'}), 200

            def action_to_execute():
                webbrowser.open(url)

            planifier_derniere_action(action_to_execute, f"open-url {url}")
            return jsonify({'status': 'success', 'message': 'URL mise en file !'}), 200
        print("[-] Erreur : URL vide lors de la tentative d'ouverture")
        return jsonify({'status': 'error', 'message': 'URL vide'}), 400
    except Exception as e:
        print(f"[-] Erreur lors de l'ouverture de l'URL : {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/type', methods=['POST'])
def type_text():
    """Simule la saisie clavier d'une chaîne de texte avec protection anti-rafale."""
    try:
        data = request.json or {}
        text = data.get('text', '')
        if text:
            age = verifier_age_et_extraire_t()
            if age is not None and age > 5.0:
                return jsonify({'status': 'ignored', 'message': 'Texte trop ancien ignoré'}), 200

            def action_to_execute():
                pyautogui.write(text, interval=0)

            planifier_derniere_action(action_to_execute, "type_text")
            return jsonify({'status': 'success', 'message': 'Texte mis en file !'}), 200
        print("[-] Erreur : Texte vide lors de la tentative de saisie")
        return jsonify({'status': 'error', 'message': 'Texte vide'}), 400
    except Exception as e:
        print(f'[-] Erreur de saisie : {str(e)}')
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/move', methods=['POST'])
def move_mouse():
    """Déplace directement le curseur de la souris avec protection anti-rafale."""
    try:
        data = request.get_json(silent=True) or {}
        dx = int(data.get('dx', 0))
        dy = int(data.get('dy', 0))
        if dx != 0 or dy != 0:
            age = verifier_age_et_extraire_t()
            if age is not None and age > 5.0:
                return jsonify({'status': 'ignored', 'message': 'Mouvement trop ancien ignoré'}), 200

            def action_to_execute():
                pyautogui.moveRel(dx, dy)

            planifier_derniere_action(action_to_execute, "move_mouse")
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        print(f'[-] Erreur lors du déplacement de la souris : {str(e)}')
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    print('=== Serveur Télécommande PC démarré ===')
    app.run(host='0.0.0.0', port=5000, threaded=True)