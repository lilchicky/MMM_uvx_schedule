Module.register("uvx_schedule", {

    defaults: {
        text: "Hello World!"
    },

    getScripts: function() {
        return ["uvx_schedule.js"];
    },

    getDom: function() {

        var wrapper = document.createElement("div");
        wrapper.innerHTML = this.config.text;
        return wrapper;

    }

} );