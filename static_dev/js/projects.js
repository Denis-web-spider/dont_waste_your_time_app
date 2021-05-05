let add_project_form = document.forms.add_project;
let projects_table = document.querySelector('[class~=projects-table]');

add_project_form.addEventListener('submit', add_project);

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
