import os
import asyncio
import re
import json
from datetime import datetime
from telethon import TelegramClient, events
from telethon.events import ChatAction
from predictor import CardPredictor
from aiohttp import web
import time

# Configuration par défaut pour Replit
API_ID = int(os.getenv('API_ID', '29177661'))
API_HASH = os.getenv('API_HASH', '')
BOT_TOKEN = os.getenv('BOT_TOKEN', '')
ADMIN_ID = int(os.getenv('ADMIN_ID', '1190237801'))
PORT = int(os.getenv('PORT', '5000'))

# Validation des variables requises
if not API_ID or API_ID == 0:
    raise ValueError("❌ API_ID manquant - Configurez vos Secrets")
if not API_HASH:
    raise ValueError("❌ API_HASH manquant - Configurez vos Secrets")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN manquant - Configurez vos Secrets")

print(f"✅ Configuration chargée pour Replit")
print(f"🔧 Port: {PORT}")

# Variables d'état
detected_stat_channel = None
detected_display_channel = None
confirmation_pending = {}
CONFIG_FILE = 'bot_config.json'

# Gestionnaire de prédictions
predictor = CardPredictor()

# Client Telegram avec session unique
session_name = f'replit_bot_{int(time.time())}'
client = TelegramClient(session_name, API_ID, API_HASH)

def load_config():
    """Charger la configuration depuis le fichier"""
    global detected_stat_channel, detected_display_channel
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                detected_stat_channel = config.get('stat_channel')
                detected_display_channel = config.get('display_channel')
                print(f"✅ Configuration chargée: Stats={detected_stat_channel}, Display={detected_display_channel}")
    except Exception as e:
        print(f"⚠️ Erreur chargement configuration: {e}")

def save_config():
    """Sauvegarder la configuration"""
    try:
        config = {
            'stat_channel': detected_stat_channel,
            'display_channel': detected_display_channel
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        print(f"💾 Configuration sauvegardée")
    except Exception as e:
        print(f"❌ Erreur sauvegarde: {e}")

async def start_bot():
    """Démarrer le bot"""
    try:
        load_config()
        await client.start(bot_token=BOT_TOKEN)
        print("✅ Bot démarré avec succès")
        
        me = await client.get_me()
        username = getattr(me, 'username', 'Unknown')
        print(f"🤖 Bot connecté: @{username}")
        return True
    except Exception as e:
        print(f"❌ Erreur démarrage: {e}")
        return False

# --- ÉVÉNEMENTS BOT ---
@client.on(events.ChatAction())
async def handler_join(event):
    """Gérer l'ajout du bot dans les canaux"""
    global confirmation_pending
    try:
        if event.user_joined or event.user_added:
            me = await client.get_me()
            if event.user_id == getattr(me, 'id', None):
                confirmation_pending[event.chat_id] = 'waiting_confirmation'
                
                try:
                    chat = await client.get_entity(event.chat_id)
                    chat_title = getattr(chat, 'title', f'Canal {event.chat_id}')
                except:
                    chat_title = f'Canal {event.chat_id}'

                invitation_msg = f"""🔔 **Nouveau canal détecté**

📋 **Canal** : {chat_title}
🆔 **ID** : {event.chat_id}

**Commandes de configuration** :
• `/set_stat {event.chat_id}` - Canal de statistiques
• `/set_display {event.chat_id}` - Canal de diffusion"""

                try:
                    await client.send_message(ADMIN_ID, invitation_msg)
                    print(f"📧 Invitation envoyée pour: {chat_title}")
                except Exception as e:
                    print(f"❌ Erreur invitation: {e}")
    except Exception as e:
        print(f"❌ Erreur handler_join: {e}")

@client.on(events.NewMessage(pattern=r'/set_stat (-?\d+)'))
async def set_stat_channel(event):
    """Configurer le canal de statistiques"""
    global detected_stat_channel
    try:
        if event.is_group or event.is_channel or event.sender_id != ADMIN_ID:
            return
            
        channel_id = int(event.pattern_match.group(1))
        detected_stat_channel = channel_id
        save_config()
        
        await event.respond(f"✅ **Canal de statistiques configuré**\n🆔 ID: {channel_id}")
        print(f"📊 Canal stats configuré: {channel_id}")
    except Exception as e:
        print(f"❌ Erreur set_stat: {e}")

@client.on(events.NewMessage(pattern=r'/set_display (-?\d+)'))
async def set_display_channel(event):
    """Configurer le canal de diffusion"""
    global detected_display_channel
    try:
        if event.is_group or event.is_channel or event.sender_id != ADMIN_ID:
            return
            
        channel_id = int(event.pattern_match.group(1))
        detected_display_channel = channel_id
        save_config()
        
        await event.respond(f"✅ **Canal de diffusion configuré**\n🆔 ID: {channel_id}")
        print(f"📤 Canal display configuré: {channel_id}")
    except Exception as e:
        print(f"❌ Erreur set_display: {e}")

@client.on(events.NewMessage(pattern='/start'))
async def start_command(event):
    """Message de bienvenue"""
    welcome_msg = """🎯 **Bot de Prédiction - Replit Edition**

🔹 **Développé par Sossou Kouamé Appolinaire**

**Fonctionnalités** :
• Prédictions automatiques sur déclencheurs 7, 8
• Vérification des résultats en temps réel
• Configuration simple des canaux

**Configuration** :
1. Ajoutez le bot dans vos canaux
2. Utilisez `/set_stat [ID]` et `/set_display [ID]`

**Commandes** :
• `/start` - Ce message
• `/status` - État du bot (admin)
• `/reset` - Réinitialiser (admin)

🚀 **Hébergé sur Replit**"""
    
    await event.respond(welcome_msg)

@client.on(events.NewMessage(pattern='/status'))
async def show_status(event):
    """Afficher le statut"""
    if event.sender_id != ADMIN_ID:
        return
        
    status_msg = f"""📊 **Statut du Bot Replit**

🔧 **Configuration** :
• Canal stats: {'✅' if detected_stat_channel else '❌'} ({detected_stat_channel})
• Canal display: {'✅' if detected_display_channel else '❌'} ({detected_display_channel})

📈 **Prédictions** :
• Actives: {len(predictor.prediction_status)}
• Total: {len(predictor.status_log)}

🌐 **Serveur** : Port {PORT}"""
    
    await event.respond(status_msg)

@client.on(events.NewMessage(pattern='/reset'))
async def reset_bot(event):
    """Réinitialiser le bot"""
    global detected_stat_channel, detected_display_channel
    if event.sender_id != ADMIN_ID:
        return
        
    detected_stat_channel = None
    detected_display_channel = None
    confirmation_pending.clear()
    predictor.reset()
    save_config()
    
    await event.respond("🔄 Bot réinitialisé avec succès")

@client.on(events.NewMessage())
async def handle_messages(event):
    """Traiter les messages du canal de statistiques"""
    try:
        if detected_stat_channel is None or event.chat_id != detected_stat_channel:
            return
            
        message_text = event.message.message if event.message else ""
        if not message_text:
            return
            
        print(f"📨 Message reçu: {message_text[:50]}...")
        
        # Vérifier si c'est un déclencheur de prédiction
        predicted, predicted_game, suit = predictor.should_predict(message_text)
        if predicted:
            prediction_text = f"🎯Nº:{predicted_game} 🔵Dis🔵tri🚥:statut :⌛"
            await broadcast(prediction_text, predicted_game)
            print(f"✅ Prédiction générée: #{predicted_game}")
            
        # Vérifier les résultats
        verified, number = predictor.verify_prediction(message_text)
        if verified is not None and number is not None:
            statut = predictor.prediction_status.get(number, '❌')
            await edit_or_send_prediction(number, statut)
            print(f"✅ Résultat vérifié: #{number} = {statut}")
            
    except Exception as e:
        print(f"❌ Erreur handle_messages: {e}")

async def broadcast(message, game_number=None):
    """Diffuser un message"""
    if detected_display_channel:
        try:
            sent_message = await client.send_message(detected_display_channel, message)
            if game_number:
                predictor.store_prediction_message(game_number, sent_message.id, detected_display_channel)
            print(f"📤 Message diffusé: {message[:30]}...")
        except Exception as e:
            print(f"❌ Erreur broadcast: {e}")

async def edit_or_send_prediction(game_number, status):
    """Modifier ou envoyer le message de prédiction"""
    try:
        message_info = predictor.get_prediction_message(game_number)
        if message_info:
            new_text = f"🎯Nº:{game_number} 🔵Dis🔵tri🚥:statut :{status}"
            await client.edit_message(
                message_info['chat_id'], 
                message_info['message_id'], 
                new_text
            )
        else:
            status_text = f"🎯Nº:{game_number} 🔵Dis🔵tri🚥:statut :{status}"
            await broadcast(status_text)
    except Exception as e:
        print(f"❌ Erreur edit_prediction: {e}")

# --- SERVEUR WEB POUR REPLIT ---
async def health_check(request):
    """Health check endpoint"""
    return web.Response(text="🤖 Bot Telegram actif sur Replit!", status=200)

async def bot_info(request):
    """Informations du bot"""
    info = {
        "status": "online",
        "platform": "Replit",
        "stat_channel": detected_stat_channel,
        "display_channel": detected_display_channel,
        "predictions_active": len(predictor.prediction_status),
        "total_predictions": len(predictor.status_log)
    }
    return web.json_response(info)

async def create_web_server():
    """Créer le serveur web"""
    app = web.Application()
    app.router.add_get('/', health_check)
    app.router.add_get('/health', health_check)
    app.router.add_get('/info', bot_info)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f"🌐 Serveur web démarré sur 0.0.0.0:{PORT}")
    return runner

# --- FONCTION PRINCIPALE ---
async def main():
    """Fonction principale"""
    print("🚀 Démarrage du bot sur Replit...")
    
    try:
        # Démarrer le serveur web
        await create_web_server()
        print(f"✅ Serveur web actif sur port {PORT}")
        
        # Démarrer le bot
        if await start_bot():
            print("✅ Bot Telegram en ligne")
            print(f"🔗 URL publique: https://{os.getenv('REPL_SLUG', 'your-repl')}.{os.getenv('REPL_OWNER', 'username')}.repl.co")
            await client.run_until_disconnected()
        else:
            print("❌ Échec du démarrage")
            
    except Exception as e:
        print(f"❌ Erreur critique: {e}")
    finally:
        try:
            await client.disconnect()
            print("🔌 Bot déconnecté")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(main())
