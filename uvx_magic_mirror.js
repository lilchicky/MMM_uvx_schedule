Module.register("uvx_magic_mirror", {
    
    defaults: {
      text: "Hello World!",
    },
  
    
    getDom: function () {
      var wrapper = document.createElement("div");
      this.text=getTimesFromFile;
      wrapper.innerHTML = this.config.text;
      return wrapper;
    },

    getTimesFromFile: function() {
        const fs = require('fs');
        fs.readFile('2230_north_stops.txt', (err, input) => {
            if (err) throw err;
            return input.toString();
        })
    }

  });