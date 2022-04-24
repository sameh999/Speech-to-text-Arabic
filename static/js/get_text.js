
var submitButton = document.getElementById('submitButton');
var speechTranscript = document.getElementById('speechTranscript')

submitButton.addEventListener('click', getTextfile);

function getTextfile()
{
  $.get('../results.txt', {cache:false}, function(data) 
  {
    if (data !== " ") {
        console.log(data)
      document.write("<h1>Hello World is found</h1");
    }
    else {
        console.log("<h1> file empty </h1>")

        document.write("It's NOT found");
    } 
    setTimeout(getTextfile, 1000);
 });
} 
