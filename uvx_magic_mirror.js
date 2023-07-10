Module.register("uvx_magic_mirror", {
    
    defaults: {

      "updateInterval" : 60000,
      "fadeSpeed": 0,
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

      this.testText = "";

      this.schedules = {};
      this.schedules.weekOrem = "LOADING...";
      this.sendSocketNotification('START');
  
      // Schedule update timer.
      setInterval(() => {
        this.updateDom(this.config.fadeSpeed);
      }, this.config.updateInterval);
    },

    socketNotificationReceived: function(notification, payload) {
      if (notification === "SCHEDULES") {
        this.schedules.weekOrem = payload.week_orem;
      }
    },

    getWeekTimes: function(scheduleIn, satScheduleIn) {
      let scheduleTimes = scheduleIn;
      let satScheduleTimes = satScheduleIn;

      let hour = moment().hour();
      let minutes = moment().minute();
      let day = moment().day();

      for(let x = 0; x < scheduleTimes.length; x++) {
        let times = scheduleTimes[x].split(":");

        // Same hour check as Saturday 
        // See: getSatTimes()
        if (parseInt(times[0]) === hour) {

          // If schedule minutes are greater than current minutes
          if (parseInt(times[1]) > minutes) {
            return "" + scheduleTimes[x];
          }

          // Next hour jump, same as saturday
          else if (x < scheduleTimes.length - 1 && parseInt((scheduleTimes[x + 1].split(":")[0])) !== hour) {
            return "" + scheduleTimes[x + 1];
          }

          // End of day check for midnight schedules
          else if (x >= scheduleTimes.length - 1) {
            return "" + scheduleTimes[0];
          }
        }

        // Check for unlisted schedule hours
        else if (x >= scheduleTimes.length - 1) {

          // If it is Friday morning, print the first weekday schedule
          // If it is Friday night, print the first Saturday schedule
          if (day === 5) {
            if (hour <= 4) {
              return "" + scheduleTimes[0];
            }
            else {
              return "" + satScheduleTimes[0];
            }
          }

          // For other days of the week (Mon - Thurs) just print the first schedule of 
          // the weekday array
          else {
            return "" + scheduleTimes[0];
          }
          
        }
      }

    },

    getSatTimes: function(satTimesIn) {
      let satScheduleTimes = satTimesIn;

      let hour = moment().hour();
      let minutes = moment().minute();

      // Go through Saturday schedule times
      for(let x = 0; x < satScheduleTimes.length; x++) {
        let times = satScheduleTimes[x].split(":");

        // If the current hour matches the iterated schedule hour (22:00 == 22:05)
        if (parseInt(times[0]) === hour) {

          // If the iterated schedule time is LARGER than the current time, print as the next bus
          if (parseInt(times[1]) > minutes) {
            return "" + satScheduleTimes[x];
          }

          // If we reach the end of matching hours, print the first time of the next schedule hours
          // (last stop at 22:49, time is 22:50, print out first time in 23:00)
          else if (x < satScheduleTimes.length - 1 && parseInt((satScheduleTimes[x + 1].split(":")[0])) !== hour) {
            return "" + satScheduleTimes[x + 1];
          }

          // If it is after the last Saturday stop, print out the Sunday message
          // For edge cases like if it is 00:50
          else if (x >= satScheduleTimes.length - 1) {
            return "No Service Until Monday";
          }
        }

        // For if the current hour never matches a scheduled hour
        else if (x >= satScheduleTimes.length - 1) {

          // If it is in the morning, print the first bus stop of the day
          if (hour <= 6) {
            return "" + satScheduleTimes[0];
          }

          // If it is at night, print out Sunday message
          // I don't actually think this is ever necessary, because the schedule runs to midnight
          else {
            return "No Service Until Monday";
          }
        }
      }

    },

    updateDisplay: function() {

      const weekTimesOrem = [
        "4:34",
        "5:04",
        "5:34",
        "6:04",
        "6:34",
        "6:49",
        "7:04",
        "7:16",
        "7:22",
        "7:28",
        "7:34",
        "7:40",
        "7:46",
        "7:52",
        "7:58",
        "8:04",
        "8:10",
        "8:16",
        "8:22",
        "8:28",
        "8:34",
        "8:40",
        "8:46",
        "8:52",
        "8:58",
        "9:04",
        "9:10",
        "9:16",
        "9:22",
        "9:28",
        "9:34",
        "9:40",
        "9:46",
        "9:52",
        "9:58",
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
        "15:01",
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
        "00:19",
        "00:49"
    ];
    const weekTimesProvo = [
      "4:18",
      "4:48",
      "5:18",
      "5:48",
      "6:23",
      "6:46",
      "7:06",
      "7:20",
      "7:26",
      "7:32",
      "7:38",
      "7:44",
      "7:50",
      "7:56",
      "8:02",
      "8:08",
      "8:14",
      "8:20",
      "8:26",
      "8:32",
      "8:38",
      "8:44",
      "8:50",
      "8:56",
      "9:02",
      "9:08",
      "9:14",
      "9:20",
      "9:26",
      "9:32",
      "9:38",
      "9:44",
      "9:50",
      "9:56",
      "10:02",
      "10:08",
      "10:14",
      "10:20",
      "10:26",
      "10:37",
      "10:47",
      "10:57",
      "11:07",
      "11:17",
      "11:27",
      "11:37",
      "11:47",
      "11:57",
      "12:07",
      "12:17",
      "12:27",
      "12:37",
      "12:47",
      "12:57",
      "13:07",
      "13:17",
      "13:27",
      "13:37",
      "13:47",
      "13:57",
      "14:07",
      "14:17",
      "14:28",
      "14:34",
      "14:40",
      "14:46",
      "14:52",
      "14:58",
      "15:04",
      "15:10",
      "15:16",
      "15:22",
      "15:28",
      "15:34",
      "15:40",
      "15:46",
      "15:52",
      "15:58",
      "16:04",
      "16:10",
      "16:16",
      "16:22",
      "16:28",
      "16:34",
      "16:40",
      "16:46",
      "16:52",
      "16:58",
      "17:04",
      "17:10",
      "17:16",
      "17:22",
      "17:28",
      "17:38",
      "17:48",
      "17:58",
      "18:07",
      "18:17",
      "18:27",
      "18:37",
      "18:47",
      "18:57",
      "19:07",
      "19:17",
      "19:27",
      "19:37",
      "19:47",
      "19:57",
      "20:07",
      "20:17",
      "20:27",
      "20:41",
      "20:56",
      "21:11",
      "21:28",
      "21:43",
      "21:58",
      "22:13",
      "22:28",
      "22:58",
      "23:28",
      "23:58",
      "00:28"
  ];
    const satTimesOrem = [
      "6:32",
      "7:02",
      "7:21",
      "7:36",
      "7:51",
      "8:06",
      "8:21",
      "8:36",
      "8:51",
      "9:06",
      "9:21",
      "9:36",
      "9:51",
      "10:06",
      "10:23",
      "10:38",
      "10:53",
      "11:08",
      "11:23",
      "11:38",
      "11:53",
      "12:08",
      "12:23",
      "12:38",
      "12:53",
      "13:08",
      "13:23",
      "13:38",
      "13:53",
      "14:08",
      "14:23",
      "14:38",
      "14:53",
      "15:08",
      "15:23",
      "15:38",
      "15:53",
      "16:08",
      "16:23",
      "16:38",
      "16:53",
      "17:08",
      "17:23",
      "17:38",
      "17:53",
      "18:06",
      "18:21",
      "18:36",
      "18:51",
      "19:06",
      "19:21",
      "19:36",
      "19:51",
      "20:06",
      "20:21",
      "20:36",
      "20:51",
      "21:06",
      "21:21",
      "21:36",
      "21:51",
      "22:06",
      "22:21",
      "22:36",
      "22:51",
      "23:06",
      "23:36",
      "00:08",
      "00:38"
    ];
    const satTimesProvo = [
      "5:51",
      "6:21",
      "6:51",
      "7:10",
      "7:25",
      "7:40",
      "7:55",
      "8:10",
      "8:25",
      "8:40",
      "8:55",
      "9:10",
      "9:25",
      "9:40",
      "9:55",
      "10:10",
      "10:25",
      "10:43",
      "10:58",
      "11:13",
      "11:28",
      "11:43",
      "11:58",
      "12:13",
      "12:28",
      "12:43",
      "12:58",
      "13:13",
      "13:28",
      "13:43",
      "13:58",
      "14:13",
      "14:28",
      "14:43",
      "14:58",
      "15:13",
      "15:28",
      "15:43",
      "15:58",
      "16:13",
      "16:28",
      "16:43",
      "16:58",
      "17:13",
      "17:28",
      "17:43",
      "17:58",
      "18:12",
      "18:27",
      "18:42",
      "18:57",
      "19:12",
      "19:27",
      "19:42",
      "19:57",
      "20:12",
      "20:27",
      "20:40",
      "20:55",
      "21:10",
      "21:25",
      "21:40",
      "21:55",
      "22:10",
      "22:25",
      "22:40",
      "22:55",
      "23:25",
      "23:55",
      "00:25"
    ];

      const day = moment().day();

      // If it is Sunday...
      if (day === 0) {

        // If Sunday, just say default message
        return "Next UVX Buses:\n \nTowards Orem: No Service Until Monday\nTowards Provo: No Service Until Monday\n \nPlan for a 5 minute walk,\nholidays may change service!";
      }

      // If it is Saturday...
      else if (day === 6) {
        return "Next UVX Buses:\n \nTowards Orem: " + this.getSatTimes(satTimesOrem) + "\nTowards Provo: " + this.getSatTimes(satTimesProvo) + "\n \nPlan for a 5 minute walk,\nholidays may change service!";
        
      }

      // If it is a weekday...
      else if (day !== 0 && day !== 6) {
        return "Next UVX Buses:\n \nTowards Orem: " + this.getWeekTimes(this.schedules.weekOrem, satTimesOrem) + "\nTowards Provo: " + this.getWeekTimes(this.schedules.weekOrem, satTimesProvo) + "\n \nPlan for a 5 minute walk,\nholidays may change service!";
      }

      return "Next UVX Buses:\n \nError";
    },

    getDom: function() {
        const wrapper = document.createElement("div");
        wrapper.className = "thick normal bright pre-line";

        const display = document.createElement("span");

        // Break the schedule message into parts based on the new line text
        const parts = this.updateDisplay().split("\n");

        // Actually make each part on a new line by inserting a <br>
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