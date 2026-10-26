from flask import Flask, jsonify, request
import pyautogui

pyautogui.FAILSAFE = False

app = Flask(__name__)


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


# Route pour presser une touche ou effectuer un raccourci prédéfini
@app.route('/press/<action_type>', methods=['GET', 'POST'])
def press_key(action_type):
  actions_autorisees = [
      'escape',
      'tab',
      'shift-tab',
      'enter',
      'up',
      'down',
      'left',
      'right',
      'volumeup',
      'volumedown',
      'click',
      'ctrl-w',
      'browser-back',
      'browser-forward',
  ]

  # Distance de déplacement du curseur pour les flèches (20 pixels)
  MOVE_PIXELS = 20

  if action_type in actions_autorisees:
    try:
      if action_type == 'shift-tab':
        pyautogui.hotkey('shift', 'tab')
      elif action_type == 'ctrl-w':
        pyautogui.hotkey('ctrl', 'w')
      elif action_type == 'browser-back':
        # Simule le bouton "Précédent" du navigateur (Alt + Flèche Gauche)
        pyautogui.hotkey('alt', 'left')
      elif action_type == 'browser-forward':
        # Simule le bouton "Suivant" du navigateur (Alt + Flèche Droite)
        pyautogui.hotkey('alt', 'right')
      elif action_type == 'click':
        pyautogui.click()
      # Les flèches déplacent désormais le curseur de la souris de 20px
      elif action_type == 'up':
        pyautogui.moveRel(0, -MOVE_PIXELS)
      elif action_type == 'down':
        pyautogui.moveRel(0, MOVE_PIXELS)
      elif action_type == 'left':
        pyautogui.moveRel(-MOVE_PIXELS, 0)
      elif action_type == 'right':
        pyautogui.moveRel(MOVE_PIXELS, 0)
      elif action_type in ['volumeup', 'volumedown']:
        pyautogui.press(action_type)
      else:
        pyautogui.press(action_type)

      print(f'[+] Action exécutée avec succès : {action_type}')
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


# Route pour taper du texte arbitraire envoyé depuis le champ de saisie
@app.route('/type', methods=['POST'])
def type_text():
  try:
    data = request.json or {}
    text = data.get('text', '')
    if text:
      pyautogui.write(text, interval=0.01)
      print(f"[+] Texte saisi : '{text}'")
      return jsonify({'status': 'success', 'message': 'Texte saisi !'}), 200
    return jsonify({'status': 'error', 'message': 'Texte vide'}), 400
  except Exception as e:
    print(f'[-] Erreur de saisie : {str(e)}')
    return jsonify({'status': 'error', 'message': str(e)}), 500


# Route pour déplacer la souris dynamiquement (ex: joystick)
@app.route('/move', methods=['POST'])
def move_mouse():
  try:
    data = request.json or {}
    dx = int(data.get('dx', 0))
    dy = int(data.get('dy', 0))
    if dx != 0 or dy != 0:
      pyautogui.moveRel(dx, dy)
    return jsonify({'status': 'success'}), 200
  except Exception as e:
    return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
  print('=== Serveur Télécommande PC démarré ===')
  app.run(host='0.0.0.0', port=5000)