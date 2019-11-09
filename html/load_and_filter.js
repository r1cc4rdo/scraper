var event_template = Handlebars.compile($("#event-template").html()); // event card template

function build_event_db(json_payload) // rebuild event database from json blob
{
    var event_db = []
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
        event_db.push(event_dict);
    });
    return event_db;
}

function update_content(group_by) // re-group items based on criteria
{
    var event_groups = new Proxy({}, {get: (self, key) => { if (!(key in self)) self[key] = []; return self[key]; }}); // default dict
    var key_map = {event: "title", date: "date_string", category: "categories"};
    var group_key = key_map[group_by.toLowerCase()];
    json_events.forEach(function(pg_event)
    {
        var keys = pg_event[group_key];
        if (!Array.isArray(keys)) keys = [keys];
        keys.forEach((key) => event_groups[key.charAt(0).toUpperCase() + key.slice(1)].push(pg_event));
    });

    html_content = "";
    for(var group_key in event_groups) // {{#each object}} {{@key}}: {{this}} {{/each}}
    {
        html_content += event_template({section: group_key, show_tags: group_by == "event", events: event_groups[group_key]});
    }
    $("#content").html(html_content);
    $("#group_by_dropdown").html("Sort by: " + group_by);

    apply_filters();
}

function apply_filters() // filter items based on search term, date and time filters
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
}

var json_events = [];
$.getJSON("events.json").then((json_payload) =>
{
    json_events = build_event_db(json_payload); // the json events can span a variable number of days, so need to adjust UI range
    days_range = Math.ceil((json_events[json_events.length - 1]["end_epoch"] - json_events[0]["start_epoch"]) / 86400)
    $("#date_range").slider({range: true, min: 0, max: days_range - 1, step: 1, values: [0, days_range - 1]});
    $("#search_box").val(new URL(window.location.href).searchParams.get("search")).trigger("input"); // populate with url request
    update_content("Date");
});

