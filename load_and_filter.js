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
    var event_groups = {};
    switch(group_by)
    {
    case 'event':

        event_groups = group_events(function(e){ return e['title'] });
        break;

    case 'date':

        event_groups = group_events(function(e){ return e['dotw'] + ', ' + e['month'] + ' ' + e['day'] });
        break;

    default: // category

        json_events.forEach(function(pg_event)
        {
            pg_event['categories'].forEach(function(category)
            {
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
        html_content += event_template({section: group_key, events: event_groups[group_key]});
    }
    $("#content").html(html_content);
}

function setup_ui()
{
    $(".day-filter").checkboxradio({icon: false});

    $("#group-by").selectmenu({change: function(event, ui)
    {
        update_content(ui.item.label.toLowerCase());
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
    update_content("date");
});

$(function()
{
    setup_ui();
});
