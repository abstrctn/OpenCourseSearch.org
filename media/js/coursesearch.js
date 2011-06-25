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
    //new Workspace();
    
    
    $(window).trigger('hashchange');
    
    return this;
  };
  
})();

OCS.utils.init_vs = function() {
  VS.init({
    container : $('.visual_search'),
    autocompleteTutor : true,
    query     : '',
    facetTutor : true,
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
  data = {
    network : OCS.options.network,
    session : OCS.options.session,
    query   : query,
  };
  OCS.app.controller.saveLocation("search/" + encodeURIComponent(query));
  $.ajax(OCS.utils.get_api_url('course'), {
    dataType : "jsonp",
    data     : data,
    success  : function(response) {
      var results = new OCS.model.Results(response.results);
      var resultsView = new OCS.view.Results({
        collection: results,
        el: $('#results')
      });
      resultsView.render();
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
    
    _.each(options.choices, function(choice) {
      OCS.config.facets[options.category].push({
        value : choice.name,
        lavel : choice.name
      });
    });
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
  },
  render : function() {
    alert('rendering');
    $(this.el).html(JST['search_result']( this.model.toJSON() ));
  }
});

OCS.model.Results = Backbone.Collection.extend({
  model : OCS.model.SearchResult
});

OCS.controller = Backbone.Controller.extend({
  routes : {
    "":                      "search", // #search
    "search/":               "search", // #search
    "search/:query":         "search", // #search/biology
    "search/:query/p:page":  "search", // #search/biology/p4
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
    
    this.collection.each(function(result) {
      that._resultViews.push(new OCS.view.Result({
        model : result,
        tagName : 'div'
      }));
    });
  },
  
  render : function() {
    var that = this;
    $(this.el).empty();
    _(this._resultViews).each(function(dv) {
      $(that.el).append(dv.render().el);
    });
  },
  
  add: function(result) {
    var result_view = new OCS.view.SearchResult({
      model: result
    });
    
    this._result_views[result.get('id')] = result_view;
    result_view.render();
  }
});



window.JST = window.JST || {};

window.JST['search_result'] = _.template('<div class="result clearfix result-<%= id %>">\
        <div class="top clearfix">\
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
              <span class="number">class #</span>\
              <span class="meets"><span class="meet">\
                <span class="day">days</span>\
                <span class="time">times</span>\
                <span class="location">location</span>\
              </span></span>\
              <span class="prof">professor</span>\
              <span class="units">credits</span>\
              <span class="status">status</span>\
              <span class="name">name</span>\
              <span class="percentage"></span>\
            </div>\
          <% for (var section_index = 0; section_index < sections.length; section_index++){ %>\
            <% var sec = sections[section_index]; %>\
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
              <div class="notes"><%= sec.notes %></div>\
            </div>\
            <% if (sec.notes) { %>\
            <% } %>\
          <% } %>\
          </div>\
        </div>\
      </div>');

