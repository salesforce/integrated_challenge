window.challenge.data = undefined;
window.challenge.result = undefined;

window.challenge.renderer = new markdownit({
    html: true,
    linkify: true,
});

window.challenge.preRender = function () {

};

window.challenge.render = function (markdown) {
    return window.challenge.renderer.render(markdown);
};


window.challenge.postRender = function () {
    window.challenge.result = getUrlParameter("testResult");
    if(window.challenge.result) {
        window.challenge.evaluateResult();
    } 
};

window.challenge.evaluateResult = function() { 
    var res = JSON.parse(window.challenge.result);
    if(res.success) {
        $(".challenge-desc").html("Congratulations! Your flag value is: " + res.flag);
        $("#submit-key").html("Submit Flag");
    } else {
        $(".challenge-desc").html("Sorry, you still need to do more to get this flag.");
        $("#submit-key").html("Try Again");
    }
}

window.challenge.submit = function (cb, preview) {
    if(!window.challenge.result) {
        // submit to validator
        $("#final").submit();
    } else {
        var res = JSON.parse(window.challenge.result);
        if(!res.success) {
            var u = new URL(window.location.href);
            var newURL = u.origin + u.pathname + u.hash;
            window.location.assign(newURL);
            var submission = "";
        } else {
            var submission = res.flag;
            var challenge_id = parseInt($('#challenge-id').val());
            //var submission = $('#submission-input').val();
            var url = "/api/v1/challenges/attempt";        
            if (preview) {
                url += "?preview=true";
            }
            var params = {
                'challenge_id': challenge_id,
                'submission': submission
            };
            CTFd.fetch(url, {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(params)
            }).then(function (response) {
                if (response.status === 429) {
                    // User was ratelimited but process response
                    return response.json();
                }
                if (response.status === 403) {
                    // User is not logged in or CTF is paused.
                    return response.json();
                }
                return response.json();
            }).then(function (response) {
                cb(response);
            });    
            }
    }
};

function getUrlParameter(name) {
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    var results = regex.exec(location.search);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
};