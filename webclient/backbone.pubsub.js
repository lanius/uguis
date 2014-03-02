;(function (){
  'use strict';

  var pubsub = {};
  _.extend(Backbone.View.prototype, {
    subscribe: function (eventname, func) {
      if (!pubsub[eventname]) {
        pubsub[eventname] = [];
      }
      pubsub[eventname].push([this, func]);
    },
    unsubscribe: function (eventname) {
      if (!eventname) {
        for (var evname in pubsub) {
          if (pubsub.hasOwnProperty(evname)) {
            this.unsubscribe(evname);
          }
        }
        return;
      }
      var viewAndFuncs = pubsub[eventname];
      var targets = _.filter(viewAndFuncs, function (viewAndFunc) {
        var view = viewAndFunc[0];
        if (view === this) {
          return viewAndFunc;
        }
      }, this);
      _.each(targets, function (viewAndFunc) {
        viewAndFuncs.splice(_.indexOf(viewAndFuncs, viewAndFunc), 1);
      });
    },
    publish: function (eventname) {
      if (_.isUndefined(pubsub[eventname])) {
        return;
      }
      var args = Array.prototype.slice.call(arguments, 1, arguments.length);
      _.each(pubsub[eventname], function (viewAndFunc) {
        var view = viewAndFunc[0];
        var func = viewAndFunc[1];
        func.apply(view, args);
      });
    }
  });

  Backbone.PubSub = {
    publishToViews: Backbone.View.prototype.publish
  };

}());
