module.exports = function(grunt) {

  grunt.initConfig({
    htmllint: {
      all: ["templates/*.html"]
    },
    jshint: {
        // define the files to lint
    files: ["Gruntfile.js", "static/simpleui.js"],
        // configure JSHint (documented at http://www.jshint.com/docs/)
    options: {
        // more options here if you want to override JSHint defaults
        "unused": true,
        "boss": true,
        "curly": true,
        "eqeqeq": true,
        "eqnull": true,
        "expr": true,
        "immed": true,
        "noarg": true,
        "quotmark": "double",
        "smarttabs": true,
        "trailing": true,
        "undef": true,
        globals: {
            "$": false,
            jQuery: true,
            console: true,
            module: true,
            browser: true,
            }
            
        }
    }
    });

  grunt.loadNpmTasks("grunt-html");
  grunt.loadNpmTasks("grunt-contrib-jshint");
  //grunt.loadNpmTasks('grunt-contrib-watch');

  grunt.registerTask("default", ["htmllint","jshint"]);

};