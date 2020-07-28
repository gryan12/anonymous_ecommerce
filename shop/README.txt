Demo implementation of a transaction using aca-py.

Run demo code:

    --> In current state needs to have an Indy ledger running on port 9000.
        I currently run a BCV ledger locally which can be installed and run with docker here:
            will take a look at moving to docker compose so all of this can be done automatically.

    --> start_shop_agent script can be run with four different agent names as follows:
            ./start_shop_agent flaskvendor
            ./start_shop_agent flaskshipper
            ./start_shop_agent flaskbank
            ./start_shop_agent flaskuser
            each should be run in a separate terminal window. The web interface and aca-py swagger API can then be
            accessed via localhost on the ports displayed in the terminal output, shown below for convenience:

            bank:     interface: :7032/home    swagger API: :7031
            vendor:   interface: :7042/home    swagger API: :7041
            shipper:  interface: :7052/home    swagger API: :7051
            user:     interface: :9052/home    swagger API: :9051


    Demo uses a web interface, and is implemented with Flask.
    The interface in particular is very much a WIP, with all rednered rtext currently left as raw json and there being little
    action enforcement.

    PLan to soon setup clear rendering of javascript and server-push events for a clear event-log on the interface page,
    to make it much more clear what aries-indy protocols have been / are being executed.

   Connections:
        --> connections currently establishes through pasting invitation JSON. invitation creation and receipt is done on the
            home pages of the interface.

            --nb temporarily will need to input a new invite when connceting to a previous agent (i.e. only current connection
                 is used for anoncreds exchange). will change this soon

Demo flow (not enforced):

1.     User agent establishes connection with bank.

2.     bank issues credential to user.

3.     User establishes connection with vendor.

4.     Vendor requests proof of payment, user obliges

5.     User establishes connection with shipping service.

6.    Shipping service requests proof of package ownership, user obliges.


Implementing the other variation(s) atm but above is only flow that works so far.








