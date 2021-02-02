(function() {
    $('input[type=checkbox]#article-head-selectAll').click(function() {
        $("input[name=article-check-inner]").prop('checked', $(this).prop('checked'));
        $("input[type=checkbox]#article-foot-selectAll").prop('checked', $(this).prop('checked'));
    });
    $('input[type=checkbox]#article-foot-selectAll').click(function() {
        $("input[name=article-check-inner]").prop('checked', $(this).prop('checked'));
        $("input[type=checkbox]#article-head-selectAll").prop('checked', $(this).prop('checked'));
    });
});

(function() {
    $('input[type=checkbox]#role-head-selectAll').click(function() {
        $("input[name=role-check-inner]").prop('checked', $(this).prop('checked'));
        $("input[type=checkbox]#role-foot-selectAll").prop('checked', $(this).prop('checked'));
    });
    $('input[type=checkbox]#role-foot-selectAll').click(function() {
        $("input[name=role-check-inner]").prop('checked', $(this).prop('checked'));
        $("input[type=checkbox]#role-head-selectAll").prop('checked', $(this).prop('checked'));
    });
});