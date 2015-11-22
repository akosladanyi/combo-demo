(function worker() {
  $.ajax({
    url: 'getconnectedclients/',
    success: function(data) {
      //$('.result').html(data);
      console.log('update!');
      for (var i = 0; i < data.length; i++)
      {
        var n_id = data[i]['network_id'];
        var n_el_id = '#client_list_' + n_id;
        var $n_el = $(n_el_id);
        $n_el.empty();
        for (var j = 0; j < data[i]['clients'].length; j++)
        {
          var name = data[i]['clients'][j]['client_name'];
          var ul = data[i]['clients'][j]['ul_speed'].toFixed(2);
          var dl = data[i]['clients'][j]['dl_speed'].toFixed(2);
          $n_el.append('<li>' + name + ' (UL: ' + ul + ' kbps DL: ' + dl + ' kbps)' + '</li>');
        }
      }
    },
    complete: function() {
      setTimeout(worker, 5000);
    }
  });
})();
