(function() {

  var $ = jQuery;
  
  if (!window.OCS) window.OCS       = {};
  if (!OCS.utils) OCS.utils         = {};
  if (!OCS.config) OCS.config       = {};
  if (!OCS.app) OCS.app             = {};
  if (!OCS.templates) OCS.templates = {};
  if (!OCS.model) OCS.model         = {};
  if (!OCS.view) OCS.view           = {};
  if (!OCS.controller) OCS.controller = {};
  
  OCS.init = function(options) {
    var defaults = {
      network     : '',
      session     : '',
      api         : '0.1',
      urls        : {
        base      : 'http://api.opencoursesearch.org',
        course    : 'course',
        session   : 'session',
        network   : 'network',
      },
      callbacks   : {
        search    : $.noop,
      }
    };
    OCS.options           = _.extend({}, defaults, options);
    OCS.options.callbacks = _.extend({}, defaults.callbacks, options.callbacks);
    
    OCS.app.results = new OCS.model.Results();
    
    this.utils.init_vs();
    this.utils.load_session_data();

    OCS.app.controller = new OCS.controller;
    Backbone.history.start();
    
    $(window).trigger('hashchange');
    
    return this;
  };
  
})();

OCS.utils.init_vs = function() {
  VS.init({
    container : $('.visual_search'),
    query     : '',
    facetTutor : false,
    callbacks : {
      search : function(query) {
        OCS.utils.search(query);
      },
      
      // These are the categories that will be autocompleted in an empty input.
      facetMatches : function() {
        facets = [ 'professor', 'status' ];
        facets.push.apply(facets, OCS.utils.all_facets() || []);
        return facets;
      },
      
      // These are the values that match specific categories, autocompleted
      // in a category's input field.
      valueMatches : function(category) {
        switch (category) {
        case 'level':
          return OCS.config.facets.level || [];
        case 'college':
          return OCS.config.facets.college || [];
        case 'subject':
          return OCS.config.facets.subject || [];
        case 'status':
          return [
            { value: 'open', label: 'Open' },
            { value: 'wait-list', label: 'Wait List' },
            { value: 'closed', label: 'Closed' }
          ];
        }
      }
    }
  });
}

OCS.utils.load_session_data = function() {
  var data = {
    network : OCS.options.network,
    session : OCS.options.session,
  }
  $.ajax(OCS.utils.get_api_url('session'), {
    dataType : "jsonp",
    data     : data,
    success  : function(data) {
      OCS.utils.add_facet({
        category : 'level', 
        choices  : data.levels
      });
      OCS.utils.add_facet({
        category : 'college', 
        choices  : data.colleges
      });
      OCS.utils.add_facet({
        category : 'subject', 
        choices  : data.subjects
      });
    },
  });
};

// Performs a query
OCS.utils.search = function(query, page) {
  query = query || '';
  page = page || 1;
  data = {
    network : OCS.options.network,
    session : OCS.options.session,
    query   : query,
    page    : page,
  };
  if (page > 1)
    OCS.app.controller.saveLocation("/search/" + encodeURIComponent(query) + "/p" + page);
  else
    OCS.app.controller.saveLocation("/search/" + encodeURIComponent(query));
  $.ajax(OCS.utils.get_api_url('course'), {
    dataType : "jsonp",
    data     : data,
    success  : function(response) {
      var results = new OCS.model.Results(response.results);
      var resultsSummary = new OCS.model.SearchResultSummary({
        offset : response.offset,
        page   : response.page,
        total  : response.total,
        num    : response.num,
        more   : response.more,
        results_per_page : response.results_per_page
      });
      if (OCS.app.resultsView == undefined) {
        OCS.app.resultsView = new OCS.view.Results({
          collection : results,
          summary : resultsSummary,
          el : $('#results')
        });
        OCS.app.resultsView.render();
      }
      else {
        OCS.app.resultsView.collection = results;
        OCS.app.resultsView.summary = resultsSummary;
        OCS.app.resultsView.render();
      }
    }
  });
};

OCS.utils.get_api_url = function(method) {
  return OCS.options.urls.base + "/" + OCS.options.api + "/" + OCS.options.urls[method];
};

OCS.utils.add_facet = function(options) {
  options = options || {};
  
  // Don't add facet if no options available
  if (options.choices.length > 0) {
    // Set defaults
    if (!OCS.config.facets) OCS.config.facets = {};
    if (!OCS.config.facets[options.category]) OCS.config.facets[options.category] = [];
    
    // Remove choices that have identical names (Some schools have both undergrad and
    // graduate version of a subject with the same name).
    var choices = _.map(options.choices, function(choice) {
      return choice.name;
    });
    var uniq_choices = _.map(_.uniq(choices), function(choice) {
      return {value: choice, label: choice} 
    });
    OCS.config.facets[options.category] = uniq_choices;
  }
};

// Returns a list of all facets available for this search
OCS.utils.all_facets = function() {
  var keys = [];
  for (var i in OCS.config.facets)
    keys.push(i);
    //keys.push(OCS.utils.titleize(i));
  return keys;
};

// Turns "title" into "Title"
OCS.utils.titleize = function(str) {
  titleized = "";
  _.each(str, function(letter) {
    if (titleized.length == 0)
      titleized += letter.toUpperCase();
    else
      titleized += letter;
  });
  return titleized;
};

OCS.model.SearchResult = Backbone.Model.extend({
  initialize : function() {
    //
  }
});

OCS.model.SearchResultSummary = Backbone.Model.extend({
  initialize : function() {
    //
  }
});

OCS.model.Results = Backbone.Collection.extend({
  model : OCS.model.SearchResult
});

OCS.controller = Backbone.Controller.extend({
  routes : {
    //"":                      "search", // #/search
    "/search/":               "search", // #/search
    "/search/:query":         "search", // #/search/biology
    "/search/:query/p:page":  "search", // #/search/biology/p4
  },
  
  search: function(query, page) {
    query = query || "";
    // you must be doing something wrong here - should only have to call it once
    var query = decodeURIComponent(decodeURIComponent(query));
    VS.app.searchBox.setQuery(query);
    OCS.utils.search(query, page);
  }
});

// An individual result in the result listing
OCS.view.Result = Backbone.View.extend({
  initialize : function() {
    
  },
  template : JST['search_result'],
  
  tagName: "div",
  className: "result clearfix",
  
  events : {
    "click .top": "expandResult"
  },
  
  render: function() {
    $(this.el).html(JST['search_result'](this.model.toJSON() ));
    return this;
  },
  
  expandResult: function(event) {
    $(event.target).next().toggleClass('inactive');
    $(event.target).parent().toggleClass('expanded');
  }
  
});

// A collection of Result views
OCS.view.Results = Backbone.View.extend({
  initialize : function() {
    var that = this;
    this._resultViews = [];
    
    this.summary = this.options.summary;
    this.render();
    this.collection.bind("refresh", function() {that.render()});
    _.bindAll(this, "render");
  },
  
  events : {
    "click .more-results": "nextPage",
  },
  
  render : function() {
    var that = this;
    $('.landing').fadeOut('slow', function() {
      $(that).remove();
      that.updateViews();
      $(that.el).empty();
      $(that.el).append(JST['results_summary'](that.summary.toJSON() ));
      _(that._resultViews).each(function(dv) {
        $(that.el).append(dv.render().el);
      });
      if (that.summary.attributes.more) {
        $(that.el).append(JST['more_results'](that.summary.toJSON() ));
      }
    });
  },
  
  updateViews: function() {
    that = this;
    that._resultViews = [];
    this.collection.each(function(result) {
      that._resultViews.push(new OCS.view.Result({
        model : result,
        tagName : 'div'
      }));
    });
  },
  
  nextPage : function() {
    //OCS.app.resultsView.collection.remove();
    OCS.app.resultsView.el.empty();
    
    console.log('next page clicked');
    var page = OCS.app.resultsView.summary.attributes.page + 1;
    OCS.utils.search(VS.app.searchBox.getQuery(), page);
  }
});



window.JST = window.JST || {};

window.JST['results_summary'] = _.template('<div class="results_summary">\
  <% if (offset + num <= total) { %>\
  <span class="page">Showing <%= offset + 1 %> - <%= offset + num %> of <%= total %> results</span>\
  <% } else { %>\
  <span class="page">Showing all <%= num %> results</span>\
  <% } %>\
</div>');
window.JST['more_results'] = _.template('<div class="more-results">More</div>');

window.JST['search_result'] = _.template('\
  <div class="top clearfix result-<%= id %> status-<%= status.replace(/[^-a-zA-Z0-9,&\s]+/ig, "").replace(/\\s/gi, "-").toLowerCase() %>">\
    <div class="names">\
      <p class="course_name"><%= name %></p>\
      <% if (classification.college) { %>\
        <p class="college_name"><%= classification.college.name %></p>\
      <% } %>\
      <p class="classification_name"><%= classification.name %></p>\
    </div>\
    <div class="meta">\
      <p class="classfication_code"><%= classification.code %>-<%= number %></p>\
      <p class="level_name"><%= level %></p>\
      <p class="grading"><%= grading %></p>\
    </div>\
  </div>\
  <div class="extra inactive">\
    <% if(description) { %>\
      <div class="description">\
        <%= description %>\
      </div>\
    <% } %>\
    <div class="sections">\
      <div class="section column_heads">\
        <% if (available_stats["number"]) { %><span class="number">class #</span><% } %>\
        <span class="meets">\
          <% if (available_stats["meets.day"]) { %><span class="day">days</span><% } %>\
          <% if (available_stats["meets.start"]) { %><span class="time">times</span><% } %>\
          <% if (available_stats["meets.location"]) { %><span class="location">location</span><% } %>\
        </span>\
        <% if (available_stats["prof"]) { %><span class="prof">professor</span><% } %>\
        <% if (available_stats["units"]) { %><span class="units">credits</span><% } %>\
        <% if (available_stats["component"]) { %><span class="component">component</span><% } %>\
        <% if (available_stats["status.label"]) { %><span class="status">status</span><% } %>\
        <% if (available_stats["status.seats"]) { %><span class="seats">seats</span><% } %>\
        <% if (available_stats["status.waitlist"]) { %><span class="waitlist">waitlist</span><% } %>\
        <% if (available_stats["name"]) { %><span class="name">name</span><% } %>\
        <span class="percentage"></span>\
      </div>\
    <% for (var section_index = 0; section_index < sections.length; section_index++){ %>\
      <% var sec = sections[section_index]; %>\
      <div class="section <%= ["even", "odd"][section_index % 2] %> status-<%= sec.status.label.replace(/[^-a-zA-Z0-9,&\s]+/ig, "").replace(/\\s/gi, "-").toLowerCase() %> clearfix">\
        <% if (available_stats["number"]) { %><span class="number"><%= sec.number %></span><% } %>\
        <span class="meets">\
        <% for (var meeting_index = 0; meeting_index < sec.meets.length; meeting_index++){ %>\
          <% var meet = sec.meets[meeting_index]; %>\
          <span class="day"><%= meet.day %></span>\
          <span class="time"><% if (meet.start && meet.end){ %><%= meet.start %> - <%= meet.end %><% } %></span>\
          <% if (available_stats["meets.location"] || available_stats["meets.room"]) { %><span class="location"><%= meet.location %> <%= meet.room %></span><% } %>\
        <% } %>\
        </span>\
        <% if (available_stats["prof"]) { %><span class="prof"><%= sec.prof %></span><% } %>\
        <% if (available_stats["units"]) { %><span class="units"><%= sec.units %> unit<%= sec.units == "1" ? "" : "s" %></span><% } %>\
        <% if (available_stats["component"]) { %><span class="component"><%= sec.component %></span><% } %>\
        <% if (available_stats["status.label"]) { %><span class="status"><%= sec.status.label %></span><% } %>\
        <% if (available_stats["name"]) { %><span class="name"><%= sec.name %></span><% } %>\
        \
        <% if (available_stats["status.seats"] && sec.status.seats != null) { %><span class="seats">\
          <%= sec.status.seats.taken %>\
          <% if (sec.status.seats.total) { %> / <%= sec.status.seats.total %> taken<% } %>\
        </span><% } %>\
        \
        <% if (available_stats["status.waitlist"] && sec.status.waitlist != null) { %><span class="waitlist">\
          <%= sec.status.waitlist.taken %> on waitlist\
        </span><% } %>\
        \
        <% if (available_stats["notes"]) { %><div class="notes"><%= sec.notes %></div><% } %>\
      </div>\
    <% } %>\
    </div>\
  </div>');

