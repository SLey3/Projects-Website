function initEditProfMenu(user, page_url, name_input_field,
    name_validate_url, name_process_url,
    username_input_field, username_validate_url,
    username_process_url) {
    $(function() {
        $("#name-edit-btn").on('click', function() {
            $.confirm({
                title: 'Edit Name',
                theme: 'supervan',
                autoClose: 'cancel|16500',
                draggable: false,
                columnClass: 'medium',
                animation: 'rotateYR',
                closeAnimation: 'rotateXR',
                animationSpeed: 1500,
                content: '' +
                    `<form id="edit-name-form" method="POST" action="${page_url}">` +
                    '<div class="form-group">' +
                    '<label> New Name:</label>' +
                    `${name_input_field}` +
                    '<input id="hidden-inpt" type="hidden" />' +
                    '</div>' +
                    '</div>' +
                    '</form>',
                buttons: {
                    cancel: function() {},
                    formSubmit: {
                        text: 'Submit',
                        btnClass: 'btn-blue',
                        keys: ['enter'],
                        action: async() => {
                            const validationResult = async(oldname, newname) => {
                                let url = `${name_validate_url}`;
                                try {
                                    const res = await axios.post(url, {
                                        oldname: oldname,
                                        newname: newname
                                    });
                                    return res.data;
                                } catch (error) {
                                    return false;
                                }
                            }

                            let result = await validationResult(`${user.name}`, $("#edit-name-input").val());

                            if (typeof result === 'boolean' || typeof result === 'undefined') {
                                $.alert({
                                    content: "Something went wrong",
                                    title: "ERROR",
                                    type: "red"
                                })
                                return false;
                            }

                            if (!result.status) {
                                let errs = result.field_errs;
                                let content = "The name did not meet the following requirements:";
                                for (let err of errs) {
                                    content += `\n - ${err}`;
                                }
                                $.alert({
                                    title: "Form Validation",
                                    content: content,
                                    type: "red"
                                })
                                return false;
                            } else {
                                $.ajax({
                                    method: 'POST',
                                    url: `${name_process_url}`,
                                    data: {
                                        oldname: `${user.name}`,
                                        newname: $("#edit-name-input").val()
                                    }
                                }).done(
                                    setTimeout(function() {
                                        location.reload(true);
                                    }, 1500));
                            }
                        }
                    }
                },
                onContentReady: function() {
                    let jc = this;
                    this.$content.find('form').on('submit', function(e) {
                        e.preventDefault();
                        jc.$$formSubmit.trigger('click');
                    });
                }
            });
        });

        $("#username-edit-btn").on('click', function() {
            $.confirm({
                title: 'Edit Username',
                theme: 'supervan',
                autoClose: 'cancel|16500',
                draggable: false,
                columnClass: 'medium',
                animation: 'rotateYR',
                closeAnimation: 'rotateXR',
                animationSpeed: 1500,
                content: '' +
                    // <form id='acc-info-edit-usrnm-form'  method='POST' action=${page_url}>${username_input_field}${username_sbmt_field}</form>
                    `<form id='acc-info-edit-usrnm-form'  method='POST' action=${page_url}>` +
                    '<div class="form-group">' +
                    '<label> New Username:</label>' +
                    `${username_input_field}` +
                    '<input id="hidden-inpt" type="hidden" />' +
                    '</div>' +
                    '</div>' +
                    '</form>',
                buttons: {
                    cancel: function() {},
                    formSubmit: {
                        text: 'Submit',
                        btnClass: 'btn-blue',
                        keys: ['enter'],
                        action: async() => {
                            const validationResult = async(old_user_name, new_user_name) => {
                                let url = `${username_validate_url}`;
                                try {
                                    const res = await axios.post(url, {
                                        oldusername: old_user_name,
                                        newusername: new_user_name
                                    });
                                    return res.data;
                                } catch (error) {
                                    return false;
                                }
                            }

                            let result = await validationResult(`${user.name}`, $("#edit-name-input").val());

                            if (typeof result === 'boolean' || typeof result === 'undefined') {
                                $.alert({
                                    content: "Something went wrong",
                                    title: "ERROR",
                                    type: "red"
                                })
                                return false;
                            }

                            if (!result.status) {
                                let errs = result.field_errs;
                                let content = "The name did not meet the following requirements:";
                                for (let err of errs) {
                                    content += `\n - ${err}`;
                                }
                                $.alert({
                                    title: "Form Validation",
                                    content: content,
                                    type: "red"
                                })
                                return false;
                            } else {
                                $.ajax({
                                    method: 'POST',
                                    url: `${username_process_url}`,
                                    data: {
                                        oldusername: `${user.name}`,
                                        newusername: $("#edit-name-input").val()
                                    }
                                }).done(
                                    setTimeout(function() {
                                        location.reload(true);
                                    }, 1500));
                            }
                        }
                    }
                },
                onContentReady: function() {
                    let jc = this;
                    this.$content.find('form').on('submit', function(e) {
                        e.preventDefault();
                        jc.$$formSubmit.trigger('click');
                    });
                }
            });
        });
    });
}