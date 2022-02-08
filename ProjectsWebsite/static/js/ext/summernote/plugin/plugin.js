/**
 *
 * copyright 2022 Sergio Ley.
 * license: MIT
 */
(function(factory) {
    /* Global define */
    if (typeof define === 'function' && define.amd) {
        define(['jquery'], factory);
    } else if (typeof module === 'object' && module.exports) {
        module.exports = factory(require('jquery'));
    } else {
        factory(window.jQuery);
    }
}(function($) {
    /**
     * @class plugin.videoUpload
     *
     * videoUpload Plugin
     */

    // inserts plugin langInfo
    $.extend(true, $.summernote.lang, {
        // the only supported language
        'en-US': {
            videoUpload: {
                dialogTitle: "Upload Video",
                uploadFromFile: "Video file",
                uploadFromUrl: "Youtube Video url",
                okButton: "Upload",
                tooltip: 'VideoUpload Plugin'
            }
        }
    });

    // inserts the plugin's icon and tooltip
    $.extend($.summernote.options, {
        videoUpload: {
            icon: '<i class="note-icon-video"></i>'
        }
    });

    // Plugin source while also adding it to the summernote plugins list
    $.extend($.summernote.plugins, {
        /**
         *  @param {Object} context - Summernote context object has status of editor.
         */
        'videoUpload': function(context) {
            // needed constant definitions
            const self = this;
            const ui = $.summernote.ui;
            const $note = context.layoutInfo.note;
            const $editor = context.layoutInfo.editor;
            const $editable = context.layoutInfo.editable;
            const $toolbar = context.layoutInfo.toolbar;
            const options = context.options;
            const lang = options.langInfo;

            // render plugin button
            context.memo('button.videoUpload', function() {
                // Creation of plugin button
                let button = ui.button({
                    // icon
                    contents: options.videoUpload.icon,
                    tooltip: lang.videoUpload.tooltip,
                    click: function(e) {
                        context.invoke('videoUpload.show');
                    }
                });
                return button.render();
            });

            // Plugin Initialization
            this.initialize = function() {
                let $container = options.dialogsInBody ? $(document.body) : $editor;
                let body = [
                    '<div class="note-form-group note-group-select-file">',
                    '<label class="note-form-label">' + lang.videoUpload.uploadFromFile + '</label>',
                    '<input class="note-file-input note-form-control note-input" type="file" name="videUploadfiles" />',
                    '</div>',
                    '<br>',
                    '<div class="note-form-group note-group-select-url" style="overflow:auto;">',
                    '<label class="note-form-label">' + lang.videoUpload.uploadFromUrl + '</label>',
                    '<input class="note-video-url form-control note-form-control note-input col-md-12"',
                    'placeholder="Enter Video Url" type="text" />',
                    '</div>'
                ].join("");

                let footer = '<button href="#" class="btn btn-primary note-videoUpload-btn">' + lang.videoUpload.okButton +
                    '</button>';

                // Plugin Dialog
                this.$dialog = ui.dialog({
                    // set title
                    title: lang.videoUpload.dialogTitle,
                    // set body
                    body: body,
                    // set footer
                    footer: footer,
                    // Adds Modal to the DOM
                }).render().appendTo($container);
            };

            // Plugin destroy
            this.destroy = function() {
                ui.hideDialog(this.$dialog);
                this.$dialog.remove();
            };

            // Binds Enter Key
            this.bindEnterKey = function($input, $btn) {
                $input.on('keypress', function(event) {
                    if (event.keyCode === 13) {
                        $btn.trigger('click');
                    }
                });
            };

            // Binds Labels
            this.bindLabels = function() {
                self.$dialog.find('.form-control:first').focus().select();
                self.$dialog.find('label').on('click', function() {
                    $(this).parent().find(".form-control:first").focus();
                });
            };

            // Upload video url with jquery Ajax method
            this.uploadVideoUrl = function(url) {};

            // Upload video from file path
            this.uploadVideoFile = function(data) {};

            // Shows Plugin Dialog
            this.show = function() {
                context.invoke('editor.saveRange');
                this.showvideoUploadDialog().then(function(editorInfo) {
                    ui.hideDialog(self.self.$dialog);
                    context.invoke('editor.restoreRange');
                }).fail(function() {
                    context.invoke('editor.restoreRange');
                });
            };

            // showvideoUploadDialog helper function used above in the show function
            this.showvideoUploadDialog = function() {
                return $.Deferred(function(deferred) {
                    let $pluginBtn = self.$dialog.find('.note-videoUpload-btn');
                    let $pluginFileInput = self.$dialog.find('note-file-input');
                    let $pluginUrlInput = self.$dialog.find('note-video-url')

                    ui.onDialogShown(self.$dialog, function() {
                        context.triggerEvent('dialog.shown');
                        $pluginBtn.click(function(e) {
                            e.preventDefault();
                            deferred.resolve($pluginUrlInput.val());
                        });
                        self.bindEnterKey($pluginUrlInput, $pluginBtn);
                        self.bindLabels();
                    });

                    ui.onDialogHidden(self.$dialog, function() {
                        $pluginBtn.off('click');

                        if (deferred.state() === 'pending')
                            deferred.reject();
                    });

                    ui.showDialog(self.$dialog);
                });
            };
        }
    });
}));