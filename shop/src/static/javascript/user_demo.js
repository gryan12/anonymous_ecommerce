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

 function requestPurchase() {
   var xhttp = new XMLHttpRequest();
   xhttp.onreadystatechange = function() {
     if (this.readyState == 4 && this.status == 200) {
         location.reload(true)
     }
   };
   xhttp.open("GET", "/credentials/shop/request_purchase/", true);
   xhttp.send();
 }

