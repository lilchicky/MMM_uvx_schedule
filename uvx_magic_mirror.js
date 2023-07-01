Module.register("uvx_magic_mirror", {
    
    defaults: {
      nextStop: "Hello World!"
    },

    start: function() {
        Log.log('Starting Module: ' + this.name);
        this.nextStop = "Loading...";
    },
  
    getTimesFromFile: function() {
        const fs = require('fs');
        fs.readFile('2230_north_stops.txt', (err, input) => {
            if (err) throw err;
            return input.toString();
        })
    },

    getDom: function () {
      var wrapper = document.createElement("div");
      this.nextStop=getTimesFromFile();
      wrapper.innerHTML = this.config.text;
      return wrapper;
    }

  });