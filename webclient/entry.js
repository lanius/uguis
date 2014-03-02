;(function (exports){
  'use strict';

  var EntryItem = Backbone.Model.extend({
    initialize: function () {
      var id = this.get('id');
      this.set('likeUrl', this.buildUrl(id, 'like'));
      this.set('dislikeUrl', this.buildUrl(id, 'dislike'));
      this.set('readUrl', this.buildUrl(id, 'read'));

      this.on('change', this.onChanged);
    },
    buildUrl: function (id, path) {
      return '/entries/' + id + '/' + path;
    },
    onChanged: function () {
      this.save(this.changedAttributes(), {patch: true});
    },
    toggle: function (attr) {
      this.set(attr, !this.get(attr));
    }
  });

  var EntryItemView = Backbone.Epoxy.View.extend({
    el: $('#entry-item-template').html(),
    bindings: {
      '.entry-item-feed': 'text: feed',
      '.entry-item-date': 'text: created_date',
      '.entry-item-like a': 'like: is_liked, attr:{href: likeUrl}',
      '.entry-item-dislike a': 'dislike: is_disliked, attr:{href: dislikeUrl}',
      '.entry-item-link a': 'text: title, attr:{href: url}',
      '.entry-item-readmark a': 'attr:{href: readUrl}'
    },
    bindingHandlers: {
      like: function ($el, isLiked) {
        $el.text(isLiked ? 'liked' : 'like');
      },
      dislike: function ($el, isDisliked) {
        $el.text(isDisliked ? 'disliked' : 'dislike');
      }
    },
    events: {
      'click .entry-item-like a': 'onLikeClicked',
      'click .entry-item-dislike a': 'onDislikeClicked',
      'click .entry-item-link a': 'onLinkClicked',
      'click .entry-item-readmark a': 'onReadmarkClicked'
    },
    onLikeClicked: function (e) {
      e.preventDefault();
      this.model.toggle('is_liked');
    },
    onDislikeClicked: function (e) {
      e.preventDefault();
      this.model.toggle('is_disliked');
    },
    onLinkClicked: function (e) {
      e.preventDefault();
      this.model.set('is_liked', true);
      window.open(this.model.get('url'));
    },
    onReadmarkClicked: function (e) {
      e.preventDefault();
      this.publish('entry.item.read', this.model);
    }
  });

  var EntryList = Backbone.Collection.extend({
      model: EntryItem,
      view: EntryItemView,
      url: '/entries/',
      markToReadUntil: function (frontier) {
        var index = this.indexOf(frontier);
        var entries = this.slice(0, index + 1);
        var idList = entries.map(function (e) { return e.get('id'); });
        $.post('/entries/read', {id_list: JSON.stringify(idList)});
      },
      removeUntil: function (frontier) {
        var index = this.indexOf(frontier);
        var entries = this.slice(0, index + 1);
        this.remove(entries);
      }
  });

  var EntryListView = Backbone.Epoxy.View.extend({
    fetching: false,
    closed: false,

    initialize: function(options) {
      this.type = options.type;
      this.fetchParams = options.fetchParams || {};
      this.collection = options.collection;

      this.subscribe('entry.list.open.' + this.type, this.open);
      this.subscribe('main.close', this.close);
      this.subscribe('entry.list.reset', this.reset);
      this.subscribe('entry.item.read', this.markToRead);

      this.listenToScroll();
    },
    setFetchParams: function (params) {
      _.extend(this.fetchParams, params);
    },
    open: function (params) {
      this.closed = false;
      this.$el.show();
      $('html').scrollTop(0);

      this.setFetchParams(params);

      if (this.collection.isEmpty()) {
        this.fill();
      }
    },
    close: function () {
      this.closed = true;
      this.$el.hide();
    },
    reset: function () {
      this.collection.reset();
    },
    markToRead: function (frontierModel) {
      if (this.closed) {
        return;
      }

      var collection = this.collection;
      collection.markToReadUntil(frontierModel);
      collection.removeUntil(frontierModel);
      $('html').animate({scrollTop: 0});

      if (collection.length < this.fetchParams.count) {
        this.fill(); // remaining entries are too little
      }
    },
    fill: function () {
      if (this.closed) {
        return;
      }
      if (this.fetching) {
        return;
      }

      this.fetching = true;

      var params = _.clone(this.fetchParams);
      params.offset = this.collection.length;

      var view = this;
      this.collection.fetch({
        remove: false, // append mode
        data: params,
        success: function () {
          view.fetching = false;
        },
        error: function () {
          view.fetching = false;
          //view.fill(); // retry
        }
      });
    },
    listenToScroll: function () {
      // note: this method bind onScroll event of document object to view,
      // so care not to leak memory when attempt to remove this view.
      var view = this;
      $(document).on('scroll', function () {
        if ((view.getScrolledHeight() / view.getDisplayHeight()) < 0.8) {
          return;
        }
        view.fill();
      });
    },
    getDisplayHeight: function () {
      return $(document).height();
    },
    getScrolledHeight: function () {
      return $(window).scrollTop() + $(window).height();
    }
  });

  exports.Entry = {
    EntryItem: EntryItem,
    EntryItemView: EntryItemView,
    EntryList: EntryList,
    EntryListView: EntryListView,

    initialize: function () {
      new EntryListView({
        el: '#entry-list-default',
        type: 'default',
        fetchParams: {count: 30, priority: 5, order: 'desc'},
        collection: new EntryList()
      });

      new EntryListView({
        el: '#entry-list-top',
        type: 'top',
        fetchParams: {count: 30, priority: 5, order: 'desc'},
        collection: new EntryList()
      });

      new EntryListView({
        el: '#entry-list-all',
        type: 'all',
        fetchParams: {count: 30, priority: 0, order: 'asc'},
        collection: new EntryList()
      });
    }
  };

}(window));
