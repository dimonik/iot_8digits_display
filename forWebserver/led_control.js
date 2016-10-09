// theory https://developer.mozilla.org/en-US/docs/Web/API/WebSocket
// how use json https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_client_applications

    var ws;

    function opensocket() {

        var serverlog = document.getElementById("serverlog");
        serverlog.innerHTML = serverlog.innerHTML + "<br>trying to connect...";

        ws = new WebSocket("ws://192.168.1.1:12345/");

        ws.onopen = function(){
            serverlog.innerHTML = serverlog.innerHTML + "<br>connected to server";
        };

        ws.onclose = function(event) {
            if (event.wasClean) {
                serverlog.innerHTML = serverlog.innerHTML + "<br>clean disconnect";
            } else {
                serverlog.innerHTML = serverlog.innerHTML + "<br>dirty disconnect";
            }
            serverlog.innerHTML = serverlog.innerHTML + "<br>" + "Code: " + event.code + " Reason: " + event.reason;
        };
        
        ws.onerror = function(error) {
            serverlog.innerHTML = serverlog.innerHTML + "<br>Error: " + error.message;
        };
        
        ws.onmessage = function(event){
            serverlog.innerHTML = serverlog.innerHTML + "<br><< data received: " + event.data;
        };
    }
    
    function closesocket() {
        ws.close(1000, "");
    }

    function postmsg(text){
        ws.send(text);
        showMessage(text);
        serverlog.innerHTML = serverlog.innerHTML + "<br>>> data sent: " + text;
    }
    
    // send message using publish form
    function formPublish() {
        var outgoingMessage = document.forms.publish.message.value;
        postmsg(outgoingMessage);
        return false;
    };
    
    // show message inside div#subscribe
    function showMessage(message) {
        var messageElem = document.createElement('div');
        messageElem.appendChild(document.createTextNode(message));
        document.getElementById('subscribe').appendChild(messageElem);
    }
