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
                tooltip: "VideoUpload Plugin",
                unsupportedFileTypeError: "Filetype does not match one of a video (e.g. .mp4, .webm)"
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

            this.iterfileasDataUrl = function(file) {
                return $.Deferred(function(deferred) {
                    $.extend(new FileReader(), {
                        onload: function(evt) {
                            console.log("onload");
                            let videoBuffer = evt.target.result;

                            let _blob = new Blob([new Uint8Array(videoBuffer), { type: 'video/mkv' }]); // preset to mkv currently until I create method to find the extension of the file

                            let videoUrl = window.URL.createObjectURL(_blob);

                            deferred.resolve(video);
                        },
                        onerror: function(er) {
                            console.log("Error:  ", er.message);
                            throw er.message;
                            //deferred.reject(er);
                        }
                    }).readAsArrayBuffer(file);
                }).promise();
            }

            // Upload video url with iframe element with youtube embed url created from code provided
            this.uploadVideoUrl = function(url) {
                let base_url = "https://www.youtube.com/embed/";
                let in_url = url.includes(base_url);
                let ab_channel = url.includes("&ab_channel=")
                if (in_url) {
                    if (ab_channel) {
                        url = url.split("&ab_channel=")[0];
                    }
                    let $ytembed = $(`<iframe width="500" height="350" src="${url}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>`);
                    self.insertData($ytembed);
                } else {
                    url = url.split("?v=")[1];
                    if (ab_channel) {
                        url = url.split("&ab_channel=")[0];
                    }
                    let embedurl = base_url + url;
                    let $ytembed = $(`<iframe width="500" height="350" src="${embedurl}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>`);
                    self.insertData($ytembed);
                }
            };

            // Upload video from file path
            this.uploadVideoFile = function(data) {
                // TODO: Fix broken function
                $.each(data, function(idx, file) {
                    let fname = file.name;
                    console.log(fname);
                    console.log(file);
                    console.log(typeof file);
                    let videoRegExp = /^.+.(mp4|ogv|webm|x-matroska)$/;
                    let videoBase64RegExp = /^data:(video\/mpeg|video\/mp4|video\/ogv|video\/webm).+$/;
                    let $file;


                    const reader = new FileReader();

                    reader.onload = function(evt) {
                        console.log("onload");
                        let videoBuffer = evt.target.result;

                        let _blob = new Blob([new Uint8Array(videoBuffer), { type: 'video/mp4' }]); // preset to mkv currently until I create method to find the extension of the file

                        let videoUrl = window.URL.createObjectURL(_blob);

                        $file = videoUrl;

                        if (videoUrl.match(videoRegExp) || videoUrl.match(videoBase64RegExp)) {
                            console.log("matched");
                            $file = $("<video controls>").attr('src', videoUrl);
                            $file.addClass('note-file-clip');

                            context.invoke('editor.beforeCommand');

                            if (typeof fname === 'string') {
                                $file.attr('data-filename', fname);
                            }

                            $file.show();
                            context.invoke('editor.insertNode', $file[0]);

                            context.invoke('editor.afterCommand');
                        }
                    }

                    reader.readAsArrayBuffer(file);
                });
            };

            // insert either iframe or file data into the editor
            this.insertData = function(data) {
                $file = data;

                context.invoke('videoUpload.beforeCommand');

                $file.show();
                context.invoke('editor.insertNode', $file[0]);

                context.invoke('editor.afterCommand');
            };

            // Shows Plugin Dialog
            this.show = function() {;
                context.invoke('editor.saveRange');
                this.showvideoUploadDialog().then(function(editorInfo) {
                    ui.hideDialog(self.$dialog);
                    context.invoke('editor.restoreRange');
                    if (typeof editorInfo === 'string') { // youtube url
                        self.uploadVideoUrl(editorInfo);
                    } else {
                        self.uploadVideoFile(editorInfo);
                    }
                }).fail(function() {
                    context.invoke('editor.restoreRange');
                });
            };

            // showvideoUploadDialog helper function used above in the show function
            this.showvideoUploadDialog = function() {
                return $.Deferred(function(deferred) {
                    let $pluginBtn = self.$dialog.find('.note-videoUpload-btn');
                    let $pluginFileInput = self.$dialog.find('.note-file-input');
                    let $pluginUrlInput = self.$dialog.find('.note-video-url')

                    ui.onDialogShown(self.$dialog, function() {
                        context.triggerEvent('dialog.shown');

                        $pluginFileInput.replaceWith($pluginFileInput.clone().on('change', function(event) {
                            deferred.resolve(event.target.files || event.target.value);
                        }).val(''));

                        $pluginBtn.click(function(e) {
                            e.preventDefault();
                            deferred.resolve($pluginUrlInput.val());
                        });
                        $pluginUrlInput.on("keyup paste", function() {
                            let url = $pluginUrlInput.val();
                            ui.toggleBtn($pluginFileInput, url);
                        }).val('');
                        self.bindEnterKey($pluginUrlInput, $pluginBtn);
                        self.bindLabels();
                    });

                    ui.onDialogHidden(self.$dialog, function() {
                        $pluginUrlInput.off('keyup paste keypress');
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