/*! MatDialog.js - v1.0.0 - 27/5/2017
 * https://ujjwalguptaofficial.github.io/MatDialog/
 * Copyright (c) 2017 @Ujjwal Gupta; Licensed Apache2.0 */
var __extends = (this && this.__extends) || (function () {
    var extendStatics = Object.setPrototypeOf ||
        ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
        function (d, b) { for (var p in b) if (b.hasOwnProperty(p)) d[p] = b[p]; };
    return function (d, b) {
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
var Helper = (function () {
    function Helper() {
        this.IsDismissible = false;
        this.openModal = function (callBack, isInput) {
            this.CallBack = callBack;
            var That = this;
            $('#divMatDialog .modal').modal('open');
            $('#divMatDialog .modal').on('click', '.modal-button', function () {
                var Modal = $('#divMatDialog .modal'), DialogType = Modal.data('type'), Value = $(this).data('val');
                Modal.modal('close');
                (Value == null) ? false : Value;
                if (That.CallBack != null) {
                    if (DialogType == 'alert') {
                        That.CallBack();
                    }
                    else if (DialogType == 'confirm') {
                        That.CallBack(JSON.parse(Value));
                    }
                    else if (DialogType == 'prompt') {
                        if (JSON.parse(Value)) {
                            var InputValue;
                            if (That.Option.Input) {
                                InputValue = That.getPromptInputValue(That.Option.Input.Type);
                            }
                            else {
                                InputValue = $('#divMatDialog .modal input[type="text"]').val();
                            }
                            That.CallBack(InputValue && InputValue.length > 0 ? InputValue : null);
                        }
                        else {
                            That.CallBack(null);
                        }
                    }
                    else if (DialogType == 'create') {
                        That.CallBack(Value);
                    }
                }
            });
            $('body').on('click', '.modal-overlay', function () {
                if (That.CallBack != null && That.IsDismissible) {
                    var DialogType = $('#divMatDialog .modal').data('type');
                    if (DialogType == 'alert') {
                        That.CallBack();
                    }
                    else if (DialogType == 'confirm') {
                        That.CallBack(false);
                    }
                    else if (DialogType == 'prompt' || DialogType == 'dialog') {
                        That.CallBack(null);
                    }
                }
            });
            if (isInput) {
                $('#divMatDialog .modal .modal-content input').focus();
            }
        };
        this.closeModal = function (callBack) {
            $('#divMatDialog .modal').modal('close');
            if (callBack) {
                callBack();
            }
        };
        this.registerModal = function (config) {
            var DefaultConfig = {
                Dismissible: true,
                EndingTop: '2%',
                InDuration: 300,
                OutDuration: 200,
                Opacity: 0.5,
                StartingTop: '2%',
                OnCompleted: function () {
                    $('#divMatDialog .modal').off('click', '.modal-button');
                    $('body').off('click', '.modal-overlay');
                }
            };
            if (config) {
                this.IsDismissible = config.Dismissible == null ? false : config.Dismissible;
                $('.modal').modal({
                    dismissible: config.Dismissible != null ? config.Dismissible : DefaultConfig.Dismissible,
                    opacity: config.Opacity ? config.Opacity : DefaultConfig.Opacity,
                    inDuration: config.InDuration ? config.InDuration : DefaultConfig.InDuration,
                    outDuration: config.OutDuration ? config.OutDuration : DefaultConfig.OutDuration,
                    startingTop: config.StartingTop ? config.StartingTop : DefaultConfig.StartingTop,
                    endingTop: config.EndingTop ? config.EndingTop : DefaultConfig.EndingTop,
                    complete: DefaultConfig.OnCompleted
                });
            }
            else {
                $('.modal').modal({
                    dismissible: DefaultConfig.Dismissible,
                    opacity: DefaultConfig.Opacity,
                    inDuration: DefaultConfig.InDuration,
                    outDuration: DefaultConfig.OutDuration,
                    startingTop: DefaultConfig.StartingTop,
                    endingTop: DefaultConfig.EndingTop,
                    complete: DefaultConfig.OnCompleted
                });
            }
        };
    }
    Helper.prototype.getPromptInputValue = function (type) {
        switch (type) {
            case 'text':
            case 'date':
            case 'number':
            case 'email':
            case 'password': return $('#divMatDialog .modal input[type=' + type + ']').val();
            case 'select': return $('#divMatDialog .modal #selectMatDialog').val();
            case 'radio': return $('#divMatDialog .modal input[name="radioMatDialog"]:checked').val();
            case 'check':
            case 'checkbox':
                var Values = [];
                $('#divMatDialog .modal input[name="checkMatDialog"]:checked').each(function () {
                    Values.push($(this).val());
                });
                return Values;
            default: return $('#divMatDialog .modal input[type="text"]').val();
        }
    };
    return Helper;
}());
var MatDialogs;
(function (MatDialogs) {
    var Prompt = (function () {
        function Prompt(option) {
            this.getInnerContent = function (input) {
                var Type = (!input || !input.Type) ? 'Text' : input.Type;
                switch (Type) {
                    case 'text':
                    case 'date':
                    case 'number':
                    case 'email':
                    case 'password': return '<input type="' + input.Type + '"/>';
                    case 'select': if (input.Values && input.Values.length > 0) {
                        var Content = '<select id="selectMatDialog" class="browser-default">';
                        input.Values.forEach(function (value) {
                            Content += '<option value=' + value.Value + '>' + value.Text + '</option>';
                        });
                        Content += '</select>';
                        return Content;
                    }
                    else {
                        console.error('no values provided');
                        return '';
                    }
                    case 'radio': if (input.Values && input.Values.length > 0) {
                        var Content = "";
                        input.Values.forEach(function (value, index) {
                            Content += '<div class="margin-top-5px"><input type="radio" id=' + index + ' name="radioMatDialog" value="' + value.Value + '"/><label for=' + index + '>' + value.Text + '</label></div>';
                        });
                        return Content;
                    }
                    else {
                        console.error('no values provided');
                        return '';
                    }
                    case 'check':
                    case 'checkbox': if (input.Values && input.Values.length > 0) {
                        var Content = "";
                        input.Values.forEach(function (value, index) {
                            Content += '<div class="margin-top-5px"><input type="checkbox" id=' + index + ' name="checkMatDialog" value=' + value.Value + '><label for=' + index + '>' + value.Text + '</label></div>';
                        });
                        return Content;
                    }
                    else {
                        console.error('no values provided');
                        return '';
                    }
                    default: return '<input type="text" />';
                }
            };
            if (typeof (option) === 'object') {
                this.createCustomPrompt(option);
            }
            else {
                this.createPrompt(option);
            }
        }
        Prompt.prototype.createPrompt = function (Msg) {
            var ElementInnerHTML = '<div class="modal-header">' +
                '<span class="prompt-msg">' + Msg + '</span>' +
                '<i class="modal-button material-icons right-align header-close-icon">&#xE5CD;</i></div>' +
                '<div class="divider"></div><div class="modal-content"><input type="text" /></div>' + '<div class="divider"></div>' +
                '<div class="modal-footer"><a href="#!" data-val="false" class="modal-button btn waves-effect waves-green prompt btn-cancel">Cancel</a>' +
                '<a href="#!" data-val="true" class="modal-button btn waves-effect waves-green prompt btn-ok">Ok</a></div>';
            $('#divMatDialog .modal').data('type', 'prompt').html(ElementInnerHTML);
        };
        Prompt.prototype.createCustomPrompt = function (option) {
            if (option.ExecuteBefore) {
                option.ExecuteBefore();
            }
            var OkLabel = (option.Buttons && option.Buttons.Ok && option.Buttons.Ok.Label) ? option.Buttons.Ok.Label : 'Ok', CancelLabel = (option.Buttons && option.Buttons.Cancel && option.Buttons.Cancel.Label) ? option.Buttons.Cancel.Label : 'Cancel';
            var ElementInnerHTML = '<div class="modal-header">' +
                '<span class="prompt-msg">' + option.Text + '</span>' +
                '<i class="modal-button material-icons right-align header-close-icon">&#xE5CD;</i></div>' +
                '<div class="divider"></div><div class="modal-content">' + this.getInnerContent(option.Input) + '</div><div class="divider"></div>' +
                '<div class="modal-footer"><a href="#!" data-val="false" class="modal-button btn waves-effect waves-green prompt btn-cancel">' + CancelLabel + '</a>' +
                '<a href="#!" data-val="true" class="modal-button btn waves-effect waves-green prompt btn-ok">' + OkLabel + '</a></div>';
            $('#divMatDialog .modal').data('type', 'prompt').html(ElementInnerHTML);
            if (option.Buttons && option.Buttons.Ok && option.Buttons.Ok.Class) {
                $('#divMatDialog .modal .prompt.btn-ok').addClass(option.Buttons.Ok.Class);
            }
            if (option.Buttons && option.Buttons.Cancel && option.Buttons.Cancel.Class) {
                $('#divMatDialog .modal .prompt.btn-cancel').addClass(option.Buttons.Cancel.Class);
            }
            if (option.ExecuteAfter) {
                option.ExecuteAfter();
            }
        };
        return Prompt;
    }());
    MatDialogs.Prompt = Prompt;
})(MatDialogs || (MatDialogs = {}));
var MatDialogs;
(function (MatDialogs) {
    var Alert = (function () {
        function Alert(option) {
            if (typeof (option) === 'object') {
                this.createCustomAlert(option);
            }
            else {
                this.createAlert(option);
            }
        }
        Alert.prototype.createAlert = function (Msg) {
            var ElementInnerHTML = '<div class="modal-header">' +
                '<i class="modal-button material-icons right-align header-close-icon">&#xE5CD;</i></div>' +
                '<div class="divider"></div><div class="modal-content">' + Msg + '</div>' + '<div class="divider"></div>' +
                '<div class="modal-footer"><a href="#!" class="modal-button btn waves-effect waves-green">Ok</a></div>';
            $('#divMatDialog .modal').data('type', 'alert').html(ElementInnerHTML);
        };
        Alert.prototype.createCustomAlert = function (option) {
            if (option.ExecuteBefore) {
                option.ExecuteBefore();
            }
            var ButtonContent = (option.Button && option.Button.Label) ? option.Button.Label : 'Ok';
            var ElementInnerHTML = '<div class="modal-header">' +
                '<i class="modal-button material-icons right-align header-close-icon">&#xE5CD;</i></div>' +
                '<div class="divider"></div><div class="modal-content">' + option.Text + '</div>' + '<div class="divider"></div>' +
                '<div class="modal-footer"><a href="#!" class="modal-button btn waves-effect waves-green">' + ButtonContent + '</a></div>';
            $('#divMatDialog .modal').data('type', 'alert').html(ElementInnerHTML);
            if (option.Button && option.Button.Class) {
                $('#divMatDialog .modal .btn').addClass(option.Button.Class);
            }
            if (option.ExecuteAfter) {
                option.ExecuteAfter();
            }
        };
        return Alert;
    }());
    MatDialogs.Alert = Alert;
})(MatDialogs || (MatDialogs = {}));
var MatDialog = (function (_super) {
    __extends(MatDialog, _super);
    function MatDialog(config) {
        var _this = _super.call(this) || this;
        _this.setModalConfig = function (config) {
            this.registerModal(config);
        };
        if (document.getElementById('divMatDialog') == null) {
            var container = document.createElement('div');
            container.id = 'divMatDialog';
            container.innerHTML = '<div class="modal"></div>';
            document.body.appendChild(container);
        }
        _this.registerModal(config);
        return _this;
    }
    MatDialog.prototype.alert = function (message, callBack) {
        new MatDialogs.Alert(message);
        this.openModal(callBack);
    };
    MatDialog.prototype.confirm = function (message, callBack) {
        new MatDialogs.Confirm(message);
        this.openModal(callBack);
    };
    MatDialog.prototype.prompt = function (message, callBack) {
        new MatDialogs.Prompt(message);
        this.Option = message;
        this.openModal(callBack, true);
    };
    MatDialog.prototype.create = function (option, callBack) {
        if (option) {
            new MatDialogs.Dialog(option);
            this.openModal(callBack);
        }
        else {
            console.error('no Dialog option provided');
        }
    };
    return MatDialog;
}(Helper));
;
var MatDialogs;
(function (MatDialogs) {
    var Confirm = (function () {
        function Confirm(option) {
            this.createCustomConfirm = function (option) {
                if (option.ExecuteBefore) {
                    option.ExecuteBefore();
                }
                var OkLabel = (option.Buttons && option.Buttons.Ok && option.Buttons.Ok.Label) ? option.Buttons.Ok.Label : 'Ok', CancelLabel = (option.Buttons && option.Buttons.Cancel && option.Buttons.Cancel.Label) ? option.Buttons.Cancel.Label : 'Cancel';
                var ElementInnerHTML = '<div class="modal-header">' +
                    '<i class="modal-button material-icons right-align header-close-icon">&#xE5CD;</i></div>' +
                    '<div class="divider"></div><div class="modal-content">' + option.Text + '</div>' + '<div class="divider"></div>' +
                    '<div class="modal-footer"><a href="#!" data-val="false" class="modal-button btn waves-effect waves-green confirm btn-cancel">' + CancelLabel + '</a>' +
                    '<a href="#!" data-val="true" class="modal-button btn waves-effect waves-green confirm btn-ok">' + OkLabel + '</a></div>';
                $('#divMatDialog .modal').data('type', 'confirm').html(ElementInnerHTML);
                if (option.Buttons && option.Buttons.Ok && option.Buttons.Ok.Class) {
                    $('#divMatDialog .modal .confirm.btn-ok').addClass(option.Buttons.Ok.Class);
                }
                if (option.Buttons && option.Buttons.Cancel && option.Buttons.Cancel.Class) {
                    $('#divMatDialog .modal .confirm.btn-cancel').addClass(option.Buttons.Cancel.Class);
                }
                if (option.ExecuteAfter) {
                    option.ExecuteAfter();
                }
            };
            if (typeof (option) === 'object') {
                this.createCustomConfirm(option);
            }
            else {
                this.createConfirm(option);
            }
        }
        Confirm.prototype.createConfirm = function (Msg) {
            var ElementInnerHTML = '<div class="modal-header">' +
                '<i class="modal-button material-icons right-align header-close-icon">&#xE5CD;</i></div>' +
                '<div class="divider"></div><div class="modal-content">' + Msg + '</div>' + '<div class="divider"></div>' +
                '<div class="modal-footer"><a href="#!" data-val="false" class="modal-button btn waves-effect waves-green confirm btn-cancel">Cancel</a>' +
                '<a href="#!" data-val="true" class="modal-button btn waves-effect waves-green confirm btn-ok">OK</a></div>';
            $('#divMatDialog .modal').data('type', 'confirm').html(ElementInnerHTML);
        };
        return Confirm;
    }());
    MatDialogs.Confirm = Confirm;
})(MatDialogs || (MatDialogs = {}));
var MatDialogs;
(function (MatDialogs) {
    var Dialog = (function () {
        function Dialog(option) {
            this.createDialog = function (option) {
                if (option.ExecuteBefore) {
                    option.ExecuteBefore();
                }
                var ElementInnerHTML = '';
                if (option.Title) {
                    ElementInnerHTML += '<div class="modal-header">';
                    if (option.Title.Label) {
                        ElementInnerHTML += '<span class="prompt-msg">' + option.Title.Label + '</span>';
                    }
                    if (option.Title.ShowClose == undefined || JSON.parse(option.Title.ShowClose)) {
                        ElementInnerHTML += '<i class="modal-button material-icons right-align header-close-icon">&#xE5CD;</i>';
                    }
                    ElementInnerHTML += '</div><div class="divider"></div>';
                }
                if (option.Content) {
                    ElementInnerHTML += '<div class="modal-content ' + (option.Content.Class ? option.Content.Class : "") + '">' + option.Content.Label + '</div>';
                }
                var BottomHtml = "";
                if (option.ButtonType) {
                    var CancelLabel = 'Cancel', OkLabel = 'Ok';
                    if (option.ButtonType.toLowerCase() == 'alert') {
                        BottomHtml = '<a href="#" data-val="true" class="modal-button btn waves-effect waves-green prompt btn-ok">' + OkLabel + '</a>';
                    }
                    else {
                        BottomHtml = '<a href="#" data-val="false" class="modal-button btn waves-effect waves-green prompt btn-cancel" > ' + CancelLabel + ' </a>' +
                            '<a href="#" data-val="true" class="modal-button btn waves-effect waves-green prompt btn-ok">' + OkLabel + '</a>';
                    }
                }
                else if (option.Buttons) {
                    for (var item, i = option.Buttons.length - 1; i >= 0; i--) {
                        item = option.Buttons[i];
                        BottomHtml += '<a href="#!" data-val="' + item.Value + '" class="modal-button btn waves-effect waves-green btns ' + (item.Class ? item.Class : "") + '">' + item.Label + '</a>';
                    }
                }
                if (BottomHtml.length > 0) {
                    ElementInnerHTML += '<div class="divider"></div><div class="modal-footer">' + BottomHtml + '</div>';
                }
                $('#divMatDialog .modal').html(ElementInnerHTML).data('type', 'create');
                if (option.ExecuteAfter) {
                    option.ExecuteAfter();
                }
            };
            this.createDialog(option);
        }
        return Dialog;
    }());
    MatDialogs.Dialog = Dialog;
})(MatDialogs || (MatDialogs = {}));