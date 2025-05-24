$(document).ready(function() {
    $('#avaliacaoForm').on('submit', function(event) {
        event.preventDefault();

        var formData = {
            name: $('#name').val(),
            balance: parseFloat($('#balance').val()),
            purchases: parseFloat($('#purchases').val()),
            cash_advance: parseFloat($('#cash_advance').val()),
            credit_limit: parseFloat($('#credit_limit').val()),
            payments: parseFloat($('#payments').val())
        };

        $.ajax({
            type: 'POST',
            url: 'http://localhost:8000/avaliar',
            data: JSON.stringify(formData),
            contentType: 'application/json',
            success: function(response) {
                $('#resultado').html('<p>Resultado: ' + response.resposta + '</p>');
            },
            error: function(error) {
                $('#resultado').html('<p>Ocorreu um erro com a análise.</p><p>' + error.message +'</p>');
            }
        });
    });
});