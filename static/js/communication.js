var socket = io.connect('http://' + document.domain + ':' + location.port);
var room_details=null;
var users_afk={}
socket.on('message',function(txt){
    console.log("GOT MSG:",txt)
});
socket.on('user_list',function(userlist){
    editor.setValue(userlist.program_text)
    jqconsole.Append('<div class="yellow-text">There Are ('+userlist.active_users.length.toString()+') Users already here</div>')
    socket.emit('sync_request',{'room_details':room_details})
});
socket.on('user_speech',function(data){
    var msg = data.room_details.username+" says:<i><strong>"+data.message+"</strong></i>"
    jqconsole.Append('<div class="white-text">'+msg+'</div>')
})
socket.on('user_run',function(data){
    console.log("ON RUN:",data)
    runit(data['username'])
})
function find_user_element(username){
    var ele = $('.chip:contains("'+username+' assignment") > i');
    if(ele.length > 1) {
        for (var i = 0; i < ele.length; i++) {
            var elem = $(ele[i]);
            var txt = elem.parent().text();
            var needle = username+" assignment_";
            if (txt.match("^"+needle)){
                ele = elem;
                break;
            }

        }
    }
    return ele
}
socket.on("focus_update",function(data){
    console.log("FOCUS:",data)
    var msg='';

    // var ele = $('#user-'+data.user_id.toString());
    var ele = find_user_element(data.room_details.username)
    console.log("UPDT:",ele)
    if(data.action=="LOST"){
        ele.removeClass('green')
        ele.addClass('red')
        users_afk[data.room_details.username] = new Date()
        msg =  data.room_details.username+' has '+data.action+' focus@'+users_afk[data.room_details.username].toTimeString()
    }else if(data.action == "GAINED"){
        ele.addClass('green')
        ele.removeClass('red')
        var times = Math.round((new Date()-users_afk[data.room_details.username])/1000)
        var secs = times%60
        var mins = Math.floor(times/60)
        msg =  data.room_details.username+' lost focus for'
        msg += ' '+mins.toString()+"mins, "+secs.toString()+"secs"
        Materialize.toast(msg,4000)
    }

})
socket.on('user_joined',function(data){
    jqconsole.Append('<div class="teal-text lighten-2"> USER '+data.username+' has joined the room!</div>')
});
socket.on('sync_result',function(data){
    console.log("SYNCH:",data)

    var users = data['all_users']
    if (users){
        var span = $('<span>')
        for(var i=0;i<users.length;i++) {
            var color = "gray"
            var icon = "assignment_ind"
            if (users[i].online) {
                color = "green"
            } else {
                color = "gray"
            }
            if (users[i].is_AFK) {
                color = 'red';
                icon = 'assignment_late'
            }
            console.log("???")
            var id = "user-" + users[i]['id'];
            var drop_id = 'dropdown-user-' + users[i]['id']
            if ($('#' + drop_id).length) {
                // console.log("exists??")
                $('#' + drop_id + " > a").data("target", users[i])
            } else {

                var ele = $('<ul class="dropdown-content" id="' + drop_id + '">')
                ele.html($("#user-info-dropdown-template").html())
                console.log("ELE.children", ele.find('a'))
                ele.find('a').data('target', users[i])

                $("body").append(ele)
            }
            span.append('<div  class="chip user-dropdown" data-activates=\'' + drop_id + '\'>' + users[i].username + ' <i id="' + id + '" class="material-icons ' + color + '">' + icon + '</i></div>')
        }

    }
    $("#users_div").html(span)
    $(".user-dropdown").dropdown({
          inDuration: 300,
          outDuration: 225,
          constrainWidth: false, // Does not change width of dropdown to that of the activator
          hover: true, // Activate on hover
          gutter: 0, // Spacing from edge
          belowOrigin: true, // Displays dropdown below the button
          alignment: 'left', // Displays dropdown with edge aligned to the left of button
          stopPropagation: false // Stops event propagation
        });

    // editor.setValue(data.program_text)
});
socket.on('user_left',function(data){
    jqconsole.Append('<div class="red-text darken-2"> USER '+data.username+' has left the room!</div>')
});
socket.on('editor_change_event',function(data){
    if(data['room_details']['username'] == room_details.username)return;
    var current_text_lines = editor.getValue().split("\n")

    var start_line = data['start']['row']
    var end_line = data['end']['row']
    var end_line_text = current_text_lines[end_line]
    var start_line_text = current_text_lines[start_line]
    if(data['action']=="insert"){
        console.log("INSERT?")
        var line0 = data['lines'].shift();
        // if (line0 == "")line0="\n"
        var lhs = start_line_text.substring(0,data['start']['column'])

        var rhs = start_line_text.substring(data['start']['column'])
        console.log("B4:",current_text_lines,data['lines'])
        if(!data['lines'].length) {
            current_text_lines[start_line] = lhs + line0 + rhs
        }else{
            current_text_lines[start_line] = lhs + line0;
            var lineN = data['lines'].pop()
            data['lines'].push(lineN+rhs)
            if(data['lines'].length) {
                current_text_lines.splice(start_line + 1, 0,...data['lines'])
            }

        }
        // console.log("AF:",current_text_lines)
        // for(var i=1;i<data['lines'].length;i++){
        //     current_text_lines.splice(start_line+i,0,data['lines'][i])
        // }
    }else if(data['action'] == "remove"){
        var lhs = start_line_text.substring(0,data['start']['column'])
        var rhs = end_line_text.substring(data['end']['column'])
        var new_line = lhs + rhs

        current_text_lines.splice(start_line,end_line-start_line+1,new_line)
    }
    editor.setValue(current_text_lines.join("\n"))
    console.log("Update Editor:",data)

})
function socket_join_room(user_name,room_name){
    if(!room_name&&user_name.username&&user_name.room){
        room_name = user_name.room
        user_name = user_name.username
    }
    room_details = {username:user_name,room:room_name}
    socket.emit('join',room_details)
}
function socket_run(){
    socket.emit('run',room_details)

}
window.onbeforeunload = function(){socket.emit('leave',room_details)}
$(function(){
    editor.session.on('change',function (changeEvent,editor_session) {
        if (editor.curOp && editor.curOp.command.name){
           changeEvent['room_details'] = room_details
           socket.emit('on_editor_change',changeEvent)
        }
        else {
            console.log("other change, dont broadcast event!")
        }
        //
    });
    $(window).focus(function() {
        socket.emit("focus_gained",{'room_details':room_details,'time':new Date().toISOString()})
        console.log("FOCUSED",new Date())
    }).blur(function() {
        socket.emit("focus_lost",{'room_details':room_details,'time':new Date().toISOString()})
        console.log("UnFocused",new Date())
    });

});