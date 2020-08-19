Demo implementation of a transaction using aca-py.

Run demo code:

    --> The demo code utilises the public BCGov Von test network and therefore requires an internet connection.

    --> Running instructions: clone this repositary and then run the ./start_shop_agent script for all four agents as outlined below.

    --> start_shop_agent script can be run with four different agent names as follows:
            ./start_shop_agent flaskvendor
            ./start_shop_agent flaskshipper
            ./start_shop_agent flaskbank
            ./start_shop_agent flaskuser
            each should be run in a separate terminal window. The web interface and aca-py swagger API can then be
            accessed via localhost on the ports displayed in the terminal output, shown below for convenience:

            bank:     interface: :7032/home    swagger API: :7041
            vendor:   interface: :7042/home    swagger API: :7041
            shipper:  interface: :7052/home    swagger API: :7051
            user:     interface: :7062/home    swagger API: :7051

    Demo uses a web interface, and is implemented with Flask.

   Connections:
            Connections between agents are established through pasting invite json details.


The intended flow of agent actions is outlined below. There is the option of directly choosing to issue and request credentials and proofs,
with the actions under the credentials and proof tabs resepectively, or the shop tab provides a guided/enforced sequence of actions between
the agents.

Demo flow:

1.     User agent establishes connection with the vendor.

2.     User requests to purchase an item.

3.     Vendor approves purchase request (automated to reduce clutter steps)

4.     User establishes connection with Bank.

5.     The user proves payment agreement to the Bank.

6.     The bank issues a proof of payment credential to the user.

7.     The user establishes a fresh connection (or can reuse) with the vendor.

8.     The user proves payment to the vendor

9.     The vendor issues the user a credential containing the package number for their goods

10.    The shipping service establishes a connection to the vendor.

11.    The shipping service issues a credential confirming receipt of package number to the vendor

12.    The vendor resues conneciton to user to propose proof of reciept (that package at shipping service)

13.    The user establishes a connection with the shipping service.

14.    The user proves package ownership to the vendor.

15.    Completed. (upon success, the shipper would label and send goods at this point)


6.    Shipping service requests proof of package ownership, user obliges.


File description:

Assumptions:
    The public DID of payment services are made available through application code.
    The public DID of the shipping service used is made available through application code.
    The public DID of the vendor is known through the application code



