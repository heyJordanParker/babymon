var express = require('express');
var app = express();
var path = require('path');
var favicon = require('serve-favicon');
var logger = require('morgan');
var cookieParser = require('cookie-parser');
var bodyParser = require('body-parser');
var http = require('http').Server(app);
var io = require('socket.io')(http);
var watch = require('node-watch');
var fs = require('fs');
var lib = require('./lib/lib');
var path = require('path');
var config = require('./lib/config')

FILES_DIRECTORY = config.state_files.directory;
CAMERA_FILE = config.state_files.camera_file;
AUDIO_FILE = config.state_files.mic_file;
IMAGE_FILE = config.state_files.image_file;
UPDATE_SPEED = config.sensor.update_speed;

var next_update = Date.now();

// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'jade');

// uncomment after placing your favicon in /public
app.use(favicon(__dirname + '/public/favicon.ico'));
app.use(logger('dev'));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

/* GET home page. */
app.get('/', function(req, res) {
    res.render('index');
});


/// catch 404 and forwarding to error handler
app.use(function(req, res, next) {
    var err = new Error('Not Found');
    err.status = 404;
    next(err);
});

http.listen(3000, function(){
  console.log('Socket.io listening on *:3000');
});

/// error handlers

// development error handler
// will print stacktrace
// if (app.get('env') === 'development') {
//     app.use(function(err, req, res, next) {
//         res.status(err.status || 500);
//         res.render('error', {
//             message: err.message,
//             error: err
//         });
//     });
// }
//
// // production error handler
// // no stacktraces leaked to user
// app.use(function(err, req, res, next) {
//     res.status(err.status || 500);
//     res.render('error', {
//         message: err.message,
//         error: {}
//     });
// });

watch(FILES_DIRECTORY, function(file_path) {
  try {
    file_name = path.basename(file_path);

    if(file_name == CAMERA_FILE) {
      fs.readFile(file_path, 'utf8', function (err,data) {
        if (err) {
          return console.log(err);
        }
        data = lib.parseCameraData(data);
        if(data == -1) {
          return;
        }
        io.emit('camera_update', data);
      });

    } else if(file_name == AUDIO_FILE) {
      fs.readFile(file_path, 'utf8', function (err,data) {
        if (err) {
          return console.log(err);
        }
        data = lib.parseAudioData(data);
        if(data == -1) {
          return;
        }
        io.emit('audio_update', data);
      });
    } else if(file_name == IMAGE_FILE) {
      var date = new Date().getTime()
      if(date <= next_update) {
        return;
      }
      var updateTime = new Date(date + UPDATE_SPEED);
      next_update = updateTime.getTime();

      fs.createReadStream(file_path).pipe(fs.createWriteStream('./public/camera.bmp'));
      io.emit('image_update');
    } else {
      return;
    }
  }
  catch(err) {
    console.log("Parsing Exception: " + err);
  }
});

module.exports = app;
