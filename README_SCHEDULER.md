# 🚀 Système de Planification Automatique des Prédictions

## 📋 Vue d'ensemble

Le système de planification automatique permet au bot de générer et gérer des prédictions automatiques selon un planning quotidien prédéfini. Ce système inclut :

- **Planification automatique** : 144 créneaux quotidiens (toutes les 10 minutes)
- **Lancement automatique** : Envoi des prédictions aux heures programmées
- **Vérification automatique** : Surveillance des résultats dans le canal source
- **Mise à jour en temps réel** : Édition des messages avec les statuts finaux

## 🏗️ Architecture

### Fichiers principaux

- `scheduler.py` - Classe PredictionScheduler principale
- `prediction.yaml` - Fichier de planification quotidienne
- `main.py` - Intégration avec les commandes `/scheduler` et `/schedule_info`

### Composants clés

1. **PredictionScheduler** : Classe principale de gestion
2. **Planification YAML** : Stockage persistant des données
3. **Boucle de surveillance** : Traitement en arrière-plan
4. **Système de vérification** : Contrôle automatique des résultats

## 📊 Structure de données

### Format YAML de planification

```yaml
N010:
  lanceur: N007
  heure_lancement: "00:06"
  heure_prediction: "00:09"
  statut: "⌛"
  message_id: null
  chat_id: null
  launched: false
  verified: false
```

### Champs expliqués

- **lanceur** : Numéro de jeu déclencheur (avec décalage 1-4 min)
- **heure_lancement** : Moment d'envoi de la prédiction
- **heure_prediction** : Heure cible de la prédiction
- **statut** : État actuel (⌛, ✅, ❌)
- **message_id** : ID du message envoyé (pour édition)
- **chat_id** : ID du canal de destination
- **launched** : Prédiction envoyée (true/false)
- **verified** : Résultat vérifié (true/false)

## 🤖 Commandes disponibles

### `/scheduler [commande]`

Gestion principale du planificateur :

- `start` - Démarre le planificateur automatique
- `stop` - Arrête le planificateur
- `status` - Affiche le statut actuel
- `generate` - Génère une nouvelle planification
- `config [source_id] [target_id]` - Configure les canaux

### `/schedule_info`

Affiche les informations détaillées :
- Prochaines prédictions en attente
- État de la planification actuelle
- Statistiques de lancement

## 🔧 Configuration

### Prérequis

1. **Canal source** : Surveillance des résultats
2. **Canal cible** : Diffusion des prédictions
3. **Configuration des canaux** via `/set_stat` et `/set_display`

### Démarrage rapide

```bash
# 1. Générer une planification
/scheduler generate

# 2. Configurer les canaux (optionnel)
/scheduler config -1001234567890 -1001987654321

# 3. Démarrer le planificateur
/scheduler start
```

## ⚡ Fonctionnement automatique

### Cycle de traitement

1. **Surveillance** : Vérification toutes les 30 secondes
2. **Lancement** : Envoi des prédictions à l'heure programmée
3. **Vérification** : Contrôle des résultats dans le canal source
4. **Mise à jour** : Édition des messages avec statuts finaux

### Algorithme de décalage

- **Décalages possibles** : 1-4 minutes avant l'heure cible
- **Limite décalage -1** : Maximum 3 occurrences par jour
- **Distribution aléatoire** : Répartition équilibrée des créneaux

## 📈 Statistiques et suivi

### Indicateurs disponibles

- **Total de prédictions** : 144 par jour
- **Prédictions lancées** : Nombre envoyé
- **Prédictions vérifiées** : Nombre avec résultat final
- **En attente** : Prédictions non encore envoyées
- **Prochaine prédiction** : Prochaine heure de lancement

### Format des prédictions

```
🔵 N010 📌 D🔵 statut :'⌛'  # Initial
🔵 N010 📌 D🔵 statut :✅   # Réussite
🔵 N010 📌 D🔵 statut :❌   # Échec
```

## 🔄 Gestion des erreurs

### Mécanismes de sécurité

- **Persistance YAML** : Sauvegarde automatique
- **Gestion d'exceptions** : Traitement des erreurs réseau
- **Reconnexion automatique** : Reprise après panne
- **Vérification d'intégrité** : Contrôle des données

### Résolution de problèmes

1. **Erreur de lancement** : Vérifier la configuration des canaux
2. **Pas de vérification** : Contrôler le canal source
3. **Planification corrompue** : Régénérer avec `/scheduler generate`

## 🎯 Avantages

### Automatisation complète

- **Prédictions 24h/24** : Fonctionnement continu
- **Zéro intervention** : Gestion autonome
- **Mise à jour temps réel** : Statuts instantanés

### Flexibilité

- **Configuration dynamique** : Changement de canaux en direct
- **Planification régénérable** : Nouveaux horaires quotidiens
- **Contrôle administrateur** : Commandes de gestion complètes

## 📝 Journal des modifications

### Version actuelle (Janvier 2025)

✅ **Implémenté**
- Système de planification quotidienne automatique
- 144 créneaux de prédiction (toutes les 10 minutes)
- Commandes de gestion `/scheduler` et `/schedule_info`
- Vérification automatique des résultats
- Persistance YAML des données
- Intégration complète avec le bot principal

### Fonctionnalités futures

🔄 **En développement**
- Statistiques avancées de performance
- Planification personnalisée par utilisateur
- Intégration avec système de notifications

---

**Développé par Sossou Kouamé Appolinaire**  
*Système de prédictions automatiques pour bot Telegram*