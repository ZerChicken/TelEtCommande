"""
Généré par Gemini
"""
from flask import Flask, jsonify, request
import pyautogui

# Désactive la sécurité de coin d'écran PyAutoGUI (optionnel, évite les blocages si la souris bouge)
pyautogui.FAILSAFE = False

app = Flask(__name__)


@app.route('/press/<key>', methods=['GET', 'POST'])
def press_key(key):
  # Liste des touches autorisées pour éviter toute exécution indésirable
  touches_autorisees = ['escape', 'tab', 'enter', 'up', 'down', 'left', 'right']

  if key in touches_autorisees:
    try:
      pyautogui.press(key)
      print(f'[+] Touche simulée avec succès : {key}')
      return jsonify(
          {'status': 'success', 'message': f'Touche {key} simulée !'}
      ), 200
    except Exception as e:
      print(f'[-] Erreur lors de la simulation de {key}: {str(e)}')
      return jsonify({'status': 'error', 'message': str(e)}), 500
  else:
    print(f'[-] Tentative de touche non autorisée : {key}')
    return jsonify(
        {'status': 'error', 'message': 'Touche non autorisée'}
    ), 400


if __name__ == '__main__':
  # host='0.0.0.0' permet d'écouter sur toutes les interfaces réseau, y compris Tailscale
  # Le port 5000 est utilisé par défaut
  print("=== Serveur de télécommande démarré ===")
  print("En attente de requêtes via Tailscale...")
  app.run(host='0.0.0.0', port=5000)