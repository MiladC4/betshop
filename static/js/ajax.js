    $(document).ready(function(){
        var betForm = $(".form-betslip-ajax")

        betForm.submit(function(event){
            event.preventDefault();
            console.log("form did not send")
            var thisForm = $(this)
            var actionEndpoint = thisForm.attr("action");
            var httpMethod = thisForm.attr("method");
            var formData = thisForm.serialize();

            $.ajax({
                url: actionEndpoint,
                method: httpMethod,
                data: formData,
                success: function(data){
                    var slipOdds = $(".betslip-span")
                    slipOdds.text(data.slipOdds + " $" + data.slipDue)
                },
                error: function(errorData){
                    console.log(errorData)
                }
            })
        })

        var betForm = $(".form-parley-ajax");

        betForm.submit(function(event){
            event.preventDefault();
            console.log("form did not send");
            var thisForm = $(this);
            var actionEndpoint = thisForm.attr("action");
            var httpMethod = thisForm.attr("method");
            var formData = thisForm.serialize();

            $.ajax({
                url: actionEndpoint,
                method: httpMethod,
                data: formData,
                dataType: 'json',
                success: function(data){
                    var slipOdds = $(".betslip-span")

                    // console.log(data.slipBets);
                    slipOdds.text(data.slipOdds + " $" + data.slipDue + data.minPrice);

                    var options, index, select, option;

                    select = document.getElementById('bet_id');

                    select.options.length = 0;

                    dataBet = data.slipBets; // Or whatever source information you're working with
                    console.log(dataBet)
                    $.each(options, function(index,item) {
                        option = options[index];
                        console.log(option.pk)
                        select.options.add(new Option(item.price, option.pk));
                    });
                },
                error: function(errorData){
                    console.log(errorData)
                }
            });
        });


    });
                    for (i = 0; i < dataSlipBets.length; i++) {

                        tableBet = dataSlipBets[i]
                        slipTableHtml += "<tr><th scope='row'>" + i +"</th><td><a href='#'>" + tableBet.fields.home + ": " + tableBet.fields.type + "</a></td><td>" + tableBet.fields.price + "</td></tr>"
                        $('#slip-table-body').html(slipTableHtml)
                    };