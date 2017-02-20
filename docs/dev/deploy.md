# Déploiement

## Installer l'application

Commençons par préparer le système :

* Installer [`virtualenv`](http://docs.python-guide.org/en/latest/dev/virtualenvs/)
* Installer [`Apache`](https://github.com/GrahamDumpleton/mod_wsgi#system-requirements)

Puis installons l'application :

* Cloner ce dépôt
* Se rendre dans le dossier `tools` et créer un environnement virtuel `bvc` en Python 3 : `virtualenv bvc -p python3`
* Se replacer à la racine du projet : `cd ..`
* Personnaliser les variables d'environnement contenues dans le fichier `env_vars.sh`. Il est possible de placer ce fichier dans un autre répertoire.
* Travailler dans l'environnement virtuel : `source ./work_in_env.sh <chemin-fichier-variables-env>`
* Installer les dépendances : `pip install -r requirements.txt`
* S'assurer que Django est configuré pour la [production](https://docs.djangoproject.com/fr/1.10/howto/deployment/checklist/)
* Créer la base de données : `./manage.py makemigrations ; ./manage.py migrate`
* Créer le compte admin : `./manage.py createsuperuser`
* Installer `mod_wsgi` : `pip install mod_wsgi`
* [Configurer mod_wsgi pour Django](https://github.com/GrahamDumpleton/mod_wsgi#using-mod_wsgi-express-with-django)
* Créer la tâche plannifiée des rappels : `python tools/create_reminders_cron.py`

## Configurer l'application

* Lancer l'application comme expliqué [ici](https://github.com/GrahamDumpleton/mod_wsgi#using-mod_wsgi-express-with-django)
* Sur le site, dans la partie d'administration (`/admin`), créer une configuration
