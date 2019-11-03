var event_template = Handlebars.compile($("#event-template").html());

var json_events = [];
$.getJSON("events.json").then(function(json_payload)
{
    var keys = json_payload[0];
    var prefix = "https://planetgranite.com/sv/event/";
    json_payload.slice(1, json_payload.length).forEach((values, index) =>
    {
        var event_dict = {id: index};
        keys.forEach((key, i) => event_dict[key] = values[i]);

        start_date = new Date(event_dict["start_epoch"] * 1000);
        end_date = new Date(event_dict["end_epoch"] * 1000);
        event_dict["start_date"] = start_date;
        event_dict["end_date"] = end_date;
        event_dict["date_string"] = start_date.toDateString();
        event_dict["time_string"] = start_date.toTimeString().substring(0, 5);
        event_dict["duration_minutes"] = Math.floor((end_date - start_date) / 60 / 1000);

        event_dict["recurring"] = event_dict["recurring"] ? prefix.concat(event_dict["recurring"]) : false;
        event_dict["link"] = prefix.concat(event_dict["link"]);

        event_dict["search"] = ["title", "instructor", "substitutes"].map(k => event_dict[k]).concat(event_dict["categories"]).join(";");
        json_events.push(event_dict);
    });

    days_range = Math.ceil((json_events[json_events.length - 1]["end_epoch"] - json_events[0]["start_epoch"]) / 86400)
    $("#date_range").slider({range: true, min: 0, max: days_range - 1, step: 1, values: [0, days_range - 1]});

    update_content("date");
});

function group_events(key_function)
{
    var groups = {};
    json_events.forEach(function(pg_event)
    {
        var group_key = key_function(pg_event);
        if (group_key in groups)
        {
            groups[group_key].push(pg_event);
        }
        else
        {
            groups[group_key] = [pg_event];
        }
    });
    return groups;
}

function update_content(group_by)
{
    // sort

    var event_groups = {};
    switch(group_by)
    {
    case "event":

        event_groups = group_events(e => e["title"]);
        break;

    case "date":

        event_groups = group_events(e => e["date_string"]);
        break;

    default: // category

        json_events.forEach(function(pg_event)
        {
            pg_event["categories"].forEach(function(category)
            {
                category = category.charAt(0).toUpperCase() + category.slice(1)
                if (category in event_groups)
                {
                    event_groups[category].push(pg_event);
                }
                else
                {
                    event_groups[category] = [pg_event];
                }
            });
        });
    }

    html_content = "";
    for(var group_key in event_groups) // {{#each object}} {{@key}}: {{this}} {{/each}}
    {
        html_content += event_template({section: group_key, show_tags: group_by == "event", events: event_groups[group_key]});
    }
    $("#content").html(html_content);
    $("#group_by").html("Group by: " + group_by);

    apply_filters();
}

function apply_filters()
{
    var reference_date = new Date(json_events[0]["start_epoch"] * 1000);
    reference_date.setHours(0);
    reference_date.setMinutes(0);
    reference_date.setSeconds(0);

    var search_term = $("#search_box").val();
    var date_range = $("#date_range").slider("values");
    var time_range = $("#time_range").slider("values");

    $(".event-group").hide();
    json_events.forEach(function(event, index)
    {
        var days_from_reference = (event.start_date - reference_date) / 86400000;
        var date_filter = (days_from_reference >= date_range[0]) && (days_from_reference - 1 <= date_range[1]);
        var time_filter = (event.start_date.getHours() >= time_range[0]) &&
                          ((event.end_date.getHours() + (event.end_date.getMinutes() > 0 ? 1 : 0)) <= time_range[1]);
        var search_filter = event["search"].toLowerCase().includes(search_term.toLowerCase());

        var filter_pass = date_filter && time_filter && search_filter;
        var rows = $(".event-" + index).toggle(filter_pass);
        if (filter_pass) rows.closest(".event-group").show();
    });

    $("#search_icon").attr("class", "w3-large fa " + (search_term.length == 0 ? "fa-search" : "fa-close"));
}

$(function()
{
    $(".group_filter").click((e) => update_content(e.target.innerText.toLowerCase()));

    $("#reset_time_filter").hide();
    $("#reset_time_filter").click(() => $("#time_range").slider("values", [0, 24]));
    $("#time_range").slider({range: true, min: 0, max: 24, step: 1, values: [0, 24]});
    $("#time_range").on("slide slidechange", (event, ui) =>
    {
        start_time = (ui.values[0] <= 9 ? "0" : "") + ui.values[0] + ":00";
        end_time = (ui.values[1] <= 9 ? "0" : "") + ui.values[1] + ":00";

        $("#time_start").text(start_time);
        $("#time_end").text(end_time);

        var active = JSON.stringify(ui.values) != "[0,24]"
        $("#reset_time_filter").toggle(active);
        $("#time_label").html(active ? start_time + " <i class=\"fa fa-angle-double-right\"></i> " + end_time : "Anytime");

        apply_filters();
    });

    $("#reset_date_filter").hide();
    $("#date_range").slider({range: true, min: 0, max: 1, step: 1, values: [0, 1]});
    $("#reset_date_filter").click(() => $("#date_range").slider("values", [0, $("#date_range").slider("option", "max")]));
    $("#date_range").on("slide slidechange", (event, ui) =>
    {
        var date_reference = json_events[0]["start_date"];
        date_reference.setHours(12);
        date_reference.setMinutes(0);
        date_reference.setSeconds(0);
        var epoch_reference = date_reference.getTime();

        var epoch_left_range = epoch_reference + 86400000 * ui.values[0];
        var epoch_right_range = epoch_reference + 86400000 * ui.values[1];
        $(".date_start").text(new Date(epoch_left_range).toDateString().substring(0, 10));
        $(".date_end").text(new Date(epoch_right_range).toDateString().substring(0, 10));

        var max = $("#date_range").slider("option", "max");
        $("#reset_date_filter").toggle((ui.values[0] != 0) || (ui.values[1] != max));

        apply_filters();
    });

    $("#search_box").bind("keyup change", () => apply_filters()); // search on type
    $("#search_icon").parent().click(() => $("#search_box").val("").change()); // search clear button
    $("#search_box").val(new URL(window.location.href).searchParams.get("search")); // populate with url request

    $(document).keydown(() => $("#search_box").focus());
});
