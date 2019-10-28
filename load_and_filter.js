//function group_by_title()
//{
//    sort by category, events first
//}
//
//function group_by_date()
//{
//    sort by time
//}
//
//function group_by_category()
//{
//    events first then alphabetic
//}

var event_template = Handlebars.compile($("#event-template").html());

function update_content(group_by)
{
    var event_groups = {};
    json_events.forEach(function(pg_event)
    {
        var group_key = pg_event[group_by];
        if (group_key in event_groups)
        {
            event_groups[group_key].push(pg_event);
        }
        else
        {
            event_groups[group_key] = [pg_event];
        }
    });

    html_content = "";
    for(var group_key in event_groups) // {{#each object}} {{@key}}: {{this}} {{/each}}
    {
        html_content += event_template({section: group_key, events: event_groups[group_key]});
    }
    $("#content").html(html_content);
}

function setup_ui()
{
    $(".day-filter").checkboxradio({icon: false});

    $("#group-by").selectmenu({change: function(event, ui)
    {
        var group_by = ui.item.label == "Date" ? "date" : ui.item.label == "Event" ? "title" : "title";
        update_content(group_by);
    }});

    $("#hours_range").slider({range: true, min: 0, max: 24, step: 1, values: [0, 24], slide: function(event, ui)
    {
        $("#hours_label").val(ui.values[0] + " - " + ui.values[1]);
    }});

    $("#days_range").slider({range: true, min: 0, max: 15, step: 1, values: [0, 15], slide: function(event, ui)
    {
        $("#days_label").val(ui.values[0] + " - " + ui.values[1]);
    }});
}

var json_events = [];
$.getJSON("events.json").then(function(json_payload)
{
    var keys = json_payload[0];
    json_payload.slice(1, json_payload.length - 1).forEach(function(values)
    {
        var event_dict = {};
        keys.forEach((key, i) => event_dict[key] = values[i]);
        json_events.push(event_dict);
    });
    update_content("title");
});

$(function()
{
    setup_ui();
});
