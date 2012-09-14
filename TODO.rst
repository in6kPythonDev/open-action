
Matteo
------

DONE
^^^^

* ActionCreateView: creazione politician_set e media_set da fare come category_set e geoname_set
* test per ActionCreateView 
* ActionUpdateView: aggiornamento del post e dei campi ManyToManyField. Verificare che non è posibile aggiornarlo in un certo stato.
* test per ActionUpdateView
* refactoring: Rinomina app askbot_model_extension in askbot_extension --> modificare anche la guida di installazione
* doc: Verifica come fa askbot metodi "assert" e revisione check permessi modifica azione
* nei test: Verifica possibità richiesta ajax dal test-client 
* nei test: sostituire add_for con add_to nei nomi dei metodi di test 
* nei test: nei motodi che testano l'aggiunta di un voto, controllare anche che il conto dei voti nella Action/commento sia davvero aumentato di uno
* nelle eccezioni: aggiungere eccezioni 'VoteUnauthorizedOnComment'e 'InvalidReferralError' 

TODO
^^^^

* aggiungere campo created_by nella Action e settarlo nella creazione (nella Action.save())                     | OK testato
* nei test, scrivere una funzione per la gestione di richieste ajax (migliorare la gestione già implementata)   | OK testato
* nelle views: reimplementare l'update dei campi xxxx_set nella view di update della Action                     | OK testato 
* NEW: FOLLOW an Action: vedere askbot come fa --> implementare test/vista/finta notifica                       | OK testato
* nelle view e nei test: solo l'owner della Action la puo modificare (text)                                     | OK testato

* [in sospeso] NEW: Moderatori: leggere specifiche - a cosa servono i moderatori?:
    viste:
        * ActionModeratorsAdd, 
        * ActionModeratorsManage

* Documentazione viste e modello https://github.com/openpolis/open-action/wiki/
* Commenti nelle viste

* nel modello della Action property -- referrers -- restituisce un QS di utenti che sono l'owner e i moderators per l'azione. v
* nel modello Action aggiungere campo -- moderator_set -- v
* solo owner e moderatori (che insieme compongono i -- referrers --) possono scrivere blogpost per una action. Implementare il controllo nelle assert nel modello User. v
* tutti i referrers possono settare lo stato victory che però dovà essere verificato ed eventualmente accettato dallo staff:
    fare un modello "ActionRequest" con campi: v
        * Action, 
        * il tipo di richiesta, 
        * le note,
        * 'requested_at' datetime,
        * un campo 'is_processed' per considerare la richiesta processata e non visualizzarla piu nell'admin
* controllare campi da nascondere nelle form v
* TESTARE l'aggiunta del voto tramite token v
* inserire un controllo che logghi il caso in cui un utente voti con se stesso come referente v
* inserire campo 'is_deleted' nel modello ActionCategory v
* nessuna operazione è eseguibile sulla Action se questa è in stato 'canceled' --> implementare controlli nelle estensioni di askbot (asserts e pre_save) v

* creare una vista, relativa al modello NoticeSetting, che aggiunga nuovi tipi di notifiche relative ad un particolare utente e collegate ad uno o piu backends
* [non prioritario] modifica dei tag di una azione: i referrers (e di conseguenza i moderatori) possono modificare i tag di una Action.
* I tag sono inseriti nella form di update di una Action alla stregua dei campi xxx_set (inserimento di una lista di tags che vanno a sovrascrivere la vecchia lista). Per questo sarebbe meglio creare un metodo generico che presi in input due set di oggetti (relativi nel nostro caso rispettivamente agli oggetti da collegare all'istanza della form e a quelli da scollegare) ritorni come output due set di oggetti tali che il primo set indica gli oggetti da rimuovere e il secondo quelli da aggiungere (nel nostro caso rispettivamente quelli da scollegare dall'istanza e quelli da collegarvi). 


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

Setter
------

Problema dei setter. Essendoci oggetti innestati ho un problema nel settare 
temporaneamente gli attributi. Ad esempio v. property "score".

Posso definire il setter di score, ma lo devo salvare subito in "question"
altrimenti se da fuori faccio action.save(), non salvo lo score dato che è in "question"

Settare un attributo dizionario che mappa gli attributi modificati e riutilizzarlo nella save()

Mini_views
----------

* Modulo action.mini_views per isolare le parti ajax singole
* Edit della action alla jeditable

User
----

* Global impact factor generale del sistema <--- lo studiano loro e mi danno le specifiche
* Local impact factor <-- quanto ho influenzato in una action
* Login --> connect user to social network e notifiche

note...
--------

* Tell Django BTS to s/user/obj parameter in TokenGenerator and add get_timeout_days method to PasswordResetTokenGenerator

DONE
-----
* Action: Creazione --> aggiungere la scelta delle categorie
* Action: Calcolo del threshold 
* Action: token
* Viste: se la vista è ajax wrappa le eccezioni in response_error, e i successi in response_success

