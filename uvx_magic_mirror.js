Module.register("uvx_magic_mirror", {
    
    defaults: {
      stopTimes: {
        "stop_1": "0434",
        "stop_2": "0504",
        "stop_3": "0534",
        "stop_4": "0604",
        "stop_5": "0634",
        "stop_6": "0649",
        "stop_7": "0704",
        "stop_8": "0716",
        "stop_9": "0722",
        "stop_10": "0728",
        "stop_11": "0734",
        "stop_12": "0740",
        "stop_13": "0746",
        "stop_14": "0752",
        "stop_15": "0758",
        "stop_16": "0804",
        "stop_17": "0810",
        "stop_18": "0816",
        "stop_19": "0822",
        "stop_20": "0828",
        "stop_21": "0834",
        "stop_22": "0840",
        "stop_23": "0846",
        "stop_24": "0852",
        "stop_25": "0858",
        "stop_26": "0904",
        "stop_27": "0910",
        "stop_28": "0916",
        "stop_29": "0922",
        "stop_30": "0928",
        "stop_31": "0934",
        "stop_32": "0940",
        "stop_33": "0946",
        "stop_34": "0952",
        "stop_35": "0958",
        "stop_36": "1004",
        "stop_37": "1010",
        "stop_38": "1016",
        "stop_39": "1022",
        "stop_40": "1032",
        "stop_41": "1042",
        "stop_42": "1052",
        "stop_43": "1102",
        "stop_44": "1112",
        "stop_45": "1122",
        "stop_46": "1132",
        "stop_47": "1142",
        "stop_48": "1152",
        "stop_49": "1202",
        "stop_50": "1212",
        "stop_51": "1222",
        "stop_52": "1232",
        "stop_53": "1242",
        "stop_54": "1252",
        "stop_55": "1302",
        "stop_56": "1312",
        "stop_57": "1322",
        "stop_58": "1332",
        "stop_59": "1342",
        "stop_60": "1352",
        "stop_61": "1402",
        "stop_62": "1412",
        "stop_63": "1422",
        "stop_64": "1432",
        "stop_65": "1442",
        "stop_66": "1449",
        "stop_67": "1455",
        "stop_68": "1401",
        "stop_69": "1507",
        "stop_70": "1513",
        "stop_71": "1519",
        "stop_72": "1525",
        "stop_73": "1531",
        "stop_74": "1537",
        "stop_75": "1543",
        "stop_76": "1549",
        "stop_77": "1555",
        "stop_78": "1601",
        "stop_79": "1607",
        "stop_80": "1613",
        "stop_81": "1619",
        "stop_82": "1625",
        "stop_83": "1631",
        "stop_84": "1637",
        "stop_85": "1643",
        "stop_86": "1649",
        "stop_87": "1655",
        "stop_88": "1701",
        "stop_89": "1707",
        "stop_90": "1713",
        "stop_91": "1719",
        "stop_92": "1725",
        "stop_93": "1731",
        "stop_94": "1737",
        "stop_95": "1743",
        "stop_96": "1752",
        "stop_97": "1802",
        "stop_98": "1812",
        "stop_99": "1822",
        "stop_100": "1832",
        "stop_101": "1842",
        "stop_102": "1852",
        "stop_103": "1902",
        "stop_104": "1912",
        "stop_105": "1922",
        "stop_106": "1932",
        "stop_107": "1942",
        "stop_108": "1952",
        "stop_109": "2002",
        "stop_110": "2012",
        "stop_111": "2022",
        "stop_112": "2032",
        "stop_113": "2042",
        "stop_114": "2054",
        "stop_115": "2109",
        "stop_116": "2124",
        "stop_117": "2139",
        "stop_118": "2154",
        "stop_119": "2209",
        "stop_120": "2224",
        "stop_121": "2239",
        "stop_122": "2259",
        "stop_123": "2319",
        "stop_124": "2349",
        "stop_125": "2319",
        "stop_126": "2349"
      },

      "updateInterval" : 1 * 60 * 1000,
      "fadeSpeed": 4000,
      "text": ""
    },

    getScripts: function() {
      return ["uvx_magic_mirror.js"];
    },

    start: async function () {
      Log.info(`Starting module: ${this.name}`);
  
      this.lastComplimentIndex = -1;
  
      if (this.config.remoteFile !== null) {
        const response = await this.loadComplimentFile();
        this.config.compliments = JSON.parse(response);
        this.updateDom();
      }
  
      // Schedule update timer.
      setInterval(() => {
        this.updateDom(this.config.fadeSpeed);
      }, this.config.updateInterval);
    },
  
    /**
     * Generate a random index for a list of compliments.
     *
     * @param {string[]} compliments Array with compliments.
     * @returns {number} a random index of given array
     */
    randomIndex: function (compliments) {
      if (compliments.length === 1) {
        return 0;
      }
  
      const generate = function () {
        return Math.floor(Math.random() * compliments.length);
      };
  
      let complimentIndex = generate();
  
      while (complimentIndex === this.lastComplimentIndex) {
        complimentIndex = generate();
      }
  
      this.lastComplimentIndex = complimentIndex;
  
      return complimentIndex;
    },
  
    /**
     * Retrieve an array of compliments for the time of the day.
     *
     * @returns {string[]} array with compliments for the time of the day.
     */
    complimentArray: function () {
      const hour = moment().hour();
      const date = moment().format("YYYY-MM-DD");
      let compliments = [];
  
      // Add time of day compliments
      if (hour >= this.config.morningStartTime && hour < this.config.morningEndTime && this.config.compliments.hasOwnProperty("morning")) {
        compliments = [...this.config.compliments.morning];
      } else if (hour >= this.config.afternoonStartTime && hour < this.config.afternoonEndTime && this.config.compliments.hasOwnProperty("afternoon")) {
        compliments = [...this.config.compliments.afternoon];
      } else if (this.config.compliments.hasOwnProperty("evening")) {
        compliments = [...this.config.compliments.evening];
      }
  
      // Add compliments based on weather
      if (this.currentWeatherType in this.config.compliments) {
        Array.prototype.push.apply(compliments, this.config.compliments[this.currentWeatherType]);
      }
  
      // Add compliments for anytime
      Array.prototype.push.apply(compliments, this.config.compliments.anytime);
  
      // Add compliments for special days
      for (let entry in this.config.compliments) {
        if (new RegExp(entry).test(date)) {
          Array.prototype.push.apply(compliments, this.config.compliments[entry]);
        }
      }
  
      return compliments;
    },
  
    /**
     * Retrieve a file from the local filesystem
     *
     * @returns {Promise} Resolved when the file is loaded
     */
    loadComplimentFile: async function () {
      const isRemote = this.config.remoteFile.indexOf("http://") === 0 || this.config.remoteFile.indexOf("https://") === 0,
        url = isRemote ? this.config.remoteFile : this.file(this.config.remoteFile);
      const response = await fetch(url);
      return await response.text();
    },
  
    /**
     * Retrieve a random compliment.
     *
     * @returns {string} a compliment
     */
    getRandomCompliment: function () {
      // get the current time of day compliments list
      const compliments = this.complimentArray();
      // variable for index to next message to display
      let index;
      // are we randomizing
      if (this.config.random) {
        // yes
        index = this.randomIndex(compliments);
      } else {
        // no, sequential
        // if doing sequential, don't fall off the end
        index = this.lastIndexUsed >= compliments.length - 1 ? 0 : ++this.lastIndexUsed;
      }
  
      return compliments[index] || "";
    },
  
    // Override dom generator.
    getDom: function () {
      const wrapper = document.createElement("div");
      wrapper.className = this.config.classes ? this.config.classes : "thin xlarge bright pre-line";
      // get the compliment text
      const complimentText = this.getRandomCompliment();
      // split it into parts on newline text
      const parts = complimentText.split("\n");
      // create a span to hold the compliment
      const compliment = document.createElement("span");
      // process all the parts of the compliment text
      for (const part of parts) {
        if (part !== "") {
          // create a text element for each part
          compliment.appendChild(document.createTextNode(part));
          // add a break
          compliment.appendChild(document.createElement("BR"));
        }
      }
      // only add compliment to wrapper if there is actual text in there
      if (compliment.children.length > 0) {
        // remove the last break
        compliment.lastElementChild.remove();
        wrapper.appendChild(compliment);
      }
      return wrapper;
    },
  
    // Override notification handler.
    notificationReceived: function (notification, payload, sender) {
      if (notification === "CURRENTWEATHER_TYPE") {
        this.currentWeatherType = payload.type;
      }
    }

  });