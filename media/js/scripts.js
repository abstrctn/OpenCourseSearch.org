$(document).ready(function() {  
  /* results */
  $('.result .top').live('click', function() {
    $(this).next().next().toggleClass('inactive');
    $(this).parent().toggleClass('expanded');
  });
  $('.result .top').live({
    mouseenter: function() {
      $(this).css('z-index', 20);
      $(this).parent().css('z-index', 20);
      $(this).next().css('z-index', 15);
      $(this).next().animate({'top': '+=15'}, 250, function() {});
    },
    mouseleave: function() {
      $(this).next().animate({'top': '-=15'}, 100, function() {
        $(this).prev().css('z-index', 10);
        $(this).prev().parent().css('z-index', 10);
        $(this).css('z-index', 5);
      });
    }
  });
  $('.next-page').live('click', function() {
    offset = $(this).attr('value');
    search.call(offset);
    return false;
  });
  /* end results */
  
  if ($('#textsearch').length == 1)
    interval = setInterval('search.checkTextSearch();', 500)
  
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
  
  /* session switcher */
  $('.session-switcher-current').live('click', function() {
    $(this).toggleClass('clicked');
    $(this).next().toggleClass('active');
  });
  /* end session switcher */

  // show data viz by default
  //update_stats.call();
  
  //search.activate();
  //search.call(1);
});

search = {
  network: null,
  session: null,
  url: '/api/course',
  session_data_url: '/api/session',
  search_text: 'Search (subject, professor, keyword...)',
  active: false,
  subjects_hold: null,
  text_hold: '',
  last_search: null,
  
  set_vars: function(network, session) {
    search.network = network;
    search.session = session;
  },
  activate: function(callback) {
    search.active = true;
    
    // transfer data viz selections to search selections
    if ($('.stats-selectors .colleges .option.active').length > 0) {
      id = $('.stats-selectors .colleges .option.active').attr('college_id');
      $('#college').val(id);
    }
    if ($('.stats-selectors .subjects .option.active').length > 0) {
      id = $('.stats-selectors .subjects .option.active').attr('subject_id');
      $('#subject').val(id);
    }
    
    console.log("status fade out");
    $('.stats-selectors, #results').fadeOut('slow', function() {
      $(this).hide();
      $('#results').html('');
      if(callback)
        callback();
      $('#results').fadeIn('fast', function() {
        //$('#results').fadeIn('slow');
      });
    }).slideUp('slow');
  },
  loading: function(type) {
    if (type == "start") {
      $('.page-loading').addClass('active');
    }
    if (type == "stop") {
      $('.page-loading').removeClass('active');
    }
  },
  deactivate: function() {
    search.active = false;
    console.log("Results fade out");
    $('#results').fadeOut('slow', function() {
      $(this).hide();
      $('#results').html('').show();
      
      // deactive stats selectors / clean slate
      $('.stats-selectors .option').removeClass('active').show();
      $('.stats-selectors').fadeIn('slow', function() {
        update_stats.call();
      });
    }).slideUp('slow');
  },
  checkTextSearch: function() {
    val = $('#textsearch')[0].value;
    if (val != search.text_hold && val != search.search_text) {
      if (!search.active)
        search.activate();
      search.text_hold = val;
      search.call(0);
    };
  },
  call: function(offset) {
    if (!search.active)
      return;
    text = $('#textsearch')[0].value;
    if (text == search.search_text)
      text = '';
    college = ''
    if ($('#college option:selected')[0] != undefined)
      college = $('#college option:selected')[0].value.replace('-', '');
    level = '';
    if ($('#level option:selected')[0] != undefined)
      level = $('#level option:selected')[0].value.replace('-', '');
    subject = '';
    if ($('#subject option:selected')[0] != undefined)
      subject = $('#subject option:selected')[0].value.replace('-', '');
    data = {
      'level': level,
      'college': college,
      'subject': subject,
      'query': text,
      'offset': offset,
      'network': search.network,
      'session': search.session,
    };
    if (text == '' && data['level'] == '' && data['college'] == '' && data['subject'] == '') {
      // return to data viz
      search.deactivate();
      return;
    }
    search.loading("start");
    if (search.last_search)
      search.last_search.abort();
    search.last_search = $.getJSON(search.url, data, function(response) {
      var output = _.template(search.results_template, {response : response} );
      if (response.offset == 0) {
        $("#results").html(output);
      }
      else {
        $(".next-page").remove();
        $("#results").append(output);
      }
      search.loading("stop");
    });
  },
  populate_facets: function(callback) {
    data = {
      'network': search.network,
      'session': search.session,
    };
    $.getJSON(search.session_data_url, data, function(response) {
      var output = _.template(search.facets_template, {
        levels : response.levels,
        colleges : response.colleges,
        subjects : response.subjects,
      });
      $(".searchfilters").append(output);
      var output = _.template(search.stats_selectors_template, {
        colleges : response.colleges,
        subjects : response.subjects,
      });
      $(".stats-selectors").html(output);
      if (callback)
        callback();
    });
  },
  prepare_facets: function() {
    search.subjects_hold = $('#subject option');
    $('.text-searcher').change(function() {
      search.call(0);
    });
    $('.drop-searcher').change(function() {
      if (!search.active)
        search.activate(function() {search.call(0)});
      else
        search.call(0);
    });
    $('#college').change(function() {
      id = $('#college option:selected')[0].value;
      $('#subject option').remove();
      $('#subject').append(search.subjects_hold);
      $('#subject > option[college!=' + id + ']').remove();
      $('#subject').prepend(search.subjects_hold[0]);
      $('#subject').val('-');
      search.call(0);
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
      search.call(0);
    });
    $('.query-remove').live('click', function() {
      $('#textsearch')[0].value = search.search_text;
      search.call(0);
      //if (val != search.text_hold && val != search.search_text) {
      //  $('#textsearch')[0].value = search.search_text;
      //  search.checkTextSearch();
      //}
    });
  },
  prepare_stats: function() {
    $('.stats-selectors .colleges .option').live('click', function() {
      act = $(this).hasClass('active');
      $('.stats-selectors .colleges .option').removeClass('active');
      $('.stats-selectors .subjects .option').removeClass('active');
      if (!act) {
        $(this).addClass('active');
        id = $(this).attr('college_id');
        $('.stats-selectors .subjects .option[college_id=' + id + ']').show();
        $('.stats-selectors .subjects .option[college_id!=' + id + ']').hide();
      } else {
        // unselecting a college - show everything
        $('.stats-selectors .subjects .option').show();
      }
      update_stats.call();
    });
    $('.stats-selectors .subjects .option').live('click', function() {
      act = $(this).hasClass('active');
      $('.stats-selectors .subjects .option').removeClass('active');
      if (!act)
        $(this).addClass('active');
      update_stats.call();
    });
    $('.stats-selectors .boxes .box').live('click', function() {
    });
  },
  result: null,
  results_template: '\
    <div class="results_container">\
    <% for (var result_index = 0; result_index < response.results.length; result_index++){ %>\
      <% var r = response.results[result_index]; %>\
      <div class="result clearfix result-<%= r.id %>">\
        <div class="top clearfix">\
          <div class="names">\
            <p class="course_name"><%= r.name %></p>\
            <% if (r.classification.college) { %>\
              <p class="college_name"><%= r.classification.college.name %></p>\
            <% } %>\
            <p class="classification_name"><%= r.classification.name %></p>\
          </div>\
          <div class="meta">\
            <p class="classfication_code"><%= r.classification.code %>-<%= r.number %></p>\
            <p class="level_name"><%= r.level %></p>\
            <p class="grading"><%= r.grading %></p>\
          </div>\
        </div>\
        <div class="top-arrow"></div>\
        <div class="extra inactive">\
          <% if(r.description) { %>\
            <div class="description">\
              <%= r.description %>\
            </div>\
          <% } %>\
          <div class="sections">\
            <div class="section column_heads">\
              <span class="number">class #</span>\
              <span class="meets"><span class="meet">\
                <span class="day">days</span>\
                <span class="time">times</span>\
                <span class="location">location</span>\
              </span></span>\
              <span class="prof">professor</span>\
              <span class="units">units/credits</span>\
              <span class="status">status</span>\
              <span class="name">name</span>\
              <span class="percentage"></span>\
            </div>\
          <% for (var section_index = 0; section_index < r.sections.length; section_index++){ %>\
            <% var sec = r.sections[section_index]; %>\
            <div class="section <%= ["even", "odd"][section_index % 2] %> status-<%= sec.status.label.replace(/[^-a-zA-Z0-9,&\s]+/ig, "").replace(/\\s/gi, "-").toLowerCase() %> clearfix">\
              <span class="number"><%= sec.number %></span>\
              <span class="meets">\
              <% for (var meeting_index = 0; meeting_index < sec.meets.length; meeting_index++){ %>\
                <% var meet = sec.meets[meeting_index]; %>\
                <div class="meet">\
                  <span class="day"><%= meet.day %>&nbsp;</span>\
                  <span class="time"><% if (meet.start && meet.end){ %><%= meet.start %> - <%= meet.end %><% } %>&nbsp;</span>\
                  <span class="location"><% if (meet.location && meet.room){ %><%= meet.location %> <%= meet.room %><% } %>&nbsp;</span>\
                </div>\
              <% } %>\
              </span>\
              <span class="prof"><%= sec.prof %>&nbsp;</span>\
              <span class="units"><%= sec.units %> unit<%= sec.units == "1" ? "" : "s" %>&nbsp;</span>\
              <span class="status"><%= sec.status.label %></span>\
              <span class="name"><%= sec.name %></span>\
              <% if (sec.status.seats) { %>\
                <span class="percentage"><%= sec.status.seats.taken %>\
                <% if (sec.status.seats.total) { %> / <%= sec.status.seats.total %><% } %>\
                 seats taken</span>\
              <% } %>\
              <% if (sec.status.label == "Wait List" && sec.status.waitlist) { %>\
                <span class="percentage"><%= sec.status.waitlist.taken %> on waitlist</span>\
              <% } %>\
            </div>\
            <% if (sec.notes) { %>\
            <div class="notes"><%= sec.notes %></div>\
            <% } %>\
          <% } %>\
          </div>\
        </div>\
      </div>\
     <% } %>\
     \
    <% if(response.more) { %>\
    <div class="next-page" href="#" value="<%= response.results_per_page + response.offset %>">\
      More\
    </div>\
    <% } else { %>\
    <div class="no-next-page">\
      No more courses\
    </div>\
    <% } %>\
  </div>',
  facets_template: '\
    <ul class="filters clearfix">\
      <% if (levels && levels.length > 1) { %>\
      <li class="fil-level">\
        <span class="remove">x</span>\
        <span class="name">Level</span>\
        <select id="level" class="drop-searcher">\
          <option value="-">All</option>\
          <% for (var index = 0; index < levels.length; index++){ %>\
          <% var l = levels[index]; %>\
          <option value="<%= l.id %>"><%= l.name %></option>\
          <% } %>\
        </select>\
      </li>\
      <% } %>\
      <% if (colleges && colleges.length > 1) { %>\
      <li class="fil-college">\
        <span class="remove">x</span>\
        <span class="name">College</span>\
        <select id="college" class="drop-searcher">\
          <option value="-">All</option>\
          <% for (var index = 0; index < colleges.length; index++){ %>\
          <% var c = colleges[index]; %>\
          <option value="<%= c.id %>"><%= c.name %></option>\
          <% } %>\
        </select>\
      </li>\
      <% } %>\
      <% if (subjects && subjects.length > 1) { %>\
      <li class="fil-subject">\
        <span class="remove">x</span>\
        <span class="name">Subject</span>\
        <select id="subject" class="drop-searcher">\
          <option value="-">All</option>\
          <% for (var index = 0; index < subjects.length; index++){ %>\
          <% var s = subjects[index]; %>\
          <option value="<%= s.id %>"<% if (s.college){ %> college="<%= s.college %>"<% } %>>\
            <%= s.name %> (<%= s.code %>)\
          </option>\
          <% } %>\
        </select>\
      </li>\
      <% } %>\
    </ul>\
  ',
  stats_selectors_template: '\
    <div class="options colleges clearfix">\
      <% for (var index = 0; index < colleges.length; index++){ %>\
        <% var c = colleges[index]; %>\
        <div class="option" college_id="<%= c.id %>">\
          <%= c.name %>\
        </div>\
      <% } %>\
    </div>\
    <div class="options subjects clearfix">\
      <% for (var index = 0; index < subjects.length; index++){ %>\
        <% var s = subjects[index]; %>\
        <div class="option" <% if (s.college){ %> college_id="<%= s.college %>"<% } %> subject_id="<%= s.id %>">\
          <p><%= s.name %></p>\
        </div>\
      <% } %>\
    </div>\
  '
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
update_stats = {
  network: null,
  session: null,
  url: '/stats/search/',
  set_vars: function(network, session) {
    update_stats.network = network;
    update_stats.session = session;
  },
  call: function() {
    $('#results').addClass('loading');
    college = $('.colleges .option.active').attr('college_id');
    if (college == undefined)
      college = '';
    subject = $('.subjects .option.active').attr('subject_id');
    if (subject == undefined)
      subject = '';
    data = {
      /*'level': $('#level option:selected')[0].value.replace('-', ''),*/
      'college': college,
      'subject': subject,
      'institution': update_stats.network,
      'session': update_stats.session
    };
    $.get(update_stats.url, data, function(result) {
      $("#results").html(result).removeClass('loading');
      // show results on enter, only if in a sub section
      if (!(data['college'] == '' && data['subject'] == '')) {
        $(window).bind('keydown', function(e) {
          code = (e.keyCode ? e.keyCode : e.which);
          if (code == 13) {
            $(window).unbind('keydown');
            if (!search.active)
              search.activate(function() {search.call()});
            else
              search.call();
          }
        });
      }
    });
  },
};