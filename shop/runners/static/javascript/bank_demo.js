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

