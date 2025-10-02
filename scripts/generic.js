function replaceTimePeriodStrings() {
    const today = new Date();

    document.querySelectorAll('.time-period-label').forEach(label => {
        const yStart = parseInt(label.dataset.yStart);
        const mStart = parseInt(label.dataset.mStart);
        const dStart = parseInt(label.dataset.dStart);

        var yEnd = parseInt(label.dataset.yEnd);
        var mEnd = parseInt(label.dataset.mEnd);
        var dEnd = parseInt(label.dataset.dEnd);

        // -1 indicates to use present day
        const usePresentDay = (yEnd === -1 || mEnd === -1 || dEnd === -1);

        const endDate = usePresentDay ? today : new Date(yEnd, mEnd - 1, dEnd);

        const startDate = new Date(yStart, mStart - 1, dStart);

        var years = endDate.getFullYear() - startDate.getFullYear();
        var months = endDate.getMonth() - startDate.getMonth();
        var days = endDate.getDate() - startDate.getDate();

        if (days < 0) {
            months--;
            const prevMonth = new Date(endDate.getFullYear(), endDate.getMonth(), 0);
            days += prevMonth.getDate();
        }

        if (months < 0) {
            years--;
            months += 12;
        }

        // Format the label
        const pad = n => String(n).padStart(2, '0');
        label.innerHTML = `<span style="color: #ff0000">${pad(years)}Y</span> ${pad(months)}M ${pad(days)}D ${usePresentDay ? "+" : ""}`;
    });
}

function populateWebsiteModeDropdown(currentMode) {
    const ALL_WEBSITE_MODES = ["professional", "articles", "cooking"];
    const WEBSITE_MODE_DESCRIPTIONS = {
        "professional": "Professional information",
        "articles": "Notes on technology",
        "cooking": "My cooking book",
    }
    
    // Populate the dropdown
    const dropDownElement = document.getElementById("website-mode-drop-down");

    modeListInnerHTML = ``;

    ALL_WEBSITE_MODES.forEach(mode => {
        // Populate the mode list
        modeListInnerHTML += `
            <div class="mode-entry">
                <h1 ${mode == currentMode ? `id="current"` : ``}>${mode.toUpperCase()}</h1>
                <p>${WEBSITE_MODE_DESCRIPTIONS[mode]}</p>
            </div>
        `
    });

    dropDownElement.innerHTML = `
        <h1>${currentMode.toUpperCase()}</h1>
        <p>${WEBSITE_MODE_DESCRIPTIONS[currentMode]}</p>
        <div class="content">
            ${modeListInnerHTML}
        </div>
    `

    // Detect click on any mode entry
    document.querySelector('.drop-down .content').addEventListener('click', function(event) {
        const modeEntry = event.target.closest('.mode-entry');

        if (modeEntry) {
            const h1 = modeEntry.querySelector('h1');
            const parsedModeName = h1.textContent.toLowerCase();

            // Push new URL
            const newUrl = new URL(window.location);
            newUrl.search = "";
            newUrl.searchParams.set("page", parsedModeName);
            history.pushState({"page": parsedModeName}, "", newUrl);

            // Load page
            setPage(`${parsedModeName}.html`);
        }
    });
}

// Navigation hander, because the website operates on loading & unloading the content in <body> instead of reloading the entire page (Which flashes the user with white)
async function setPage(page) {
    const url = `/pages/${page}`;
    console.log(url);
    const response = await fetch(url);
    if (!response.ok) {
        log.error("Could not find requested page");
        return;
    }
    const htmlText = await response.text();

    const parser = new DOMParser();
    const newDoc = parser.parseFromString(htmlText, 'text/html');

    const newContent = newDoc.querySelector('#page-content');
    const appRoot = document.getElementById('page-content');

    if (newContent && appRoot) {
        appRoot.innerHTML = newContent.innerHTML;
    } else {
        console.error("Failed to find page-content in fetched page");
    }

    onPageLoad();
}

function onPageLoad() {
    const urlParams = new URLSearchParams(window.location.search);
    var page = urlParams.get("page");
    if (page == null) { page = "professional"; }

    populateWebsiteModeDropdown(page);
    replaceTimePeriodStrings();
}

function setPageFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    var page = urlParams.get("page");
    if (page == null) { page = "professional"; }

    switch (page) {
        case "cooking":
            var recipe = urlParams.get("recipe");

            if (recipe == null) {
                setPage("cooking.html");
            } else {
                setPage(`cooking_${recipe}.html`);
            }

            break;
    
        default:
            setPage(`${page}.html`);
            break;
    }

}

// First website load, set the page
setPageFromURL();

// Bind URL change to page changing request
function historyChanged(popstateEvent) {
    setPageFromURL();
}
window.addEventListener("popstate", historyChanged);
