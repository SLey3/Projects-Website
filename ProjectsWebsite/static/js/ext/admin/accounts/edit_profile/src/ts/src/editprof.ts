/*
Includes: editProfInit
Desc: to initialize the events for the edit profile section of the Administrator edit profile page
*/

import * as $ from 'jquery';

import { addHoverElement } from './hoverinit';

const spanOrderList = [
    ".info-name",
    ".info-email",
    ".info-password",
    ".info-active-status",
    ".info-acc-create",
    ".info-blacklist-status"
];

function capitalize(string: string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

interface editProfElements {
    elements: Array<string>,
    label: string,
    section_item: string
}

export function editProfInit(icnid: string, spanClass: string, section_name: string, outs: editProfElements) {
    let label = outs.label;
    let elements = outs.elements;
    $(`#${icnid}`).on('click', function() {
        let index = spanOrderList.indexOf(spanClass);
        if (index > -1) {
            spanOrderList.splice(index, 1);
        }
        $(".edit-icon").each(function() {
            $(this).css("opacity", 0);
        });

        $(".fa.fa-pencil-square").each(function() {
            $(this).css('cursor', 'default');
        });

        $("information#prof-info span").each(function() {
            $(this).addClass("prof-info-btn-clicked");
            $(this).off('mouseenter mouseleave');
        });
        for (var s = 0; s < spanOrderList.length; s++) {
            let Class = spanOrderList[s];
            $(Class).on('mouseenter', function() {
                $(this).css("letter-spacing", "1.1px");
                $(this).css("font-style", "normal");
                $(this).css("font-weight", 0);
                $(this).css("font-size", "16px");
            });
            $(Class).on('mouseleave', function() {
                console.log("Form active, Will not proceed with hover effects.");
            });
        }
        $(".info-name").replaceWith($(`<form id="edit-${section_name.toLowerCase()}-form" name="${section_name.toLowerCase()}-form" action="{{ request.url }}" method="POST">` + '{{ info_forms.csrf_token }}' + `${label}` + `${elements[0]}` + `${elements[1]}` + `<div id="minus-icn" class="close-edit-${section_name.toLowerCase()}-align close-edit-${section_name.toLowerCase()}-icon">` + '<i class="fa fa-minus-square-o" aria-hidden="true">' + '</i>' + '</div>' + '</form>'));
        $("#minus-icn").on('click', function() {
            $(`form#edit-${section_name.toLowerCase()}-form`).replaceWith($('<span id="order-1" name="info-txt-span" class="info-name">' + `${capitalize(section_name)}: ${outs.section_item}` + '</span>'));
            $(".edit-icon").each(function() {
                $(this).css("opacity", 1);
            });
            $(".fa.fa-pencil-square").each(function() {
                $(this).css("cursor", 'pointer');
            });
            $("information#prof-info span").each(function() {
                $(this).removeClass("prof-info-btn-clicked");
            });
            for (var s = 0; s < spanOrderList.length; s++) {
                let Class = spanOrderList[s];
                $(Class).on('mouseenter', function() {
                    $(this).css('content', '');
                    $(this).css('z-index', 10);
                    $(this).css('font-style', 'italic');
                    $(this).css('font-weight', '650px');
                    $(this).css('font-size', '35px');
                });
                $(Class).on('mouseleave', function() {
                    $(this).css('z-index', 0);
                    $(this).css('font-style', 'normal');
                    $(this).css('font-weight', 0);
                    $(this).css('font-size', '16px');
                })
                addHoverElement();
            }
        });
    });
}