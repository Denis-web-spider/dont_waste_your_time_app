let add_project_form = document.forms.add_project;
let projects_table = document.querySelector('[class~=projects-table]');
let project_modal = document.getElementById('project-modal');

add_project_form.addEventListener('submit', add_project);
projects_table.addEventListener('click', show_change_modal);
project_modal.addEventListener('click', process_click_on_modal);

async function add_project (event) {
    event.preventDefault();
    const csrftoken = getCookie('csrftoken');

    let fetch_url = window.location.origin + '/ru/api/v1/projects/';

    let form_data = new FormData(add_project_form);

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
        insert_tr_in_projects_table(result);
    }
}

function insert_tr_in_projects_table (data) {
    let tbody = projects_table.querySelector('tbody');

    let tr = document.createElement('tr');
    tr.setAttribute('data-project_id', data.id);
    tr.setAttribute('data-activity', data.activity);
    tr.setAttribute('data-status', data.status);
    tr.setAttribute('data-title', data.title);
    tr.setAttribute('data-bs-toggle', 'modal');
    tr.setAttribute('data-bs-target', '#project-modal');

    tr.append(
        create_td(data.title)
    );
    tr.append(
        create_td(data.status)
    );
    tr.append(
        create_td(data.activity)
    );
    tr.append(
        create_td(data.total_time)
    );
    tr.append(
        create_td(datetime_format(data.created))
    );
    tr.append(
        create_td(datetime_format(data.finished))
    );

    tbody.prepend(tr);
}

function create_td (content) {
    let td = document.createElement('td');
    td.textContent = content;
    return td
}

function datetime_format (date_string) {
    let datetime = new Date(Date.parse(date_string));
    if (datetime == 'Invalid Date') return date_string;

    let day = datetime.getDate();
    if (day < 10) day = '0' + day;

    let month = datetime.getMonth();
    if (month < 10) month = '0' + month;

    let year = datetime.getFullYear();

    let hours = datetime.getHours();
    if (hours < 10) hours = '0' + hours;

    let minutes = datetime.getMinutes();
    if (minutes < 10) minutes = '0' + minutes;

    return day + '.' + month + '.' + year + ' ' + hours + ':' + minutes
}

////////////////////////////////
////////// modal ////////////
////////////////////////////////

function show_change_modal (event) {
    let target = event.target;
    if (target.tagName != 'tr') target = target.closest('tr');
    if (!target.dataset.project_id) return;

    let modal_form = project_modal.querySelector('form');

    modal_form.elements.title.value = target.dataset.title;
    modal_form.elements.project_id.value = target.dataset.project_id;

    for (let option of modal_form.elements.status.options) {
        if (option.text == target.dataset.status || option.value == target.dataset.status) {
            option.selected = true;
        } else {
            option.selected = false;
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

    if (target.dataset.action == 'delete') delete_project();
    if (target.dataset.action == 'patch') patch_project();
}

async function delete_project () {
    const csrftoken = getCookie('csrftoken');

    let fetch_url = window.location.origin + '/ru/api/v1/projects/';

    let modal_form = project_modal.querySelector('form');
    let project_id = modal_form.elements.project_id.value;

    let data = new FormData();
    data.append('project_id', project_id);

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
        projects_table.querySelector('tr[data-project_id="' + project_id + '"]').remove()
    }

    close_project_modal();
}

async function patch_project () {
    const csrftoken = getCookie('csrftoken');

    let fetch_url = window.location.origin + '/ru/api/v1/projects/';

    let modal_form = project_modal.querySelector('form');
    let project_id = modal_form.elements.project_id.value;

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
        patch_tr(projects_table.querySelector('tr[data-project_id="' + project_id + '"]'), result)
    }

    close_project_modal();
}

function patch_tr(tr, data) {
    tr.setAttribute('data-title', data.title);
    tr.setAttribute('data-activity', data.activity);
    tr.setAttribute('data-status', data.status);
    let td_list = tr.querySelectorAll('td');

    td_list[0].textContent = data.title;
    td_list[1].textContent = data.status;
    td_list[2].textContent = data.activity;
    td_list[4].textContent = datetime_format(data.created);
    td_list[5].textContent = datetime_format(data.finished);
}

function close_project_modal () {
    let click_event = new Event('click', {"bubbles":true, "cancelable":true});
    project_modal.querySelector('button[class=btn-close]').dispatchEvent(click_event);
}

////////////////////////////////
////////// end modal ////////////
////////////////////////////////
