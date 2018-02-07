
function initializeEditor(div_id,theme_name,language_mode) {
    var editor = ace.edit(div_id);
    editor.setShowPrintMargin(false);
    theme_name = theme_name?theme_name:"monokai"
    editor.setTheme("ace/theme/"+theme_name);
    language_mode = language_mode?language_mode:"python"
    editor.session.setMode("ace/mode/"+language_mode);
    console.log("OK SETUP EDITOR!!!",theme_name,language_mode)

    return editor
}
var editor;
$(function(){
    editor = initializeEditor('editor');
    // initializeEditor('editor-interactive');
});