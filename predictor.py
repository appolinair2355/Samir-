import re
import random
from typing import Tuple, Optional, List

class CardPredictor:
    """Card game prediction engine with pattern matching and result verification"""
    
    def __init__(self):
        self.last_predictions = []  # Liste [(numéro, combinaison)]
        self.prediction_status = {}  # Statut des prédictions par numéro
        self.processed_messages = set()  # Pour éviter les doublons
        self.status_log = []  # Historique des statuts
        self.prediction_messages = {}  # Stockage des IDs de messages de prédiction
        self.trigger_numbers = [6, 7, 8, 9]  # Numéros déclencheurs variables
        self.last_trigger_used = None  # Dernier déclencheur utilisé pour éviter répétition
        
    def reset(self):
        """Reset all prediction data"""
        self.last_predictions.clear()
        self.prediction_status.clear()
        self.processed_messages.clear()
        self.status_log.clear()
        self.prediction_messages.clear()
        self.last_trigger_used = None
        print("Données de prédiction réinitialisées")

    def extract_game_number(self, message: str) -> Optional[int]:
        """Extract game number from message using pattern #N followed by digits"""
        try:
            # Look for patterns like "#N 123", "#N123", "#N60.", etc.
            match = re.search(r"#N\s*(\d+)\.?", message, re.IGNORECASE)
            if match:
                number = int(match.group(1))
                print(f"Numéro de jeu extrait: {number}")
                return number
            
            # Alternative pattern matching
            match = re.search(r"jeu\s*#?\s*(\d+)", message, re.IGNORECASE)
            if match:
                number = int(match.group(1))
                print(f"Numéro de jeu alternatif extrait: {number}")
                return number
                
            print(f"Aucun numéro de jeu trouvé dans: {message}")
            return None
        except (ValueError, AttributeError) as e:
            print(f"Erreur extraction numéro: {e}")
            return None

    def extract_symbols_from_parentheses(self, message: str) -> List[str]:
        """Extract content from parentheses in the message"""
        try:
            return re.findall(r"\(([^)]*)\)", message)
        except Exception:
            return []

    def count_total_cards(self, symbols_str: str) -> int:
        """Count total card symbols in a string"""
        # Compter d'abord les versions emoji, puis les versions simples
        # pour éviter le double comptage
        emoji_symbols = ['♠️', '♥️', '♦️', '♣️']
        simple_symbols = ['♠', '♥', '♦', '♣']
        
        # Remplacer les emojis par des marqueurs temporaires pour éviter le double comptage
        temp_str = symbols_str
        emoji_count = 0
        
        for emoji in emoji_symbols:
            count = temp_str.count(emoji)
            emoji_count += count
            # Remplacer par des marqueurs pour éviter le recomptage
            temp_str = temp_str.replace(emoji, 'X')
        
        # Compter les symboles simples restants
        simple_count = 0
        for symbol in simple_symbols:
            simple_count += temp_str.count(symbol)
            
        total = emoji_count + simple_count
        print(f"Comptage cartes détaillé: emoji={emoji_count}, simple={simple_count}, total={total} dans '{symbols_str}'")
        return total

    def normalize_suits(self, suits_str: str) -> str:
        """Normalize and sort card suits"""
        # Map emoji versions to simple versions
        suit_map = {
            '♠️': '♠', '♥️': '♥', '♦️': '♦', '♣️': '♣'
        }
        
        normalized = suits_str
        for emoji, simple in suit_map.items():
            normalized = normalized.replace(emoji, simple)
        
        # Extract only card symbols and sort them
        suits = [c for c in normalized if c in '♠♥♦♣']
        return ''.join(sorted(set(suits)))

    def should_predict(self, message: str) -> Tuple[bool, Optional[int], Optional[str]]:
        """Determine if a prediction should be made based on the message"""
        try:
            # Extract game number
            game_number = self.extract_game_number(message)
            if game_number is None:
                return False, None, None

            # Variable trigger system - avoid using the same trigger consecutively
            last_digit = game_number % 10
            if last_digit not in self.trigger_numbers:
                return False, None, None
            
            # Si c'est le même déclencheur que la dernière fois, parfois ignorer pour variabilité
            if (self.last_trigger_used == last_digit and 
                len(self.last_predictions) > 0 and 
                random.random() < 0.3):  # 30% chance d'ignorer pour forcer variabilité
                print(f"🔄 Déclencheur {last_digit} ignoré pour variabilité (dernier: {self.last_trigger_used})")
                return False, None, None

            # Calculate predicted game number
            predicted_game = ((game_number // 10) + 1) * 10
            
            # ANTI-DOUBLON: Check if predicted game already has a prediction (any status)
            if predicted_game in self.prediction_status:
                print(f"❌ Prédiction déjà existante pour le jeu #{predicted_game} (statut: {self.prediction_status[predicted_game]}), ignoré")
                return False, None, None
            
            # ANTI-DOUBLON: Double check from processed messages to avoid scheduler conflicts
            if f"auto_prediction_{predicted_game}" in self.processed_messages:
                print(f"❌ Prédiction automatique déjà planifiée pour #{predicted_game}, ignoré")
                return False, None, None
            
            # Check if current game already processed
            if game_number in self.processed_messages:
                print(f"Jeu #{game_number} déjà traité, ignoré")
                return False, None, None

            # Extract symbols from parentheses
            matches = self.extract_symbols_from_parentheses(message)
            if not matches:
                return False, None, None

            # Get first group of symbols
            first_group = matches[0]
            suits = self.normalize_suits(first_group)
            
            if not suits:
                return False, None, None

            # Mark current game as processed and update last trigger used
            self.processed_messages.add(game_number)
            self.last_trigger_used = last_digit
            
            # Create prediction for target game
            self.prediction_status[predicted_game] = '⌛'
            self.last_predictions.append((predicted_game, suits))
            
            print(f"✅ Prédiction manuelle créée: Jeu #{predicted_game} -> {suits} (déclenchée par #{game_number}, trigger={last_digit})")
            print(f"📊 Prédictions actives: {[k for k, v in self.prediction_status.items() if v == '⌛']}")
            return True, predicted_game, suits

        except Exception as e:
            print(f"Erreur dans should_predict: {e}")
            return False, None, None
    
    def store_prediction_message(self, game_number: int, message_id: int, chat_id: int):
        """Store prediction message ID for later editing"""
        self.prediction_messages[game_number] = {'message_id': message_id, 'chat_id': chat_id}
        
    def get_prediction_message(self, game_number: int):
        """Get stored prediction message details"""
        return self.prediction_messages.get(game_number)

    def verify_prediction(self, message: str) -> Tuple[Optional[bool], Optional[int]]:
        """Verify prediction results based on verification message"""
        try:
            # Check for verification tags
            if not any(tag in message for tag in ["✅", "🔰", "❌", "⭕", "⏰"]):
                return None, None

            # Extract game number
            game_number = self.extract_game_number(message)
            if game_number is None:
                print(f"Aucun numéro de jeu trouvé dans: {message}")
                return None, None

            print(f"Numéro de jeu du résultat: {game_number}")

            # Si le message contient ⏰, considérer comme plus de 2 cartes et continuer la vérification
            if "⏰" in message:
                print(f"⏰ détecté dans le message - considéré comme plus de 2 cartes")
                
                # Vérifier s'il y a des prédictions expirées (jeu > prédiction+2)
                expired_predictions = []
                for pred_num, status in self.prediction_status.items():
                    if status == '⌛' and game_number > pred_num + 2:
                        expired_predictions.append(pred_num)
                
                # Marquer les prédictions expirées comme échouées
                for pred_num in expired_predictions:
                    statut = '❌❌'
                    self.prediction_status[pred_num] = statut
                    self.status_log.append((pred_num, statut))
                    print(f"Prédiction expirée: #{pred_num} marquée comme échouée (jeu {game_number} > {pred_num}+2)")
                    return False, pred_num
                
                # Si aucune prédiction expirée, continuer l'attente
                print(f"Jeu #{game_number} avec ⏰ - aucune prédiction expirée, continuer l'attente")
                return None, None

            # Extract symbol groups
            groups = self.extract_symbols_from_parentheses(message)
            if len(groups) < 2:
                print(f"Groupes de symboles insuffisants: {groups}")
                return None, None

            first_group = groups[0]
            second_group = groups[1]
            print(f"Groupes extraits: '{first_group}' et '{second_group}'")

            def is_valid_result():
                """Check if the result has valid card distribution (2+2)"""
                count1 = self.count_total_cards(first_group)
                count2 = self.count_total_cards(second_group)
                print(f"Comptage cartes: groupe1={count1}, groupe2={count2}")
                return count1 == 2 and count2 == 2

            # Vérifier les prédictions en attente dans le bon ordre
            # 1. Chercher d'abord si ce jeu correspond exactement à une prédiction (offset 0)
            # 2. Puis vérifier si c'est le jeu suivant d'une prédiction (offset +1)
            # 3. Puis vérifier si c'est 2 jeux après une prédiction (offset +2)
            
            for offset in range(3):  # Check 0, 1, 2 offsets
                predicted_number = game_number - offset
                print(f"Vérification si le jeu #{game_number} correspond à la prédiction #{predicted_number} (offset {offset})")
                
                if (predicted_number in self.prediction_status and 
                    self.prediction_status[predicted_number] == '⌛'):
                    print(f"Prédiction en attente trouvée: #{predicted_number}")
                    
                    if is_valid_result():
                        # Success with offset indicator
                        if offset == 0:
                            statut = '✅0️⃣'  # Perfect timing
                        elif offset == 1:
                            statut = '✅1️⃣'  # 1 game late
                        else:
                            statut = '✅2️⃣'  # 2 games late
                            
                        self.prediction_status[predicted_number] = statut
                        self.status_log.append((predicted_number, statut))
                        print(f"Prédiction réussie: #{predicted_number} validée par le jeu #{game_number} (offset {offset})")
                        return True, predicted_number
                    else:
                        # Failed prediction - invalid card count
                        statut = '❌❌'
                        self.prediction_status[predicted_number] = statut
                        self.status_log.append((predicted_number, statut))
                        print(f"Prédiction échouée: #{predicted_number} - résultat invalide (cartes incorrectes)")
                        return False, predicted_number

            # Si aucune prédiction trouvée dans les 3 offsets, chercher les prédictions expirées
            expired_predictions = []
            for pred_num, status in self.prediction_status.items():
                if status == '⌛' and game_number > pred_num + 2:
                    expired_predictions.append(pred_num)
            
            # Marquer les prédictions expirées comme échouées
            for pred_num in expired_predictions:
                statut = '❌❌'
                self.prediction_status[pred_num] = statut
                self.status_log.append((pred_num, statut))
                print(f"Prédiction expirée: #{pred_num} marquée comme échouée")
                return False, pred_num

            print(f"Aucune prédiction correspondante trouvée pour le jeu #{game_number}")
            print(f"Prédictions actuelles en attente: {[k for k, v in self.prediction_status.items() if v == '⌛']}")
            return None, None

        except Exception as e:
            print(f"Erreur dans verify_prediction: {e}")
            return None, None

    def get_statistics(self) -> dict:
        """Get prediction statistics"""
        try:
            total_predictions = len(self.status_log)
            if total_predictions == 0:
                return {
                    'total': 0,
                    'wins': 0,
                    'losses': 0,
                    'pending': len([s for s in self.prediction_status.values() if s == '⌛']),
                    'win_rate': 0.0
                }

            wins = sum(1 for _, status in self.status_log if '✅' in status)
            losses = sum(1 for _, status in self.status_log if '❌' in status or '⭕' in status)
            pending = len([s for s in self.prediction_status.values() if s == '⌛'])
            win_rate = (wins / total_predictions * 100) if total_predictions > 0 else 0.0

            return {
                'total': total_predictions,
                'wins': wins,
                'losses': losses,
                'pending': pending,
                'win_rate': win_rate
            }
        except Exception as e:
            print(f"Erreur dans get_statistics: {e}")
            return {'total': 0, 'wins': 0, 'losses': 0, 'pending': 0, 'win_rate': 0.0}

    def get_recent_predictions(self, count: int = 10) -> List[Tuple[int, str]]:
        """Get recent predictions with their status"""
        try:
            recent = []
            for game_num, suits in self.last_predictions[-count:]:
                status = self.prediction_status.get(game_num, '⌛')
                recent.append((game_num, suits, status))
            return recent
        except Exception as e:
            print(f"Erreur dans get_recent_predictions: {e}")
            return []
