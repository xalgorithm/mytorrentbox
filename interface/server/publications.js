Meteor.publish("magnets", function () {
    return Magnets.find().fetch();
});
var magneturls = {}
Meteor.startup(function(magneturls) {
    i = 0
    while( i < 20 ) {
        var x1 = new Date();
        x1.toString('dddd, MMMM, YYYY, H:M');
        var magneturls = {
            _magid: i,
            _magdate: x1,
            _magUrl: "www.google.com",
        }
        i++;
        x1 = null;

        if(typeof Magnets.findOne() === 'undefined') {
            num = magneturls.length;
            p = 0;
            while(p < num) {
                Magnets.insert(magneturls[i]);
                p++;
            }
        }
    }

});