var config = require('./config')

CAMERA_CONFIG = config.sensor.camera
AUDIO_CONFIG = config.sensor.audio
IMAGE_FILE = config.image


function checkForMotion(history, threshold, sample_size) {
  for (var i = 0, len = history.length - sample_size; i < len; ++i) {
      var motionRate = 0;
      for(var s = 0; s < sample_size; ++s) {
        if(history[i + s]) {
            ++motionRate;
        }
      }
      if(motionRate >= threshold) {
        return true;
      }
  }
  return false;
}

module.exports = {
  parseCameraData: function(data) {
    try {
      json = JSON.parse(data);
      var result = {
        has_motion: json['motion_trigger'], // checkForMotion(json.motion_history, CAMERA_CONFIG.threshold, CAMERA_CONFIG.sample_size),
      }
      return result;
    } catch(e) {
      return -1;
    }

  },
  parseAudioData: function(data) {
    try {
      json = JSON.parse(data);
      var result = {
        has_motion: json['audio_trigger'], // checkForMotion(json.audio_history, AUDIO_CONFIG.threshold, AUDIO_CONFIG.sample_size),
      }
      return result;
    } catch(e) {
      return -1;
    }
  }
}
