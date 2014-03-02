;(function (exports){
  'use strict';

  var FeedItem = Backbone.Model.extend({
    initialize: function () {
      this.on('change', this.onChanged);
    },
    toggle: function (attr) {
      this.set(attr, !this.get(attr));
    },
    onChanged: function () {
      this.save(this.changedAttributes(), {patch: true});
    }
  });

  var FeedItemView = Backbone.Epoxy.View.extend({
    el: $('#feed-item-template').html(),
    bindings: {
      '.feed-item-title a': 'text: title, attr:{href: url}',
      '.feed-item-priority input': 'value: priority',
      '.feed-item-disable a': 'disable: is_disabled',
    },
    bindingHandlers: {
      disable: function ($el, isDisabled) {
        $el.text(isDisabled ? 'enable' : 'disable');

        var $title = $el.parents('.feed-item').find('.feed-item-title');
        $title.css('text-decoration', isDisabled ? 'line-through' : 'none');
      }
    },
    events: {
      'change .feed-item-priority input': 'onPriorityChanged',
      'click .feed-item-disable a': 'onDisableClicked'
    },
    onPriorityChanged: function () {
      this.publish('entry.list.reset');
    },
    onDisableClicked: function (e) {
      e.preventDefault();
      this.model.toggle('is_disabled');
      this.publish('entry.list.reset');
    }
  });

  var FeedList = Backbone.Collection.extend({
      model: FeedItem,
      view: FeedItemView,
      url: '/feeds/'
  });

  var FeedListView = Backbone.Epoxy.View.extend({
    el: '#feed-list',
    initialize: function(options) {
      this.collection = options.collection;
      this.subscribe('feed.list.open', this.open);
      this.subscribe('feed.list.add', this.add);
    },
    open: function () {
      if (this.collection.isEmpty()) {
        this.fill();
      }
    },
    add: function (attrs) {
      // todo: want to suppress PATCH
      this.collection.create(attrs, {wait: true, at: 0});
    },
    fill: function () {
      this.collection.fetch({}); // todo: impl callbacks
    }
  });

  var FeedAddFormView = Backbone.View.extend({
    el: '#feed-add-form',
    events: {
      'click #feed-add': 'onAddClicked'
    },
    onAddClicked: function (e) {
      e.preventDefault();
      var input = this.$('#feed-input');
      this.publish('feed.list.add', {url: input.val()});
      input.val('');
    }
  });

  var FeedSettingView = Backbone.View.extend({
    el: '#feed-setting',
    initialize: function () {
      this.subscribe('feed.setting.open', this.open);
      this.subscribe('main.close', this.close);
    },
    open: function () {
      this.$el.show();
      $('html').scrollTop(0);

      this.publish('feed.list.open');
    },
    close: function () {
      this.$el.hide();
    }
  });

  exports.Feed = {
    FeedItem: FeedItem,
    FeedItemView: FeedItemView,
    FeedList: FeedList,
    FeedListView: FeedListView,
    FeedAddFormView: FeedAddFormView,
    FeedSettingView: FeedSettingView,

    initialize: function () {
      new FeedSettingView();
      new FeedAddFormView();
      new FeedListView({collection: new FeedList()});
    }
  };

}(window));
