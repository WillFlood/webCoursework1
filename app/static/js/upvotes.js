$(document).on("click", ".upvote-button", function () {
    const heart = $(this).find("i");
    const eventId = $(this).data("event-id");
    const upvotesCountEl = $(`#upvotes-count-${eventId}`);

    $.ajax({
        url: "/upvoteEvent",
        type: "POST",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({ event_id: eventId }),
        dataType: "json",
        success: function (response) {
            if (response.status === "success") {
                // Update the upvotes count
                upvotesCountEl.text(response.upvotes_count);

                // Toggle heart icon class and color
                if (heart.hasClass("far")) {
                    heart.removeClass("far text-muted").addClass("fas text-danger");
                } else {
                    heart.removeClass("fas text-danger").addClass("far text-muted");
                }
            } else {
                alert(response.message); // Error message
            }
        },
        error: function (error) {
            console.error("Error processing Upvote:", error);
            alert("An error occurred. Please try again.");
        }
    });
});