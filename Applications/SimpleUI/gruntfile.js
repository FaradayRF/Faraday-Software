module.exports = function(grunt) {

  grunt.initConfig({
    htmllint: {
      all: ["templates/*.html"]
    }
    });

  grunt.loadNpmTasks('grunt-html');
  //grunt.loadNpmTasks('grunt-contrib-jshint');
  //grunt.loadNpmTasks('grunt-contrib-watch');

  grunt.registerTask('default', ['htmllint']);

};