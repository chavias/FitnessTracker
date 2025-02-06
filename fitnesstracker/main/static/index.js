async function updateCalendarHeatmap() {

    const response = await fetch(`/api/training_sessions`);
    const rawData = await response.json();

    const templateMap = new Map();
    rawData.forEach(item => {
        templateMap.set(item.Id, item.Template);
    });


    const cal = new CalHeatmap();
    cal.paint({
        itemSelector: "#cal-heatmap",
        domain: { type: "month", label: { position: "top" } },
        subDomain: { type: "day", radius: 2 },
        date: { start: new Date("2025-01-01") }, // Adjusted to a realistic start date
        range: 4, // Show 12 months for a full year
        scale: {
            color: {
                type: "threshold", // Better for discrete values
                domain: [1, 2, 3, 4, 5, 6], // List the numbers you want to assign colors to
                range: ['#FF6347', '#4682B4', '#32CD32', '#FFD700', '#8A2BE2', '#FF4500'], // Assign random colors for each number
                // scheme: "Blues"
            }
        },
        data: {
            source: rawData,
            type: "json",
            x: "Date",
            y: "Id",
            groupY: 'max',
        },
    },
        [
            [
                Tooltip,
                {
                    text: function (date, value, dayjsDate) {
                        return (
                            `<a href="{{ url_for('workout_sessions.create_session') }}" target="_blank">${value ? templateMap.get(value) : 'No Training'}</a> on ${dayjsDate.format('LL')}`
                        );
                    },
                }
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