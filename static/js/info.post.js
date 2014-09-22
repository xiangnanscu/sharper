$(function(){
	$('form[id^="commentform-"]').on('submit',postComment)
    //modalInfo('info.post.js 无语法错误，请放心使用')
    $('button[data-toggle="more-data"]').on('click',getComments)
    $('a.comments-total').on('click',function(){
        $(this).siblings('div[id^="comment-"]').find('button[data-toggle="more-data"]').trigger('click')
    
    })
    //$('#answerform').on('submit',postAnswer)
	function postAnswer(){
        var question_pk=$('#answerform').find('input[name="question"]').val()
        var answer_url="/api/answers"//+question_pk
        modalInfo(answer_url)
        var options = {  
            //type:'GET',
            //beforeSubmit:  showRequest, 
            url:answer_url,
            success: answerResponse,
            resetForm: true,  
            dataType:  'json'  
        }; 

		$(this).ajaxSubmit(options);
		return false;
	}

    function answerResponse(data, statusText, xhr, $form)  { 
        modalInfo('回答成功，此功能暂未完善，刷新试试')
    } 
	function postComment(){
        var options = {  
        //beforeSubmit:  showRequest,  
        success:       showBack,
        resetForm: true,  
        dataType:  'json'  
        }; 
		$(this).ajaxSubmit(options);
		return false;
	}
    function getComments(){    
        $thisButton=$(this)
        data=$thisButton.attr('data-target')
        url=$thisButton.attr('data-source')
            var options={
            type:'GET',
            url:url,
            context:$thisButton,
            dataType:'json',
            data:{data_target:data},
            success:showMore
            }
        $.ajax(options);
    }
})

function showBack(data, statusText, xhr, $form)  {
    $commentsList=updateComments(data) 
    $form.parent().collapse('hide')
            .siblings('div')
                .find('ol').replaceWith($commentsList)
            .end().collapse('show')
                .siblings('a.comments-total').text(data.count+"条评论")
            .end()
                .find('button[data-toggle="more-data"]').each(function(){
                    if(data.next != null){
                        $(this).attr('data-source','/api/comments/'+data.next).text('更多回应')
                    } else{
                        $(this).attr('data-source',null).text('期待更多回应')
                    }
                    })
    
    } 
    
function showMore(data, statusText, xhr)  {
    $commentsList=updateComments(data) 
    $(this).parent().find('ol').append($commentsList.find('li')).end().parent().siblings('a.comments-total').text(data.count+"条评论")
    if(data.next != null){
        $thisButton.attr('data-source','/api/comments/'+data.next).text('更多回应')
    } else{
        $thisButton.attr('data-source',null).text('期待更多回应')
    }
    }
    
function updateComments(data){
    var $commentsList=$('<ol></ol>')
    var comments=data.results
	for(i=0;i<comments.length;i++){
	   $commentsList.append("<li><span>"+comments[i].content+'&nbsp;--&nbsp;<a href="'+comments[i].user.url+'" title="'+comments[i].user.reputation+'声望,评论于'+comments[i].create_time+'" class="comment-user">'+comments[i].user.username+'</a></span></li>')
		}
    return $commentsList
}