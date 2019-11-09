function group_by_dropdown_setup()
{
    $(".group_by_item").click((e) => update_content(e.target.innerText));
}

function date_range_filter_setup()
{
    $("#date_reset_filter").hide();
    $("#date_range").slider({range: true, min: 0, max: 1, step: 1, values: [0, 1]});
    $("#date_reset_filter").click(() => $("#date_range").slider("values", [0, $("#date_range").slider("option", "max")]));
    $("#date_range").on("slide slidechange", (event, ui) =>
    {
        var date_reference = json_events[0]["start_date"];
        date_reference.setHours(12);
        date_reference.setMinutes(0);
        date_reference.setSeconds(0);
        var epoch_reference = date_reference.getTime();

        var epoch_left_range = epoch_reference + 86400000 * ui.values[0];
        var epoch_right_range = epoch_reference + 86400000 * ui.values[1];
        $(".date_start_label").text(new Date(epoch_left_range).toDateString().substring(0, 10));
        $(".date_end_label").text(new Date(epoch_right_range).toDateString().substring(0, 10));

        var max = $("#date_range").slider("option", "max");
        $("#date_reset_filter").toggle((ui.values[0] != 0) || (ui.values[1] != max));

        apply_filters();
    });
}

function time_range_filter_setup()
{
    $("#time_reset_filter").hide();
    $("#time_reset_filter").click(() => $("#time_range").slider("values", [0, 24]));
    $("#time_range").slider({range: true, min: 0, max: 24, step: 1, values: [0, 24]});
    $("#time_range").on("slide slidechange", (event, ui) =>
    {
        start_time = (ui.values[0] <= 9 ? "0" : "") + ui.values[0] + ":00";
        end_time = (ui.values[1] <= 9 ? "0" : "") + ui.values[1] + ":00";

        $("#time_start").text(start_time);
        $("#time_end").text(end_time);

        var active = JSON.stringify(ui.values) != "[0,24]"
        $("#time_reset_filter").toggle(active);
        $("#time_dropdown").html(active ? start_time + " <i class=\"fa fa-angle-double-right\"></i> " + end_time : "Anytime");

        apply_filters();
    });
}

function search_bar_setup()
{
    $("#search_box").bind("keyup input change paste", () =>  // search while typing
    {
        var icon_class = $("#search_box").val().length == 0 ? "fa-search" : "fa-close";
        $("#search_icon").attr("class", "w3-large fa " + icon_class);
        apply_filters();
    });
    $("#search_icon").parent().click(() => $("#search_box").val("").change()); // search clear button
    $(document).keydown(() => $("#search_box").focus()); // transfer focus to search bar on keypress
    $("#search_box").focus(); // initial focus
}

$(function() // configure UI elements, register callbacks
{
    group_by_dropdown_setup();
    time_range_filter_setup();
    date_range_filter_setup();
    search_bar_setup();
});
