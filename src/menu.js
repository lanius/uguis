;(function (exports){
  'use strict';

  var MenuRouter = Backbone.Router.extend({
    publish: Backbone.PubSub.publishToViews,
    routes: {
      '': 'openEntry',
      'entries': 'openEntry',
      'entries/': 'openEntry',
      'entries/:type': 'openEntry',
      'feeds/settings': 'openFeedSetting'
    },
    openEntry: function (type) {
      type = type || 'default';

      var query = this.getQueryString();
      var params = query ? this.parseQueryString(query) : {};

      this.publish('main.close');
      this.publish('entry.list.open.' + type, params);
    },
    openFeedSetting: function() {
      this.publish('main.close');
      this.publish('feed.setting.open');
    },
    getQueryString: function () {
      return window.location.search.substring(1);
    },
    parseQueryString: function (query) {
      var parsed = {};
      var vars = query.split('&');
      for (var i = 0; i < vars.length; i++) {
        var pair = vars[i].split('=');
        parsed[decodeURIComponent(pair[0])] = decodeURIComponent(pair[1]);
      }
      return parsed;
    }
  });

  var MenuView = Backbone.View.extend({
    el: '#menu-list',
    initialize: function (options) {
      this.router = options.router;
    },
    events: {
      'click #menu-entry-top-priority a': 'openTopPriority',
      'click #menu-entry-all a': 'openAllEntry',
      'click #menu-feed-setting a': 'openFeedSetting'
    },
    openTopPriority: function (e) {
      e.preventDefault();
      this.router.navigate('entries/top', {trigger: true});
    },
    openAllEntry: function (e) {
      e.preventDefault();
      this.router.navigate('entries/all', {trigger: true});
    },
    openFeedSetting: function (e) {
      e.preventDefault();
      this.router.navigate('feeds/settings', {trigger: true});
    }
  });

  exports.Menu = {
    MenuRouter: MenuRouter,
    MenuView: MenuView,

    initialize: function () {
      $('#menu-handle').sidr();
      new MenuView({router: new MenuRouter()});
    },

    start: function () {
      Backbone.history.start({pushState: true});
    }
  };

}(window));
