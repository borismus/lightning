Controller = function(engine) {
  this.engine = engine;
  
  this.mapping = {
    'nw': [37, 38], // nw
    'n': [38], // n
    'ne': [38, 39], // ne
    'w': [37], // w
    'e': [39], // e
    'sw': [37, 40], // sw
    's': [40], // s
    'se': [39, 40], // se

    'a': [32], // button 1
    'b': [90], // button 2
    'screen': [80], // pause
  };
};

Controller.prototype.init = function() {
  // Establish event mapping
  for (var id in this.mapping) {
    var elt = document.getElementById(id);
    var keyList = this.mapping[id];
    var keyPressed = function(keyList, engine) { return function() {
      for (var i = 0; i < keyList.length; i++) {
        engine.keyboard.simKeyDown({keyCode: keyList[i]});
      }}
    }(keyList, this.engine);
    
    var keyReleased = function(keyList, engine) { return function() {
      for (var i = 0; i < keyList.length; i++) {
        engine.keyboard.simKeyUp({keyCode: keyList[i]});
      }}
    }(keyList, this.engine);
    
    // elt.ontouchstart = function(id) { return function() { console.log(id); keyPressed(); }; }(id);
    elt.ontouchstart = keyPressed;
    elt.ontouchend = keyReleased;
  }
}

