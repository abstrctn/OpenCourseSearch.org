if (location.href.indexOf('http://www.opencoursesearch.org') == 0)
  window.location = 'http://nyu.opencoursesearch.org';
if (location.href.indexOf('http://opencoursesearch.org') == 0)
  window.location = 'http://nyu.opencoursesearch.org';

$(document).ready(function() {
  update.subjects_hold = $('#subject option');
  $('.searcher').change(function() {
    update.call(1);
  });
  $('#college').change(function() {
    id = $('#college option:selected')[0].value;
    $('#subject option').remove();
    $('#subject').append(update.subjects_hold);
    $('#subject > option[college!=' + id + ']').remove();
    $('#subject').prepend(update.subjects_hold[0]);
    $('#subject').val('-');
    update.call(1);
  });
  $('.next-page').live('click', function() {
    page = $(this).attr('value');
    update.call(page);
    return false;
  });
  $('ul.filters span').hover(
    function() {
      $(this).parent().addClass('remove-hover');
    },
    function() {
      $(this).parent().removeClass('remove-hover');
    }
  );
  $('ul.filters span').click(function() {
    $(this).parent().find('select').val('-');
    update.call(1);
  });
  if ($('#textsearch').length == 1)
    interval = setInterval('checkTextSearch();', 500)
  
  inbox.load();
  $("#results ul li").live('click', function() {
    id = $(this).attr('section_id');
    inbox.add(id);
  });
  $("#inbox .handle").live('click', function() {
    $("#inbox .container").toggleClass('hide');
  });
  $("#inbox ul li .remove").live('hover', function() {
    $(this).parent().toggleClass('warning');
  });
  $("#inbox ul li .remove").live('click', function() {
    id = $(this).parent().attr('section_id');
    inbox.remove(id);
  });
  $("#inbox .undo").live('click', function() {
    id = $(this).attr('section_id');
    inbox.add(id);
    return false;
  });
  $("#inbox .name").live('click', function() {
    id = $(this).parent().attr('course_id');
    // clear other filters, or we might not be able to see this class
    $("#level").val('-');
    $("#college").val('-');
    $("#subject").val('-');
    $("#textsearch").val(id);
  });

});

update = {
  url: '/do_search/',
  search_text: 'Search (subject, professor, keyword...)',
  call: function(page) {
    text = $('#textsearch')[0].value;
    if (text == update.search_text)
      text = '';
    data = {
      'level': $('#level option:selected')[0].value.replace('-', ''),
      'college': $('#college option:selected')[0].value.replace('-', ''),
      'subject': $('#subject option:selected')[0].value.replace('-', ''),
      'text': text,
      'page': page,
    };
    $.get(update.url, data, function(result) {
      if (page == 1)
        $("#results").html(result);
      else {
        $(".next-page").remove();
        $("#results").append(result);
      }
    });
  },
  subjects_hold: null,
};
inbox = {
  load: function() {
    $.ajax({
      url: '/inbox/load/',
      success: function(result) {
        $("#inbox").html(result);
      }
    });
  },
  add: function(id) {
    $.ajax({
      url: '/inbox/add/',
      data: {'id': id},
      success: function(result) {
        $("#inbox").html(result);
      }
    });
  },
  remove: function(id) {
    $.ajax({
      url: '/inbox/remove/',
      data: {'id': id},
      success: function(result) {
        $("#inbox").html(result);
      }
    });
  },
};
textHold = '';
function checkTextSearch() {
  val = $('#textsearch')[0].value;
  if (val != textHold) {
    textHold = val;
    //$('#level').change();
    update.call(1);
  };
};