var activity = "";
$(document).ready(function(){
    let dealed;
    let dma;
    let dmt;
    let dpt;
    let dmc;
    // inbound_ext_values = {};
    let jsonResponse;
    var min_selected_date = "";
    var max_selected_date = "";
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
    var code = "";
    var date_set = false;
    
    /*$("#activity").click(function(){
        code =  $(this).val();
        activity = $("#activity :selected").text();
        console.log(`Code : ${code}`);
        console.log(`Activity : ${activity}`);
    });*/

    $("#activity").click(getActivity);
    $("#distrib").click(getDistrib);

    function getDistrib(event){
        distrib_value = event.target.value
        // console.log(`Distrib : ${distrib_value}`);
    }
    
    function getActivity(event){
        code = event.target.value;
        distrib_value = $("#distrib").val()
        console.log(`Code : ${code}`);
        console.log(`Activity : ${activity}`);
        console.log(`Distrib code: ${distrib_value}`)
    }
    
    $("#filter-btn").click(function(event){
        activity = $("#activity :selected").text();
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
                    'time_interval': distrib_value
            }
            if (min_selected_date){
                // alert(min_selected_date)
                console.log(inbound_ext_values);
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
                        console.log(JSON.parse(response["message"]));
                        jsonResponse = JSON.parse(response["message"]);
                        graphJson = JSON.parse(response["graph_json"]);
                        dm_graph_json = JSON.parse(response["dm_graph_json"])
                        // document.querySelector("#graph").innerHTML = '';
                        activity = response["activity"];
                        // console.log(activity);
                        fillKPIs(jsonResponse, activity);
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
    
    $("#view").click(function(event){
        event.preventDefault();
        distrib_text = $("#distrib :selected").text()
        console.log(`Distrib text: ${distrib_text}`)
        console.log(`Distrib : ${distrib_value}`);
        if(distrib_value){
            $.ajax({
                type: 'POST',
                url: '/dashboard/visualize/',
                data: JSON.stringify({'code': distrib_value}),
                contentType: 'application/json',
                headers: {
                    "X-CSRFToken": getCookie("csrftoken")
                },
                success: function(response){
                    graphJson = JSON.parse(response["graph_json"])
                    dmGraphJson = JSON.parse(response["dm_graph_json"])
                    updateGraph(graphJson, dmGraphJson);
                },
                error: function(xhr, errmsg, err){
                    console.log(`${xhr.status}: ${xhr.responseText}`);
                }
            })
        }
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
    
    function fillKPIs(response, activity){
        $("#dealed .nb").text(response["dealed_calls"]);
        $("#wait .nb").text(response["dma"]);
        $("#processed .nb").text(response["dmt"]);
        $("#post_process .nb").text(response["dpt"]);
        $("#com .nb").text(response["dmc"]);
        // $("#date").text(min_selected_date);
        $("#activity-name").text(activity);
        Plotly.purge('calls_and_sl');
        Plotly.purge('dms');
        Plotly.plot('calls_and_sl', graphJson.data, graphJson.layout);
        Plotly.plot('dms', dm_graph_json.data, dm_graph_json.layout);
        // console.log(`Activity ${activity}`);
    }

    function updateGraph(graph_json, dm_graph_json){
        Plotly.purge('calls_and_sl');
        Plotly.purge('dms');
        Plotly.plot('calls_and_sl', graph_json.data, graph_json.layout);
        Plotly.plot('dms', dm_graph_json.data, dm_graph_json.layout);
        // Plotly.plot('dms', dm_graph_json, graph_json.data, graph_json.layout);
    }
});