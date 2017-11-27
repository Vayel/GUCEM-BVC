# Déploiement

## Installer l'application

Commençons par préparer le système :

* Installer un gestionnaire de tâches plannifiées (par exemple, `cronie`)
* Installer [`virtualenv`](http://docs.python-guide.org/en/latest/dev/virtualenvs/)
* Installer [`Apache`](https://github.com/GrahamDumpleton/mod_wsgi#system-requirements)
* Installer [`wkhtmltopdf`](https://github.com/JazzCore/python-pdfkit)
* Installer [`gdrive`](https://github.com/prasmussen/gdrive)
    * Faire en sorte qu'on puisse l'appeler via la commande `gdrive` (le placer dans `/usr/bin` avec les bons droits)
    * L'initialiser : `gdrive about`

Puis installons l'application :

* Cloner ce dépôt
* Se rendre dans le dossier `tools` et créer un environnement virtuel `bvc` en Python 3 : `virtualenv bvc -p python3`
* Personnaliser les variables d'environnement contenues dans le fichier `vars.sh`.
* Travailler dans l'environnement virtuel : `. ./work_in_env.sh`
* S'assurer que Django est configuré pour la [production](https://docs.djangoproject.com/fr/1.10/howto/deployment/checklist/)
* Personnaliser le script de sauvegarde de la base (`tools/backup_db.sh`) en spécifiant l'identifiant du fichier de sauvegarde sur GDrive (s'il n'existe pas, le créer en important à la main un fichier .sql et récupérer son id avec `gdrive list`)
* Lancer le script d'installation : `./install.sh`
* [Configurer mod_wsgi pour Django](https://github.com/GrahamDumpleton/mod_wsgi#using-mod_wsgi-express-with-django)

## Configurer l'application

* Démarrer le serveur : à la racine du projet, `./runserver.sh` (la page `/` renverra une erreur tant que le point ci-dessous n'aura pas été fait)
* Sur le site, dans la partie d'administration (`/admin`), créer une configuration
* Créer également les commissions
    * Le mot de passe n'a pas d'importance
    * L'adresse mail est obligatoire
    * Le nom d'utilisateur est le nom de la commission, de préférence avec une majuscule au début
    * Le prénom et le nom de famille n'ont pas d'importance
