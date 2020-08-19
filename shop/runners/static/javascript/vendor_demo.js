
 function issueCredential() {
   var xhttp = new XMLHttpRequest();
   xhttp.onreadystatechange = function() {
     if (this.readyState == 4 && this.status == 200) {
         location.reload(true)
     }
   };
   xhttp.open("GET", "/credentials/issue_cred", true);
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

 function approvePurchase() {
   var xhttp = new XMLHttpRequest();
   xhttp.onreadystatechange = function() {
     if (this.readyState == 4 && this.status == 200) {
         location.reload(true)
     }
   };
   xhttp.open("GET", "/credentials/shop/approve_purchase/", true);
   xhttp.send();
 }
