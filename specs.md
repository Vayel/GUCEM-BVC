Specs gestion BVC GUCEM
=======================

Données
-------

* Commandes passées au vieux camp par le respo BVC (en vrai passées au trésorier du club qui les commande par la suite)
    * A la commande : date commande / montant bons
    * A la reception : data reception / montant bons

* Commandes passées par les adhérents
    * Formulaire web
        * Nom / prénom / email / numéro licence / ESMUG ou GUCEM / montant en BVC avant réduction / remarques 
    * Etats
        1. Commande effectués (formulaire web)
        2. Commande préparée (BVC reservés dans le stock pour la commande)
        3. Commande vendue (BVC échangés contre espèces ou chèque)
        4. Commande encaissée (espèces ou chèques déposés en banque)
    
* Stock de BVC
    * Etats
        1. BVCs disponibles (arrivés par une commande au vieux camp, ajoutés au stock)
            * Peut être négatif si demande > stock
        2. BVCs commandés
        3. BVCs préparés
        4. BVCs vendus (supprimés du stock)

* Stock d'argent
    * Trésorerie : stock espèces pour rendre monnaie + équilibrage des remises en banque
    * Espèces : stock espèces des commandes vendues pas encore encaissées
    * Chèques : stock chèques des commandes vendues pas encore encaissées

* Liste adhérents
    * Liste adhérents "VIP" à -20 %
    * Liste adhérents GUCEM à -18 % pour vérif (opt.)
    * Liste adhérents ESMUG à -15 % pour vérif (opt.)

* Remises en banque
    * Historique remise en banque chèque et espèces
        * Date / numéro remise / montant total / montant detaillé avec noms + n° licenses + réductions

* Commandes Commissions
    * Formulaire web différent
        * Commission / email / montant en BVC avant réduction / descriptif achat envisagé pour trésorier
    * Etats
        1. Commande effectués (formulaire web)
        2. Commande préparée (BVC reservés dans le stock pour la commande)
        3. Commande distribuée


