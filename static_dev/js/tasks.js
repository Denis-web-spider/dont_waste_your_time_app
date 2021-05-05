let add_task_form = document.forms.add_task_form;

let start_time_input = add_task_form.elements.start;
let end_time_input = add_task_form.elements.end;
let duration_input = add_task_form.elements.duration;

add_task_form.addEventListener('change', time_input_change);
add_task_form.addEventListener('submit', add_task);

let tasks_table = document.querySelector('table[class~=tasks-table]');

function time_input_change (event) {
    if (event.target == start_time_input || event.target == end_time_input) {
        duration_input.value = calculate_duration_time();
    } else if (event.target == duration_input) {
        end_time_input.value = calculate_end_time();
    }
}

function calculate_duration_time () {
    let [start_hours, start_minutes] = start_time_input.value.split(':');
    let [end_hours, end_minutes] = end_time_input.value.split(':');

    let start_time_in_minutes = +start_hours * 60 + +start_minutes;
    let end_time_in_minutes = +end_hours * 60 + +end_minutes;

    let duration_time;
    if (end_time_in_minutes - start_time_in_minutes > 0) {
        duration_time = end_time_in_minutes - start_time_in_minutes;
    } else if (end_time_in_minutes - start_time_in_minutes < 0) {
        duration_time = (end_time_in_minutes - start_time_in_minutes) + 24 * 60;
    } else if (end_time_in_minutes - start_time_in_minutes == 0) {
        duration_time = 0;
    }
    return convert_minutes_in_time_string(duration_time);
}

function calculate_end_time () {
    let [start_hours, start_minutes] = start_time_input.value.split(':');
    let [duration_hours, duration_minutes] = duration_input.value.split(':');

    let start_time_in_minutes = +start_hours * 60 + +start_minutes;
    let duration_time_in_minutes = +duration_hours * 60 + +duration_minutes;

    let end_time;
    if (start_time_in_minutes + duration_time_in_minutes < 24 * 60) {
        end_time = start_time_in_minutes + duration_time_in_minutes;
    } else if (start_time_in_minutes + duration_time_in_minutes > 24 * 60) {
        end_time = (start_time_in_minutes + duration_time_in_minutes) - 24 * 60;
    } else {
        end_time = 0;
    }
    return convert_minutes_in_time_string(end_time);
}

function convert_minutes_in_time_string (minutes) {
    let hours = Math.floor(minutes / 60);
    minutes = (minutes % 60);

    if (hours < 10) hours = '0' + hours;
    if (minutes < 10) minutes = '0' + minutes;

    return hours + ':' + minutes;
}

async function add_task (event) {
    event.preventDefault();
    const csrftoken = getCookie('csrftoken');

    let fetch_url = window.location.origin + '/ru/api/v1/tasks/';

    let form_data = new FormData(add_task_form);

    let response = await fetch(fetch_url, {
        method: 'POST',
        mode: 'same-origin',
        headers: {
            'X-CSRFToken': csrftoken,
        },
        body: form_data
    })

    let result = await response.json();

    console.log(result);

    if (result.message) {
        alert_massage(result.message, 'success');
    }

    if (result.errors) {
        for (let error_name in result.errors) {
            let error = result.errors[error_name];
            alert_massage(error, 'danger', 10);
        }
    } else {
        insert_tr_in_tasks_table(result);
    }
}

function insert_tr_in_tasks_table (data) {
    let tasks_table_tbody = tasks_table.querySelector('tbody');

    let new_tr = document.createElement('tr');

    new_tr.append(
        create_td(data.title)
    );
    new_tr.append(
        create_td(data.project)
    );
    new_tr.append(
        create_td(data.activity)
    );
    new_tr.append(
        create_td(data.start.slice(0, -3))
    );
    new_tr.append(
        create_td(data.end.slice(0, -3))
    );
    new_tr.append(
        create_td(date_format(data.date))
    );
    new_tr.append(
        create_td(duration_format(data.duration))
    );

    tasks_table_tbody.prepend(new_tr);
}

function create_td (content) {
    let new_td = document.createElement('td');
    new_td.textContent = content;
    return new_td;
}

function duration_format (duration_time_string) {
    let hours = parseInt(duration_time_string.split(':')[0]);
    let minutes = parseInt(duration_time_string.split(':')[1]);

    if (minutes < 10) minutes = '0' + minutes;

    return hours + ':' + minutes;
}

function date_format (date_string) {
    let date = new Date(Date.parse(date_string));
    if (date == 'Invalid Date') return date_string;

    let day = date.getDate();
    if (day < 10) day = '0' + day;

    let month = date.getMonth();
    if (month < 10) month = '0' + month;

    let year = date.getFullYear();

    return day + '.' + month + '.' + year
}
