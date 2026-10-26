"""
Généré par Gemini
"""

from flask import Flask
import pyautogui

app = Flask(__name__)

@app.route('/press/<key>')
def press_key(key):
  if key in ['space', 'escape', 'enter']:
    pyautogui.press(key)
    return f'Touche {key壓} simulée !', 200
  return 'Touche non autorisée', 400


if __name__ == '__main__':
  # Écoute sur toutes les interfaces, accessible via l'IP Tailscale
  app.run(host='0.0.0.0', port=5000)