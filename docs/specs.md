Specs gestion BVC GUCEM
=======================

Données
-------

* Commandes "grosses" passées au vieux camp par le respo BVC (en vrai passées au trésorier du club qui les commande par la suite)
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
        5. Commande annulée (après X temps préparée)
    
* Stock de BVC
    * Etats
        1. BVCs disponibles (arrivés par une commande au vieux camp, ajoutés au stock)
            * Peut être négatif si demande > stock
        2. BVCs commandés
        3. BVCs préparés
        4. BVCs vendus (supprimés du stock)
    * Différencier bons 50/20/10€ (opt.)

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

Actions possibles
-----------------

* En tant qu'adhérent du club ou responsable de commission 
    * Effectuer une commande de BVC via un formulaire web du site
        * in : nom / prénom / date / num lic / type adhérent / montant / remarques 
    * Recevoir un mail de confirmation que ma commande a été prise en compte (avec rappel montant)
    * Recevoir un mail de confirmation lorsque ma commande est préparée (avec rappel montant)
    * Recevoir un mail de relance après X temps
    * Recevoir un mail indiquant que la commande est annulée
    * Pouvoir provoquer l'envoi d'un mail récapitulatif à partir de son numéro de licence. Concrètement, on le spécifie dans un formulaire puis on reçoit un mail avec ses commandes en cours et leur état.

* En tant que responsable BVC
    * Indiquer qu'une "grosse" commande a été effectuée auprès du vieux campeur
        * in : date / montant
    * Indiquer qu'une "grosse" commande a été reçue
        * in : date / montant
    * Consulter les valeurs des données en cours (décrites ci dessus)
        * Affichage stocks BVC suivant états 
            * En particulier si stock "disponible" négatif ou proche de l'être   
        * Affichage argent non remis en banque suivant états
        * Affichage commandes en cours suivant états
        * Affichages liste adhérents
    * Consulter les commandes effectuées
        * Indiquer lesquelles ont été préparées
            * in : commande / date préparation 
    * Etre notifié des commandes effectuées
        * si besoin est
    * Consulter les commandes préparées
        * Indiquer lesquelles ont été vendues / distribuées
            * in : commande / date vente / especes ou chq / montant
    * Préparer remise chèque
        * Selectionner commandes concernées parmi les commandes vendues (automatisable)
        * in : date / numéro bon de remise 
    * Préparer remise espèce
        * Séléctionner commandes concernées parmi les commandes vendues (automatisable)
        * Indiquer nombre billets 500/100/50/20/10/5€ pour vérif
        * Mouvements de trésorerie +/- possibles
        * in : date / numéro bon de remise / mouvement trésorerie / données billets
    * Indiquer perte de bons
        * in : date / pertes (+ / -) / remarques 
    
* En tant que trésorier
    * Etre notifié lorsqu'une "grosse" commande est nécéssaire
        * out : date / montant
    * Etre notifié lorsqu'une remise chèque / espèce est effectuée
        * out : date / montant total / detail commandes avec noms + numéros licence / éventuels mouvements trésorerie
    * Etre notifié lorsque une commande est distribuée à une commission
        * out : data / montant / commission / descriptif achat