# API_ID : 25087710
# API_HASH : 515303aa944af6f217c62d6e60287d11


from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
import pandas as pd
from datetime import datetime
import os


# === Identifiants API Telegram ===
api_id = 25087710    
api_hash = '515303aa944af6f217c62d6e60287d11'  
phone = '+33783304668' 

# Nom de la session locale (fichier .session créé à la première connexion)
session_name = 'test_scraper_session'

# === Dossier pour stocker les médias ===
os.makedirs('media', exist_ok=True)

# Création du client Telegram (connexion utilisateur, pas bot)
client = TelegramClient(session_name, api_id, api_hash)

async def scrape_group(group_username, limit=500):
    """
    Fonction principale pour extraire les messages d'un groupe Telegram.
    """
    await client.start(phone)  # Authentification par numéro de téléphone

    # Récupère les infos du groupe
    entity = await client.get_entity(group_username)

    # Requête d'historique des messages
    messages = await client(GetHistoryRequest(
        peer=entity,
        limit=limit,           # Nombre de messages à récupérer
        offset_date=None,
        offset_id=0,
        max_id=0,
        min_id=0,
        add_offset=0,
        hash=0
    ))

    # Liste où stocker les données des messages
    data = []

    for msg in messages.messages:
        sender_id = msg.sender_id
        date = msg.date
        text = msg.message if msg.message else ""
        has_media = msg.media is not None
        reactions = msg.reactions

        media_type = None
        media_file = None

        if has_media:
            media_type = type(msg.media).__name__
            # Téléchargement du média
            try:
                media_file = await msg.download_media(file='media/')
            except:
                media_file = "DOWNLOAD_ERROR"

        # Traitement des réactions (si disponibles)
        reaction_dict = {}
        if reactions:
            for r in reactions.results:
                reaction_dict[str(r.reaction)] = r.count

        # Ajout du message au dataset
        data.append({
            'message_id': msg.id,
            'sender_id': sender_id,
            'date': date,
            'text': text,
            'has_media': has_media,
            'media_type': media_type,
            'media_file': media_file,
            'reactions': reaction_dict
        })

    # Création d’un DataFrame Pandas pour l’analyse
    df = pd.DataFrame(data)
    today = datetime.now().strftime('%Y-%m-%d')
    df.to_csv(f'{group_username}_messages_{today}.csv', index=False)
    print(f"✅ {len(df)} messages sauvegardés dans {group_username}_messages_{today}.csv")
