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

    start: async function() {
        Log.info('Starting Module: ' + this.name);
        this.nextStop = "Loading...";

        setInterval(() => {
          this.updateDom(this.config.fadeSpeed);
        }, this.config.updateInterval);
    },

    getTime: function () {

      let thisStopTime = [];

      stopTimes.forEach(compareTime)

      let nextStopTime = generate();

      return nextStopTime;

    },

    compareTime: function(stopTime, index) {
      const hour = moment().hour();
      const minute = moment().minute();

      let thisHour = parseInt(stopTime.splice(0,2));
      let thisMinute = partInt(stoptime.splice(2,3));

      text += index + ": " + item + "<br>";

    },

    getDom: function () {
      var wrapper = document.createElement("div");

      const stopTime = this.getTime();

      const parts = stopTime.split("\n");

		  const times = document.createElement("span");

		  for (const part of parts) {
			  if (part !== "") {

			  	times.appendChild(document.createTextNode(part));

				  times.appendChild(document.createElement("BR"));
			  }
		  }

		  if (times.children.length > 0) {

		  	times.lastElementChild.remove();
		  	wrapper.appendChild(times);
		  }
      return wrapper;
    }

  });