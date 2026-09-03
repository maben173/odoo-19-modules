# Odoo 19 GitHub Authentication Module

## Guide d'Installation et Lancement

### 🚀 Démarrage Rapide

#### 1. **Cloner les dépôts**

```bash
# Dépôt principal Odoo
git clone https://github.com/maben173/odoo-19.git
cd odoo-19

# Dépôt des modules
git clone https://github.com/maben173/odoo-19-modules.git addons/custom
```

#### 2. **Configuration Docker**

```bash
# Démarrer les conteneurs
docker-compose up -d

# Vérifier le statut
docker-compose ps
```

#### 3. **Accéder à Odoo**

```
URL: http://localhost:8069
Email: admin@example.com
Mot de passe: admin
```

---

## 📋 Configuration GitHub OAuth

### Étape 1: Créer une Application GitHub

1. Allez sur https://github.com/settings/apps/new
2. Remplissez les champs:
   - **Application name**: `Odoo 19 Auth`
   - **Homepage URL**: `http://localhost:8069`
   - **Authorization callback URL**: `http://localhost:8069/auth/github/callback`
   - **Webhook URL**: `http://localhost:8069/webhook/github`

3. Cliquez "Create GitHub App"

4. Générez un Client Secret
5. Copiez:
   - Client ID
   - Client Secret

### Étape 2: Configurer dans Odoo

1. Accédez à Odoo: http://localhost:8069
2. Menu: **Paramètres > Administration > GitHub Auth > GitHub OAuth Providers**
3. Créez un nouveau fournisseur:
   - **Name**: GitHub
   - **Client ID**: [Votre Client ID]
   - **Client Secret**: [Votre Client Secret]
   - **Active**: ✓ Coché

4. Sauvegardez

---

## 🔐 Authentification GitHub dans Odoo

### Se connecter via GitHub

1. Allez sur http://localhost:8069/auth/github/login
2. Cliquez "Autoriser"
3. Vous serez automatiquement loggé dans Odoo
4. Votre profil GitHub sera synchronisé

### Informations Synchronisées

- Login GitHub
- Email GitHub
- Avatar
- Profil public
- Entreprise
- Localisation
- Bio

---

## 🔗 Webhooks GitHub

### Configuration des Webhooks

1. Allez sur votre GitHub App
2. Menu: **Webhooks**
3. Événements à activer:
   - Push events
   - Pull request events
   - Issues
   - Releases

### Événements Supportés

- **push**: Commits poussés
- **pull_request**: PR créées/mises à jour
- **issues**: Issues créées/mises à jour
- **release**: Versions publiées

### Consulter les Webhooks

Odoo > Menu: **GitHub Auth > GitHub Webhooks**

---

## 🐳 Docker Compose Complet

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: odoo
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: odoo
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  odoo:
    image: odoo:19
    depends_on:
      - postgres
    ports:
      - "8069:8069"
    environment:
      HOST: postgres
      USER: odoo
      PASSWORD: odoo
      DB_FILTER: odoo
    volumes:
      - ./addons:/mnt/extra-addons
      - ./config:/etc/odoo
      - odoo_data:/var/lib/odoo
    command: odoo -c /etc/odoo/odoo.conf

volumes:
  postgres_data:
  odoo_data:
```

---

## 📦 Installation du Module GitHub Auth

### Via Docker

```bash
# Entrer dans le conteneur
docker-compose exec odoo bash

# Installer le module
odoo-bin -c /etc/odoo/odoo.conf -d odoo --addons-path=/mnt/extra-addons -i odoo_github_auth

# Redémarrer
exit
docker-compose restart odoo
```

### Via Terminal

```bash
# Installer les dépendances
pip install requests PyJWT

# Lancer Odoo avec le module
odoo-bin --addons-path=./addons -d odoo -i odoo_github_auth
```

---

## 🔧 Commandes Utiles

```bash
# Démarrer Odoo
docker-compose up -d

# Arrêter Odoo
docker-compose down

# Voir les logs
docker-compose logs -f odoo

# Redémarrer
docker-compose restart odoo

# Accéder au shell PostgreSQL
docker-compose exec postgres psql -U odoo -d odoo

# Réinstaller le module
docker-compose exec odoo odoo-bin -c /etc/odoo/odoo.conf -d odoo -u odoo_github_auth
```

---

## 🌐 URLs Importantes

| URL | Description |
|-----|-------------|
| http://localhost:8069 | Interface Odoo |
| http://localhost:8069/web/login | Page de connexion |
| http://localhost:8069/auth/github/login | Login GitHub |
| http://localhost:8069/web/settings | Paramètres |
| http://localhost:5432 | Base de données PostgreSQL |

---

## 🆘 Dépannage

### Erreur: "GitHub authentication is not configured"
- Vérifiez que le provider GitHub est créé et actif
- Vérifiez les identifiants Client ID/Secret

### Erreur: "Failed to authenticate with GitHub"
- Vérifiez la redirect URI dans GitHub App
- Vérifiez la connexion Internet

### Webhooks ne fonctionnent pas
- Vérifiez l'URL webhook dans GitHub App
- Vérifiez les logs Odoo: `docker-compose logs -f odoo`

---

## 📚 Documentation Additionnelle

- Odoo 19 Docs: https://www.odoo.com/documentation/19.0/
- GitHub API: https://docs.github.com/en/rest
- Module Développement: Voir le dossier `odoo_github_auth/`

---

## 🎯 Prochaines Étapes

1. ✅ Installer et démarrer Odoo
2. ✅ Configurer GitHub OAuth
3. ✅ Tester la connexion GitHub
4. ✅ Explorer les webhooks
5. 🚀 Déployer en production

---

## Support

Pour toute question, veuillez consulter:
- Repository: https://github.com/maben173/odoo-19-modules
- GitHub Issues: https://github.com/maben173/odoo-19-modules/issues
