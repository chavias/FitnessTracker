// const SCRIPT_ROOT = {{ request.script_root|tojson }};

async function updateCalendarHeatmap() {

    const response = await fetch(`/api/training_sessions`);
    const rawData = await response.json();

    const templateMap = new Map();
    rawData.forEach(item => {
        templateMap.set(item.Id, item.Template);
    });

    // Extract dates from rawData
    const startDate = rawData.length
        ? new Date(Math.max(...rawData.map(d => new Date(d.Date).getTime())))
        : new Date();
    startDate.setUTCHours(0, 0, 0, 0);


    const calenderRange = 4;
    startDate.setUTCMonth(startDate.getUTCMonth() + 1 - calenderRange);

    const updatedData = rawData.map(item => {
        const newDate = new Date(item.Date); 
        newDate.setDate(newDate.getDate() + 1); 
        return {
            ...item,
            Date: newDate
        };
    });

    const cal = new CalHeatmap();
    cal.paint({
        itemSelector: "#cal-heatmap",
        domain: { type: "month", label: { position: "top" } },
        subDomain: { type: "day", radius: 1 },
        date: { start:  startDate}, // Adjusted to a realistic start date
        range: calenderRange, // Show 12 months for a full year
        scale: {
            color: {
                type: "threshold", // Better for discrete values
                domain: [1, 2, 3, 4, 5, 6], // List the numbers you want to assign colors to
                range: ['#FF6347', '#4682B4', '#32CD32', '#FFD700', '#8A2BE2', '#FF4500'], // Assign random colors for each number
                // scheme: "Blues"CD
            }
        },
        data: {
            source: updatedData,
            type: "json",
            x: "Date",
            y: "Id",
            groupY: 'max',
        },
    },
        [
            [
                Tooltip, {
                    text: function (date, value, dayjsDate) {
                        // You can now use SCRIPT_ROOT in your URL generation
                        // const sessionId = item.SessionId;
                        const url = `${SCRIPT_ROOT}}`;
                        return (
                            `<a href="${url}" target="_blank">${value ? templateMap.get(value) : 'No Training'}</a> on ${dayjsDate.format('LL')}`
                        );
                    },
                },
            ],
            // [
            //     Legend,
            //     {
            //         tickSize: 0,
            //         width: 180,
            //         itemSelector: '#ex-year-legend',
            //         label: 'Workouts',
            //     },
            // ],
            //     [
            //     CalendarLabel,
            //     {
            //         width: 30,
            //         textAlign: 'start',
            //         text: () => dayjs.weekdaysShort().map((d, i) => (i % 2 == 0 ? '' : y)),
            //     },
            // ],
        ]
    );
}

document.addEventListener("DOMContentLoaded", async function () {
    await updateCalendarHeatmap();
});