
var counter = document.getElementById("sauron");

if (localStorage.pagecount) {
	localStorage.pagecount = Number(localStorage.pagecount) + 1;
}	else
{
	localStorage.pagecount = 1;
}

counter.write(localStorage.pagecount);