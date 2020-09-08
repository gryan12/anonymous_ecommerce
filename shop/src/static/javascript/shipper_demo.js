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


$("#pack_form").submit(function(e) {
    console.log("Testing_one")
    e.preventDefault(); // avoid to execute the actual submit of the form.
    var form = $(this);
    var url = form.attr('action');
    $.ajax({
           type: "POST",
           url: url,
           dataType: 'json',
           contentType: 'application/json',
           data: form.serialize(),
           success: function(data)
           {
               alert(data); // show response from the php script.
           }
         });
});
