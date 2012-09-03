
Matteo
------


Antonio
-------

* Completare stati e documentazione action/const.py
* Verificare __unicode__ su tutte le classi
* Verificare Meta verbose_name e verbose_name_plural su tutte le classi
* Verificare verbose_name e help_text su tutti i campi del modello


Io - progetto
=============

* Definire protocollo per gestire risposte di errore, redirect, eccezioni, ...
* Decoratore: se la vista è ajax wrappa le eccezioni in response_error, e i successi in response_success

Setter
------

Problema dei setter. Essendoci oggetti innestati ho un problema nel settare 
temporaneamente gli attributi. Ad esempio v. property "score".

Posso definire il setter di score, ma lo devo salvare subito in "question"
altrimenti se da fuori faccio action.save(), non salvo lo score dato che è in "question"

Action
------

* Creazione --> aggiungere la scelta delle categorie
* Edit della action alla jeditable
* Calcolo del threshold 


User
----

* Global impact factor generale del sistema <--- lo studiano loro e mi danno le specifiche
* Local impact factor <-- quanto ho influenzato in una action

* Login --> connect user to social network e notifiche


