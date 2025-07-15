function replaceTimePeriodStrings() {
    const today = new Date();

    document.querySelectorAll('.time-period-label').forEach(label => {
        const yStart = parseInt(label.dataset.yStart);
        const mStart = parseInt(label.dataset.mStart);
        const dStart = parseInt(label.dataset.dStart);

        let yEnd = parseInt(label.dataset.yEnd);
        let mEnd = parseInt(label.dataset.mEnd);
        let dEnd = parseInt(label.dataset.dEnd);

        // -1 indicates to use present day
        const usePresentDay = (yEnd === -1 || mEnd === -1 || dEnd === -1);

        const endDate = usePresentDay ? today : new Date(yEnd, mEnd - 1, dEnd);

        const startDate = new Date(yStart, mStart - 1, dStart);

        let years = endDate.getFullYear() - startDate.getFullYear();
        let months = endDate.getMonth() - startDate.getMonth();
        let days = endDate.getDate() - startDate.getDate();

        if (days < 0) {
            months--;
            const prevMonth = new Date(endDate.getFullYear(), endDate.getMonth(), 0);
            days += prevMonth.getDate();
        }

        if (months < 0) {
            years--;
            months += 12;
        }

        const pad = n => String(n).padStart(2, '0');
        label.innerHTML = `<span style="color: #ff0000">${pad(years)}Y</span> ${pad(months)}M ${pad(days)}D ${usePresentDay ? "+" : ""}`;
    });
}

replaceTimePeriodStrings();
