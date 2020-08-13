
$(document).ready(function(){
    $.ajax({ url: "/proofs/history",
        context: document.body,
        dataType:'json',
        success: function(response){
           console.log("object: %0", response)
           console.log("object :%0", response["results"])
           var results = response["results"]
           for (var i= 0; i < results.length; i++) {
               $('#proof_ex_hist').append("Updated at: " + results[i].updated_at + "<br>");
               $('#proof_ex_hist').append("Connection ID: " + results[i].connection_id + "<br>");
               $('#proof_ex_hist').append("Role: " + results[i].role + "<br>");
               $('#proof_ex_hist').append("State: " + results[i].state + "<br>");
               if (results[i].hasOwnProperty("verified")) {
                   $('#proof_ex_hist').append("Verification Result: " + results[i].verified + "<br>");
               }
           }
           $('#proof_ex_hist').append("<br>");
    }});
});


function requestProof() {
   var xhttp = new XMLHttpRequest();
   xhttp.onreadystatechange = function() {
     if (this.readyState == 4 && this.status == 200) {
        location.reload(true)
     }
   };
   xhttp.open("GET", "/proofs/request", true);
   xhttp.send();
}


function proposeProofOfPayment() {
   var xhttp = new XMLHttpRequest();
   xhttp.onreadystatechange = function() {
     if (this.readyState == 4 && this.status == 200) {
        location.reload(true)
     }
   };
   xhttp.open("GET", "/proofs/payment/propose_proof/", true);
   xhttp.send();
}

function proposeProofOfPaymentAgreement() {
   var xhttp = new XMLHttpRequest();
   xhttp.onreadystatechange = function() {
     if (this.readyState == 4 && this.status == 200) {
        location.reload(true)
     }
   };
   xhttp.open("GET", "/proofs/payment/propose_proof/agreement", true);
   xhttp.send();
}

function proposeProofOfDispatch() {
   var xhttp = new XMLHttpRequest();
   xhttp.onreadystatechange = function() {
     if (this.readyState == 4 && this.status == 200) {
        location.reload(true)
     }
   };
   xhttp.open("GET", "/proofs/shop/dispatch", true);
   xhttp.send();
 }

function proposeProofOfOwnership() {
   var xhttp = new XMLHttpRequest();
   xhttp.onreadystatechange = function() {
     if (this.readyState == 4 && this.status == 200) {
        location.reload(true)
     }
   };
   xhttp.open("GET", "/proofs/shop/dispatch/propose_proof/ownership", true);
   xhttp.send();
 }

 function testAlert() {
    alert("TestAlert func has been called!")
 }
