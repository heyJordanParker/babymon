var app = require('express');
Stream = require('node-rtsp-stream');

var router = app.Router();

var STREAM_PORT = 8554;
var WEBSOCKET_PORT = 8084;
var STREAM_MAGIC_BYTES = 'jsmp';

var width = 320,
	height = 240;
  
// HTTP Server to accept incomming MPEG Stream
var streamServer = require('http').createServer( function(request, response) {
	var params = request.url.substr(1).split('/');

	response.connection.setTimeout(0);

	width = (params[1] || 320)|0;
	height = (params[2] || 240)|0;

	console.log(
		'Stream Connected: ' + request.socket.remoteAddress +
		':' + request.socket.remotePort + ' size: ' + width + 'x' + height
	);
	request.on('data', function(data){
		socketServer.broadcast(data, {binary:true});
	});
}).listen(STREAM_PORT);


/* GET home page. */
router.get('/', function(req, res) {
    res.render('index', { title: 'Babymon' });
});

module.exports = router;
