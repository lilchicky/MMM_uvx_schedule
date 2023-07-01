Module.register("uvx_magic_mirror", {
    
    defaults: {

      "updateInterval" : 5000,
      "fadeSpeed": 1000,
      "text": "Start Text"
    },

    getScripts: function() {
      return ["uvx_magic_mirror.js"];
    },

    start: async function () {
      Log.info(`Starting module: ${this.name}`);
  
      this.config.text = "Loading...";

      this.lastIndex = -1;
      this.numericalHour = 0;
      this.numericalMinute = 0;
      this.nextScheduleMinutes = 0;
      this.nextScheduleHours = 0;
  
      // Schedule update timer.
      setInterval(() => {
        this.updateDom(this.config.fadeSpeed);
      }, this.config.updateInterval);
    },

    updateDisplay: function() {
      const stopTimes = [
        "04:34",
        "05:04",
        "05:34",
        "06:04",
        "06:34",
        "06:49",
        "07:04",
        "07:16",
        "07:22",
        "07:28",
        "07:34",
        "07:40",
        "07:46",
        "07:52",
        "07:58",
        "08:04",
        "08:10",
        "08:16",
        "08:22",
        "08:28",
        "08:34",
        "08:40",
        "08:46",
        "08:52",
        "08:58",
        "09:04",
        "09:10",
        "09:16",
        "09:22",
        "09:28",
        "09:34",
        "09:40",
        "09:46",
        "09:52",
        "09:58",
        "10:04",
        "10:10",
        "10:16",
        "10:22",
        "10:32",
        "10:42",
        "10:52",
        "11:02",
        "11:12",
        "11:22",
        "11:32",
        "11:42",
        "11:52",
        "12:02",
        "12:12",
        "12:22",
        "12:32",
        "12:42",
        "12:52",
        "13:02",
        "13:12",
        "13:22",
        "13:32",
        "13:42",
        "13:52",
        "14:02",
        "14:12",
        "14:22",
        "14:32",
        "14:42",
        "14:49",
        "14:55",
        "14:01",
        "15:07",
        "15:13",
        "15:19",
        "15:25",
        "15:31",
        "15:37",
        "15:43",
        "15:49",
        "15:55",
        "16:01",
        "16:07",
        "16:13",
        "16:19",
        "16:25",
        "16:31",
        "16:37",
        "16:43",
        "16:49",
        "16:55",
        "17:01",
        "17:07",
        "17:13",
        "17:19",
        "17:25",
        "17:31",
        "17:37",
        "17:43",
        "17:52",
        "18:02",
        "18:12",
        "18:22",
        "18:32",
        "18:42",
        "18:52",
        "19:02",
        "19:12",
        "19:22",
        "19:32",
        "19:42",
        "19:52",
        "20:02",
        "20:12",
        "20:22",
        "20:32",
        "20:42",
        "20:54",
        "21:09",
        "21:24",
        "21:39",
        "21:54",
        "22:09",
        "22:24",
        "22:39",
        "22:59",
        "23:19",
        "23:49",
        "23:19",
        "23:49"
    ];

      return "\nRandom Time: " + this.displaySchedule(timeValue);
    },

    displaySchedule: function(timeIn) {
      //get current time values
      const hour = moment().hour();
      const minutes = moment().minute();

      timeIn.foreach(findNextSchedule);

      //Find the hour matching current hour

      return testText;
    },

    findNextSchedule: function(time, index) {
      testText += index + ": " + time + "\n";
    },

    getDom: function() {
        const wrapper = document.createElement("div");

        const display = document.createElement("span");

        const parts = this.updateDisplay().split("\n");

        for (const part of parts) {
          if (part != "") {
            display.appendChild(document.createTextNode(part));
            display.appendChild(document.createElement("BR"));
          }
        }

        if (display.children.length > 0) {
          display.lastElementChild.remove();
          wrapper.appendChild(display);
        }

        return wrapper;
    }

  });