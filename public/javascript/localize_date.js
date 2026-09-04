// Format all <time> elements to display in local timezone
Array.from(document.getElementsByTagName("time")).forEach(element => {
    const utc_datetime = new Date(element.getAttribute('datetime'));
    
    const options = {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        timeZoneName: 'short',
        hour: '2-digit',
        minute: '2-digit',
        options: '2-digit'
    };

    // If time is specified, include time
    const time_specified = element.getAttribute('datetime').includes('T');

    if (!time_specified) {
        delete options.hour;
        delete options.minute;
        delete options.timeZoneName;
    }

    const local_datetime_str = utc_datetime.toLocaleString(undefined, options);
    element.textContent = local_datetime_str;
});

Array.from(document.getElementsByClassName("duration")).forEach(element => {
    const all_time_elements = Array.from(element.getElementsByTagName("time"));

    const start_time_element = all_time_elements[0];
    const end_time_element = all_time_elements[1];

    const now = new Date();
    const start_datetime = new Date(start_time_element.getAttribute('datetime'));
    const end_datetime = end_time_element ? new Date(end_time_element.getAttribute('datetime')) : now;

    // Calculate the difference in milliseconds
    const duration_ms = end_datetime - start_datetime;

    // Calculate the different parts of the duration
    const seconds = Math.floor((duration_ms / 1000));
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    const years = Math.floor(days / 365);
    const months = Math.floor((days % 365) / 30); // Approximate months

    // Build the duration string
    var parts = [];
    if (years > 0) parts.push(`${years} year${years > 1 ? 's' : ''}`);
    if (months > 0) parts.push(`${months} month${months > 1 ? 's' : ''}`);
    if (days % 30 > 0) parts.push(`${days % 30} day${(days > 30) !== 1 ? 's' : ''}`);

    parts[0] = `<b>${parts[0]}</b>`;

    const duration_str = parts.length > 0 ? `${parts.join(' ')}` : '0 days';

    element.innerHTML += " ~ " + duration_str;

    if (now <= end_datetime) {
        element.parentElement.innerHTML = "<p class=\"tilting\">Happening right now!</p>" + element.parentElement.innerHTML;
    }
});
