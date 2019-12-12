CTFd._internal.challenge.data = undefined

CTFd._internal.challenge.renderer = CTFd.lib.markdown();


CTFd._internal.challenge.preRender = function () { }

CTFd._internal.challenge.render = function (markdown) {
    return CTFd._internal.challenge.renderer.render(markdown)
}

CTFd._internal.challenge.postRender = function () { 
    CTFd._internal.challenge.result = getUrlParameter("testResult");
    if(CTFd._internal.challenge.result) {
        CTFd._internal.challenge.evaluateResult();
    } 
}

CTFd._internal.challenge.evaluateResult = function() { 
    var res = JSON.parse(CTFd._internal.challenge.result);
    if(res.success) {
        $(".challenge-desc").html("Congratulations! Your flag value is: " + res.flag);
        $("#submit-key").html("Submit Flag");
    } else {
        $(".challenge-desc").html("Sorry, you still need to do more to get this flag.");
        $("#submit-key").html("Try Again");
    }
}

CTFd._internal.challenge.submit = function (cb, preview) {
    if(!CTFd._internal.challenge.result) {
        // submit to validator service
        $("#final").submit();
    } else {
       var challenge_id = parseInt(CTFd.lib.$('#challenge-id').val())
       var submission = CTFd.lib.$('#submission-input').val()
       var body = {
           'challenge_id': challenge_id,
            'submission': submission,
       }
       var params = {}
       if (preview) {
          params['preview'] = true
       }
       return CTFd.api.post_challenge_attempt(params, body).then(function (response) {
          if (response.status === 429) {
            // User was ratelimited but process response
            return response
          }
          if (response.status === 403) {
            // User is not logged in or CTF is paused.
            return response
          }
          return response
       })
    }
};

function getUrlParameter(name) {
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    var results = regex.exec(location.search);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
};