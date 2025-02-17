// refreshIFrame
// Refresh the log monitor iframe every 2 seconds
// needs '<body onload="refreshIFrame()">'
// and '<iframe id="logmonitor" ...'

function refreshIFrame() {
	var logmonitor = document.getElementById("logmonitor");

	if (!(logmonitor === document.activeElement)) {
		logmonitor.contentWindow.location.reload();
		logmonitor.contentWindow.scrollTo(0, 999999);
	}

	var t = setTimeout(refreshIFrame, 2000);
}
