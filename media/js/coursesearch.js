(function() {

  var $ = jQuery;
  
  if (!window.OCS) window.OCS  = {};
  if (!OCS.utils) OCS.utils  = {};
  
  OCS.init = function(options) {
    var defaults = {
      network     : '',
      session     : '',
      session_url : '',
      callbacks   : {
        search    : $.noop,
      }
    };
    OCS.options           = _.extend({}, defaults, options);
    OCS.options.callbacks = _.extend({}, defaults.callbacks, options.callbacks);
    
    this.utils.load_session_data();
    
    return this;
  };
  
})();

OCS.utils.load_session_data = function() {
  $.getJSON(this.options.session_url, data, function(response) {
  
  });
}
