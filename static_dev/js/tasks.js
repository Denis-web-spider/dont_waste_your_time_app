let task_modal = document.getElementById('task-modal');
let add_task_form = document.forms.add_task_form;
let task_modal_form = task_modal.querySelector('form');

add_task_form.addEventListener('change', time_input_change);
task_modal_form.addEventListener('change', time_input_change);
add_task_form.addEventListener('submit', add_task);

let tasks_table = document.querySelector('table[class~=tasks-table]');

tasks_table.addEventListener('click', show_change_modal);
task_modal.addEventListener('click', process_click_on_modal);

function time_input_change (event) {
    let form = this;
    let start_time_input = form.elements.start;
    let end_time_input = form.elements.end;
    let duration_input = form.elements.duration;

    if (event.target == start_time_input || event.target == end_time_input) {
        duration_input.value = calculate_duration_time(start_time_input, end_time_input);
    } else if (event.target == duration_input) {
        end_time_input.value = calculate_end_time(start_time_input, duration_input);
    }
}

function calculate_duration_time (start_time_input, end_time_input) {
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

function calculate_end_time (start_time_input, duration_input) {
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
        transform_add_task_form(result);
    }
}

function insert_tr_in_tasks_table (data) {
    let tasks_table_tbody = tasks_table.querySelector('tbody');

    let new_tr = document.createElement('tr');
    new_tr.setAttribute('data-task_id', data.id);
    new_tr.setAttribute('data-project', data.project);
    new_tr.setAttribute('data-activity', data.activity);
    new_tr.setAttribute('data-title', data.title);
    new_tr.setAttribute('data-start', data.start.slice(0, -3));
    new_tr.setAttribute('data-end', data.end.slice(0, -3));
    new_tr.setAttribute('data-date', data.date);
    new_tr.setAttribute('data-duration', data.duration.slice(0, -3));
    new_tr.setAttribute('data-bs-toggle', 'modal');
    new_tr.setAttribute('data-bs-target', '#task-modal');

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

function transform_add_task_form(data) {
    let title_input = add_task_form.elements.title;
    let start_input = add_task_form.elements.start;
    let duration_input = add_task_form.elements.duration;

    title_input.value = '';
    start_input.value = data['end'].slice(0, -3);

    let change_event = new Event('change', {bubbles: true, cancelable: true});
    duration_input.dispatchEvent(change_event);
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

////////////////////////////////
////////// modal ////////////
////////////////////////////////

function show_change_modal (event) {
    let target = event.target;
    if (target.tagName != 'tr') target = target.closest('tr');
    if (!target.dataset.task_id) return;

    let modal_form = task_modal.querySelector('form');

    modal_form.elements.title.value = target.dataset.title;
    modal_form.elements.task_id.value = target.dataset.task_id;
    modal_form.elements.start.value = target.dataset.start;
    modal_form.elements.end.value = target.dataset.end;
    modal_form.elements.date.value = target.dataset.date;
    modal_form.elements.duration.value = target.dataset.duration;

    if (!target.dataset.project) {
        modal_form.elements.project.selectedIndex = 0;
    } else {
        for (let option of modal_form.elements.project.options) {
            if (option.text == target.dataset.project) {
                option.selected = true;
            } else {
                option.selected = false;
            }
        }
    }

    if (!target.dataset.activity) {
        modal_form.elements.activity.selectedIndex = 0;
    } else {
        for (let option of modal_form.elements.activity.options) {
            if (option.text == target.dataset.activity) {
                option.selected = true;
            } else {
                option.selected = false;
            }
        }
    }
}

function process_click_on_modal (event) {
    let target = event.target;
    if (!target.dataset.action) return;

    if (target.dataset.action == 'delete') delete_task();
    if (target.dataset.action == 'patch') patch_task();
}

async function delete_task () {
    const csrftoken = getCookie('csrftoken');

    let fetch_url = window.location.origin + '/ru/api/v1/tasks/';

    let modal_form = task_modal.querySelector('form');
    let task_id = modal_form.elements.task_id.value;

    let data = new FormData();
    data.append('task_id', task_id);

    let response = await fetch(fetch_url, {
        method: 'DELETE',
        mode: 'same-origin',
        headers: {
            'X-CSRFToken': csrftoken,
        },
        body: data,
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
        tasks_table.querySelector('tr[data-task_id="' + task_id + '"]').remove()
    }

    close_project_modal();
}

async function patch_task () {
    const csrftoken = getCookie('csrftoken');

    let fetch_url = window.location.origin + '/ru/api/v1/tasks/';

    let modal_form = task_modal.querySelector('form');
    let task_id = modal_form.elements.task_id.value;

    let form_data = new FormData(modal_form);

    let response = await fetch(fetch_url, {
        method: 'PATCH',
        mode: 'same-origin',
        headers: {
            'X-CSRFToken': csrftoken,
        },
        body: form_data,
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
        patch_tr(tasks_table.querySelector('tr[data-task_id="' + task_id + '"]'), result)
    }

    close_project_modal();
}

function patch_tr(tr, data) {
    tr.setAttribute('data-project', data.project);
    tr.setAttribute('data-activity', data.activity);
    tr.setAttribute('data-title', data.title);
    tr.setAttribute('data-start', data.start.slice(0, -3));
    tr.setAttribute('data-end', data.end.slice(0, -3));
    tr.setAttribute('data-date', data.date);
    tr.setAttribute('data-duration', data.duration.slice(0, -3));
    let td_list = tr.querySelectorAll('td');

    td_list[0].textContent = data.title;
    td_list[1].textContent = data.project;
    td_list[2].textContent = data.activity;
    td_list[3].textContent = data.start.slice(0, -3);
    td_list[4].textContent = data.end.slice(0, -3);
    td_list[5].textContent = date_format(data.date);
    td_list[6].textContent = duration_format(data.duration);
}

function close_project_modal () {
    let click_event = new Event('click', {"bubbles":true, "cancelable":true});
    task_modal.querySelector('button[class=btn-close]').dispatchEvent(click_event);
}

////////////////////////////////
////////// end modal ////////////
////////////////////////////////
