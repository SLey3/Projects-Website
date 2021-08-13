/*
includes: addHoverElement
desc: Initializes the hover animation for the editProfInit function in editprof.js
*/
import * as $ from 'jquery';

type handlerFunction = () => void;

function hover(element: string, inhandler: handlerFunction, outhandler: handlerFunction) {
    $(element).on('mouseenter', inhandler);
    $(element).on('mouseleave', outhandler);
}

export function addHoverElement() {
    $("info-txt-span").each(function() {
        if (this.id == "order-1") {
            const spanOrderList = [
                "span#order-2",
                "span#order-3",
                "span#order-4",
                "span#order-5",
                "span#order-6"
            ];
            hover(`${this.nodeName.toLowerCase()}#order-1`, function() {
                $(".edit-icon").each(function() {
                    $(this).css("opacity", 0);
                });
                for (var o = 0; o < spanOrderList.length; o++) {
                    let order = spanOrderList[o];
                    $(order).addClass("lower-span-txt");
                }
            }, function() {
                $(".edit-icon").each(function() {
                    $(this).css("opacity", 1);
                });
                for (var o = 0; o < spanOrderList.length; o++) {
                    let order = spanOrderList[o];
                    $(order).removeClass("lower-span-txt");
                }
            });
        } else if (this.id == 'order-2') {
            const spanOrderList = [
                "span#order-1",
                "span#order-3",
                "span#order-4",
                "span#order-5",
                "span#order-6"
            ];

            hover(`${this.nodeName.toLowerCase()}#order-2`, function() {
                $(".edit-icon").each(function() {
                    $(this).css("opacity", 0);
                });
                for (var o = 0; o < spanOrderList.length; o++) {
                    let order = spanOrderList[o];
                    $(order).addClass("lower-span-txt");
                }
            }, function() {
                $(".edit-icon").each(function() {
                    $(this).css("opacity", 1);
                });
                for (var o = 0; o < spanOrderList.length; o++) {
                    let order = spanOrderList[o];
                    $(order).removeClass("lower-span-txt");
                }
            });
        } else if (this.id == 'order-3') {
            const spanOrderList = [
                "span#order-1",
                "span#order-2",
                "span#order-4",
                "span#order-5",
                "span#order-6"
            ];

            $(this.nodeName.toLowerCase() + "#order-3").hover(function() {
                $(".edit-icon").each(function() {
                    $(this).css("opacity", 0);
                });
                for (var o = 0; o < spanOrderList.length; o++) {
                    let order = spanOrderList[o];
                    $(order).addClass("lower-span-txt");
                }
            }, function() {
                $(".edit-icon").each(function() {
                    $(this).css("opacity", 1);
                });
                for (var o = 0; o < spanOrderList.length; o++) {
                    let order = spanOrderList[o];
                    $(order).removeClass("lower-span-txt");
                }
            });
        } else if (this.id == 'order-4') {
            const spanOrderList = [
                "span#order-1",
                "span#order-2",
                "span#order-3",
                "span#order-5",
                "span#order-6"
            ];

            hover(`${this.nodeName.toLowerCase()}#order-4`, function() {
                $(".edit-icon").each(function() {
                    $(this).css("opacity", 0);
                });
                for (var o = 0; o < spanOrderList.length; o++) {
                    let order = spanOrderList[o];
                    $(order).addClass("lower-span-txt");
                }
            }, function() {
                $(".edit-icon").each(function() {
                    $(this).css("opacity", 1);
                });
                for (var o = 0; o < spanOrderList.length; o++) {
                    let order = spanOrderList[o];
                    $(order).removeClass("lower-span-txt");
                }
            });
        } else if (this.id == 'order-5') {
            const spanOrderList = [
                "span#order-1",
                "span#order-2",
                "span#order-3",
                "span#order-4",
                "span#order-6"
            ];

            hover(`${this.nodeName.toLowerCase()}#order-5`, function() {
                $(".edit-icon").each(function() {
                    $(this).css("opacity", 0);
                });
                for (var o = 0; o < spanOrderList.length; o++) {
                    let order = spanOrderList[o];
                    $(order).addClass("lower-span-txt");
                }
            }, function() {
                $(".edit-icon").each(function() {
                    $(this).css("opacity", 1);
                });
                for (var o = 0; o < spanOrderList.length; o++) {
                    let order = spanOrderList[o];
                    $(order).removeClass("lower-span-txt");
                }
            });
        } else if (this.id == 'order-6') {
            const spanOrderList = [
                "span#order-1",
                "span#order-2",
                "span#order-3",
                "span#order-4",
                "span#order-5"
            ];

            hover(`${this.nodeName.toLowerCase()}#order-6`, function() {
                $(".edit-icon").each(function() {
                    $(this).css("opacity", 0);
                });
                for (var o = 0; o < spanOrderList.length; o++) {
                    let order = spanOrderList[o];
                    $(order).addClass("lower-span-txt");
                }
            }, function() {
                $(".edit-icon").each(function() {
                    $(this).css("opacity", 1);
                })
                for (var o = 0; o < spanOrderList.length; o++) {
                    let order = spanOrderList[o];
                    $(order).removeClass("lower-span-txt");
                }
            });
        }
    });
}