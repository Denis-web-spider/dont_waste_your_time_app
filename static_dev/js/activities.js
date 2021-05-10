let add_activity_form = document.forms.add_activity;
let activities_table = document.querySelector('table[class~=activities-table]');
let activity_modal = document.getElementById('activity-modal');

add_activity_form.addEventListener('submit', add_activity);

document.body.addEventListener('click', show_change_modal);
activity_modal.addEventListener('click', process_click_on_modal);

async function add_activity (event) {
    event.preventDefault();
    const csrftoken = getCookie('csrftoken');

    let fetch_url = window.location.origin + '/ru/api/v1/activities/';

    let form_data = new FormData(add_activity_form);

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
        update_parents_choices(result);
        insert_tr_in_activities_table(result);
        update_activities_html_list(result);
    }
}

function update_parents_choices (data) {
    let parent_select = add_activity_form.elements.parent;
    let new_option = new Option(data.title, data.id);

    if (data.parent != '-') {
        for (let option of parent_select.options) {
            if (option.text == data.parent) {
                option.after(new_option);
            }
        }
    } else {
        parent_select.append(new_option);
    }
}

function remove_from_parents_choices (title) {
    let parent_select = add_activity_form.elements.parent;

    for (let option of parent_select.options) {
        if (option.text == title) option.remove();
    }
}

function replace_parent_choices (new_option_contents) {
    let parent_select = add_activity_form.elements.parent;
    let new_select = parent_select.cloneNode();

    for (let option_content of new_option_contents) {
        new_select.append(
            new Option(option_content.text, option_content.value)
        );
    }

    parent_select.replaceWith(new_select);
}

function insert_tr_in_activities_table (data) {
    let activities_table_tbody = activities_table.querySelector('tbody');

    let new_tr = document.createElement('tr');
    new_tr.setAttribute('data-activity_id', data.id)
    new_tr.setAttribute('data-title', data.title)
    new_tr.setAttribute('data-color', data.color)
    new_tr.setAttribute('data-parent', data.parent)
    new_tr.setAttribute('data-bs-toggle', 'modal')
    new_tr.setAttribute('data-bs-target', '#activity-modal')

    new_tr.append(
        create_new_td(data.title)
    );

    let color_square_div = document.createElement('div');
    color_square_div.classList.add('color-square');
    color_square_div.style.backgroundColor = data.color;
    let color_td = create_new_td('');
    color_td.append(color_square_div);

    new_tr.append(
        color_td
    );

    new_tr.append(
        create_new_td(data.parent)
    );

    new_tr.append(
        create_new_td(data.total_time)
    );

    if (data.parent != '-') {
        for (tr of activities_table_tbody.querySelectorAll('tr')) {
            if (tr.dataset.title == data.parent) {
                tr.after(new_tr);
            }
        }
    } else {
        activities_table_tbody.append(new_tr);
    }
}

function create_new_td (content) {
    let td = document.createElement('td');
    td.textContent = content;
    return td;
}

function update_activities_html_list (data) {

    let activities_list = document.querySelector('div[class~=activities-list]');
    let new_activities_list = activities_list.cloneNode();

    for (let branch of data.activities_html_list) {
        let new_div = document.createElement('div');
        new_div.classList.add('col-lg-3');
        new_div.innerHTML = branch;

        new_activities_list.append(new_div);
    }

    activities_list.replaceWith(new_activities_list);
}

////////////////////////////////
////////// modal ////////////
////////////////////////////////

function show_change_modal (event) {
    let target = event.target;
    if (!target.dataset.activity_id) target = target.closest('[data-activity_id]');
    if (!target) return;
    if (!target.dataset.activity_id) return;

    let modal_form = activity_modal.querySelector('form');

    modal_form.elements.title.value = target.dataset.title;
    modal_form.elements.activity_id.value = target.dataset.activity_id;
    modal_form.elements.color.value = target.dataset.color;

    for (let option of modal_form.elements.parent.options) {
        if (option.text == target.dataset.parent) {
            option.selected = true;
        } else {
            option.selected = false;
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

    let fetch_url = window.location.origin + '/ru/api/v1/activities/';

    let modal_form = activity_modal.querySelector('form');
    let activity_id = modal_form.elements.activity_id.value;
    let activity_title = modal_form.elements.title.value;

    let data = new FormData();
    data.append('activity_id', activity_id);

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
        activities_table.querySelector('tr[data-activity_id="' + activity_id + '"]').remove();
        update_activities_html_list(result);
        remove_from_parents_choices(activity_title);
    }

    close_project_modal();
}

async function patch_project () {
    const csrftoken = getCookie('csrftoken');

    let fetch_url = window.location.origin + '/ru/api/v1/activities/';

    let modal_form = activity_modal.querySelector('form');
    let activity_id = modal_form.elements.activity_id.value;

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
        patch_tr(activities_table.querySelector('tr[data-activity_id="' + activity_id + '"]'), result);
        update_activities_html_list(result);
        replace_parent_choices(result.activities);
    }

    close_project_modal();
}

function patch_tr(tr, data) {
    tr.setAttribute('data-title', data.title);
    tr.setAttribute('data-color', data.color);
    tr.setAttribute('data-parent', data.parent);
    let td_list = tr.querySelectorAll('td');

    td_list[0].textContent = data.title;
    td_list[1].querySelector('div').style.backgroundColor = data.color;
    td_list[2].textContent = data.parent;
    td_list[3].textContent = data.total_time;
}

function close_project_modal () {
    let click_event = new Event('click', {"bubbles":true, "cancelable":true});
    activity_modal.querySelector('button[class=btn-close]').dispatchEvent(click_event);
}

////////////////////////////////
////////// end modal ////////////
////////////////////////////////
