if (Meteor.isClient) {
  // counter starts at 0
  BlazeLayout.setRoot('body')

  Template.mainLayout.helpers({
    counter: function () {
      return Session.get('counter');
    }
  });

  Template.mainLayout.events({
    'click button': function () {
      // increment the counter when button is clicked
      Session.set('counter', Session.get('counter') + 1);
    }
  });
}

if (Meteor.isServer) {
  Meteor.startup(function () {
    // code to run on server at startup
  });
}
