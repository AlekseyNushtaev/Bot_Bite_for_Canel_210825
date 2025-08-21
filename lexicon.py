import datetime

from config import REWARD_PER_VIEW, MAX_VIDEOS_PER_CYCLE, BONUS_BETWEEN_7_AND_8, SPONSOR_CHANNEL_LINK, COOLDOWN_DAYS, \
    BONUS_AFTER_17, MIN_WITHDRAWAL
from db.utils import format_time_remaining

lexicon_dct = {
    'de': {
        'preload_text': 'Wir finden bezahlte Videos für dich...',
        'full_load_text': 'Videos wurden erfolgreich gefunden, viel Spab beim Ansehen!',
        'welcome_title_with_first_name': '👋🏻 Willkommen, ',
        'welcome_title_without_first_name': '👋🏻 Willkommen!',
        'welcome_body': f'''
🔥 Wir verbinden TikTok-Ersteller mit unseren Nutzern. Verdiene Geld durch Steigerung ihrer Popularität.

👀 Für jede Ansicht auf TikTok zahlen wir dir {REWARD_PER_VIEW}€

☑️ Klicke auf "Verstanden" um sofort mit dem Verdienen zu beginnen.
''',
        'welcome_button': '☑️ Verstanden',
        'main_menu_button': 'Hauptmenü',
        'to_chanel_button': '📲 Kanal besuchen',
        'text_to_10_messsage': lambda x: f'''
⭕️ Du hast die maximale Anzahl erlaubter Videos erreicht ⭕️

🟢 Jedes neue Mitglied erhält nach {format_time_remaining(x)} 🕕 die Möglichkeit zur Erneuerung
🟢 Das Auszahlungssystem funktioniert einwandfrei.

Um dein tägliches Videolimit von 10 auf 20 zu erhöhen, musst du den Kanal abonnieren!
                    ''',
        'text_end_cycle': lambda x: f'''
⭕️ Du hast die maximale Anzahl erlaubter Videos erreicht ⭕️

🟢 Jedes neue Mitglied erhält nach {format_time_remaining(x)} 🕕 die Möglichkeit zur Erneuerung
🟢 Das Auszahlungssystem funktioniert einwandfrei.
                ''',
        'no_video_text': 'Noch keine Videos verfügbar, erwarte.',
        'video_text_1': lambda x: f'''
✅ Ansicht erfolgreich registriert
• Kontostand: {x}€ → {x + REWARD_PER_VIEW}€    
        ''',
        'video_text_2_in': lambda x, y: f'''
📱 Vergütung pro Ansicht: {REWARD_PER_VIEW}€

✅ Abgeschlossen: {x} von {MAX_VIDEOS_PER_CYCLE}
💰 Aktueller Kontostand: {y}€
            ''',
        'video_text_2_out': lambda x, y: f'''
📱 Vergütung pro Ansicht: {REWARD_PER_VIEW}€

✅ Abgeschlossen: {x} von {10}
💰 Aktueller Kontostand: {y}€
            ''',
        'text_between_7_and_8': f'''
🎁 Bonus: Herzlichen Glückwunsch, du hast eine zusätzliche Belohnung von unserem Sponsor erhalten!

  · {BONUS_BETWEEN_7_AND_8}€
  
  Um deinen Bonus zu erhalten, klicke auf den Button «🎁 Erhalte {BONUS_BETWEEN_7_AND_8}€»
            ''',
        'button_between_7_and_8_yes': f'🎁 Erhalte {BONUS_BETWEEN_7_AND_8}€',
        'button_between_7_and_8_no': f'⛔️ Ich lehne {BONUS_BETWEEN_7_AND_8}€ ab',
        'button_like': f'👍 Gefällt mir (+{REWARD_PER_VIEW}€)',
        'button_unlike': f'👎 Gefällt mir nicht (+{REWARD_PER_VIEW}€)',
        'button_cancel_look': '🖐 Beenden',
        'awarning_to_look': '❗️ Du hast das Video nicht bis zum Ende angesehen!',
        'text_cancel_look': 'Bestätigst du, dass du den Prozess des Ansehens bezahlter Videos beenden möchtest?',
        'button_return_to_look': '👀 Nein, weitermachen',
        'button_cancel_look_yes': '✅ Ja, beenden',
        'text_main_menu': 'Bitte wählen Sie eine Option aus dem Menü⤵️',
        'button_main_video': '☑️ Verdienen',
        'button_main_profile': '🧑‍💻 Profil',
        'button_main_money_back': '💰 Auszahlung',
        'button_check_bonus': '☑️ Bonus erhalten',
        'text_bonus_between_7_and_8': f'''
Ausgezeichnete Leistung! Um {BONUS_BETWEEN_7_AND_8}€ zu erhalten:

· Abonniere den Kanal: {SPONSOR_CHANNEL_LINK}
· Schaue dir die 5 neuesten Beiträge an.
· Fertig. Drücke den Button "Bonus erhalten" und bekomme +{BONUS_BETWEEN_7_AND_8}€!
''',
        'awarning_not_in_chanel': 'Du hast den Kanal noch nicht abonniert',
        'text_between_17_and_18': lambda x: f'''
🎁 Bonus: Neuer registrierter Benutzer!

  Kontostand: €{x} → €{x + BONUS_AFTER_17}
  
  Melden Sie sich jeden Tag in der App an, um zusätzliche Boni zu erhalten!
            ''',
        'gift_after_7_text': f'✅ Dein Kontostand wurde um den Betrag von {BONUS_BETWEEN_7_AND_8}€ erhöht, verdiene weiter mit uns!',
        'back_button': 'Zurück',
        'bonus_chanel_button': 'Erhalte 17250€',
        'profile_text': lambda x, y, z: f'''
👤Deine Erfolge!
    
Name: {x['first_name'] if x['first_name'] else '...'}
Benutzername: {x['username'] if x['username'] else '...'}
Status: {y} {z} 
Kontostand: {x['balance']}€
Gesamtansichten: {x['like_counter']}
Eingeladene Freunde: 0
Hier sind unsere gemeinsamen Erfolge 🥇
Statistik für {datetime.datetime.now().strftime("%d.%m.%Y")}:
🥇 Teilnehmer: 123.853 Personen.
🥇 Ausgezahlt: 20.140.642€.
🥇 Gesamtansichten: 530.016 Videos.

⏱️ Nächstes Update in 24 Stunden...
    ''',
        'alert_min_withdrawal': f'Mindestauszahlungsbetrag - {MIN_WITHDRAWAL}',
        'phone_button': '📱 Telefon',
        'paypal_button': '🥝 PayPal',
        'binance_button': '📒 Binance',
        'card_button': '💳 Karte',
        'text_requisites': '''
💳 Gib deine Daten für die Überweisung ein.
Unterstützte Banken - Revolut, Raiffeisen, Wise, Transilvania
🔒 Die Sicherheit der Transaktionen hat für uns oberste Priorität. Zufriedene Nutzer sind die beste Werbung für den TikTok-Bot.
        ''',
        'text_withdrawal_value': '''
Gib den Betrag ein, den du abheben möchtest
🔑 Bitte sei sorgfältig bei der Eingabe ❗️❗️❗️
        ''',
        'text_no_digits': '''
Bitte gib den genauen Betrag für die Auszahlung an. 
Schreibe nur den numerischen Wert als Antwort.

Beispiele: 100, 200, 500, 1000
            ''',
        'text_not_in_balance': lambda x, y: f'''
❗️Mindestbetrag für eine Auszahlung: {MIN_WITHDRAWAL}€
💰 Dein aktueller Kontostand: {x}€
Du musst weitere {y - x} verdienen, um eine Auszahlung beantragen zu können

Verdienstmöglichkeiten: 
• durch Ansehen von Videos
• durch Einladen von Freunden
• durch Erhalt von Sponsorenboni

🔥 Über 17250€ kannst du über den Kanal unseres Partners verdienen. Studiere die Informationen auf dem Kanal sorgfältig, um deine Mittel heute auszahlen zu können.
''',
        'text_withdrawal_good': lambda x: f'''
Auszahlungsantrag über {x}€ wurde gesendet:

Bearbeitungszeit bis zu 10 Tagen! 🎉

bitte blockiere den Bot nicht und kündige dein Kanalabonnement nicht, bevor du die Bestätigung über den Geldtransfer erhältst.

wenn du den Bot deaktivierst, verlängert sich die Zeit für den Erhalt von Informationen zur Auszahlung:

drücke „/start" um weiter zu verdienen!💸    
        ''',
        'not_in_chanel': 'Unbestätigt',
        'in_chanel': 'Bestätigt',
        'leave_chanel': 'Abgemeldet',
        'text_chanel_in': '🟢 Großartig, dein Abonnementstatus wurde aktualisiert und du hast jetzt Zugriff auf 20 Videos täglich anstatt 10.',
        'text_chanel_out': '⭕️ Wir haben festgestellt, dass du dein Kanalabonnement gekündigt hast. Das bedeutet, dass du ab jetzt nur auf 10 Videos pro Tag zugreifen kannst. Du kannst dich erneut abonnieren, um Zugang zu 20 Videos zu erhalten.'
    }
}