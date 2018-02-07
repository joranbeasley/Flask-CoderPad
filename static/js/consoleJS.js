Sk.inputfun= function(prompt) {
    jqconsole.AbortPrompt()
    return new Promise(function(accept,reject){
        jqconsole.Prompt(false,function(qq){accept(qq);jqconsole.ResumePrompt();console.log("p result:",qq)})
    })
}



function outf(text) {
    jqconsole.Write(text)
}
function builtinRead(x) {
    console.log("READ?",x)
    if (Sk.builtinFiles === undefined || Sk.builtinFiles["files"][x] === undefined)
            throw "File not found: '" + x + "'";
    return Sk.builtinFiles["files"][x];
}
function runit(username) {
    jqconsole.Append("<div class=\"blue-text\">"+username+" is running active code ...</div>")
   var start_time = new Date()
   var prog = editor.getValue();

   // var mypre = document.getElementById("editor-output");
   // mypre.innerHTML = '';
   Sk.pre = "output";
   Sk.configure({output:outf, read:builtinRead});
   (Sk.TurtleGraphics || (Sk.TurtleGraphics = {})).target = 'mycanvas';
   var myPromise = Sk.misceval.asyncToPromise(function() {
       return Sk.importMainWithBody("<stdin>", false, prog, true);
   });
   myPromise.then(function(mod) {
       console.log('success');
       jqconsole.Append("<div class=\"blue-text\">Run Completed in "+((new Date()-start_time)/1000.0).toFixed(2)+" seconds...</div>")
   },
       function(err) {
       jqconsole.Append("<div class=\"red-text\">"+err.toString()+"</div>")
       console.log(err.toString());
   });
}
var jqconsole
$(function () {
    jqconsole = $('#console').jqconsole('METER Interview Code Pad\nPython 2.7\n', '   ');
    var startPrompt = function () {
      // Start the prompt with history enabled.
      jqconsole.Prompt(true, function (input) {
        // Output input with the class jqconsole-output.
        // jqconsole.Write(input + '\n', 'jqconsole-output');
        socket.emit('speak',{'room_details':room_details,message:input})
        // Restart the prompt.
        jqconsole.ResumePrompt();
      });
    };
    jqconsole.ResumePrompt = startPrompt
    startPrompt();

  });