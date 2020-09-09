Demo implementation of a transaction using aca-py.

Run demo code:

    --> The demo code utilises the public BCGov Von test network and therefore requires an internet connection.
    --> The start up bash scripts were written on linux: definitely works on linux, windows i assume not

    --> Running instructions: clone this repositary and then run the ./start_shop_agent script for all four agents as outlined below.

    --> start_shop_agent script can be run with four different agent names as follows:
            ./start_shop_agent vendor
            ./start_shop_agent shipper
            ./start_shop_agent bank
            ./start_shop_agent user
            each should be run in a separate terminal window. The web interface and aca-py swagger API can then be
            accessed via localhost on the ports displayed in the terminal output, shown below for convenience:

            bank:     interface: :7032/    swagger API: :7041
            vendor:   interface: :7042/    swagger API: :7041
            shipper:  interface: :7052/    swagger API: :7051
            user:     interface: :7062/    swagger API: :7061

    Demo uses a web interface, and is implemented with Flask.

   Connections:
            Connections between agents are established through pasting invite json details.
            Click on the create invitation on either shipper, vendor, bank, copy the JSON, and then
            paste it into the invite text area.

            Note that the demo assumes that any actions performed are intended for the recipient specified
            under "current_connection" on either the Shop or Connecitons tab.
            A different connection can be chosen under the Connections tab where


Credential exchange history (as stored by aca-py agent), and currently stored crededntials, can be seen on the credentials tab.
Proof exchange history can be seen on the proofs tab.
Connection history can be seen on the connections tab.

Guidance for next stage in the protocol found on the shop tab, which can also be used for
generating and

The intended flow of agent actions is outlined below. There is the option of directly choosing to issue and request credentials and proofs,
with the actions under the credentials and proof tabs resepectively, or the shop tab provides a guided/enforced sequence of actions between
the agents.



Demo flow:

1.     User agent establishes connection with the vendor.

2.     User requests to purchase an item.

3.     Vendor approves purchase request (automated to reduce clutter steps and for time)

4.     User establishes connection with Bank.

5.     The user (proposes) proof of payment agreement to the Bank.

6.     The bank issues a payment credential to the user.

7.     The user establishes a fresh connection (or can reuse) with the vendor.

8.     The user proves payment to the vendor

9.     The vendor issues the user a credential containing the package number for their goods

10.    The shipping service establishes a connection to the vendor.

11.    The shipping service issues a credential confirming receipt of package number to the vendor

12.    The vendor reuses conneciton to user to propose proof of reciept (that package at shipping service)

13.    The user establishes a connection with the shipping service.

14.    The user proves package ownership to the vendor.

15.    Completed. (upon success, the shipper would label and send goods at this point)

16.    Shipping service requests proof of package ownership, user obliges.





