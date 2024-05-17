$(document).ready(function(){
    var min_selected_date = ""
    var max_selected_date = ""
    var mindate = new Date("2021-04-20");
    /*mindate.setDate(mindate.getDate() - 8);*/
    var maxdate = new Date();
    maxdate.setDate(maxdate.getDate() - 1);
    var cleared_dates = [];
    let dd;
    $('#minMaxExample').datepicker({
        // language: 'en',
        range : true,
        minDate : mindate,
        maxDate : maxdate,
        multipleDates: true,
        multipleDatesSeparator: " - ",
        onSelect: function(formattedDate, dates, inst){
            // console.log(date.toLocaleDateString());
            cleared_dates = [];
            console.log(dates.length);
            // console.log(dates);
            if (dates.length > 0){
                dates.forEach(function(date){
                    cleared_dates.push(date.toLocaleDateString());
                })
                // dd = dates;
            }
            console.log(cleared_dates);
            // else if (dates.length == 1){
            //     cleared_dates = dates[0].toLocaleDateString();
            // }
        }
    });
    var activity = "";
    var code = "";
    var date_set = false;
    
    $("#activity").click(function(){
        code =  $(this).val();
        activity = $("#activity :selected").text();
    });
    
    $("button").click(function(event){
        
        event.preventDefault();
        console.log(cleared_dates);
        // console.log(dd);
        console.log(`Activité  - ${activity}`);
        console.log(`Code - ${code}`);
        min_selected_date = cleared_dates[0];
        if (code && cleared_dates.length > 0){
            if(cleared_dates.length == 1){
                max_selected_date = min_selected_date;
            }else{
                max_selected_date = cleared_dates[1];
            }

            $.ajax({
                type: 'POST',
                // url: '/process'
            })

            console.log(`Min date - ${min_selected_date}
            Max date - ${max_selected_date}`);
        }
        // if (code && cleared_dates.length != 0){
        //     min_selected_date = cleared_dates[0];
        //     if (cleared_dates.length = 1){
        //         max_selected_date = cleared_dates[0];
        //     }
        //     else{
        //         max_selected_date = cleared_dates[1]
        //     }
        //     console.log("--------Activity fully loaded-------");
        //     console.log(`Min date - ${min_selected_date}
        //     Max date - ${max_selected_date}
        //     `);
        //     console.log(cleared_dates);
        // }
    });
});