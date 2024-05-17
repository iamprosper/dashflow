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
            
            console.log(`Min date - ${min_selected_date}
            Max date - ${max_selected_date}`);
            var inbound_ext_values = {
                'code': code,
                'activity': activity,
                'start_date': min_selected_date,
                'end_date': max_selected_date,
            }
            if (min_selected_date){
                // alert(min_selected_date)
                $.ajax({
                    type: 'POST',
                    url: '/dashboard/',
                    data: JSON.stringify(inbound_ext_values),
                    contentType: 'application/json',
                    headers: {
                        "X-CSRFToken": getCookie("csrftoken")
                    },
                    success: function(response){
                        console.log(response);
                    },
                    error: function(xhr, errmsg, err){
                        console.log(`${xhr.status}: ${xhr.responseText}`);
                    }
                    // url: '/process'
                })
            }

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

    function getCookie(name){
        var cookieValue = null;
        if (document.cookie && document.cookie != ''){
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++){
                var cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) == (name + '=')){
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});