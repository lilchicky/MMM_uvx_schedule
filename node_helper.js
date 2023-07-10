const NodeHelper = require("node_helper");
var fs = require("fs");

module.exports = NodeHelper.create({
    start: function() {
        
    },

    socketNotificationRecieved: function(notification) {
        if (notification === "START") {
            this.getSchedules();
        }
    },

    getSchedules: function() {
        var scheduleList = {};

        var test_text = fs.readFileSync("./test_text.txt", "utf-8");
        var textByLine = test_text.split(",");

        scheduleList.week_orem = textByLine;

        this.sendSocketNotification("SCHEDULES", scheduleList);
    }
})