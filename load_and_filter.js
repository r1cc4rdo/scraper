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
}

function filter_text(search_term)
{
    $(".event-group").each(function(group_index, group)
    {
        var event_count = 0;
        $(this).find(".event-title").each(function(cell_index, cell)
        {
            var visible = cell.innerText.toLowerCase().includes(search_term);
            $(this).parent().toggle(visible);
            event_count += visible;
        });
        $(this).toggle(event_count > 0)
    });

    var search_icon = $("#search_icon");
    var [is, ic] = ["fa-search", "fa-close"];
    if (search_term.length == 0) [is, ic] = [ic, is];
    search_icon.removeClass(is);
    search_icon.addClass(ic);
}

function setup_ui()
{
    $("#search_box").bind("keyup change", (e) => filter_text(e.target.value)); // search on type
    $("#search_icon").parent().click(() =>  // search clear button
    {
        $("#search_box").val("");
        filter_text("");
    });

    $(".group_filter").click((e) =>
    {
        update_content(e.target.innerText.toLowerCase());
        filter_text($("#search_box").val());
    });

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
    var prefix = "https://planetgranite.com/sv/event/";
    json_payload.slice(1, json_payload.length).forEach(values =>
    {
        var event_dict = {};
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

        json_events.push(event_dict);
    });
    update_content("date");
});

$(function()
{
    setup_ui();
});
