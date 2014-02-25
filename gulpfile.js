var gulp = require('gulp');
var gutil = require('gulp-util');
var clean = require('gulp-clean');
var filter = require('gulp-filter');
var flatten = require('gulp-flatten');
var concat = require('gulp-concat');

var bower = require('gulp-bower-files');
var uglify = require('gulp-uglify');
var jshint = require('gulp-jshint');
var plato = require('gulp-plato');

var minifycss = require('gulp-minify-css');


var dirs = {
  src: 'src',
  libs: 'libs', // temporary dir for concatenated bower libraries
  dest: 'static'
};

var scripts = [
  'backbone.pubsub.js',
  'menu.js',
  'feed.js',
  'entry.js',
  'bootstrap.js'
].map(function (name) { return dirs.src + '/' + name; });

var styles = [
  'menu.css',
  'content.css',
  'feed.css',
  'entry.css'
].map(function (name) { return dirs.src + '/' + name; });

var filenames = {
  libscript: 'libs.js', // temporary file
  libstyle: 'libs.css', // temporary file
  script: 'script.js',
  style: 'style.css',
};

var deps = {
  scripts: [].concat(dirs.libs + '/' + filenames.libscript, scripts),
  styles: [].concat(dirs.libs + '/' + filenames.libstyle, styles)
};


gulp.task('libscript', function () {
  return bower()
    .pipe(filter('**/*.js'))
    .pipe(flatten())
    .pipe(concat(filenames.libscript))
    .pipe(gulp.dest(dirs.libs));
});


gulp.task('libstyle', function () {
  return bower()
    .pipe(filter('**/*.css'))
    .pipe(flatten())
    .pipe(concat(filenames.libstyle))
    .pipe(gulp.dest(dirs.libs));
});


gulp.task('script', ['libscript'], function () {
  gulp.src(deps.scripts)
    .pipe(gutil.env.debug ? gutil.noop(): uglify())
    .pipe(concat(filenames.script))
    .pipe(gulp.dest(dirs.dest));
});


gulp.task('style', ['libstyle'], function () {
  gulp.src(deps.styles)
    .pipe(gutil.env.debug ? gutil.noop(): minifycss())
    .pipe(concat(filenames.style))
    .pipe(gulp.dest(dirs.dest));
});


gulp.task('clean', function () {
  gulp.src(dirs.libs)
    .pipe(clean());
  gulp.src(dirs.dest)
    .pipe(clean());
});


gulp.task('lint', function () {
  gulp.src(scripts)
    .pipe(jshint())
    .pipe(jshint.reporter('default'));
});


gulp.task('report', function () {
  gulp.src(scripts)
    .pipe(plato('report'));
});


gulp.task('build', ['script', 'style']);


gulp.task('default', ['build']);
