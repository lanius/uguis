var gulp = require('gulp');


var dirs = {
  src: 'webclient',
  libs: 'building_libs', // temporary dir for concatenated bower libraries
  dest: 'uguis/static'
};

var srcnames = {

  scripts: [
    'backbone.pubsub.js',
    'menu.js',
    'feed.js',
    'entry.js',
    'bootstrap.js'
  ].map(function (name) { return dirs.src + '/' + name; }),

  styles: [
    'menu.css',
    'content.css',
    'feed.css',
    'entry.css'
  ].map(function (name) { return dirs.src + '/' + name; })

};

var destnames = {
  scriptlib: 'libs.js', // temporary file
  stylelib: 'libs.css', // temporary file
  script: 'script.js',
  style: 'style.css',
};

var deps = {
  scripts: [].concat(dirs.libs + '/' + destnames.scriptlib, srcnames.scripts),
  styles: [].concat(dirs.libs + '/' + destnames.stylelib, srcnames.styles)
};



var helpers = {

  libs: function (pattern, destname) {
    var bower = require('gulp-bower-files');
    var filter = require('gulp-filter');
    var flatten = require('gulp-flatten');
    var concat = require('gulp-concat');
    return bower()
      .pipe(filter(pattern))
      .pipe(flatten())
      .pipe(concat(destname))
      .pipe(gulp.dest(dirs.libs));
  },

  apps: function (srcfiles, destfile, minifyfunc) {
    var gutil = require('gulp-util');
    var concat = require('gulp-concat');
    return gulp.src(srcfiles)
      .pipe(gutil.env.debug ? gutil.noop(): minifyfunc())
      .pipe(concat(destfile))
      .pipe(gulp.dest(dirs.dest));
  }

};


gulp.task('scriptlib', function () {
  return helpers.libs('**/*.js', destnames.scriptlib);
});


gulp.task('stylelib', function () {
  return helpers.libs('**/*.css', destnames.stylelib);
});


gulp.task('script', ['scriptlib'], function () {
  helpers.apps(deps.scripts, destnames.script, require('gulp-uglify'));
});


gulp.task('style', ['stylelib'], function () {
  helpers.apps(deps.styles, destnames.style, require('gulp-minify-css'));
});


gulp.task('clean', function () {
  var clean = require('gulp-clean');
  gulp.src(dirs.libs)
    .pipe(clean());
  gulp.src(dirs.dest)
    .pipe(clean());
});


gulp.task('lint', function () {
  var jshint = require('gulp-jshint');
  gulp.src(srcnames.scripts)
    .pipe(jshint())
    .pipe(jshint.reporter('default'));
});


gulp.task('report', function () {
  var plato = require('gulp-plato');
  gulp.src(srcnames.scripts)
    .pipe(plato('report'));
});


gulp.task('build', ['script', 'style']);


gulp.task('default', ['build']);
