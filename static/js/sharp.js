jQuery(function(){

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function csrfSafeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    function sameOrigin(url) {
        var host = document.location.host;
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        !(/^(\/\/|http:|https:).*/.test(url));
    }       

    var csrftoken = getCookie('csrftoken');

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    }); 

    function acceptOn(){
        var thisbutton=$(this)
        var data={hoster:thisbutton.parent().parent().attr("id"),}
        $.ajax({
            type:"POST",
            url:"/common/accept/",
            data:data,
            dataType:'text',
            success:function(txt,textStatus){
                thisbutton.removeClass("accept-off").addClass("accept-on").off('click',acceptOn)
                $.each(thisbutton.parent().parent().siblings(), function(){ 
                    $(this).children(".post-left").children(".accept-off").remove()})
            },
            error:function(xhr,textStatus,errorFhrown){
                modalInfo('未知错误')
            }
        })
    }

    function voteUp(){
        var thisbutton=$(this)
        var bro=thisbutton.siblings(".vote-down-off")
        $.ajax({
            type:"POST",
            url:"/common/vote/",
            data:{hoster:thisbutton.parent().parent().attr("id"),value:"1"},
            dataType:'text',            
            success:function(txt,textStatus){
                thisbutton.removeClass("vote-up-off").addClass("vote-up-on").off('click',voteUp)
                bro.off('click',voteDown)           
                thisbutton.siblings('.vote-num').text(txt)
            },
            error:function(xhr,textStatus,errorFhrown){
                thisbutton.off('click',voteUp)
                bro.off('click',voteDown)
            }
        })
    }
    
    function  voteDown(){   
        var thisbutton=$(this)
        var bro=thisbutton.siblings(".vote-up-off")
        $.ajax({
            type:"POST",
            url:"/common/vote/",
            data:{hoster:thisbutton.parent().parent().attr("id"),value:"-1"},
            dataType:'text',
            success:function(txt,textStatus){
                thisbutton.removeClass("vote-down-off").addClass("vote-down-on").off('click',voteDown)
                bro.off('click',voteUp)
                thisbutton.siblings('.vote-num').text(txt)
            },
            error:function(xhr,textStatus,errorFhrown){
                thisbutton.off('click',voteDown)
                bro.off('click',voteUp)
            }
        })
    }

    function favorOn(){
        var thisbutton=$(this)
        $.ajax({
            type:"POST",
            url:'/common/favor/',
            data:{hoster:thisbutton.parent().parent().attr("id")},
            dataType:'text',
            success:function(txt,textStatus){
                thisbutton.removeClass('favor-off').addClass("favor-on").off('click',favorOn)
                thisbutton.siblings('.favor-num').text(txt)
            },
            error:function(xhr,textStatus,errorFhrown){
                modalInfo('未知错误')
            }
        })
    }
    
    function favorOff(){
        var thisbutton=$(this)
        $.ajax({
            type:"POST",
            url:'/common/favor/',
            data:{hoster:thisbutton.parent().parent().attr("id")},
            dataType:'text',
            success:function(txt,textStatus){
                thisbutton.removeClass('favor-on').addClass("favor-off").off('click',favorOff)
                thisbutton.siblings('.favor-num').text(txt)
            },
            error:function(xhr,textStatus,errorFhrown){
                modalInfo('未知错误')
            }
        })
    }

    function commentsHide(){
        var thisbutton=$(this)
        thisbutton.siblings().hide()
        thisbutton.removeClass('comments-hide').addClass("comments-show").off('click',commentsHide).on('click',commentsShow)
        thisbutton.text('显示评论')
    }

    function commentsShow(){
        var thisbutton=$(this)
        thisbutton.siblings().show()
        thisbutton.removeClass('comments-show').addClass("comments-hide").off('click',commentsShow).on('click',commentsHide)
        thisbutton.text('隐藏评论')
    }

    $(".vote-up-off").on('click',voteUp)
    $(".vote-down-off").on('click',voteDown)
    $(".accept-off").on('click',acceptOn)
    $(".favor-off").on('click',favorOn)
    $(".favor-on").on('click',favorOff)
    $(".comments-hide").on('click',commentsHide)
    $(".comments-show").on('click',commentsShow)
    
})
