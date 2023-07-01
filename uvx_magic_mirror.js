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
  
      // Schedule update timer.
      setInterval(() => {
        this.updateDom(this.config.fadeSpeed);
      }, this.config.updateInterval);
    },

    updateDisplay: function() {
      const stopTimes = [
        "0434",
        ["0504",
        "0534"],
        ["0604",
        "0634",
        "0649"],
        ["0704",
        "0716",
        "0722",
        "0728",
        "0734",
        "0740",
        "0746",
        "0752",
        "0758"],
        ["0804",
        "0810",
        "0816",
        "0822",
        "0828",
        "0834",
        "0840",
        "0846",
        "0852",
        "0858"],
        ["0904",
        "0910",
        "0916",
        "0922",
        "0928",
        "0934",
        "0940",
        "0946",
        "0952",
        "0958"],
        ["1004",
        "1010",
        "1016",
        "1022",
        "1032",
        "1042",
        "1052"],
        ["1102",
        "1112",
        "1122",
        "1132",
        "1142",
        "1152"],
        ["1202",
        "1212",
        "1222",
        "1232",
        "1242",
        "1252"],
        ["1302",
        "1312",
        "1322",
        "1332",
        "1342",
        "1352"],
        ["1402",
        "1412",
        "1422",
        "1432",
        "1442",
        "1449",
        "1455",
        "1401"],
        ["1507",
        "1513",
        "1519",
        "1525",
        "1531",
        "1537",
        "1543",
        "1549",
        "1555"],
        ["1601",
        "1607",
        "1613",
        "1619",
        "1625",
        "1631",
        "1637",
        "1643",
        "1649",
        "1655"],
        ["1701",
        "1707",
        "1713",
        "1719",
        "1725",
        "1731",
        "1737",
        "1743",
        "1752"],
        ["1802",
        "1812",
        "1822",
        "1832",
        "1842",
        "1852"],
        ["1902",
        "1912",
        "1922",
        "1932",
        "1942",
        "1952"],
        ["2002",
        "2012",
        "2022",
        "2032",
        "2042",
        "2054"],
        ["2109",
        "2124",
        "2139",
        "2154"],
        ["2209",
        "2224",
        "2239",
        "2259"],
        ["2319",
        "2349",
        "2319",
        "2349"]
      ];

      return "\nRandom Time: " + this.displaySchedule(timeValue);
    },

    displaySchedule: function(timeIn) {
      //get current time values
      const hour = moment().hour();
      const minutes = moment().minute();

      for (let x = 0; x < timeIn.length; x++) {
        let hourOne = timeIn[x][0].charAt(0);
        let hourTwo = timeIn[x][0].charAt(1);
        numericalHour = parseInt(("" + hourOne + hourTwo));
        if (numericalHour === hour) {
          for (let y = 0; y < timeIn[x].length; y++) {
            let minuteOne = timeIn[x][y].charAt(2);
            let minuteTwo = timeIn[x][y].charAt(3);
            numericalMinute = parseInt(("" + minuteOne + minuteTwo));
            if (minutes < numericalMinute && y < timeIn[x].length) {
              var nextScheduleMinutes = "" + minuteOne + "" + minuteTwo;
              var nextScheduleHours = "" + hourOne + "" + hourTwo;
              break;
            }
            else if (y >= timeIn[x].length && x < timeIn.length) {
              let minuteOne = timeIn[x+1][0].charAt(2);
              let minuteTwo = timeIn[x+1][0].charAt(3);
              var nextScheduleMinutes = "" + minuteOne + "" + minuteTwo;
              let hourOne = timeIn[x+1][0].charAt(0);
              let hourTwo = timeIn[x+1][0].charAt(1);
              var nextScheduleHours = "" + hourOne + "" + hourTwo;
              break;
            }
            else if (y >= timeIn[x].length && x >= timeIn.length) {
              let minuteOne = timeIn[0][0].charAt(2);
              let minuteTwo = timeIn[0][0].charAt(3);
              var nextScheduleMinutes = "" + minuteOne + "" + minuteTwo;
              let hourOne = timeIn[0][0].charAt(0);
              let hourTwo = timeIn[0][0].charAt(1);
              var nextScheduleHours = "" + hourOne + "" + hourTwo;
            }
          }
        }
      }

      return nextScheduleHours + ":" + nextScheduleMinutes;
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