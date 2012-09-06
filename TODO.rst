
Matteo
------

DONE
^^^^

* ActionCreateView: creazione politician_set e media_set da fare come category_set e geoname_set
* test per ActionCreateView 
* ActionUpdateView: aggiornamento del post e dei campi ManyToManyField. Verificare che non è posibile aggiornarlo in un certo stato.
* test per ActionUpdateView

TODO
^^^^

* refactoring: Rinomina app askbot_model_extension in askbot_extension --> modificare anche la guida di installazione                                10 min 5 min
* doc: Verifica come fa askbot metodi "assert" e revisione check permessi modifica azione                                                            25 min 10 min
* nei test: Verifica possibità richiesta ajax dal test-client                                                                                        20 min 
* nelle views: reimplementare l'update dei campi xxxx_set nella view di update della Action                                                          30 min 
* nei test: sostituire add_for con add_to nei nomi dei metodi di test                                                                                 5 min 
* nei test: nei motodi che testano l'aggiunta di un voto, controllare anche che il conto dei voti nella Action/commento sia davvero aumentato di uno 20 min 
* nelle view e nei test: solo l'owner della Action la puo modificare (text)                                                                          25 min
* nelle eccezioni: aggiungere eccezioni 'VoteUnauthorizedOnComment'e 'InvalidReferralError'                                                           5 min 

NOTE
^^^^

* get_latest_by nella classe Meta di Action prende il thread come primo - e unico - parametro 

Antonio
-------

* Completare stati e documentazione action/const.py
* Verificare __unicode__ su tutte le classi
* Verificare Meta verbose_name e verbose_name_plural su tutte le classi
* Verificare verbose_name e help_text su tutti i campi del modello


Io - progetto
=============

CHIEDERE
--------

* Territori --> autocompletamento con django-ajax-autocomplete?
* Categorie --> Condivisione modello e fixtures di default
* In generale tutto quello che non deve essere tradotto all'utente ok in inglese, ma per il resto risparmio della traduzione ok? 
* Definire protocollo per gestire risposte di errore, redirect, eccezioni, ...
* Decoratore: se la vista è ajax wrappa le eccezioni in response_error, e i successi in response_success

Setter
------

Problema dei setter. Essendoci oggetti innestati ho un problema nel settare 
temporaneamente gli attributi. Ad esempio v. property "score".

Posso definire il setter di score, ma lo devo salvare subito in "question"
altrimenti se da fuori faccio action.save(), non salvo lo score dato che è in "question"

Mini_views
----------

* Modulo action.mini_views per isolare le parti ajax singole

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

note...
--------

* Tell Django BTS to s/user/obj parameter in TokenGenerator and add get_timeout_days method to PasswordResetTokenGenerator

