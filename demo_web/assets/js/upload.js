// Define processing URL and form element
const url = 'https://demo-web-scorrea.herokuapp.com/sentiment_pred'
const form = document.querySelector('form')


form.addEventListener('submit', e => {
    e.preventDefault()
  
    const files = document.querySelector('[type=file]').files;
    const formData = new FormData();
    formData.append('image', files[0]);

    fetch(url, {
        method: 'POST',
        body: formData,
    })
    .then(function(res){ return res.json(); })
    .then(function(data){ 
        if (data.success) {
            $("#imgalign").html('<img style="width:100%" src="data:image/png;base64,' + data.image[0] + '" />');
            // $("#idtable").html('<tr><th>Face</th><th>Anger</th><th>Happy</th><th>Disgust</th><th>Fear</th> \
            //     <th>Neutral</th><th>Sadness</th><th>Surprise</th></tr>');
            predictions = data.predictions;
            out = '<tr><th>Face</th><th>Anger</th><th>Happy</th><th>Disgust</th><th>Fear</th> \
                    <th>Neutral</th><th>Sadness</th><th>Surprise</th></tr>';
            for (var i=0, item; item=predictions[i]; i++) {
                 out += '<tr><td>'+ item['face'] +'</td><td>'+ item['anger'] + 
                        '</td><td>'+ item['happy'] +'</td><td>'+ item['disgust'] +
                        '</td><td>'+ item['fear'] +'</td><td>'+ item['neutral'] +
                        '</td><td>'+ item['sadness'] +'</td><td>'+ item['surprise'] +
                        '</td></tr> ';
            }
            $("#idtable").html(out);
        }else {console.log('Error')}
    })
  })