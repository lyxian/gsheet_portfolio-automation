# gsheet > portfolio-automation

Features :

- server to receives requests
  - timings
    - sg : 10am, 1pm, 3pm, 6pm
    - us : 10am, 12pm, 2pm, 5pm
- gsheet to update spreadsheet
  - deal with formulae, cell format
- deploy to Heroku
  - configure secrets
  - configure Heroku env

Extras :

- integrate encryptionStore

##Packages (list required packages & run .scripts/python-pip.sh)
cryptography==37.0.4
oauth2client==4.1.3
pendulum==2.1.2
requests==2.28.1
gspread==5.4.0
pyyaml==6.0
flask==2.2.2
##Packages
