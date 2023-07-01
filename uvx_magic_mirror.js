Module.register("uvx_magic_mirror", {
    
    defaults: {
      nextStop: "Hello World!"
    },

    start: function() {
        Log.log('Starting Module: ' + this.name);
        this.nextStop = "Loading...";
    },
  
    getTimesFromFile: function() {
        const times = require('./2230_north_stops.json');
        console.log(data);
    },

    getDom: function () {
      var wrapper = document.createElement("div");
      getTimesFromFile();
      wrapper.innerHTML = this.config.text;
      return wrapper;
    }

  });