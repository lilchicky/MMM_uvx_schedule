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
        document.getElementById('2230_north_stops.txt').addEventListener('stops', function() {
            var fileReader = new FileReader();
            fileReader.onload=function(){
                document.getElementById('output').textContent=fileReader.result;
            }
            return fileReader.readAsText(this.files[0]);
        })
    }

  });