// Handle offline caching of favorites

var SongDatabase = function() {
  
  // Create database
  var db = openDatabase('guitarunleashed', "1.0", "HTML5 Database API", 200000);
  
  // If necessary, create a table for storing song json (id, json)
  db.transaction(function(tx) {
    tx.executeSql("SELECT COUNT(*) FROM Songs", [], function(result) {
      // alert('loaded table');
    }, function(tx, error) {
      tx.executeSql("CREATE TABLE Songs (id REAL UNIQUE, json TEXT)", [], function(result) { 
        // alert('created table');
      });
    });
  });
  
  this.getSong = function(id, callback) {
    // Gets the JSON for a particular song by ID
    db.transaction(function (tx) {
      tx.executeSql("SELECT json FROM Songs WHERE id = " + id + ";", [],
        function(tx, result) {
          if (! callback) {
            // alert('Callback required for SongDatabase.getSong!');
            return;
          }
          var ret = result.rows.length ? unescape(result.rows.item(0).json) : null;
          callback(ret);
        }, 
        function(tx, error) {
          alert(error);
        }
      );
    });
  };
  
  this.addSong = function(id, json, callback) {
    // Adds the JSON for a particular song by ID
    db.transaction(function (tx) {
      tx.executeSql("INSERT INTO Songs (id, json) VALUES ("+ id +", '" + escape(json) + "')", [],
        function(result) { 
          // alert('added ' + id);
          callback();
        }, 
        function(tx, error) {
          alert(error);
        }
      );
    });
  };
  
  this.removeSong = function(id, callback) {
    // Removes a song by ID
    db.transaction(function (tx) {
      tx.executeSql("DELETE FROM Songs WHERE id = "+ id +";", [],
        function(result) { 
          // alert('removed ' + id);
          callback();
        }, 
        function(tx, error) {
          alert(error);
        }
      );
    });
  };
  
  this.getSongList = function(callback) {
    // Gets a list of all IDs
    db.transaction(function (tx) {
      tx.executeSql("SELECT id FROM Songs", [],
        function(tx, result) {
          var ids = [];
          for (var i = 0; i < result.rows.length; i++) {
            var id = result.rows.item(i).id;
            ids.push(id);
          }
          if (! callback) {
            alert('Callback required for SongDatabase.getSongList!');
          }
          callback(ids);
        },
        function(tx, error) {
          alert(error);
        });
      });
  };
  
};