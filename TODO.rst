
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
* I tag sono inseriti nella form di update di una Action alla stregua dei campi xxx_set (inserimento di una lista di tags che vanno a sovrascrivere la vecchia lista). Per questo sarebbe meglio creare un metodo generico che presi in input due set di oggetti (relativi nel nostro caso rispettivamente agli oggetti da collegare all'istanza della form e a quelli da scollegare) ritorni come output due set di oggetti tali che il primo set indica gli oggetti da rimuovere e il secondo quelli da aggiungere (nel nostro caso rispettivamente quelli da scollegare dall'istanza e quelli da collegarvi). v 

* Creare una nuova a applicazione (organization) con tre modelli ( vedere documento di analisi) v
* creare una vista, relativa al modello NoticeSetting, che aggiunga nuovi tipi di notifiche relative ad un particolare utente e collegate ad uno o piu backends

* rinominare l'applicazione 'connection' in 'organization' v
* spostare UserNotice in oa_notification/models.py v
* implementare una gestione di segnale che alla creazione di un post nel blog nella post_save del modello Post (controllando che l'istanza sia di tipo answer) prenda i referrers ed i followers della action e invii loro una notifica --> in oa_notification/handlers.py v
* nella post_save dell'user, nel caso in cui questo sia attivo (is_active = True) creare un'istanza di NoticeSetting per l'utente con backend openaction = True v
* Implementare il backend di openaction --> eredita da notification.backend.base.BasBackend e al suo interno instanzia UserNotice (vedere ad esempio l'implementazione di oa_notification/backend/facebook.py ) v
* Creare una property in organization che ritorni il QS degli utenti che seguono l'associazione v

* sostituire UserNotice con Notice nel backend di openaction V
* creare una view in organization per implementare la follow --> creazione del mapping di tipo follow tra utente e associazione V 
* sostituire user_join_same_action con user_join_your_action in oa_notification/handlers
* modificare l'handler notify_action_get_level_step in oa_notification/handlers in modo che i segnali che riceve vengano gestiti solamente se lo stato ricevuto è READY V
* nella vista organization/UserFollowOrgView controllare se l'utente è già collegato all'associazione: in questo caso, controllare se il campo is_follower è uguale a True: se è così l'utente era già collegato all'associazione e quindi va sollevata un'eccezione V
* sostituire user_set_default_notice_bacKend a comment_your_action in oa_notification/handlers V
* implementare eccezioni in organization V

* provare a escluedere i nuovi attributie che estendono Vote, lasciando solo referral --> sembrano non funzionar, non vengon oaggiunti nel db......

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

* [TODO futuro]: controllare (e quindi attivare) quale backand ha scelto l'utente (per ora previsti FB e TW) 
* [non prioritario] implementare generiche viste per il modello UserNotice (List/Add/Edit/Delete)
* [non prioritario] testare l'aggiunta dei tags in fase di creazione del blogpost V
* [non prioritario] modifica dei tag di una azione: i referrers (e di conseguenza i moderatori) possono modificare i tag di una Action.
* [in sospeso] Moderatori: leggere specifiche - a cosa servono i moderatori?:
    viste:
        * ActionModeratorsAdd, 
        * ActionModeratorsManage
* [non prioritario] Documentazione viste e modello https://github.com/openpolis/open-action/wiki/

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

