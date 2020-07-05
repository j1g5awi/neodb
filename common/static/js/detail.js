$(document).ready( function() {
    
    $(".modal-close").on('click', function() {
        $(this).parents(".modal").hide();
        $(".bg-mask").hide();
    });

    // pop up new rating modal
    $("#addMarkPanel button").each(function() {
        $(this).click(function(e) {
            e.preventDefault();
            let title = $(this).text().trim();
            $(".mark-modal__title").text(title);
            $(".mark-modal__body textarea").val("");
            let status = $(this).data('status')
            $("input[name='status'][value='"+status+"']").prop("checked", true)
            $(".bg-mask").show();
            $(".mark-modal").show();

            // if wish, hide rating widget in modal
            if ($(this).attr("id") == "wishButton") {
                console.log($(this).attr("id"))
                $(".mark-modal .rating-star-edit").hide();
            } else {
                $(".mark-modal .rating-star-edit").show();
            }

        });
    })

    // pop up modify mark modal
    $(".mark-panel a.edit").click(function(e) {
        e.preventDefault();
        let title = $(".mark-panel__status").text().trim();
        $(".mark-modal__title").text(title);
        $(".bg-mask").show();
        $(".mark-modal").show();
    });

    // readonly star rating of detail display section
    let ratingLabels = $("#main .rating-star");
    $(ratingLabels).each( function(index, value) {
        let ratingScore = $(this).data("rating-score") / 2;
        $(this).starRating({
            initialRating: ratingScore,
            readOnly: true,
        });
    });
    // readonly star rating at aside section
    ratingLabels = $("#aside .rating-star");
    $(ratingLabels).each( function(index, value) {
        let ratingScore = $(this).data("rating-score") / 2;
        $(this).starRating({
            initialRating: ratingScore,
            readOnly: true,
            starSize: 15,
        });
    });

    // editable rating star in modal
    ratingLabels = $("#modals .rating-star-edit");
    $(ratingLabels).each( function(index, value) {
        let ratingScore = $("input[type='hidden'][name='rating']").val() / 2;
        let label = $(this);
        label.starRating({
            initialRating: ratingScore,
            starSize: 20,
            onHover: function(currentIndex, currentRating, $el){
                $("input[type='hidden'][name='rating']").val(currentIndex);
            },
            onLeave: function(currentIndex, currentRating, $el){
                $("input[type='hidden'][name='rating']").val(currentRating * 2);
            }            
        });
    });
    
    // hide rating star when select wish
    const WISH_CODE = 1;
    if ($("#statusSelection input[type='radio']:checked").val() == WISH_CODE) {
        $(".mark-modal .rating-star-edit").hide();
    }
    $("#statusSelection input[type='radio']").click(function() {
        if ($(this).val() == WISH_CODE) {
            $(".mark-modal .rating-star-edit").hide();
        } else {
            $(".mark-modal .rating-star-edit").show();
        }
        
    });

    // show confirm modal
    $(".mark-panel a.delete").click(function(e) {
        e.preventDefault();
        $(".confirm-modal").show();
        $(".bg-mask").show();
    });

    // confirm modal
    $(".confirm-modal input[type='submit']").click(function(e) {
        e.preventDefault();
        $(".mark-panel form").submit();
    });
    

    // hide long text
    let copy = $(".entity-desc__content").clone()
        .addClass('entity-desc__content--folded')
        .css("visibility", "hidden");

    $(".entity-desc__content").after(copy);
    if ($(".entity-desc__content").height() > copy.height()) {
        $(".entity-desc__content").addClass('entity-desc__content--folded');
        $(".entity-desc__unfold-button").removeClass("entity-desc__unfold-button--hidden");
        console.log($(".entity-desc__content").height())
        console.log(copy.height())
    }
    copy.remove();

    // expand hidden long text
    $(".entity-desc__unfold-button a").click(function() {
        $(".entity-desc__content").removeClass('entity-desc__content--folded');
        $(".entity-desc__unfold-button").remove();
    });
});