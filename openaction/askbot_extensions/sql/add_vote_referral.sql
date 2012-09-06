ALTER TABLE "vote" ADD COLUMN "referral_id" 
     integer REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED
;
