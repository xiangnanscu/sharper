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

	function reCreateForm(url,row,col,word){
		//评论,回答,回复客户端通用渲染框
		//如果需要从服务器获得信息,则不要用这个
		return '<form action="'+url+'" method="post"><p>\
		<textarea rows="'+row+'" cols="'+col+'" placeholder="写下你的'+word+'" \
		id="id_content" name="content"></textarea></p>\
		<input type="submit" value="提交" /></form>'
	}

	function reUpdateForm(url,row,col,word,content){
		//评论,回答,回复客户端通用渲染框
		return '<form action="'+url+'" method="post"><p>\
		<textarea rows="'+row+'" cols="'+col+'" placeholder="写下你的'+word+'" \
		id="id_content" name="content">'+content+'</textarea></p>\
		<input type="submit" value="提交" />  <span class="cancel">取消</span></form>'
	}

	function acceptOn(){
		var thisbutton=$(this)
		var hoster=$("#"+thisbutton.attr("name")) //找到回答的id元素
		$.ajax({
			type:"POST",
			url:"/common/accept/",
			data:{
				hoster:hoster.attr("id"),
			},
			dataType:'text',
			success:function(txt,textStatus){
				thisbutton.removeClass("accept-off").addClass("accept-on").off('click',acceptOn)
				//成功采纳答案后,其他回答的采纳标记应该被移除.
				//这个是查找所有类名为.accept-off的元素并直接移除.
				$(".accept-off").remove()
				var rep=thisbutton.parents().siblings('.post-right').children('.post-reputation')
				rep.text(txt)
			},
			error:function(xhr,textStatus,errorFhrown){
				modalInfo('未知错误')
			}
		})
	}

	function voteUp(){
		//只要点击了,无论成功还是失败,均取消顶按钮和踩按钮的监听.
		//刷新页面可以重新尝试.
		var thisbutton=$(this)
		var bro=thisbutton.siblings(".vote-down-off")
		$.ajax({
			type:"POST",
			url:"/common/vote/",
			data:{
				hoster:thisbutton.attr("name"),
				value:"1",
			},
			dataType:'text',			
			success:function(txt,textStatus){
				//txt格式'票数@声望数'
				var arr=txt.split('@')
				thisbutton.removeClass("vote-up-off").addClass("vote-up-on").off('click',voteUp)
				bro.off('click',voteDown)			
				thisbutton.siblings('.vote-num').text(arr[0])
				var rep=thisbutton.parents().siblings('.post-right').children('.post-reputation')
				rep.text(arr[1])
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
			data:{
				hoster:thisbutton.attr("name"),
				value:"-1"
			},
			dataType:'text',
			success:function(txt,textStatus){
				var arr=txt.split('@')
				thisbutton.removeClass("vote-down-off").addClass("vote-down-on").off('click',voteDown)
				bro.off('click',voteUp)
				thisbutton.siblings('.vote-num').text(arr[0])
				var rep=thisbutton.parents().siblings('.post-right').children('.post-reputation')
				rep.text(arr[1])
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
			data:{hoster:thisbutton.attr("name")},
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
			data:{hoster:thisbutton.attr("name")},
			dataType:'text',
			success:function(txt,textStatus){
				//用户点击之后,取消监听.防止不必要的数据库更新(比如用户多点了一下,或者因为太卡,狂点).
				//如果用户想反悔,需要刷新页面再点.
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
		//这个按钮的所有级别祖先中,类名为comments的祖先的所有子类元素
		//排除掉自身,全部隐藏.然后自身的类名改变,事件监听函数改变
		//为什么不直接thisbutton.siblings().hide()?因为为了thisbutton深度增加后也能正确隐藏
		thisbutton.parents(".comments").children().not(thisbutton).hide()
		thisbutton.removeClass('comments-hide').addClass("comments-show")//(由于on指定了selector,所以这里不用手动增删监听).off('click',commentsHide).on('click',commentsShow)
		thisbutton.html('<i class="fa fa-folder"></i>')
	}

	function commentsShow(){
		var thisbutton=$(this) 
		thisbutton.parents(".comments").children().show()
		thisbutton.removeClass('comments-show').addClass("comments-hide")//.off('click',commentsShow).on('click',commentsHide)
		thisbutton.html('<i class="fa fa-folder-open"></i>')
	}

	function commentCreate(){
		//在添加评论按钮<a>前面插入<form>
		//这个是评论条目数小于6的情况,直接客户端渲染,无需加载额外评论,无需访问服务器.
		//严格意义上说,可能会有误差.
		//比如用户A访问q问题时只有1条评论,在他对q提交评论之前,其他用户对q提交了新的评论c,
		//用户A提交之后如果不刷新页面,就看不到c
		//但这种情况应该比较少,故先忽略.
		event.preventDefault()
		var thisbutton=$(this)
		var url=thisbutton.attr("href")
		thisbutton.before(reCreateForm(url,3,75,'评论'))
		var submit=thisbutton.prev().find('input[type="submit"]') //这个是form的提交按钮.
		//alert(submit.attr("type"))
		submit.on('click',commentCreateSubmit) //添加监听,这个没办法,必须手动加.因为和其他共用了form
		thisbutton.remove() //加载出评论输入框后,添加评论按钮<a>删除
	}

	function commentCreateRest(){
		//待解决:IE11有BUG.非首次点击,不再会调用此函数,也不会和服务器交互.只会显示之前的评论条目.
		//必须重启浏览器并首次点击才正常加载.
		//chrome有BUG.如果先点击此按钮,再点击渲染出来的form的上面2条评论的更新按钮,则会发现其
		//ajax监听已失效.
		event.preventDefault()
		var thisbutton=$(this) //'添加并显示剩余评论'按钮,紧跟评论条目
		var url=thisbutton.attr("href")
		$.ajax({
			type:"GET",
			dataType: "json",
			url:url,
			success:function(responseData){
				//删除所有老评论
				thisbutton.siblings('.comments-content').remove()
				//插入所有评论
				thisbutton.before(responseData.success_items) 
				//再统一添加'更新'监听
				//thisbutton.siblings('.comments-content').children('.comment-update').on('click',commentUpdate)
				//thisbutton.before(reCreateForm(url,3,75,'评论'))
				var submit=thisbutton.prev().find('input[type="submit"]') //这个是form的提交按钮.
				submit.on('click',commentCreateSubmit) //添加监听
				thisbutton.remove() //加载出评论输入框后,添加评论并显示剩余按钮<a>删除
			},
			error:function(xhr,textStatus,errorFhrown){
				alert('未知错误')
			}
		})
	} 

	function commentCreateSubmit(){
		//把用户成功提交的评论插进去.或者显示错误信息.
		event.preventDefault()
		var thisbutton=$(this)
		var form=thisbutton.parent()
		var url=form.attr("action") //url在父类form的action里
		var content=thisbutton.siblings().find("#id_content").val()
		var captcha_0=thisbutton.siblings().find("#id_captcha_0").val()
		var captcha_1=thisbutton.siblings().find("#id_captcha_1").val()
		$.ajax({
			type:"POST",
			dataType: "json",
			url:url,
			data:{
				content:content, //获取文本框内容
				captcha_0:captcha_0,
				captcha_1:captcha_1,
			},
			success:function(responseData){
				if (responseData.form_valid==true){
					var x=form.siblings('.comments-hide').length //如果没有'隐藏评论'按钮,那么提交评论后应该要加上.
					if (x==0){
						form.after('<a class="comments-hide"><i class="fa fa-folder-open"></i></a>')
						//form.next().on('click',commentsHide) //更新:现在不用
					}
					//成功返回评论后,要在末尾重新添加按钮.以便用户继续提交评论
					form.after('<a class="comment-create" href="'+url+'"><i class="fa fa-comment"></i></a>')
					//form.next().on('click',commentCreate) //更新:现在不用
					form.after(responseData.success_items) //更新当前评论条目
					//上面插入的最新条目,要为'更新'按钮添加监听.更新:现在不用
					//form.next().find('.comment-update').on('click',commentUpdate)
					form.remove() //移除提交form
				} else {
					form.children().not(thisbutton).remove() //除提交按钮之外的全部移除
					form.prepend(responseData.error_items) //插入服务器传来的出错信息
				}

			},
			error:function(xhr,textStatus,errorFhrown){
				alert('未知错误')
			}
		})
	}

	function commentUpdate(){
		event.preventDefault()
		var thisbutton=$(this)
		var commentDiv=thisbutton.parent()
		//首先判断commentDiv下方是不是已经有update form对象了.
		//有的话,直接显示它,没有才需要加载.
		//因为用户有可能蛋疼地点击'编辑评论'->'取消'->'编辑评论'
		//由于点击'取消'时实际上是把form隐藏起来
		//这个时候就无需加载新的form.直接show即可
		var is_form=commentDiv.next().is('form')
		//当用户点击'添加评论'后,最下面一条评论的下方便会有create form
		//而create form是不能当做update form的.需要加一个判断
		if (is_form&&commentDiv.next().attr('action').indexOf('/update/')!=-1) {
			commentDiv.next().show()
		} else {
			var url=thisbutton.attr("href")
			var content=thisbutton.siblings("span").text()
			var form=reUpdateForm(url,3,75,'评论',content) //生成更新框form
			commentDiv.after(form) //在原评论对象的下方插入form
			var form=commentDiv.next() //要这样才能指定插入后的form.直接用上面的form变量不行.
			var submit=form.find('input[type="submit"]') //这个是form的提交按钮.
			submit.on('click',commentUpdateSubmit) //添加监听
			var cancel=form.find('.cancel') //这个是取消更新的按钮.
			cancel.on('click',cancelCommentUpdate)			
		}
		commentDiv.hide() //加载出评论输入框后,原评论对象区域隐藏
	}

	function cancelCommentUpdate(){
		//'取消'按钮的父类是form
		var form=$(this).parent()
		form.hide()
		form.prev().show()
	}

	function commentUpdateSubmit(){
		//把用户成功提交的评论插进去.或者显示错误信息.
		event.preventDefault()
		var thisbutton=$(this)
		var form=thisbutton.parent()
		var url=form.attr("action") //url在父类form的action里
		var content=thisbutton.siblings().find("textarea").val()
		$.ajax({
			type:"POST",
			dataType: "json",
			url:url,
			data:{
				content:content, //获取文本框内容
			},
			success:function(responseData){
				if (responseData.form_valid==true){
					form.prev().remove() //移除原评论
					form.before(responseData.success_items)
					//form.prev().find('.comment-update').on('click',commentUpdate)
					form.remove() //移除提交form
				} else {
					form.children().not(thisbutton).remove() //除提交按钮之外的全部移除
					form.prepend(responseData.error_items) //插入服务器传来的出错信息
				}

			},
			error:function(xhr,textStatus,errorFhrown){
				alert('未知错误')
			}
		})
	}

	function reUpdate(){
		event.preventDefault()
		var thisbutton=$(this)
		//隐藏sep分割线
		thisbutton.prev().hide()
		//首先暂时隐藏'回复'按钮
		thisbutton.hide()
		//回复内容区域
		var contentdiv=thisbutton.parent().siblings(".post-content")
		//整个回复区域
		var rediv=contentdiv.parent().parent()
		//加载编辑框
		//如果之前已经加载好了编辑框,则直接显示即可
		if (contentdiv.next().is('form')) {
			contentdiv.next().show()
		} else {
			var url=thisbutton.attr("href")
			var content=contentdiv.text()
			contentdiv.after(reUpdateForm(url,6,75,'回应',content))
			var form=contentdiv.next() 
			var submit=form.find('input[type="submit"]') //这个是form的提交按钮.
			submit.on('click',reUpdateSubmit) //添加监听
			var cancel=form.find('.cancel') //这个是取消更新的按钮.
			cancel.on('click',cancelReUpdate)
		}
		//隐藏原文本区域
		contentdiv.hide()
	}

	function cancelReUpdate(){
		//'取消'按钮的父类是form
		var form=$(this).parent()
		//隐藏本form
		form.hide()
		//显示原回应文本区域
		form.siblings('.post-content').show()
		//显示'编辑'按钮
		form.siblings('.post-action').children().show()
	}

	function reUpdateSubmit(){
		//把用户成功提交的评论插进去.或者显示错误信息.
		event.preventDefault()
		var thisbutton=$(this)
		var form=thisbutton.parent()
		var rediv=form.parent().parent() //整个回复区域
		var url=form.attr("action") //url在父类form的action里
		var content=thisbutton.siblings().find("textarea").val()
		$.ajax({
			type:"POST",
			dataType: "json",
			url:url,
			data:{
				content:content, //获取文本框内容
			},
			success:function(responseData){
				if (responseData.form_valid==true){
					//原内容之前插入新内容
					rediv.before(responseData.success_items) //刷新整个回应区域
					//newre=rediv.prev() //由于selector指定了几个自动添加监听的类.这里不用手动为新插入的元素添加任何监听
					rediv.remove() //移除原回应
				} else {
					form.children().not(thisbutton).remove() //除提交按钮之外的全部移除
					form.prepend(responseData.error_items) //插入服务器传来的出错信息
				}

			},
			error:function(xhr,textStatus,errorFhrown){
				alert('未知错误')
			}
		})
	}

/*	$("body").on("click",".vote-up-off",voteUp)
	$("body").on("click",".vote-down-off",voteDown)
	$("body").on("click",".accept-off",acceptOn)
	$("body").on("click",".favor-off",favorOn)
	$("body").on("click",".favor-on",favorOff)*/
	$("body").on("click",".re-update",reUpdate)
	$("body").on("click",".comment-update",commentUpdate)
	$("body").on("click",".comments-hide",commentsHide)
	$("body").on("click",".comments-show",commentsShow)
	$("body").on("click",".comment-create",commentCreateRest)
	$("body").on("click",".comment-create-rest",commentCreateRest)

	$(".vote-up-off").on('click',voteUp)
	$(".vote-down-off").on('click',voteDown)
	$(".accept-off").on('click',acceptOn)
	$(".favor-off").on('click',favorOn)
	$(".favor-on").on('click',favorOff)

/*	$(".re-update").on('click',reUpdate)
	$(".comment-update").on('click',commentUpdate)
	$(".comments-hide").on('click',commentsHide)
	$(".comments-show").on('click',commentsShow)
	$(".comment-create").on('click',commentCreate)
	$(".comment-create-rest").on('click',commentCreateRest)*/

	
})
