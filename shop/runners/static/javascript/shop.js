function getUserActions(stage) {
        if (stage === "start") {
            $('#t_stage').append("Start: make purchase request")
            $('#actions').append('<button type="button" onclick = "requestPurchase()">Purchase Item</button>')
        }

        else if (stage === "agreement_proposed") {
            $('#t_stage').append('Requested purchase: awaiting response')
        }

        else if (stage === "agreement_received") {
            $('#t_stage').append('Purchase approved, next step: Payment')
            $('#actions').append ('<button type="button" onclick = "proposeProofOfPaymentAgreement()">Make Payment</button>')
        }

        else if (stage === "payment_agreement_proven") {
            $('#t_stage').append('Payment in process; awaiting bank response')
        }

        else if (stage === "payment_credential_received") {
            $('#t_stage').append('Payment made. Next step: proving payment to vendor')
            $('#actions').append('<button type="button" onclick = "proposeProofOfPayment()">Prove Payment to Vendor</button>')
        }

        else if (stage === "payment_credential_proven") {
            $('#t_stage').append('Proven payment to vendor.<br>Awaiting package credential.')
        }

        else if (stage === "package_credential_received") {
            $('#t_stage').append('Received package credential. <br> Awaiting proof of receipt')
        }

        else if (stage === "package_receipt_validated") {
            $('#t_stage').append('Proven dispatch.<br> Next stage: prove ownership to shipper')
            $('#actions').append('<button type="button" onclick = "proposeProofOfOwnership()">Prove Package Ownership</button>')
        }

        else if (stage === "completed") {
            $('#t_stage').append('Transaction completed')
        }
}
function getVendorActions(stage) {
    if (stage === "start") {
        $('#t_stage').append("Start: awaiting purchase request")
    }

    else if (stage === "purchase_requested") {
        $('#t_stage').append('Requested purchase: automatically agreeing...')
    }

    else if (stage === "purchase_approved") {
        $('#t_stage').append('Purchase approved, awaiting proof of payment')
    }

    else if (stage === "payment_proven") {
        $('#t_stage').append('Payment proven. <br> Packaging goods...')
        $('#actions').append('<button type="button" onclick = "issueCredential()">Issue Package Credential</button>')
    }

    else if (stage === "package_shipped") {
    $('#t_stage').append('Package shipped. Awaiting confirmation of receipt by shipping service')
    }

    else if (stage === "receipt_confirmed") {
        $('#t_stage').append('Shipper has received package. <br> Next stage: prove to user that package at shipping service')
        $('#actions').append('<button type="button" onclick = "proposeProofOfDispatch()">Prove Package Status to User</button>')
    }

    else if (stage === "completed") {
        $('#t_stage').append('Vendors role in the transaction has been completed')
    }
}
function getBankActions(stage) {
    if (stage === "start") {
        $('#t_stage').append("Start: awaiting proof of payment agreement")
    }
    else if (stage === "payment_agreement_validated") {
        $('#t_stage').append('Agreement validated. <br> Next stage: issue payment credential')
        $('#actions').append('<button type="button" onclick = "issueCredential()">Issue Payment Confirmation Credential</button>')
    }
    else if (stage === "completed") {
        $('#t_stage').append('Role in transaction completed.<br> Successfully issued confirmation of payment to user.')
    }
}

function getShipperActions(stage) {
    if (stage === "start") {
        $('#t_stage').append("Start: awaiting packages...")
        $('#actions').append('<button type="button" onclick = "issueCredential()">Send Receipt Credential</button>')
        $('#package_form').append('<br><label for="pack_no"> Input Package Number </label> ' +
                                  '<input type="text" id="pack_no"/><button type="submit">Submit</button>')
    }

    else if (stage === "receipt_issued") {
        $('#t_stage').append('Credential issued: awaiting proof of ownership of package')
    }
    else if (stage === "completed") {
        $('#t_stage').append('Transaction completed! Shipping...')
    }

}
function get(stage) {
    if (stage === "start") {
        $('#t_stage').append("Start: awaiting proof of payment agreement")
    }

    else if (stage === "purchase_requested") {
        $('#t_stage').append('Agreement validated. <br> Next stage: issue payment credential')
        $('#actions').append('<button type="button" onclick = "issueCredential()">Issue Package Credential</button>')
    }
}

$(document).ready(function() {
    var name = '{{ name }}'
    var stage = '{{ stage }}'

    if (name === "user") {
        console.log("user func, ".concat(name, " ", stage))
        getUserActions(stage)
    }
    else if (name === "vendor") {
        console.log("vendor func, ".concat(name, " ", stage))
        getVendorActions(stage)
    }
    else if (name === "bank") {
        console.log("bank func, ".concat(name, " ", stage))
        getBankActions(stage)

    }else if (name === "shipper") {
        console.log("shipper func, ".concat(name, " ", stage))
        getShipperActions(stage)
    }
});

 function createInvite() {
   var xhttp = new XMLHttpRequest();
   xhttp.onreadystatechange = function() {
     if (this.readyState == 4 && this.status == 200) {
       document.getElementById("demo").innerHTML =
       "<h3> Invite Details: <br>" + this.responseText + "</h3>";
     }
   };
   xhttp.open("GET", "/connections/create_invite", true);
   xhttp.send();
 }

 function getStatus() {
   var xhttp = new XMLHttpRequest();
   xhttp.onreadystatechange = function() {
     if (this.readyState == 4 && this.status == 200) {
       document.getElementById("demo").innerHTML =
       "<h3> Server Status JSON: " +  this.responseText + "</h3>";

     }
   };
   xhttp.open("GET", "/status", true);
   xhttp.send();
}


function sendShipping(e) {
    console.log("Testing_two")
        e.preventDefault();
        var package = document.getElementById('pack_no').value
        var package_data = {"package_no": package}
        var url = "/home/shop/package/input"
        $.ajax({
               type: "POST",
               url: url,
               dataType: 'json',
               contentType: 'application/json',
               data: package_data,
               success: function(data)
               {
                    console.log("success")
                    //location.reload(true)
               }
             });
}

$(document).ready(function(){
    $.ajax({ url: "/connections/get_active_connections",
        context: document.body,
        dataType: 'json',
        success: function(response){
           var current = false
           for (var key in response) {
               console.log("object: %0", response)
                    if (key === "current_connection") {
                        var current = true;
                        var curr = response[key]
                        $('#current_connection').append(response[key]);
                    }
            }

            if (!current) {
                        $('#current_connection').append("None");
            }

        }});
});

function reload() {
    setTimeout(location.reload.bind(location), 60000);
}

//function getTransactionDetails() {
//    console.log("transaction req")
//    $.ajax({ url: "/home/shop/transaction",
//        context: document.body,
//        dataType:'json',
//        success: function(response){
//           var results = response
//               for (var key in response) {
//                if (response.hasOwnProperty(key)) {
//                    console.log(key + " -> " + response[key]);
//                    if (key != 'result' && key != 'current_connection') {
//                        console.log("in key")
//                    }
//                }
//            }
//    }});
//}
