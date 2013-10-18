function p2s_nl2br (str, is_xhtml) {   
var breakTag = (is_xhtml || typeof is_xhtml === 'undefined') ? '<br />' : '<br>';    
return (str + '').replace(/([^>\r\n]?)(\r\n|\n\r|\r|\n)/g, '$1'+ breakTag +'$2');
}

function p2s_linkify(inputText) {
    var replaceText, replacePattern1, replacePattern2, replacePattern3;

    //URLs starting with http://, https://, or ftp://
    replacePattern1 = /(\b(https?|ftp):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/gim;
    replacedText = inputText.replace(replacePattern1, '<a href="$1" target="_blank">$1</a>');

    //URLs starting with "www." (without // before it, or it'd re-link the ones done above).
    replacePattern2 = /(^|[^\/])(www\.[\S]+(\b|$))/gim;
    replacedText = replacedText.replace(replacePattern2, '$1<a href="http://$2" target="_blank">$2</a>');

    //Change email addresses to mailto:: links.
    replacePattern3 = /(\w+@[a-zA-Z_]+?\.[a-zA-Z]{2,6})/gim;
    replacedText = replacedText.replace(replacePattern3, '<a href="mailto:$1">$1</a>');

    return replacedText
}

function p2s_linkify2(html) {
  return html
         .replace(/[^\"]http(.*)\.([a-zA-Z]*)/g, ' <a href="http$1.$2">http$1.$2</a>');
}

function showBadgeDetail(badge_id) {
	$.ajax({
          type: "POST",
          data: {
				badge_id: badge_id
		  },
          url: "/badges/detail/",
          error: function(request, textStatus, e) {
				
		  },
			
		  success: function(data, textStatus, request) {
		  		
		  		var badge = data.data
		  		var html = "<img src='"+badge.image_url+"' align='left' style='width:150px;height:150px;'/>";
		  		html += '<br/><p><b>Description:</b> ' + p2s_linkify2(p2s_nl2br(badge.description,true))+'</p>';
		  		html+='<p><b>Criteria:</b> ' + p2s_linkify2(p2s_nl2br(badge.criteria,true))+'</p>';
		  		
				$('#badgeModalDescription').html(html);
				$('#badgeModalTitle').html(badge.name);
				$('#badgeModal').modal();
		  }
			
        });
}

function showPathwayDetail(pathway_id) {
	$.ajax({
          type: "POST",
          data: {
				pathway_id: pathway_id
		  },
          url: "/pathways/details/",
          error: function(request, textStatus, e) {
				
		  },
			
		  success: function(data, textStatus, request) {
		 		var html = "<img src='"+data.data.image_url+"' align='left' style='width:150px;height:150px;'/>";
		  		html += '<br/><p><b>Description:</b> ' + p2s_linkify2(p2s_nl2br(data.data.description,true))+'</p>';
		  		
				$('#pathwayModalDescription').html(html);
				$('#pathwayModalTitle').html(data.data.name);
				$('#pathwayModal').modal();
		  }
			
        });
}



function showAwardDetail(award_id, allowOBI) {
	$.ajax({
          type: "POST",
          data: {
				award_id: award_id
		  },
          url: "/awards/detail/",
          error: function(request, textStatus, e) {
				
		  },
			
		  success: function(data, textStatus, request) {
		  		
		  		var award = data.data
		  		var html = "<img src='"+award.image_url+"' align='left' style='width:150px;height:150px;'/>";
		  		html += '<b>Awarded to you on '+award.date_created+'</b><br/><br/>';
		  		html += '<b>Description:</b> ' + p2s_linkify(p2s_nl2br(award.description,false));
		  		html+='<br/><br/><b>Criteria:</b> ' + p2s_linkify(p2s_nl2br(award.criteria,false));
		  		
				$('#awardModalDescription').html(html);
				$('#awardModalTitle').html("<i class='icon icon-star'></i> "+award.name);
				$('#awardModal').modal();
				$('#backpackButton').unbind('click').click(function(){sendToOBI(award_id)});
				if(allowOBI) {
					$('#backpackButton').show();
				} else {
					$('#backpackButton').hide();
				}
		  }
			
        });
}

function loadBadges(pathway_id) {

	//pathway_id = $('#selectPathway').val();
	
    $.ajax({
          type: "POST",
          data: {
				pathway_id: pathway_id
		  },
          url: "/pathways/badges/json/",
          error: function(request, textStatus, e) {
				
		  },
			
		  success: function(data, textStatus, request) {
				var badgeList = data.data;
				var length = badgeList.length;
				var pageHTML = '';
	
			
				$('.page2').html('');
				
				for(i=0;i<length;++i) {
					badge = badgeList[i];
					pageHTML+="<div class='pbadge'><a href='javascript:void(0)' onclick='showBadgeDetail(\""+badge.id+"\")'><img src='"+badge.image_url+"' style='width:100%;height:100%;'/></a><br/>";
					pageHTML+="<span>"+badge.name+"</span></div>";
					
				}
				
				
				$('#pathwayBadges'+pathway_id).html(pageHTML);
			
				
		  }
			
        });
   
}
