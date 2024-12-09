$(document).ready(function () {
    //RSVP button, when clicked
    $(document).on("click", ".rsvp-button", function () {
        const button = $(this);
        const eventId = button.data("event-id");
        const attendeesCountEl = $(`#attendees-count-${eventId}`);

        $.ajax({
            url: "/rsvpEvent",
            type: "POST",
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify({ event_id: eventId }),
            dataType: "json",
            success: function (response) {
                if (response.status === "success") {
                    //Update the attendees count
                    attendeesCountEl.text(response.attendees_count);

                    //Toggle button text and style
                    if (button.text().trim() === "RSVP") {
                        button.text("Cancel RSVP").removeClass("btn-primary").addClass("btn-danger");
                    } else {
                        button.text("RSVP").removeClass("btn-danger").addClass("btn-primary");
                    }
                } else {
                    alert(response.message); //Error message
                }
            },
            error: function (error) {
                console.error("Error processing RSVP:", error);
                alert("An error occurred. Please try again.");
            }
        });
    });
});
