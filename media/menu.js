function hmenuhover()
{
	if(!document.getElementById("hmenu"))
		return;
	var lis = document.getElementById("hmenu").getElementsByTagName("LI");
	for (var i=0;i<lis.length;i++)
	{
		lis[i].onmouseover=function(){this.className+=" iehover";}
		lis[i].onmouseout=function() {this.className=this.className.replace(new RegExp(" iehover\\b"), "");}
	}
}
if (window.attachEvent)
	window.attachEvent("onload", hmenuhover);
