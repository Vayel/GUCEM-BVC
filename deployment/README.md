# Déploiement

## Installer l'application

```bash
make build
make create
```

Dans le conteneur :

* Initialiser gdrive : `gdrive about`
* Personnaliser le fichier `tools/vars.sh`
* S'assurer que Django est configuré pour la [production](https://docs.djangoproject.com/fr/1.10/howto/deployment/checklist/)
* Personnaliser le script de sauvegarde de la base (`tools/backup_db.sh`) en spécifiant l'identifiant du fichier de sauvegarde sur GDrive (s'il n'existe pas, le créer en important à la main un fichier .sql et récupérer son id avec `gdrive list`)
* Lancer le script d'installation : `cd tools; ./install.sh`
* [Configurer mod_wsgi pour Django](https://github.com/GrahamDumpleton/mod_wsgi#using-mod_wsgi-express-with-django)

## Configurer l'application

```bash
make run
# La page `/` renverra une erreur tant que le point ci-dessous n'aura pas été fait
```

* Sur le site, dans la partie d'administration (`/admin`), créer une configuration
* Créer également les commissions
    * Le mot de passe n'a pas d'importance
    * L'adresse mail est obligatoire
    * Le nom d'utilisateur est le nom de la commission, de préférence avec une majuscule au début
    * Le prénom et le nom de famille n'ont pas d'importance
