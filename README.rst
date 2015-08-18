
Aqua
-------------------------------

Work schedule manager (Django).

Commands
-------------------------------

python manage.py

- runserver: start de testserver
- calculate_roster: rooster verdelen
  - eerste argument is ID van rooster (zonder argument geeft overzicht)
  - -a is de bonus voor meer beschilbaarheid (standaard 18)
- makemigrations, migrate, syncdb: database updaten (in die volgorde)
- collectstatic: static files in /static/ zetten (bij serververhuizing)
- export_backup: zet een backup in /backups/

Use / contributing
-------------------------------

Aqua was not made with open-sourcing in mind. Development time was short, which didn't help code clarity, and documentation is non-existent.
If you still want to use it, you're free to do so; it has worked well for us.


